import os
import json
import logging

from functools import cache
from dotenv import load_dotenv

from sqlalchemy import create_engine, text

load_dotenv('.env')
POSTGRES_CONNECTION_STRING = os.getenv('POSTGRES_CONNECTION_STRING')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@cache
def get_pg_engine(autocommit = True):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    certificate = os.path.join(current_dir, '..', 'keys', 'ca-certificate.crt')
    engine = create_engine(POSTGRES_CONNECTION_STRING, connect_args={
        'sslmode': 'verify-full',
        'sslrootcert': certificate,
    })

    if autocommit:
        return engine.execution_options(isolation_level="AUTOCOMMIT")

    return engine

def get_table_name(table_name):
    return f'public.{ENVIRONMENT.lower()}_{table_name}'

def get_or_create_user(user):
    engine = get_pg_engine()

    select_query = text(f"select * from {get_table_name('users')} where id = :id")
    insert_query = text(f"""
        insert into {get_table_name('users')}
            (id, first_name, last_name, username, language_code)
        values (:id, :first_name, :last_name, :username, :language_code)
    """)

    with engine.connect() as connection:
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
    engine = get_pg_engine()

    update_query = text(f"""
        update {get_table_name('users')} set current_set = :current_set where id = :id
    """)

    with engine.connect() as connection:
        try:
            connection.execute(update_query, {**user, 'current_set': json.dumps(current_set)})
            return user
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

def get_all_cards():
    engine = get_pg_engine()

    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM {get_table_name('cards')};"))
        rows = result.fetchall()
        rows_as_dicts = [row._asdict() for row in rows]
        return rows_as_dicts