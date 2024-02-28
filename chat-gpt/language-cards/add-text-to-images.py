import json
from PIL import Image, ImageDraw, ImageFont

#https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def split_string_into_parts(s, n_parts):
    """
    Разделить строку `s` на `n_parts` примерно равных частей по пробелам.
    
    :param s: Строка для разделения
    :param n_parts: Количество частей
    :return: Список частей строки
    """
    # Разбиваем строку на слова
    words = s.split()
    
    # Если количество частей больше количества слов, возвращаем слова (каждое слово в отдельной части)
    if n_parts >= len(words):
        return words + [''] * (n_parts - len(words))  # Добавляем пустые строки, если частей должно быть больше
    
    # Вычисляем примерное количество слов в каждой части
    words_per_part = len(words) / n_parts
    
    # Разделяем слова по частям
    parts = []
    current_part = []
    current_length = 0
    for word in words:
        current_part.append(word)
        current_length += len(word)
        
        # Проверяем, достигли ли мы примерной длины текущей части
        if len(current_part) >= round(words_per_part) and len(parts) < n_parts - 1:
            parts.append(' '.join(current_part))
            current_part = []
    
    # Добавляем оставшиеся слова в последнюю часть
    parts.append(' '.join(current_part))
    
    return parts

def add_text_to_image(image_path, output_path, text_sr, text_en, text_ru, font_path):
    # Load the image
    image = Image.open(image_path)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    # Create a separate image for the semi-transparent rectangle
    rect_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
    rect_draw = ImageDraw.Draw(rect_image)

    opacity = int(255 * 0.6)
    text_y = image.height * 3 / 4 - 8;
    rect_draw.rounded_rectangle(
        [8, text_y, image.width - 8, image.height - 8], 
        fill=(0, 0, 0, opacity), 
        radius=16
    )

    # Blend this rectangle with the base image
    image.paste(rect_image, (0, 0), rect_image)

    font_size = 48
    font_sr = ImageFont.truetype(font_path, font_size)
    text_color = "white"

    text_x = 32
    text_y += 16

    rows = []

    text_width, text_height = get_text_dimensions(text_sr, font_sr)
    if text_width > image.width - 16:
        rows.extend(split_string_into_parts(text_sr, 2))
    else:
        rows.extend([text_sr, '\n'])

    text_width, text_height = get_text_dimensions(text_ru, font_sr)
    if text_width > image.width - 16:
        rows.extend(split_string_into_parts(text_ru, 2))
    else:
        rows.extend([text_ru, '\n'])

    text_width, text_height = get_text_dimensions(text_ru, font_sr)
    if text_width > image.width - 16:
        rows.extend(split_string_into_parts(text_en, 2))
    else:
        rows.extend([text_en, '\n'])

    for i, r in enumerate(rows):
        draw.text((text_x, text_y), r, fill=text_color, font=font_sr)
        text_y += font_size + 2 + (8 if i % 2 == 1 else 0)

    # Save the image
    image.save(output_path)

with open('language-images.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

source_folder = 'source-images/'
result_folder = 'result-images/'
font_path = '/System/Library/Fonts/Helvetica.ttc'

for item in data:
    image_path = source_folder + item['image']

    text_sr = item['sr']
    text_en = item['en']
    text_ru = item['ru']
    output_path = result_folder + item['image']

    # Call the function
    add_text_to_image(image_path, output_path, text_sr, text_en, text_ru, font_path)

