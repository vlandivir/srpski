from sqlalchemy import text
from postgres_db import get_table_name, get_key_name

add_card_id = text(f"""
    DROP TRIGGER IF EXISTS update_cards_updated_at ON {get_table_name('cards')};
    DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

    ALTER TABLE {get_table_name('cards')} ADD COLUMN id BIGINT NOT NULL DEFAULT 0;
    UPDATE {get_table_name('cards')} SET id = generated_at;

    -- ALTER TABLE {get_table_name('cards')} ADD CONSTRAINT cards_id_unique UNIQUE (id);

    ALTER TABLE {get_table_name('user_card_responses')} DROP CONSTRAINT {get_key_name('user_card_responses_card_image_fkey')};

    ALTER TABLE {get_table_name('cards')} DROP CONSTRAINT {get_key_name('cards_pkey')};
    ALTER TABLE {get_table_name('cards')} ADD PRIMARY KEY (id);

    ALTER TABLE {get_table_name('user_card_responses')} ADD COLUMN card_id BIGINT NOT NULL DEFAULT 0;
    UPDATE {get_table_name('user_card_responses')}
    SET card_id = {get_table_name('cards')}.id
    FROM {get_table_name('cards')}
    WHERE {get_table_name('user_card_responses')}.card_image = {get_table_name('cards')}.image;

    -- ALTER TABLE {get_table_name('user_card_responses')} DROP COLUMN card_image;

    ALTER TABLE {get_table_name('user_card_responses')} ADD CONSTRAINT fk_card_id
    FOREIGN KEY (card_id) REFERENCES {get_table_name('cards')}(id);

    INSERT INTO {get_table_name('db_history')} (version) VALUES (2);
    COMMIT;
""")

# defaultdb=> select count(*) from local_cards;
#  count
# -------
#    166
# (1 row)

# defaultdb=> select count(*) from local_user_card_responses;
#  count
# -------
#    151
# (1 row)
