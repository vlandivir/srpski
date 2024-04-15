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


WAITING_FOR_IMAGE, WAITING_FOR_RU, WAITING_FOR_SR = range(3)

async def start(update: Update, context: CallbackContext) -> int:
    await update.callback_query.answer()
    await update.callback_query.message.reply_text('Пожалуйста, отправьте картинку')
    return WAITING_FOR_IMAGE

# async def text_received(update: Update, context: CallbackContext) -> int:
#     try:
#         data = json.loads(update.message.text)

#         if all(key in data for key in ["en", "ru", "sr"]) and all(type(data[key]) == str and data[key] for key in ["en", "ru", "sr"]):
#             sanitized_en = re.sub(r'[^a-z0-9\s]', '', data['en'].lower())
#             image_filename = f"{'-'.join(sanitized_en.split())}-{int(time.time())}.webp"
#             data['image'] = image_filename
#             context.user_data['data'] = data
#             await update.message.reply_text(f'JSON корректный. Теперь отправьте картинку.\n{json.dumps(data, indent=2)}')
#             return WAITING_FOR_IMAGE
#         else:
#             await update.message.reply_text('JSON не соответствует требуемой структуре.')
#             return ConversationHandler.END
#     except json.JSONDecodeError:
#         await update.message.reply_text('Ошибка в формате JSON. Попробуйте снова.')
#         return ConversationHandler.END

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

    # add_text_to_image_do(bucket_name, 'srpski-sources/', 'srpski/', filename, data)
    # insert_new_card(data)

    # await update.message.reply_text(f'Картинка получена и обработана - {filename}. Можно снова отправить текст')

    print(f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/{folder}/{filename}?upts={int(time.time())}')

    chat_id = update.effective_chat.id
    await context.bot.send_photo(
        chat_id=chat_id,
        photo = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/{folder}/{filename}?upts={int(time.time())}',
        caption='Полученная картинка',
    )
    return ConversationHandler.END

# Обработчик команды /cancel
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
            # WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    return conversation_handler
