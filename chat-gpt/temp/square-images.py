from PIL import Image
import os

source_dir = 'source-images'
target_dir = 'processed-images'

# Создаем целевую директорию, если она еще не существует
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# Перебираем все файлы в исходной директории
for filename in os.listdir(source_dir):
    if filename.endswith('.webp'):  # Проверяем, что файл имеет формат WEBP
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, filename)

        # Открываем изображение
        with Image.open(source_path) as img:
            # Определяем размеры для обрезки, чтобы сделать изображение квадратным
            width, height = img.size
            new_height = width

            # Если изображение уже квадратное, копируем его без изменений
            if height == width:
                img.save(target_path, 'webp')
            else:
                # Обрезаем изображение, оставляя верхнюю часть
                img_cropped = img.crop((0, 0, width, new_height))
                img_cropped.save(target_path, 'webp')
