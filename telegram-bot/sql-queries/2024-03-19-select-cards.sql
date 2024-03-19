
with
last_card_responses as (
    select distinct on (card_image) *
    from prod_user_card_responses
    order by card_image, created_at desc
),
candidate_cards as (
    select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 100
                when ucr.created_at > '2024-03-19 00:00:00' then -1 / card_weight
                else card_weight
            end as corrected_weight
        from prod_cards c
        left join last_card_responses ucr
        on c.image = ucr.card_image
        where generated_at in (
            1709852998, 1709817403, 1709850768, 1710281342, 1709165254, 1709222004, 1710283068, 1709850582, 1710464678, 1677538821, 1709920538, 1710464286, 1709237792, 1709207757, 1710280277, 1710282816, 1709250521, 1677539257, 1710280084, 1710495773
        )
        order by generated_at
)
select *
    from candidate_cards
    order by corrected_weight desc
;



with
last_card_responses as (
    select distinct on (card_image) *
    from prod_user_card_responses
    order by card_image, created_at desc
),
candidate_cards as (
    select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 100
                when ucr.created_at > '2024-03-19 00:00:00' then -1 / card_weight
                else card_weight
            end as corrected_weight
        from prod_cards c
        left join last_card_responses ucr
        on c.image = ucr.card_image
        order by generated_at
)
select *
    from candidate_cards
    order by corrected_weight desc
;