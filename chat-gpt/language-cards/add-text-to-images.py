import os
import json
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

def add_text_properties(text, color, new_image_width, font_48, rows, gaps, colors, fonts):
    text_width, text_height = get_text_dimensions(text, font_48)
    rows_count = text_width / (new_image_width - 64)

    if rows_count > 2:
        font_size = 40
        rows.extend(split_string_into_parts(text, 2))
        gaps.extend([(8, font_size + 2), (0, font_size + 2), (0, font_size + 2)])
        colors.extend([color, color])
        fonts.extend([font_size, font_size])
    elif rows_count > 1:
        font_size = 48
        rows.extend(split_string_into_parts(text, 2))
        gaps.extend([(8, font_size + 2), (0, font_size + 2)])
        colors.extend([color, color])
        fonts.extend([font_size, font_size])
    else:
        font_size = 48
        rows.extend([text])
        gaps.extend([(font_size * 0.5, font_size * 1.5 + 2)])
        colors.extend([color])
        fonts.extend([font_size])

def add_text_to_image(image_path, output_path, text_sr, text_en, text_ru, font_path):
    original_image = Image.open(image_path)

    new_height = int(original_image.height * 4 / 3)
    new_image = Image.new("RGB", (original_image.width, new_height))

    new_image.paste(original_image, (0, 0))

    reflected_new = original_image.transpose(Image.FLIP_TOP_BOTTOM)
    reflected_blurred_new = reflected_new.filter(ImageFilter.GaussianBlur(15))

    # Вычисление области, куда будет вставлено размытое отражение
    reflection_height_new = new_height - original_image.height
    reflected_blurred_resized_new = reflected_blurred_new.resize((original_image.width, reflection_height_new))

    # Вставка размытого отражения в нижнюю часть нового холста
    new_image.paste(reflected_blurred_resized_new, (0, original_image.height))

    # Initialize the drawing context
    draw = ImageDraw.Draw(new_image)

    # Create a separate image for the semi-transparent rectangle
    rect_image = Image.new('RGBA', new_image.size, (0, 0, 0, 0))
    rect_draw = ImageDraw.Draw(rect_image)

    opacity = int(255 * 0.8)
    text_y = new_image.height * 3 / 4 - 8
    rect_draw.rounded_rectangle(
        [8, text_y, new_image.width - 8, new_image.height - 8],
        fill=(0, 0, 0, opacity),
        radius=16
    )

    # Blend this rectangle with the base image
    new_image.paste(rect_image, (0, 0), rect_image)

    font_32 = ImageFont.truetype(font_path, 40)
    font_48 = ImageFont.truetype(font_path, 48)

    text_x = 32
    text_y += 16

    # Инициализация списков
    rows = []
    colors = []
    gaps = []
    fonts = []

    # Параметры
    lavender = (230, 230, 250, 225)  # Лавандовый
    pale_blue = (175, 238, 238, 225)  # Бледно-голубой
    pastel_peach = (255, 218, 185, 225)  # Пастельный персик

    # Вызов функции для каждого блока текста
    add_text_properties(text_sr, pale_blue, new_image.width, font_48, rows, gaps, colors, fonts)
    add_text_properties(text_ru, lavender, new_image.width, font_48, rows, gaps, colors, fonts)
    add_text_properties(text_en, pastel_peach, new_image.width, font_48, rows, gaps, colors, fonts)

    for i, r in enumerate(rows):
        top, bottom = gaps[i]
        text_y += top
        draw.text((text_x, text_y), r, fill=colors[i], font=(font_48 if fonts[i] == 48 else font_32))
        text_y += bottom

    # Save the image
    new_image.save(output_path)

script_dir = os.path.dirname(os.path.abspath(__file__))

json_file = os.path.join(script_dir, 'language-images.json')
with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

source_folder = os.path.join(script_dir, 'source-images/')
result_folder = os.path.join(script_dir, '..', '..', 'telegram-bot/' 'release-cards/')
font_path = '/System/Library/Fonts/Helvetica.ttc'

for item in data:
    image_path = source_folder + item['image']

    text_sr = item['sr']
    text_en = item['en']
    text_ru = item['ru']
    output_path = result_folder + item['image']

    # Call the function
    add_text_to_image(image_path, output_path, text_sr, text_en, text_ru, font_path)
