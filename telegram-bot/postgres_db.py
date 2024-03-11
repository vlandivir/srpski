import os
import logging

from dotenv import load_dotenv

from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, VARCHAR, JSON, select, text

load_dotenv('.env')
POSTGRES_CONNECTION_STRING = os.getenv('POSTGRES_CONNECTION_STRING')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

current_dir = os.path.dirname(os.path.abspath(__file__))
certificate = os.path.join(current_dir, '..', 'keys', 'ca-certificate.crt')
engine = create_engine(POSTGRES_CONNECTION_STRING, connect_args={
    'sslmode': 'verify-full',
    'sslrootcert': certificate
})

def get_table_name(table_name):
    return f'public.{ENVIRONMENT.lower()}_{table_name}'

# def fetch_all_rows(table_name):
#     with engine.connect() as connection:
#         metadata = MetaData(bind=engine)
#         table = Table(table_name, metadata, autoload_with=engine)
#         query = select([table])
#         result = connection.execute(query)
#         return [dict(row) for row in result]

def create_or_update_db():
    create_table_chats = text(f"""
        CREATE TABLE IF NOT EXISTS {get_table_name('chats')} (
            id VARCHAR(255) PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            username VARCHAR(255),
            language_code CHAR(2),
            current_set JSONB
        );
    """)

    with engine.connect() as connection:
        connection.execute(create_table_chats)
        connection.commit()
