select * from prod_cards where sr like 'Pričao%';

-[ RECORD 1 ]+----------------------------------------------------------------
en           | I talked with the clocks on the wall about time
ru           | Я разговаривал с часами на стене о времени
sr           | Pričao sam sa satovima na zidu o vremenu
image        | i-talked-with-the-clocks-on-the-wall-about-time-1709000000.webp
generated_at | 1709000000
tags         |
created_at   | 2024-03-13 22:32:32.042216+00
updated_at   | 2024-03-13 22:32:32.042216+00

-- select * from prod_user_card_responses limit 1;

select * from prod_user_card_responses where card_image = 'i-talked-with-the-clocks-on-the-wall-about-time-1709000000.webp';

-[ RECORD 8 ]-+----------------------------------------------------------------
user_id       | 150847737
card_image    | i-talked-with-the-clocks-on-the-wall-about-time-1709000000.webp
created_at    | 2024-03-26 21:49:06.579401+00
user_response | button_easy
card_weight   | 0.5
-[ RECORD 9 ]-+----------------------------------------------------------------
user_id       | 150847737
card_image    | i-talked-with-the-clocks-on-the-wall-about-time-1709000000.webp
created_at    | 2024-04-01 06:28:29.232196+00
user_response | button_ok
card_weight   | 0.25
-[ RECORD 10 ]+----------------------------------------------------------------
user_id       | 150847737
card_image    | i-talked-with-the-clocks-on-the-wall-about-time-1709000000.webp
created_at    | 2024-04-01 06:34:47.794306+00
user_response | button_easy
card_weight   | 0.0625

--

with
last_card_responses as (
    select distinct on (card_image) *
    from prod_user_card_responses
    order by card_image, created_at desc
),
candidate_cards as (
    select c.image, c.generated_at, ucr.card_weight, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 100
                when ucr.created_at > '2024-03-20 10:55:00' then -1 / card_weight
                else card_weight
            end as corrected_weight
        from prod_cards c
        left join last_card_responses ucr
        on c.image = ucr.card_image and ucr.user_id = '150847737'
        where image = 'i-talked-with-the-clocks-on-the-wall-about-time-1709000000.webp'
        order by generated_at
)
select *
    from candidate_cards
    order by corrected_weight desc
;

select c.*, card_weight, user_response,
    case when ucr.user_id is null then 100
        when ucr.created_at > '2024-04-02 10:55:00' then -1 / card_weight
        else card_weight
    end as corrected_weight
    from prod_cards c
    left join prod_user_card_responses ucr
    on c.image = ucr.card_image
    where c.generated_at = '1709000000' and ucr.user_id = '150847737'
    order by ucr.created_at desc
    limit 1
;