import json
import time

from sys import getsizeof
from pympler import asizeof

from google_db_api import get_gspread_client

def get_cards():
    client = get_gspread_client()

    sheet_id = '1rnD7wWNl8NqyKL3amafrArzHmapA1QrrsB7PAAWR-7w'
    sheet_name = 'Cards'

    start_time = time.time()

    worksheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    data = worksheet.get_all_records()

    elapsed_time = time.time() - start_time

    json_string = json.dumps(data, indent=0) # indent=4 делает вывод читаемым
    size_sys = getsizeof(json_string)
    size_pympler = asizeof.asizeof(data)

    print(f'Data string count: {len(data)}')
    print(f'Load time: {elapsed_time} seconds')
    print(f"Data size as text: {size_sys} bytes")
    print(f"Full data size: {size_pympler} bytes")

    return data
