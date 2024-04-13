from sqlalchemy import text
from postgres_db import get_table_name

run = text(f"""
    ALTER TABLE {get_table_name('user_card_responses')} DROP COLUMN card_image;

    ALTER TABLE {get_table_name('cards')} ADD COLUMN author_id character varying(255);

    ALTER TABLE {get_table_name('cards')} ADD COLUMN notes text;

    ALTER TABLE {get_table_name('cards')} ADD CONSTRAINT fk_author FOREIGN KEY (author_id) REFERENCES {get_table_name('users')} ON DELETE SET NULL;

    COMMIT;
""")
