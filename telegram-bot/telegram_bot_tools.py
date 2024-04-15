from PIL import Image
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

    square_image = Image.new('RGB', (max_side, max_side), (0, 0, 0))
    left = (max_side - width) // 2
    top = (max_side - height) // 2
    square_image.paste(image, (left, top))

    if max_side > 1024:
        square_image = square_image.resize((1024, 1024), Image.Resampling.LANCZOS)

    return square_image, None
