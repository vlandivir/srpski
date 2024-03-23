import os

from dotenv import load_dotenv

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

from telegram_bot_helpers import common_button_handler
from telegram_bot_new_card_conversation import get_new_card_conversation_handler
from telegram_bot_cards import (
    update_cards, say_hello, button_next_card, button_card_response, button_new_cards, button_stats
)

from postgres_create_or_update_db import create_or_update_db

load_dotenv('.env')

token = os.getenv('VLANDIVIR_BOT_TOKEN')
token = os.getenv('TEST_BOT_TOKEN', token) # for local run python3 telegram-bot/vlandivir_bot.py

create_or_update_db()

async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat_id = common_button_handler(update)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Учить карточки', callback_data=f'button_next'),
            InlineKeyboardButton('Подробная справка', callback_data=f'button_help'),
        ]
    ])

    await context.bot.send_message(
        chat_id=chat_id,
        text='Бот помогает учить сербский язык, используя flash cards',
        reply_markup=keyboard
    )

async def oops_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text='Ой, здесь пока ничего нет...',
    )

async def button_more(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat_id = common_button_handler(update)

    keyboard_rows = []
    keyboard_rows.append(
        [
            InlineKeyboardButton('Stats', callback_data=f'button_stats'),
            InlineKeyboardButton('New cards', callback_data=f'button_new_cards'),
        ]
    )

    if (user['id'] == '150847737'):
        keyboard_rows.append(
        [
            InlineKeyboardButton('Add card', callback_data=f'button_add_card'),
        ]
    )

    keyboard = InlineKeyboardMarkup(keyboard_rows)

    await context.bot.send_message(
        chat_id=chat_id,
        text='Что желаете?',
        reply_markup=keyboard
    )

def main():
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler('hello', say_hello))
    app.add_handler(CommandHandler('update', update_cards))

    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_complex:'))
    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_hard:'))
    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_ok:'))
    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_easy:'))
    app.add_handler(CallbackQueryHandler(button_next_card, pattern='^button_next$'))

    app.add_handler(CallbackQueryHandler(oops_handler, pattern='^button_help$'))

    app.add_handler(CallbackQueryHandler(button_more, pattern='^button_more$'))
    app.add_handler(CallbackQueryHandler(button_stats, pattern='^button_stats$'))
    app.add_handler(CallbackQueryHandler(button_new_cards, pattern='^button_new_cards$'))

    app.add_handler(get_new_card_conversation_handler())

    app.add_handler(MessageHandler(filters.ALL, default_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
