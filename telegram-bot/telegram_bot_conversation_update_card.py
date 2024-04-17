import json

from postgres_db_cards import update_card

from do_space import add_text_to_image_do

from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)

# Состояние для ConversationHandler, ожидающее JSON
WAITING_FOR_JSON = 0

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text('Пожалуйста, отправьте текст.')
    button_data = query.data.split(':')
    context.user_data['data'] = button_data[1]

    return WAITING_FOR_JSON

async def json_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        print(update)
        data = json.loads(update.message.text)

        if all(key in data for key in ["en", "ru", "sr"]) and all(type(data[key]) == str and data[key] for key in ["en", "ru", "sr"]):
            card_id = context.user_data.get('data')
            image = update_card(card_id, data)

            print(image)
            if image:
                add_text_to_image_do(
                    'vlandivir', f'srpski-sources/{image}', 'srpski/', image, {'image': image, **data}
                )
                await update.message.reply_text(f'JSON корректный. Карточка обновлена')
            else:
                await update.message.reply_text(f'Файл не найден')

        else:
            await update.message.reply_text('JSON не соответствует требуемой структуре.')

        return ConversationHandler.END

    except json.JSONDecodeError:
        await update.message.reply_text('Ошибка в формате JSON. Попробуйте снова.')
        return ConversationHandler.END

def get_update_card_conversation_handler():
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^update_card:')],
        states={
            WAITING_FOR_JSON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, json_handler)
            ],
        },
        fallbacks=[]
    )

    return conversation_handler
