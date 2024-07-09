import os
import pprint

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv('.env')

client = OpenAI(
    api_key = os.getenv('OPEN_API_TEST'),
)

def get_vector_store(store_name):
    stores_list = client.beta.vector_stores.list()
    for vector_store in stores_list.data:
        if vector_store.name == store_name:
            return vector_store

    vector_store = client.beta.vector_stores.create(name = store_name)
    return vector_store

STORE_NAME = 'vlandivir_dairy'
vector_store = get_vector_store(STORE_NAME)
pprint.pprint(vector_store.to_dict())
print('\n')

all_files = list(client.beta.vector_stores.files.list(vector_store.id))
pprint.pprint(all_files)
print('\n')

script_dir = os.path.dirname(os.path.abspath(__file__))
dairy_dir = os.path.join(script_dir, '..', 'dnevnik')

file_paths = []
for filename in os.listdir(dairy_dir):
    file_paths.append(os.path.join(dairy_dir, filename))
pprint.pprint(file_paths)
pprint.pprint(len(file_paths))

file_streams = [open(path, "rb") for path in file_paths]
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
   vector_store_id=vector_store.id, files=file_streams,
)

# pprint.pprint(file_batch.to_dict())

# gpt-3.5-turbo-1106
# gpt-4o
