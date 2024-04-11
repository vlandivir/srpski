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
    text_width, text_height = get_text_dimensions(text, font)
    return text_width < width

def split_by_two_sentences(text, font, color, width, rows, colors, fonts):
    sentences = split_text_into_sentences(text, 2)
    s1, s2 = sentences[0], sentences[1] if len(sentences) == 2 else 0
    print(sentences)

    if if_fits_to_width(s1, font, width) and if_fits_to_width(s2, font, width):
        rows.extend([s1, s2])
        fonts.extend([font, font])
        colors.extend([color, color])
        print(f'2 sentences {font.size}')
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
        print(f'2 words {font.size}')
        return True

    return False

def add_text_properties(text, color, gap, width, rows, gaps, colors, fonts):
    f36, f42, f48 = get_fonts()

    if if_fits_to_width(text, f48, width):
        rows.extend([text])
        gaps.extend([(gap + 24, 48 + 40)])
        fonts.extend([f48])
        colors.extend([color])
        print('1 all 48')
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

@cache
def get_fonts():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'NimbusSanLRegular.ttf')

    font_36 = ImageFont.truetype(font_path, 36)
    font_42 = ImageFont.truetype(font_path, 42)
    font_48 = ImageFont.truetype(font_path, 48)

    return (font_36, font_42, font_48)

def add_text_to_image(output_path, texts):

    width = 1024
    height = int(1024 * 2.4)
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
        print('')
        print(text)
        add_text_properties(text, text_colors[i % 3], 0 if i % 3 else 32, new_image.width - 64, rows, gaps, colors, fonts)

    for i, r in enumerate(rows):
        top, bottom = gaps[i]
        text_y += top
        draw.text((text_x, text_y), r, fill=colors[i], font=fonts[i])
        text_y += bottom

    # Save the image
    print(output_path)
    new_image.save(output_path)

script_dir = os.path.dirname(os.path.abspath(__file__))
# font_path = os.path.join(script_dir, 'NimbusSanLRegular.ttf')

texts = [
    "Short message",
    "Two string message. Сообщение в две строки. Делим по словам!",
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
    "Two string message. Короткий текст. Сообщение в две строки",
    "Hoćeš li mi pomoći da pomerim frižider? Drage volje ali bojim se da nemam vremena.",
    "Мадам, не могли бы вы сказать мне, где находится супермаркет? Идите прямо и поверните направо на третьем перекрёстке.",
]

release_folder = os.path.join(script_dir)
output_path = release_folder + '/test-text-sizes.webp'

add_text_to_image(output_path, texts)
