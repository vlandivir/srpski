SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'prod_cards';

 column_name  |        data_type         | character_maximum_length
--------------+--------------------------+--------------------------
 updated_at   | timestamp with time zone |
 generated_at | bigint                   |
 created_at   | timestamp with time zone |
 image        | character varying        |                      255
 en           | text                     |
 tags         | ARRAY                    |
 ru           | text                     |
 sr           | text                     |
(8 rows)

\d prod_cards

                             Table "public.prod_cards"
    Column    |           Type           | Collation | Nullable |      Default
--------------+--------------------------+-----------+----------+-------------------
 en           | text                     |           | not null |
 ru           | text                     |           | not null |
 sr           | text                     |           | not null |
 image        | character varying(255)   |           | not null |
 generated_at | bigint                   |           | not null |
 tags         | text[]                   |           |          |
 created_at   | timestamp with time zone |           |          | CURRENT_TIMESTAMP
 updated_at   | timestamp with time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "prod_cards_pkey" PRIMARY KEY, btree (image)
Referenced by:
    TABLE "prod_user_card_responses" CONSTRAINT "prod_user_card_responses_card_image_fkey" FOREIGN KEY (card_image) REFERENCES prod_cards(image)
Triggers:
    update_cards_updated_at BEFORE UPDATE ON prod_cards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()

===

    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        username VARCHAR(255),
        language_code CHAR(2),
        current_set JSONB
    );

    CREATE TABLE IF NOT EXISTS cards (
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
    ON cards FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE INDEX IF NOT EXISTS cards_generated_at_idx ON cards (generated_at);

    CREATE TABLE IF NOT EXISTS user_card_responses (
        user_id VARCHAR(255) NOT NULL,
        card_image VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        user_response TEXT NOT NULL,
        card_weight FLOAT NOT NULL DEFAULT 1024,
        PRIMARY KEY (user_id, card_image, created_at),
        FOREIGN KEY (user_id) REFERENCES {get_table_name('users')}(id),
        FOREIGN KEY (card_image) REFERENCES {get_table_name('cards')}(image)
    );

У меня есть вот такой скрипт для создания БД. Какие запросы надо сделать для таких изменений.

1. удалить триггер update_cards_updated_at
2. удалить функцию update_updated_at_column
3. в таблицу cards добавить поле id значение которого будет равно generated_at
4. сделать это поле первичным ключом и обновить связь с таблицей user_card_responses
