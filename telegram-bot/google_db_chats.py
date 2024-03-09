from google_db_api import get_or_create_google_sheet, get_gspread_client, update_sheet_with_dict

def get_or_create_chat_data(chat_key, data):
    sheet_data = get_or_create_google_sheet(chat_key)

    client = get_gspread_client();

    if (sheet_data['is_new']):
        spreadsheet = client.open_by_key(sheet_data['id'])

        worksheet_list = spreadsheet.worksheets()
        worksheet_list[0].update_title('Chat')

        spreadsheet.add_worksheet(title='Messages', rows=100, cols=10)

    return update_sheet_with_dict(sheet_data['id'], 'Chat', data)