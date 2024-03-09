import os
import json
import gspread

from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

FOLDER_ID = '1UP-LExkCE0jJDQ3NSnlyNXzFv86eIoiJ'

GSPREAD_CLIENT = None

current_dir = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(current_dir, '..', 'keys', 'srpski-data-e364d16a7d45.json')

def get_gspread_client():
    global GSPREAD_CLIENT

    if GSPREAD_CLIENT is not None:
        return GSPREAD_CLIENT

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    GSPREAD_CLIENT = gspread.authorize(creds)

    return GSPREAD_CLIENT

def get_or_create_google_sheet(file_name):
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )

    drive_service = build('drive', 'v3', credentials=credentials)

    query = f"name = '{file_name}' and '{FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    if files:
        print(f'File already exists. ID: {files[0].get('id')}')
        return { 'id': files[0].get('id'), 'is_new': False }

    file_metadata = {
        'name': file_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [FOLDER_ID]
    }

    file = drive_service.files().create(body=file_metadata, fields='id').execute()

    print('File ID: %s' % file.get('id'))

    return { 'id': file.get('id'), 'is_new': True }

def add_missing_columns(worksheet, required_columns):
    existing_headers = worksheet.row_values(1)
    current_cols = len(existing_headers)

    for column_name in required_columns:
        if column_name not in existing_headers:
            current_cols += 1
            worksheet.update_cell(1, current_cols, column_name)

def update_sheet_with_dict(spreadsheet_id, worksheet_title, data_dict):
    client = get_gspread_client()
    try:
        sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_title)
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open_by_key(spreadsheet_id).add_worksheet(title=worksheet_title, rows=100, cols=10)

    required_headers = ['key', 'value', 'updated_at']
    add_missing_columns(sheet, required_headers)

    existing_rows = sheet.get_all_records()
    existing_keys = {row['key']: row for row in existing_rows}

    key_to_row_number = {}
    for index, row in enumerate(existing_rows, start=2):  # Начинаем с 2, т.к. 1 - это заголовок
        key_to_row_number[row['key']] = index

    row_index = len(existing_rows) + 2  # Начальный индекс для новых строк (учитывая заголовок)
    for key, value in data_dict.items():
        if isinstance(value, dict):
            value = str(value)
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if key in existing_keys:
            existing_row = existing_keys[key]
            if existing_row['value'] != value:
                cell_range = f"B{key_to_row_number[key]}:C{key_to_row_number[key]}"
                sheet.update(cell_range, [[value, update_time]])
        else:
            sheet.append_row([key, value, update_time], table_range=f"A{row_index}")
            row_index += 1

    updated_rows = sheet.get_all_records()
    updated_dict = {row['key']: json.loads(row['value']) if row['value'].startswith('{') else row['value'] for row in updated_rows}

    return updated_dict
