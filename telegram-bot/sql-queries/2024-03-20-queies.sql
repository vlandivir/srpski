select * from prod_user_card_responses
    where card_image in (select card_image from prod_user_card_responses order by created_at desc limit 1)
    order by created_at;

with
last_card_responses as (
    select distinct on (card_image) *
    from prod_user_card_responses
    order by card_image, created_at desc
),
candidate_cards as (
    select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 100
                when ucr.created_at > '2024-03-20 02:30:00' then -1 / card_weight
                else card_weight
            end as corrected_weight
        from prod_cards c
        left join last_card_responses ucr
        on c.image = ucr.card_image
        order by generated_at
)
select random() * corrected_weight as rnd, *
    from candidate_cards
    order by 1 desc
    limit 20
;

WITH ranked_responses AS (
  SELECT
    user_id,
    card_image,
    DATE(created_at) AS response_date,
    user_response,
    ROW_NUMBER() OVER (PARTITION BY user_id, card_image, DATE(created_at) ORDER BY created_at DESC) AS rank
  FROM prod_user_card_responses
)
SELECT
  response_date,
  COUNT(DISTINCT card_image) AS unique_cards_shown,
  COUNT(DISTINCT user_response) AS unique_responses
FROM ranked_responses
WHERE rank = 1
GROUP BY response_date
ORDER BY response_date;

WITH ranked_responses AS (
  SELECT
    user_id,
    card_image,
    DATE(created_at) AS response_date,
    user_response,
    ROW_NUMBER() OVER (PARTITION BY user_id, card_image, DATE(created_at) ORDER BY created_at DESC) AS rank
  FROM prod_user_card_responses
  WHERE DATE(created_at) BETWEEN CURRENT_DATE - INTERVAL '1 day' AND CURRENT_DATE
),
filtered_responses AS (
  SELECT
    response_date,
    user_response,
    COUNT(card_image) AS cards_per_response
  FROM ranked_responses
  WHERE rank = 1
  AND user_response IN ('button_easy', 'button_ok', 'button_hard', 'button_complex')
  GROUP BY response_date, user_response
)
SELECT
  response_date,
  SUM(CASE WHEN user_response = 'button_easy' THEN cards_per_response ELSE 0 END) AS easy_cards,
  SUM(CASE WHEN user_response = 'button_ok' THEN cards_per_response ELSE 0 END) AS ok_cards,
  SUM(CASE WHEN user_response = 'button_hard' THEN cards_per_response ELSE 0 END) AS hard_cards,
  SUM(CASE WHEN user_response = 'button_complex' THEN cards_per_response ELSE 0 END) AS complex_cards
FROM filtered_responses
GROUP BY response_date
ORDER BY response_date;
