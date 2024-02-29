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

    font_size = 48
    font_sr = ImageFont.truetype(font_path, font_size)

    text_x = 32
    text_y += 16

    rows = []
    colors = []
    gaps = []

    # (230, 230, 250, 225) # Лавандовый
    # (175, 238, 238, 225) # Бледно-голубой
    # (255, 218, 185, 225) # Пастельный персик

    text_width, text_height = get_text_dimensions(text_sr, font_sr)
    if text_width > new_image.width - 32:
        rows.extend(split_string_into_parts(text_sr, 2))
        gaps.extend([(0, font_size + 2), (0, font_size + 2)])
        colors.extend([(175, 238, 238, 225), (175, 238, 238, 225)])
    else:
        rows.extend([text_sr])
        gaps.extend([(font_size * 0.5, font_size * 1.5 + 2)])
        colors.extend([(175, 238, 238, 225)])

    text_width, text_height = get_text_dimensions(text_ru, font_sr)
    if text_width > new_image.width - 32:
        rows.extend(split_string_into_parts(text_ru, 2))
        gaps.extend([(8, font_size + 2), (0, font_size + 2)])
        colors.extend([(230, 230, 250, 225), (230, 230, 250, 225)])
    else:
        rows.extend([text_ru])
        gaps.extend([(font_size * 0.5, font_size * 1.5 + 2)])
        colors.extend([(230, 230, 250, 225)])

    text_width, text_height = get_text_dimensions(text_en, font_sr)
    if text_width > new_image.width - 32:
        rows.extend(split_string_into_parts(text_en, 2))
        gaps.extend([(8, font_size + 2), (0, font_size + 2)])
        colors.extend([(255, 218, 185, 225), (255, 218, 185, 225)])
    else:
        rows.extend([text_en])
        gaps.extend([(font_size * 0.5, font_size * 1.5 + 2)])
        colors.extend([(255, 218, 185, 225)])

    for i, r in enumerate(rows):
        top, bottom = gaps[i]
        text_y += top
        draw.text((text_x, text_y), r, fill=colors[i], font=font_sr)
        text_y += bottom

    # Save the image
    new_image.save(output_path)

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
