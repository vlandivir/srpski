import os
from PIL import Image, ImageFilter, ImageDraw, ImageFont

#https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def split_string_into_parts(s, n_parts):
    if n_parts <= 1:
        return [s]

    # Общая длина строки без учета пробелов для более равномерного деления
    total_length = len(s.replace(" ", ""))
    part_length = total_length / n_parts

    parts = []
    last_index = 0
    accumulated_length = 0  # Длина накопленных символов без пробелов

    for i in range(1, n_parts):
        # Планируемая длина для текущей части
        current_target = part_length * i

        while accumulated_length < current_target and last_index < len(s):
            if s[last_index] != " ":
                accumulated_length += 1
            last_index += 1

        # Находим ближайший пробел для разделения
        space_index = s.find(" ", last_index)
        if space_index == -1:  # Если пробел не найден, используем длину строки
            space_index = len(s)

        # Добавляем часть строки до найденного пробела
        parts.append(s[:space_index].strip())
        # Обновляем строку, удаляя добавленную часть
        s = s[space_index:]

        last_index = 0  # Сбрасываем индекс для новой подстроки

    # Добавляем оставшуюся часть строки
    parts.append(s.strip())

    return parts

def add_text_properties(text, color, gap, image_width, font_48, rows, gaps, colors, fonts):
    text_width, text_height = get_text_dimensions(text, font_48)
    rows_count = text_width / (image_width - 128)

    if rows_count > 2:
        font_size = 40
        rows.extend(split_string_into_parts(text, 2))
        gaps.extend([(gap + 8, font_size + 2), (0, font_size + 2)])
        colors.extend([color, color])
        fonts.extend([font_size, font_size])
    elif rows_count > 1:
        font_size = 48
        rows.extend(split_string_into_parts(text, 2))
        gaps.extend([(gap + 8, font_size + 2), (0, font_size + 2)])
        colors.extend([color, color])
        fonts.extend([font_size, font_size])
    else:
        font_size = 48
        rows.extend([text])
        gaps.extend([(gap + font_size * 0.5, font_size * 1.5 + 2)])
        colors.extend([color])
        fonts.extend([font_size])

def add_text_to_image(output_path, texts, font_path):

    width = 1024
    height = int(1024 * 2)
    new_image = Image.new("RGB", (width, height))

    # Initialize the drawing context
    draw = ImageDraw.Draw(new_image)

    # Create a separate image for the semi-transparent rectangle
    rect_image = Image.new('RGBA', new_image.size, (0, 0, 0, 0))
    rect_draw = ImageDraw.Draw(rect_image)

    opacity = int(255 * 0.8)
    text_y = 8
    rect_draw.rounded_rectangle(
        [8, text_y, new_image.width - 8, new_image.height - 8],
        fill=(0, 0, 0, opacity),
        radius=16
    )

    # Blend this rectangle with the base image
    new_image.paste(rect_image, (0, 0), rect_image)

    font_40 = ImageFont.truetype(font_path, 40)
    font_48 = ImageFont.truetype(font_path, 48)

    text_x = 32

    # Инициализация списков
    rows = []
    colors = []
    gaps = []
    fonts = []

    # Параметры
    lavender = (230, 230, 250, 225)  # Лавандовый
    pale_blue = (175, 238, 238, 225)  # Бледно-голубой
    pastel_peach = (255, 218, 185, 225)  # Пастельный персик

    text_colors = [lavender, pale_blue, pastel_peach]

    for i, text in enumerate(texts):
        print(f"{text}")
        add_text_properties(text, text_colors[i % 3], 0 if i % 3 else 16, new_image.width, font_48, rows, gaps, colors, fonts)

    for i, r in enumerate(rows):
        top, bottom = gaps[i]
        text_y += top
        draw.text((text_x, text_y), r, fill=colors[i], font=(font_48 if fonts[i] == 48 else font_40))
        text_y += bottom

    # Save the image
    print(output_path)
    new_image.save(output_path)

script_dir = os.path.dirname(os.path.abspath(__file__))

font_path = os.path.join(script_dir, 'NimbusSanLRegular.ttf')

texts = [
    "Short message",
    "Two string message. Сообщение в две строки",
    "In Belgrade, the snow that has been falling since last night has slowed down and disrupted traffic.",
    "Short message",
    "Madam could you tell me where the supermarket is? Go straight ahead and turn right at the third intersection.",
    "Short message",
    "Мадам, не могли бы вы сказать мне, где находится супермаркет? Идите прямо и поверните направо на третьем перекрёстке.",
    "Short message",
    "Gospođo možete li mi reći gde je supermarket? Idite pravo i skrenite desno na trećoj raskrsnici.",
    "Can you tell me how to get to the post office? Go on for about 200 meters it will be on your left side.",
    "Можете ли вы сказать мне, как добраться до почты? Пройдите около двухсот метров, она будет у вас слева.",
    "Možete li mi reći kako da dođem do pošte? Idite oko dvesta metara biće na vašoj levoj strani.",
    "When looking for accommodation in the mountains, it's important to consider the weather conditions.",
    "Da li se radnja otvara u osam ujutru radnim danima? Otvara se u devet ujutru radnim danima.",
    "Would you help me move the fridge? I am glad to but I am afraid I don't have the time.",
    "Ты поможешь мне переставить холодильник? Я бы с удовольствием, но боюсь, у меня нет времени.",
    "Two string message. Сообщение в две строки",
    "Hoćeš li mi pomoći da pomerim frižider? Drage volje ali bojim se da nemam vremena.",
]

release_folder = os.path.join(script_dir)
output_path = release_folder + '/test-text-sizes.webp'

add_text_to_image(output_path, texts, font_path)
