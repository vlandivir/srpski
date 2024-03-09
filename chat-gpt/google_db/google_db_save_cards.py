import os
import json

from google_db_api import get_gspread_client

def update_or_add_rows(worksheet, data):
    existing_rows = worksheet.get_all_records()
    existing_images = {row['image']: i+2 for i, row in enumerate(existing_rows)}  # +2 т.к. индексация начинается с 1, и есть заголовок

    for item in data:
        row = [item['en'], item['ru'], item['sr'], item['image']]
        if item['image'] in existing_images:
            # Обновляем существующую строку
            # worksheet.update(f'A{existing_images[item["image"]]}:D{existing_images[item["image"]]}', [row])
            worksheet.update(range_name=f'A{existing_images[item["image"]]}:D{existing_images[item["image"]]}', values=[row])
        else:
            # Добавляем новую строку
            worksheet.append_row(row)


def add_missing_columns(worksheet, required_columns):
    existing_headers = worksheet.row_values(1)
    current_cols = len(existing_headers)

    for column_name in required_columns:
        if column_name not in existing_headers:
            current_cols += 1
            worksheet.update_cell(1, current_cols, column_name)

client = get_gspread_client()

sheet_id = '1rnD7wWNl8NqyKL3amafrArzHmapA1QrrsB7PAAWR-7w'
sheet_name = 'Cards'
worksheet = client.open_by_key(sheet_id).worksheet('Cards')

required_headers = ['en', 'ru', 'sr', 'image']
add_missing_columns(worksheet, required_headers)

current_dir = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(current_dir, '..', 'language-cards', 'language-images.json')
with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Вызов функции для обновления/добавления данных
update_or_add_rows(worksheet, data)
