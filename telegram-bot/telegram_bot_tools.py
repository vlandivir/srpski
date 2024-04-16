import time

from PIL import Image
from noise import pnoise2

from tempfile import NamedTemporaryFile

async def prepare_source_image(photo_file):
    with NamedTemporaryFile(delete=False) as tmp_file:
        await photo_file.download_to_drive(
            tmp_file.name,
            read_timeout=3000,
            write_timeout=3000,
            connect_timeout=3000,
        )
        image = Image.open(tmp_file.name)

    if image.width < 600 or image.height < 600:
        return None, f'Размер изображения должен быть не менее 600x600px. {image.width}x{image.height}'

    width, height = image.size
    max_side = max(width, height)

    square_image = Image.new('RGB', (max_side, max_side))

    scale = 100.0  # Чем больше число, тем "глаже" шум
    octaves = 6  # Количество октав влияет на детализацию шума
    persistence = 0.5
    lacunarity = 2.0

    base = int(time.time() / 1000)
    print(f'Base for noise {base}')

    # Генерация шума Перлина и заполнение изображения
    for i in range(max_side):
        for j in range(max_side):
            # r = int((pnoise2(i / scale, j / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=width, repeaty=max_side, base=1) + 1) * 127.5)
            r = 0
            g = int((pnoise2(i / scale, j / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, base = base + 2) + 1) * 127.5)
            b = int((pnoise2(i / scale, j / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, base = base + 3) + 1) * 127.5)

            square_image.putpixel((j, i), (r, g, b))

    left = (max_side - width) // 2
    top = (max_side - height) // 2
    square_image.paste(image, (left, top))

    if max_side > 1024:
        square_image = square_image.resize((1024, 1024), Image.Resampling.LANCZOS)

    return square_image, None
