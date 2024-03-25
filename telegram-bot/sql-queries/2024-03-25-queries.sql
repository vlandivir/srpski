select * from docker_user_card_responses
    order by created_at desc
    limit 10;

  user_id   |                                              card_image                                               |          created_at           | user_response | card_weight
------------+-------------------------------------------------------------------------------------------------------+-------------------------------+---------------+-------------
 5804112948 | most-of-them-are-less-than-25-1709853171.webp                                                         | 2024-03-25 21:01:38.844058+00 | button_ok     |         256
 5804112948 | who-are-you-writing-to-i-am-writing-to-a-friend-1711278116.webp                                       | 2024-03-25 21:36:53.403479+00 | button_hide   |        1024

with
last_card_responses as (
    select distinct on (card_image) *
    from docker_user_card_responses
    where user_id = '5804112948'
    order by card_image, created_at desc
),
candidate_cards as (
    select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 100
                when ucr.created_at > now() then -1 / card_weight
                else card_weight
            end as corrected_weight
        from docker_cards c
        left join last_card_responses ucr
        on c.image = ucr.card_image and ucr.user_response != 'button_hide'
        order by generated_at
)
select random() * corrected_weight as rnd, *
    from candidate_cards
    order by 1 desc
    limit 20
;

with
last_card_responses as (
    select distinct on (card_image) *
    from docker_user_card_responses
    where user_id = '5804112948'
    order by card_image, created_at desc
),
candidate_cards as (
    select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at, ucr.user_response,
            case when ucr.user_id is null then 100
                when ucr.created_at > now() then -1 / card_weight
                else card_weight
            end as corrected_weight
        from docker_cards c
        left join last_card_responses ucr
        on c.image = ucr.card_image
        order by generated_at
)
select count(*) from candidate_cards where coalesce(user_response, '') != 'button_hide'
;
