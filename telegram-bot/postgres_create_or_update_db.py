from sqlalchemy import text

from postgres_db import get_pg_engine, get_table_name

create_table_users = text(f"""
    CREATE TABLE IF NOT EXISTS {get_table_name('users')} (
        id VARCHAR(255) PRIMARY KEY,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        username VARCHAR(255),
        language_code CHAR(2),
        current_set JSONB
    );
    COMMIT;
""")

create_table_cards = text(f"""
    CREATE TABLE IF NOT EXISTS {get_table_name('cards')} (
        en TEXT NOT NULL,
        ru TEXT NOT NULL,
        sr TEXT NOT NULL,
        image VARCHAR(255) UNIQUE,
        generated_at BIGINT NOT NULL,
        tags TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (image)
    );

    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE TRIGGER update_cards_updated_at BEFORE UPDATE
    ON {get_table_name('cards')} FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE INDEX IF NOT EXISTS cards_generated_at_idx ON {get_table_name('cards')} (generated_at);

    COMMIT;
""")

def create_or_update_db():
    engine = get_pg_engine(False)

    with engine.connect() as connection:
        connection.execute(create_table_users)
        connection.execute(create_table_cards)
