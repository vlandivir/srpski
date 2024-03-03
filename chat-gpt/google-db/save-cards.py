import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
    # Получаем текущие заголовки
    existing_headers = worksheet.row_values(1)
    current_cols = len(existing_headers)
    
    # Проверяем и добавляем недостающие заголовки
    for column_name in required_columns:
        if column_name not in existing_headers:
            # Добавляем новую колонку (в gspread нет прямой функции для этого, поэтому мы добавляем ячейку в новую колонку)
            current_cols += 1
            worksheet.update_cell(1, current_cols, column_name)

# Путь к файлу ключа сервисного аккаунта
# Абсолютный путь к директории текущего исполняемого файла
current_dir = os.path.dirname(os.path.abspath(__file__))

# Формирование относительного пути к файлу ключа
service_account_file = os.path.join(current_dir, '..', '..', 'keys', 'srpski-data-e364d16a7d45.json')

# Скопируйте и вставьте URL вашей Google таблицы
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1rnD7wWNl8NqyKL3amafrArzHmapA1QrrsB7PAAWR-7w/edit'

# Аутентификация и открытие таблицы
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
gc = gspread.authorize(credentials)

# Открытие таблицы по URL
sh = gc.open_by_url(spreadsheet_url)
worksheet = sh.sheet1

required_headers = ["en", "ru", "sr", "image"]
add_missing_columns(worksheet, required_headers)

json_file = os.path.join(current_dir, '..', 'language-cards', 'language-images.json')
with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Вызов функции для обновления/добавления данных
update_or_add_rows(worksheet, data)
