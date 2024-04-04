import os
import sentry_sdk

from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

from telegram_bot_helpers import common_button_handler
from telegram_bot_conversation_new_card import get_new_card_conversation_handler
from telegram_bot_conversation_hide_card import get_hide_card_conversation_handler
from telegram_bot_conversation_update_card import get_update_card_conversation_handler

from telegram_bot_messages import create_progress_bar
from telegram_bot_cards import (
    init_cards_cache, get_card_by_id, update_cards,
    say_hello, button_next_card, button_card_response, button_new_cards, button_stats
)

from postgres_create_or_update_db import create_or_update_db
from postgres_db_cards import get_card_with_weight

load_dotenv('.env')

token = os.getenv('VLANDIVIR_BOT_TOKEN')
token = os.getenv('TEST_BOT_TOKEN', token) # for local run python3 telegram-bot/vlandivir_bot.py

SENTRY_DSN = os.getenv('SENTRY_DSN')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')
TAG_NAME = os.getenv('TAG_NAME', 'LOCAL')
sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    enable_tracing=True,
    environment=ENVIRONMENT,
    release=TAG_NAME,
)

create_or_update_db()
init_cards_cache()

async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat_id = await common_button_handler(update)

    user_text = update.message.text
    is_digit = user_text.isdigit()

    if is_digit:
        card_id = int(user_text)
        card = get_card_by_id(card_id)
        if card is not None:
            keyboard = [[InlineKeyboardButton("Отправить JSON", callback_data=f'update_card:{card_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard) if (user['id'] == '150847737') else None

            upts = str(int(card['updated_at'].timestamp())) if isinstance(card['updated_at'], datetime) else ''

            card_with_weight = get_card_with_weight(user['id'], card_id)
            card_weight = card_with_weight.get('card_weight', None)
            caption = f"{create_progress_bar(card_weight)}\n" if card_weight is not None else ''
            caption += f"{str(card_weight)}"

            await context.bot.send_photo(
                chat_id=chat_id,
                photo = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/srpski/{card['image']}?upts={upts}',
                reply_markup=reply_markup,
                caption=caption
            )
            return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Учить карточки', callback_data=f'button_next'),
            InlineKeyboardButton('Статистика', callback_data=f'button_stats'),
        ],
        [
            InlineKeyboardButton('Подробная справка', callback_data=f'button_help'),
        ],
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

    app.add_handler(CallbackQueryHandler(button_stats, pattern='^button_stats$'))
    app.add_handler(CallbackQueryHandler(button_new_cards, pattern='^button_new_cards$'))

    app.add_handler(get_new_card_conversation_handler())
    app.add_handler(get_hide_card_conversation_handler())
    app.add_handler(get_update_card_conversation_handler())

    app.add_handler(MessageHandler(filters.ALL, default_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
