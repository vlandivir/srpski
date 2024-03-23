def create_progress_bar(weight):
    red_square = '🟥'
    yellow_square = '🟨'
    green_square = '🟩'
    blue_square = '🟦'
    black_square = '⬛'

    squares = [red_square] * 2 + [yellow_square] * 3 + [green_square] * 3 + [blue_square] * 2

    if weight > 1024:
        return red_square + black_square * 9
    elif weight == 0:
        return black_square * 10
    elif 0 < weight <= 1:
        return ''.join(squares)
    else:
        painted_squares = min(10, max(1, 10 - int(weight).bit_length() + 1))
        return ''.join(squares[:painted_squares]) + black_square * (10 - painted_squares)
