import json
import re
import time
import io

from PIL import Image
from tempfile import NamedTemporaryFile

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
)

from do_space import add_text_to_image_do, get_do_space_client
from postgres_db_cards import insert_new_card

WAITING_FOR_TEXT, WAITING_FOR_IMAGE = range(2)

async def start(update: Update, context: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.message.reply_text('Пожалуйста, отправьте текст.')
    return WAITING_FOR_TEXT

async def text_received(update: Update, context: CallbackContext) -> int:
    try:
        data = json.loads(update.message.text)

        if all(key in data for key in ["en", "ru", "sr"]) and all(type(data[key]) == str and data[key] for key in ["en", "ru", "sr"]):
            sanitized_en = re.sub(r'[^a-z0-9\s]', '', data['en'].lower())
            image_filename = f"{'-'.join(sanitized_en.split())}-{int(time.time())}.webp"
            data['image'] = image_filename
            context.user_data['data'] = data
            await update.message.reply_text(f'JSON корректный. Теперь отправьте картинку.\n{json.dumps(data, indent=2)}')
            return WAITING_FOR_IMAGE
        else:
            await update.message.reply_text('JSON не соответствует требуемой структуре.')
            return ConversationHandler.END
    except json.JSONDecodeError:
        await update.message.reply_text('Ошибка в формате JSON. Попробуйте снова.')
        return ConversationHandler.END

async def photo_received(update: Update, context: CallbackContext) -> int:
    data = context.user_data.get('data')
    if data is None:
        await update.message.reply_text('Не получилось прочитать данные пользователя')
        return ConversationHandler.END

    filename = data.get('image')

    photo = update.message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)

    with NamedTemporaryFile(delete=False) as tmp_file:
        await photo_file.download_to_drive(
            tmp_file.name,
            read_timeout=3000,
            write_timeout=3000,
            connect_timeout=3000,
        )
        image = Image.open(tmp_file.name)

    if image.width < 800 or image.height < 800:
        await update.message.reply_text('Размер изображения должен быть не менее 800x800px.')
        return ConversationHandler.END

    side_length = min(image.width, image.height)
    image_cropped = image.crop((0, 0, side_length, side_length))

    output_stream = io.BytesIO()
    image_cropped.save(output_stream, format='WEBP')
    output_stream.seek(0)

    client = get_do_space_client()
    bucket_name = 'vlandivir'
    object_name = 'srpski-sources/' + filename

    try:
        client.put_object(Bucket=bucket_name, Key=object_name, Body=output_stream.getvalue())
        print(f"Файл {filename} успешно загружен.")
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")

    add_text_to_image_do(bucket_name, 'srpski-sources/', 'srpski/', filename, data)
    insert_new_card(data)

    await update.message.reply_text(f'Картинка получена и обработана - {filename}. Можно снова отправить текст')
    return WAITING_FOR_TEXT

# Обработчик команды /cancel
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def get_new_card_conversation_handler():
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start, pattern='^button_add_card$')],
        states={
            WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)],
            WAITING_FOR_IMAGE: [MessageHandler(filters.PHOTO, photo_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    return conversation_handler
