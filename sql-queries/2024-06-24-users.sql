select to_char(created_at, 'YYYY.MM'), user_id, count(*) from prod_user_card_responses group by to_char(created_at, 'YYYY.MM'), user_
id order by 1 desc;

 to_char |  user_id   | count
---------+------------+-------
 2024.06 | 150847737  |    11
 2024.05 | 150847737  |    12
 2024.05 | 161295617  |     2
 2024.05 | 6156032144 |    11
 2024.04 | 150847737  |   123
 2024.04 | 532089819  |    39
 2024.03 | 150847737  |   929
 2024.03 | 807625513  |   102
