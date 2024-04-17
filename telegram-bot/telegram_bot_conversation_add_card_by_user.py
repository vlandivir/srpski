import json
import re
import time
import io

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
# from postgres_db_cards import insert_new_card
from telegram_bot_helpers import get_user_from_update
from telegram_bot_tools import prepare_source_image


WAITING_FOR_IMAGE, WAITING_FOR_SR, WAITING_FOR_RU = range(3)

async def start(update: Update, context: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.message.reply_text('Пожалуйста, отправьте картинку')
    return WAITING_FOR_IMAGE

async def photo_received(update: Update, context: CallbackContext) -> int:
    user = get_user_from_update(update)

    photo = update.message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)

    image, error = await prepare_source_image(photo_file)

    if error is not None:
        await update.message.reply_text(error)
        return ConversationHandler.END

    output_stream = io.BytesIO()
    image.save(output_stream, format='WEBP')
    output_stream.seek(0)

    client = get_do_space_client()

    filename = f'image-{user['id']}-{int(time.time())}.webp'
    folder = 'user-sources'
    bucket_name = 'vlandivir'
    object_name = f'{folder}/{filename}'

    try:
        client.put_object(Bucket=bucket_name, Key=object_name, Body=output_stream.getvalue(), ACL='public-read', ContentType='image/webp')
        print(f"Файл {filename} успешно загружен.")
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")

    imagename = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/{folder}/{filename}?upts={int(time.time())}'

    chat_id = update.effective_chat.id
    await context.bot.send_photo(
        chat_id = chat_id,
        photo = imagename,
        caption = 'Полученная картинка. Теперь отправьте предложение на сербском языке',
    )

    context.user_data['filename'] = filename

    return WAITING_FOR_SR

async def serbian_received(update: Update, context: CallbackContext) -> int:
    filename = context.user_data.get('filename')
    text = update.message.text

    bucket_name = 'vlandivir'
    new_filename = f'sr-{filename}'
    folder = 'user-sources'

    add_text_to_image_do(bucket_name, f'{folder}/{filename}', f'{folder}/', new_filename, {'sr': text, 'en': '...', 'ru': '...'})

    imagename = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/{folder}/{new_filename}?upts={int(time.time())}'

    chat_id = update.effective_chat.id
    await context.bot.send_photo(
        chat_id = chat_id,
        photo = imagename,
        caption = 'Теперь карточка выглядит так. Теперь отправьте предложение на русском языке',
    )

    context.user_data['filename'] = filename
    context.user_data['sr'] = text

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Операция отменена.',
    )

    return ConversationHandler.END

def get_add_card_by_user_conversation_handler():
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start, pattern='^button_add_user_card$')],
        states={
            WAITING_FOR_IMAGE: [MessageHandler(filters.PHOTO, photo_received)],
            WAITING_FOR_SR: [MessageHandler(filters.TEXT & ~filters.COMMAND, serbian_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    return conversation_handler
