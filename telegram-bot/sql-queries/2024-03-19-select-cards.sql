
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
            1709162213, 1709853457, 1710278633, 1710464678, 1709246693, 1709850582, 1709828417, 1710347606, 1710464448, 1709854709, 1710286151, 1710282522, 1710637192, 1709915955, 1709847783, 1709816794, 1710496437, 1710282816, 1710497474, 1709208164
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