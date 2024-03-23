import io
import os
import json
import boto3

from functools import cache
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
from PIL import Image, ImageFilter

from cards_add_text import add_text_to_image

load_dotenv('.env')
DO_SPACES_ACCESS_KEY = os.getenv('DO_SPACES_ACCESS_KEY')
DO_SPACES_SECRET_KEY = os.getenv('DO_SPACES_SECRET_KEY')

script_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(script_dir, 'NimbusSanLRegular.ttf')

json_file = os.path.join(script_dir, 'language-images.json')
with open(json_file, 'r', encoding='utf-8') as file:
    cards_data = json.load(file)

@cache
def get_do_space_client():
    endpoint_url = 'https://fra1.digitaloceanspaces.com'
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name='fra1',
        endpoint_url=endpoint_url,
        aws_access_key_id=DO_SPACES_ACCESS_KEY,
        aws_secret_access_key=DO_SPACES_SECRET_KEY
    )
    return client

def file_exists_in_do_space(bucket_name, file_path):
    client = get_do_space_client()
    response = client.list_objects_v2(Bucket=bucket_name, Prefix=file_path)
    for obj in response.get('Contents', []):
        if obj['Key'] == file_path:
            return True
    return False

def upload_files_to_digital_ocean_spaces(bucket_name, do_folder, local_folder):
    client = get_do_space_client()
    try:
        for filename in os.listdir(local_folder):
            local_path = os.path.join(local_folder, filename)
            do_path = os.path.join(do_folder, filename)
            if not file_exists_in_do_space(bucket_name, do_path):
                client.upload_file(local_path, bucket_name, do_path, ExtraArgs={'ACL': 'public-read'})
                print(f"File {filename} uploaded to {do_path}")
    except FileNotFoundError:
        print("The specified folder does not exist")
    except NoCredentialsError:
        print("Credentials not available")

def add_text_to_image_do(bucket_name, source_folder, target_folder, image_name):
    client = get_do_space_client()

    image_obj = client.get_object(Bucket=bucket_name, Key=f'{source_folder}{image_name}')
    image_content = image_obj['Body'].read()
    original_image = Image.open(io.BytesIO(image_content))

    card = next((obj for obj in cards_data if obj['image'] == image_name), None)
    new_image = add_text_to_image(original_image, card['sr'], card['en'], card['ru'], font_path)

    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='WEBP')
    img_byte_arr = img_byte_arr.getvalue()

    print(image_name)
    # new_image.save(os.path.join(script_dir, '..', 'temp', image_name));
    client.put_object(Bucket=bucket_name, Key=f'{target_folder}{image_name}', Body=img_byte_arr, ACL='public-read', ContentType='image/webp')

def sync_missing_cards(bucket_name, source_folder, target_folder):
    client = get_do_space_client()
    source_files = client.list_objects_v2(Bucket=bucket_name, Prefix=source_folder).get('Contents', [])
    target_files = client.list_objects_v2(Bucket=bucket_name, Prefix=target_folder).get('Contents', [])

    source_file_names = {file['Key'].split('/')[-1] for file in source_files}
    target_file_names = {file['Key'].split('/')[-1] for file in target_files}

    print(target_file_names - source_file_names)

    print(len(source_file_names), len(target_file_names))
    missing_files = source_file_names - target_file_names

    for file_path in missing_files:
        add_text_to_image_do(bucket_name, source_folder, target_folder, file_path)
