import os
import json
import logging
import sentry_sdk

from decimal import Decimal
from dotenv import load_dotenv
from functools import cache

from datetime import datetime, timedelta

from sqlalchemy import create_engine, text

load_dotenv('.env')
POSTGRES_CONNECTION_STRING = os.getenv('POSTGRES_CONNECTION_STRING')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')
BLOCK_HOURS = int(os.getenv('BLOCK_HOURS', '12'))

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@cache
def get_pg_engine(autocommit = True):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    certificate = os.path.join(current_dir, '..', 'keys', 'ca-certificate.crt')
    engine = create_engine(POSTGRES_CONNECTION_STRING, connect_args={
        'sslmode': 'verify-full',
        'sslrootcert': certificate,
    })

    if autocommit:
        return engine.execution_options(isolation_level="AUTOCOMMIT")

    return engine

def get_key_name(key_name):
    return f'{ENVIRONMENT.lower()}_{key_name}'

def get_table_name(table_name):
    return f'public.{ENVIRONMENT.lower()}_{table_name}'

def get_or_create_user(user):
    engine = get_pg_engine()

    select_query = text(f"select * from {get_table_name('users')} where id = :id")
    insert_query = text(f"""
        insert into {get_table_name('users')}
            (id, first_name, last_name, username, language_code)
        values (:id, :first_name, :last_name, :username, :language_code)
    """)

    with engine.connect() as connection:
        result = connection.execute(select_query, user).fetchone()
        if result:
            return result._asdict()
        else:
            try:
                connection.execute(insert_query, user)
                return user
            except Exception as e:
                print(f"Error occurred: {e}")
                return None

def update_user_current_set(user, current_set):
    engine = get_pg_engine()

    update_query = text(f"""
        update {get_table_name('users')} set current_set = :current_set where id = :id
    """)

    with engine.connect() as connection:
        try:
            connection.execute(update_query, {**user, 'current_set': json.dumps(current_set)})
            return user
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

def get_all_cards():
    engine = get_pg_engine()

    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM {get_table_name('cards')};"))
        rows = result.fetchall()
        rows_as_dicts = [row._asdict() for row in rows]
        return rows_as_dicts

def update_user_card_response(user_id, card_id, user_response):
    engine = get_pg_engine()

    response_weight_multipliers = {
        'button_complex': 4,
        'button_hard': 2,
        'button_ok': 0.5,
        'button_easy': 0.25,
        'button_hide': 1,
    }

    with engine.connect() as connection:
        latest_response_query = text(f"""
            SELECT card_weight, card_id, user_response
            FROM {get_table_name('user_card_responses')}
            WHERE user_id = :user_id AND card_id = :card_id
            ORDER BY created_at DESC
            LIMIT 1
        """)

        latest_response = connection.execute(
            latest_response_query, {"user_id": user_id, "card_id": card_id}
        ).mappings().first()

        if latest_response:
            if latest_response['user_response'] == 'button_hide':
                return

            new_weight = latest_response['card_weight'] * response_weight_multipliers[user_response]
        else:
            new_weight = 1024 * response_weight_multipliers[user_response]

        if new_weight >= 128 and (user_response == 'button_ok' or user_response == 'button_easy'):
            new_weight = new_weight / 2

        insert_response_query = text(f"""
            INSERT INTO {get_table_name('user_card_responses')} (user_id, card_id, card_image, user_response, card_weight)
            VALUES (:user_id, :card_id, :card_image, :user_response, :new_weight)
        """)

        connection.execute(insert_response_query, {
            "user_id": user_id,
            "card_id": card_id,
            "card_image": f"image_{card_id}",
            "user_response": user_response,
            "new_weight": new_weight
        })

def get_new_cards_pack(user_id):
    engine = get_pg_engine()

    n_hours_ago = datetime.now() - timedelta(hours=BLOCK_HOURS)
    select_images_query = text(f"""
        with
        last_card_responses as (
            select distinct on (card_id) *
            from {get_table_name('user_card_responses')}
            where user_id = :user_id
            order by card_id, created_at desc
        ),
        candidate_cards as (
            select c.image, c.id, ucr.card_weight, ucr.user_id, ucr.created_at, ucr.user_response,
                    case when ucr.user_id is null then 100
                        when ucr.created_at > :n_hours_ago then -1 / card_weight
                        else card_weight
                    end as corrected_weight
                from {get_table_name('cards')} c
                left join last_card_responses ucr
                on c.id = ucr.card_id
        )
        select random() * corrected_weight as rnd, *
            from candidate_cards
            where coalesce(user_response, '') != 'button_hide'
            order by 1 desc
            limit 20
        ;
    """)

    with engine.connect() as connection:
        with sentry_sdk.start_transaction(name="get_new_cards_pack"):
            result = connection.execute(
                select_images_query,
                {'user_id': user_id, 'n_hours_ago': n_hours_ago}
            ).fetchall()

    cards_list = [[row_dict['id'], row_dict['card_weight']] for row_dict in (row._asdict() for row in result)]
    return cards_list

def get_user_stats (user_id):
    engine = get_pg_engine()

    get_stats_query = text(f"""
        WITH ranked_responses AS (
            SELECT
                user_id,
                card_id,
                DATE(created_at) AS response_date,
                user_response,
                ROW_NUMBER() OVER (PARTITION BY user_id, card_id, DATE(created_at) ORDER BY created_at DESC) AS rank
            FROM {get_table_name('user_card_responses')}
            WHERE user_id = :user_id AND DATE(created_at) BETWEEN CURRENT_DATE - INTERVAL '4 day' AND CURRENT_DATE
        ),
        filtered_responses AS (
            SELECT
                response_date,
                user_response,
                COUNT(card_id) AS cards_per_response
            FROM ranked_responses
            WHERE rank = 1
                AND user_response IN ('button_easy', 'button_ok', 'button_hard', 'button_complex')
            GROUP BY response_date, user_response
        )
        SELECT
            TO_CHAR(response_date, 'DD Mon') as response_date,
            SUM(CASE WHEN user_response = 'button_complex' THEN cards_per_response ELSE 0 END) AS complex,
            SUM(CASE WHEN user_response = 'button_hard' THEN cards_per_response ELSE 0 END) AS hard,
            SUM(CASE WHEN user_response = 'button_ok' THEN cards_per_response ELSE 0 END) AS ok,
            SUM(CASE WHEN user_response = 'button_easy' THEN cards_per_response ELSE 0 END) AS easy
            FROM filtered_responses
        GROUP BY response_date
        ORDER BY response_date;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            get_stats_query,
            {'user_id': user_id}
        ).fetchall()

    result_dicts = [{key: int(value) if isinstance(value, Decimal) else value for key, value in row._asdict().items()} for row in result]
    return result_dicts
