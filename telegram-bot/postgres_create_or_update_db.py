from sqlalchemy import text

from postgres_db import get_pg_engine, get_table_name

import migrations.migrations_001_initial
import migrations.migrations_002_card_id

select_db_version =  text(f"""
    select max(version) from {get_table_name('db_history')};
""")

def create_or_update_db():
    engine = get_pg_engine(False)

    with engine.connect() as connection:
        current_version = 0

        try:
            current_version = connection.execute(select_db_version).scalar()
        except Exception as e:
            # do nothing
            print(e)

        print(f'DB VERSION: {current_version} {get_table_name('db_history')}')

        if current_version == 0:
            connection.execute(migrations.migrations_001_initial.create_table_users)
            connection.execute(migrations.migrations_001_initial.create_table_cards)
            connection.execute(migrations.migrations_001_initial.create_table_user_card_responses)
            connection.execute(migrations.migrations_001_initial.create_table_db_history)

        if current_version == 1:
            connection.execute(migrations.migrations_002_card_id.add_card_id)
