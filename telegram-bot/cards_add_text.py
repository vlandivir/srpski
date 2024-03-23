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

    total_length = len(s.replace(" ", ""))
    part_length = total_length / n_parts

    parts = []
    last_index = 0
    accumulated_length = 0

    for i in range(1, n_parts):
        current_target = part_length * i

        while accumulated_length < current_target and last_index < len(s):
            if s[last_index] != " ":
                accumulated_length += 1
            last_index += 1

        space_index = s.find(" ", last_index)
        if space_index == -1:
            space_index = len(s)

        parts.append(s[:space_index].strip())
        s = s[space_index:]

        last_index = 0

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

def add_text_to_image(original_image, text_sr, text_en, text_ru, font_path):
    new_height = int(original_image.height * 4 / 3)
    new_image = Image.new("RGB", (original_image.width, new_height))

    new_image.paste(original_image, (0, 0))

    reflected_new = original_image.transpose(Image.FLIP_TOP_BOTTOM)
    reflected_blurred_new = reflected_new.filter(ImageFilter.GaussianBlur(15))

    reflection_height_new = new_height - original_image.height
    reflected_blurred_resized_new = reflected_blurred_new.resize((original_image.width, reflection_height_new))
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

    font_40 = ImageFont.truetype(font_path, 40)
    font_48 = ImageFont.truetype(font_path, 48)

    text_x = 32
    text_y += 0

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

    print('\n\n')
    for i, r in enumerate(rows):
        top, bottom = gaps[i]
        text_y += top
        draw.text((text_x, text_y), r, fill=colors[i], font=(font_48 if fonts[i] == 48 else font_40))
        text_y += bottom
        print (r, top, bottom, fonts[i])

    return new_image
