from sqlalchemy import text
from postgres_db import get_table_name

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

create_table_user_card_responses = text(f"""
    CREATE TABLE IF NOT EXISTS {get_table_name('user_card_responses')} (
        user_id VARCHAR(255) NOT NULL,
        card_image VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        user_response TEXT NOT NULL,
        card_weight FLOAT NOT NULL DEFAULT 1024,
        PRIMARY KEY (user_id, card_image, created_at),
        FOREIGN KEY (user_id) REFERENCES {get_table_name('users')}(id),
        FOREIGN KEY (card_image) REFERENCES {get_table_name('cards')}(image)
    );

    COMMIT;
""")

create_table_db_history = text(f"""
    CREATE TABLE IF NOT EXISTS {get_table_name('db_history')} (
        version INTEGER PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    INSERT INTO {get_table_name('db_history')} (version) VALUES (1);

    COMMIT;
""")
