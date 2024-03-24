import os
import re
import json

from datetime import datetime

from sqlalchemy import text

from postgres_db import get_pg_engine, get_table_name

def insert_cards(table_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, '..', 'chat-gpt', 'language-cards', 'language-images.json')
    with open(json_file, 'r', encoding='utf-8') as file:
        data_array = json.load(file)

    insert_data_list = []

    for data in data_array:
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
        insert_data_list.append(insert_data)

    query = text(f"""
        INSERT INTO {table_name} (en, ru, sr, image, generated_at, created_at, updated_at)
        VALUES (:en, :ru, :sr, :image, :generated_at, :created_at, :updated_at)
        ON CONFLICT (image) DO NOTHING;
    """)

    engine = get_pg_engine()

    with engine.connect() as connection:
        connection.execute(query, insert_data_list)

def main():
    insert_cards('prod_cards')
    insert_cards('docker_cards')
    insert_cards(get_table_name('cards'))

if __name__ == '__main__':
    main()