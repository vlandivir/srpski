import os
import re

from datetime import datetime, timedelta

from sqlalchemy import text
from postgres_db import get_pg_engine, get_table_name

BLOCK_HOURS = int(os.getenv('BLOCK_HOURS', '12'))

def insert_new_card(data):
    engine = get_pg_engine()

    match = re.search(r'(\d+)\.webp$', data['image'])
    id = int(match.group(1)) if match else 0

    current_timestamp = datetime.now()

    insert_data = {
        'en': data['en'],
        'ru': data['ru'],
        'sr': data['sr'],
        'image': data['image'],
        'created_at': current_timestamp,
        'updated_at': current_timestamp,
        'id': id,
    }

    with engine.connect() as connection:
        table_names = ['prod_cards', 'docker_cards', 'local_cards']

        for table_name in table_names:
            insert_query = text(f"""
                INSERT INTO {table_name} (id, en, ru, sr, image, generated_at, created_at, updated_at)
                VALUES (:id, :en, :ru, :sr, :image, :id, :created_at, :updated_at)
                ON CONFLICT (image) DO NOTHING;
            """)

            connection.execute(insert_query, insert_data)

def update_card(id, data):
    engine = get_pg_engine()

    update_data = {
        'id': id,
        'updated_at': datetime.now(),
        **data
    }

    with engine.connect() as connection:
        table_names = ['docker_cards', 'local_cards', 'prod_cards']

        for table_name in table_names:
            update_query = text(f"""
                update {table_name}
                set en=:en, ru=:ru, sr=:sr, updated_at=:updated_at
                where id=:id
                returning image
            """)

            image = connection.execute(update_query, update_data)

    return image.scalar_one_or_none()

def get_card_with_weight(user_id, card_id):
    engine = get_pg_engine()
    n_hours_ago = datetime.now() - timedelta(hours=BLOCK_HOURS)

    query = text(f"""
        select c.*, card_weight, user_response,
            case when ucr.user_id is null then 100
                when ucr.created_at > :n_hours_ago then -1 / card_weight
                else card_weight
            end as corrected_weight
            from {get_table_name('cards')} c
            left join {get_table_name('user_card_responses')} ucr
            on c.id = ucr.card_id
            where c.id = :card_id and ucr.user_id = :user_id
            order by ucr.created_at desc
            limit 1
        ;
    """)

    with engine.connect() as connection:
        image = connection.execute(query, {
            "user_id": user_id,
            "card_id": card_id,
            "n_hours_ago": n_hours_ago,
        })

    return image.first()._asdict()

