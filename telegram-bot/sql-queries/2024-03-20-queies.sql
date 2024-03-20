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