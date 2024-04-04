select c.*, card_weight, user_response,
    case when ucr.user_id is null then 100
        when ucr.created_at > '2024-04-05' then -1 / card_weight
        else card_weight
    end as corrected_weight
    from public.local_cards c
    left join public.local_user_card_responses ucr
    on c.id = ucr.card_id
    where c.id = 1712270743 and ucr.user_id = '150847737'
    order by ucr.created_at desc
    limit 1
;

select * from local_cards where id = 1712270743;


select c.*, card_weight, user_response,
    case when ucr.user_id is null then 100
        when ucr.created_at > '2024-04-05' then -1 / card_weight
        else card_weight
    end as corrected_weight
    from public.local_cards c
    left join public.local_user_card_responses ucr
    on c.id = ucr.card_id and ucr.user_id = '150847737'
    where c.id = 1712270743
    order by ucr.created_at desc
    limit 1
;
