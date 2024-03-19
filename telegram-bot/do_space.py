import os
import boto3

from functools import cache
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

load_dotenv('.env')
DO_SPACES_ACCESS_KEY = os.getenv('DO_SPACES_ACCESS_KEY')
DO_SPACES_SECRET_KEY = os.getenv('DO_SPACES_SECRET_KEY')

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
