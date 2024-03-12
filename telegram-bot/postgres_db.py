import os
import json
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
    'sslrootcert': certificate,
})

autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

def get_table_name(table_name):
    return f'public.{ENVIRONMENT.lower()}_{table_name}'

def create_or_update_db():
    create_table_chats = text(f"""
        CREATE TABLE IF NOT EXISTS {get_table_name('users')} (
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

def get_or_create_user(user):
    select_query = text(f"select * from {get_table_name('users')} where id = :id")
    insert_query = text(f"""
        insert into {get_table_name('users')}
            (id, first_name, last_name, username, language_code)
        values (:id, :first_name, :last_name, :username, :language_code)
    """)

    with autocommit_engine.connect() as connection:
        result = connection.execute(select_query, user).fetchone()
        if result:
            return result._asdict()
        else:
            try:
                connection.execute(insert_query, user)
                return user
            except Exception as e:
                print(f"Error occurred: {e}")
                return None

def update_user_current_set(user, current_set):
    update_query = text(f"""
        update {get_table_name('users')} set current_set = :current_set where id = :id
    """)
    with autocommit_engine.connect() as connection:
        try:
            connection.execute(update_query, {**user, 'current_set': json.dumps(current_set)})
            return user
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
