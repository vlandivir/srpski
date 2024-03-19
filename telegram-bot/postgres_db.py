import os
import json
import random
import logging

from functools import cache
from dotenv import load_dotenv

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

def update_user_card_response(user_id, generated_at, user_response):
    engine = get_pg_engine()

    response_weight_multipliers = {
        'button_complex': 4,
        'button_hard': 2,
        'button_ok': 0.5,
        'button_easy': 0.25,
    }

    with engine.connect() as connection:
        card_image_query = text(f"""
            SELECT image FROM {get_table_name('cards')}
            WHERE generated_at = :generated_at
            LIMIT 1
        """)
        card_image_result = connection.execute(card_image_query, {"generated_at": int(generated_at)}).mappings().first()
        if not card_image_result:
            return

        print(card_image_result)
        card_image = card_image_result['image']

        latest_response_query = text(f"""
            SELECT card_weight, card_image FROM {get_table_name('user_card_responses')}
            WHERE user_id = :user_id AND card_image = :card_image
            ORDER BY created_at DESC
            LIMIT 1
        """)
        latest_response = connection.execute(latest_response_query, {"user_id": user_id, "card_image": card_image}).mappings().first()

        if latest_response:
            new_weight = latest_response['card_weight'] * response_weight_multipliers[user_response]
        else:
            new_weight = 1024 * response_weight_multipliers[user_response]

        insert_response_query = text(f"""
            INSERT INTO {get_table_name('user_card_responses')} (user_id, card_image, user_response, card_weight)
            VALUES (:user_id, :card_image, :user_response, :new_weight)
        """)

        connection.execute(insert_response_query, {
            "user_id": user_id,
            "card_image": card_image,
            "user_response": user_response,
            "new_weight": new_weight
        })

def get_new_cards_pack(user_id):
    engine = get_pg_engine()

    n_hours_ago = datetime.now() - timedelta(hours=BLOCK_HOURS)
    select_images_query = text(f"""
        with
        last_card_responses as (
            select distinct on (card_image) *
            from {get_table_name('user_card_responses')}
            order by card_image, created_at desc
        ),
        candidate_cards as (
            select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at,
                    case when ucr.user_id is null then 100
                        when ucr.created_at > '2024-03-19 00:00:00' then -1 / card_weight
                        else card_weight
                    end as corrected_weight
                from {get_table_name('cards')} c
                left join last_card_responses ucr
                on c.image = ucr.card_image
                order by generated_at
        )
        select random() * corrected_weight as rnd, *
            from candidate_cards
            order by 1 desc
            limit 20
        ;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            select_images_query,
            {'user_id': user_id, 'n_hours_ago': n_hours_ago}
        ).fetchall()

    cards_list = [[row_dict['generated_at'], row_dict['card_weight']] for row_dict in (row._asdict() for row in result)]
    return cards_list
