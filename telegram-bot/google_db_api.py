import os
import gspread

from googleapiclient.discovery import build

from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

FOLDER_ID = '1UP-LExkCE0jJDQ3NSnlyNXzFv86eIoiJ'

GSPREAD_CLIENT = None

current_dir = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(current_dir, '..', 'keys', 'srpski-data-e364d16a7d45.json')

def get_gspread_client():
    global SERVICE_ACCOUNT_FILE
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

def create_or_get_google_sheet(file_name):
    global SERVICE_ACCOUNT_FILE
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
        return files[0].get('id')

    file_metadata = {
        'name': file_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [FOLDER_ID]
    }

    file = drive_service.files().create(body=file_metadata, fields='id').execute()

    print('File ID: %s' % file.get('id'))

    return file.get('id')
