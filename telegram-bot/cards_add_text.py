import os
import re

from functools import cache
from PIL import Image, ImageFilter, ImageDraw, ImageFont

#https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def split_text_into_sentences(text, num_sentences=None):
    sentences = re.split(r'(?<!\w\.\w.)(?<=\.|\?|!)\s', text)

    if num_sentences is None or len(sentences) <= num_sentences:
        return sentences

    while len(sentences) > num_sentences:
        shortest = min(sentences, key=len)
        index = sentences.index(shortest)
        if index > 0:
            sentences[index - 1] += ' ' + sentences.pop(index)
        elif index < len(sentences) - 1:
            sentences[index] += ' ' + sentences.pop(index + 1)
        else:
            break

    return sentences

def if_fits_to_width(text, font, width):
    print(text, type(text), type(str(text)), font, width)
    text_width, text_height = get_text_dimensions(text, font)
    return text_width < width

def split_by_two_sentences(text, font, color, width, rows, colors, fonts):
    sentences = split_text_into_sentences(text, 2)
    if len(sentences) != 2:
        return False
    s1, s2 = sentences[0], sentences[1]

    if if_fits_to_width(s1, font, width) and if_fits_to_width(s2, font, width):
        rows.extend([s1, s2])
        fonts.extend([font, font])
        colors.extend([color, color])
        return True

    return False

def split_on_two_strings_by_words(text, font, color, width, rows, colors, fonts):
    words = text.split()

    k = 1
    while k < len(words) and if_fits_to_width(' '.join(words[:k]), font, width) :
        k += 1
    k -= 1

    if if_fits_to_width(' '.join(words[k:]), font, width):
        rows.extend([' '.join(words[:k]), ' '.join(words[k:])])
        fonts.extend([font, font])
        colors.extend([color, color])
        return True

    return False

def add_text_properties(text, font_path, color, gap, width, rows, gaps, colors, fonts):
    f36 = ImageFont.truetype(font_path, 36)
    f42 = ImageFont.truetype(font_path, 42)
    f48 = ImageFont.truetype(font_path, 48)

    if if_fits_to_width(text, f48, width):
        rows.extend([text])
        gaps.extend([(gap + 24, 48 + 40)])
        fonts.extend([f48])
        colors.extend([color])
        return

    if split_by_two_sentences(text, f48, color, width, rows, colors, fonts):
        gaps.extend([(gap + 8, 48), (8, 48)])
        return

    if split_by_two_sentences(text, f42, color, width, rows, colors, fonts):
        gaps.extend([(gap + 14, 42), (8, 48)])
        return

    if split_on_two_strings_by_words(text, f48, color, width, rows, colors, fonts):
        gaps.extend([(gap + 8, 48), (8, 48)])
        return

    if split_on_two_strings_by_words(text, f42, color, width, rows, colors, fonts):
        gaps.extend([(gap + 14, 42), (8, 48)])
        return

    if split_by_two_sentences(text, f36, color, width, rows, colors, fonts):
        gaps.extend([(gap + 20, 36), (8, 48)])
        return

    if split_on_two_strings_by_words(text, f36, color, width, rows, colors, fonts):
        gaps.extend([(gap + 20, 36), (8, 48)])
        return

    words = text.split()

    k = 1
    while k < len(words) and if_fits_to_width(' '.join(words[:k]), f36, width):
        k += 1
    k -= 1

    n = k + 1
    while n < len(words) and if_fits_to_width(' '.join(words[k:n]), f36, width):
        n += 1
    n -= 1

    rows.extend([' '.join(words[:k]), ' '.join(words[k:n]), ' '.join(words[n:])])
    fonts.extend([f36, f36, f36])
    colors.extend([color, color, color])

    gaps.extend([(gap + 2, 38), (2, 38), (2, 38)])

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
    text_y = new_image.height * 3 / 4 - 24

    rect_draw.rounded_rectangle(
        [8, text_y, new_image.width - 8, new_image.height - 8],
        fill=(0, 0, 0, opacity),
        radius=16
    )

    # Blend this rectangle with the base image
    new_image.paste(rect_image, (0, 0), rect_image)


    rows = []
    colors = []
    gaps = []
    fonts = []

    pale_blue = (175, 238, 238, 225)  # Бледно-голубой
    lavender = (230, 230, 250, 225)  # Лавандовый
    pastel_peach = (255, 218, 185, 225)  # Пастельный персик

    add_text_properties(text_sr, font_path, pale_blue,    0, new_image.width - 48, rows, gaps, colors, fonts)
    add_text_properties(text_ru, font_path, lavender,     0, new_image.width - 48, rows, gaps, colors, fonts)
    add_text_properties(text_en, font_path, pastel_peach, 0, new_image.width - 48, rows, gaps, colors, fonts)

    text_x = 24

    print('\n')
    for i, r in enumerate(rows):
        top, bottom = gaps[i]
        text_y += top
        draw.text((text_x, text_y), r, fill=colors[i], font=fonts[i])
        text_y += bottom

    return new_image
