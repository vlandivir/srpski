import re

from datetime import datetime

from sqlalchemy import text

from postgres_db import get_pg_engine

def insert_new_card(data):
    engine = get_pg_engine()

    match = re.search(r'(\d+)\.webp$', data['image'])
    generated_at = int(match.group(1)) if match else 0
    current_timestamp = datetime.now()

    insert_data = {
        'en': data['en'],
        'ru': data['ru'],
        'sr': data['sr'],
        'image': data['image'],
        'generated_at': generated_at,
        'created_at': current_timestamp,
        'updated_at': current_timestamp
    }

    with engine.connect() as connection:
        table_names = ['prod_cards', 'docker_cards', 'local_cards']

        for table_name in table_names:
            insert_query = text(f"""
                INSERT INTO {table_name} (en, ru, sr, image, generated_at, created_at, updated_at)
                VALUES (:en, :ru, :sr, :image, :generated_at, :created_at, :updated_at)
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
                where generated_at=:id
                returning image
            """)

            image = connection.execute(update_query, update_data)

    return image.scalar_one_or_none()
