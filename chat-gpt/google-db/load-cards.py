import os
import json
import time
import gspread

from sys import getsizeof
from pympler import asizeof

from oauth2client.service_account import ServiceAccountCredentials

current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_file = os.path.join(current_dir, '..', '..', 'keys', 'srpski-data-e364d16a7d45.json')
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
client = gspread.authorize(creds)

sheet_id = '1rnD7wWNl8NqyKL3amafrArzHmapA1QrrsB7PAAWR-7w'
sheet_name = 'Cards'

start_time = time.time()

sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
data = sheet.get_all_records()

elapsed_time = time.time() - start_time

json_string = json.dumps(data, indent=0) # indent=4 делает вывод читаемым
size_sys = getsizeof(json_string)
size_pympler = asizeof.asizeof(data)

print(f'Data string count: {len(data)}')
print(f'Load time: {elapsed_time} seconds')
print(f"Data size as text: {size_sys} bytes")
print(f"Full data size: {size_pympler} bytes")
