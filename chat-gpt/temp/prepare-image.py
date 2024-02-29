from PIL import Image, ImageFilter

# Загрузка новой изображения
new_original_image_path = '/mnt/data/A_cozy_scene_of_someone_sitting_in_a_comfortable_c.png'
new_original_image = Image.open(new_original_image_path)

# Расчет новых размеров изображения (увеличение на треть по вертикали)
new_height_new = int(new_original_image.height * 4 / 3)
new_image_new = Image.new("RGB", (new_original_image.width, new_height_new))

# Копирование оригинального изображения в верхнюю часть нового холста
new_image_new.paste(new_original_image, (0, 0))

# Создание зеркального отражения оригинального изображения и его размытие
reflected_new = new_original_image.transpose(Image.FLIP_TOP_BOTTOM)
reflected_blurred_new = reflected_new.filter(ImageFilter.GaussianBlur(15))

# Вычисление области, куда будет вставлено размытое отражение
reflection_height_new = new_height_new - new_original_image.height
reflected_blurred_resized_new = reflected_blurred_new.resize((new_original_image.width, reflection_height_new))

# Вставка размытого отражения в нижнюю часть нового холста
new_image_new.paste(reflected_blurred_resized_new, (0, new_original_image.height))

# Сохранение результата новой картинки
final_image_path_new = f'/mnt/data/i-love-drinking-milk-while-listening-to-calm-music-1709167786.webp'
new_image_new.save(final_image_path_new, "WEBP")
