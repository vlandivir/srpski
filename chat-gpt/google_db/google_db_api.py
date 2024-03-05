import os
import gspread

from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_file = os.path.join(current_dir, '..', '..', 'keys', 'srpski-data-e364d16a7d45.json')

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
    client = gspread.authorize(creds)

    return client
