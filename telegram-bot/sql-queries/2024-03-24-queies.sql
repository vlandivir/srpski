{
    "en": "What will you do this weekend? I will go out with friends.",
    "ru": "Что ты будешь делать на выходных? Я пойду гулять с друзьями.",
    "sr": "Šta ćeš raditi ovog vikenda? Izaći ću sa prijateljima.",
    "image": "i-will-go-out-with-friends_1711283466.webp"
}

select * from prod_cards where image='i-will-go-out-with-friends_1711283466.webp';

delete from local_cards where image='i-will-go-out-with-friends-1711283554.webp';
delete from docker_cards where image='i-will-go-out-with-friends-1711283554.webp';
delete from prod_cards where image='i-will-go-out-with-friends-1711283554.webp';

select * from prod_cards where image like 'i-will-go-out-with-friends%';
