select * from local_user_card_responses order by created_at desc;

with candidate_cards as (
    select c.image, c.generated_at, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 1
                when ucr.created_at > '2024-03-14 20:00:00' then -1
                else card_weight
            end as corrected_weight
        from local_cards c
        left join local_user_card_responses ucr
        on c.image = ucr.card_image
        where generated_at > 1709854096
        order by generated_at
) select random() * corrected_weight, * from candidate_cards order by 1 desc limit 20;

with candidate_cards as (
    select c.image, c.generated_at, ucr.user_id, ucr.created_at,
            case when ucr.user_id is null then 1
                when ucr.created_at > '2024-03-14 20:00:00' then -1
                else card_weight
            end as corrected_weight
        from local_cards c
        left join local_user_card_responses ucr
        on c.image = ucr.card_image
        where generated_at > 1709854096
        order by generated_at
)
select generated_at
    from candidate_cards
    order by random() * corrected_weight
    desc limit 20;

    268.1195259907223 | is-this-notebook-yours-1710280084.webp                       |   1710280084 | 150847737 | 2024-03-14 14:53:41.187727+00 |              512
   0.9144605888581714 | what-is-the-color-of-your-shoes-1710280277.webp              |   1710280277 |           |                               |                1
   0.8079574964856726 | what-is-that-that-is-an-apple-1709920538.webp                |   1709920538 |           |                               |                1
   0.6737234210057772 | whose-cellphone-is-this-this-is-my-cellphone-1710283319.webp |   1710283319 |           |                               |                1
    0.568040196793679 | where-are-my-things-1709919228.webp                          |   1709919228 |           |                               |                1
   0.5378297919323602 | is-that-an-apple-no-it-isnt-it-is-a-pear-1710278633.webp     |   1710278633 |           |                               |                1
   0.5207664040476077 | is-this-yours-some-of-this-is-mine-1709919541.webp           |   1709919541 |           |                               |                1
   0.5059252624544208 | what-is-the-name-of-the-dog-1710281342.webp                  |   1710281342 |           |                               |                1
  0.46481247274532667 | i-guess-he-is-about-40-1709855045.webp                       |   1709855045 |           |                               |                1
  0.37019354594973164 | how-long-is-the-street-1710282522.webp                       |   1710282522 |           |                               |                1
  0.34639807107023635 | is-this-your-pen-i-have-a-red-pen-1709920176.webp            |   1709920176 |           |                               |                1
  0.27409247254499536 | is-this-your-bag-no-it-isnt-1710347606.webp                  |   1710347606 |           |                               |                1
  0.20416494475094193 | where-is-the-post-office-1710283068.webp                     |   1710283068 |           |                               |                1
   0.0506790432238311 | he-is-the-youngest-in-the-family-1709854709.webp             |   1709854709 |           |                               |                1
 0.046921954179360625 | how-big-is-your-house-1710282816.webp                        |   1710282816 |           |                               |                1
  0.04126000332402735 | how-do-you-say-that-in-serbian-1710280913.webp               |   1710280913 |           |                               |                1
 0.019190140465068728 | which-is-the-right-size-1710284665.webp                      |   1710284665 |           |                               |                1
  -0.0995985854825927 | what-is-this-this-is-a-pencil-1710113813.webp                |   1710113813 | 150847737 | 2024-03-14 23:37:19.000328+00 |               -1
  -0.6360658325601387 | i-have-no-idea-1710286151.webp                               |   1710286151 | 150847737 | 2024-03-14 23:51:50.383003+00 |               -1
  -0.7225224470237728 | where-is-my-bag-it-is-on-the-desk1709915955.webp             |   1709915955 | 150847737 | 2024-03-14 23:46:39.965835+00 |               -1