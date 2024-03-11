import os
import random

from dotenv import load_dotenv

from postgres_db import create_or_update_db

from google_db_load_cards import get_cards
from google_db_chats import get_or_create_chat_data

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

load_dotenv('.env')
TAG_NAME = os.getenv('TAG_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')
POSTGRES_CONNECTION_STRING = os.getenv('POSTGRES_CONNECTION_STRING')

token = os.getenv('VLANDIVIR_BOT_TOKEN')
token = os.getenv('TEST_BOT_TOKEN', token) # for local run python3 telegram-bot/vlandivir_bot.py
current_dir = os.path.dirname(os.path.abspath(__file__))

cards_path = os.path.join(current_dir, 'release-cards')
cards_files = os.listdir(cards_path)
cards_data = get_cards()
filtered_cards = [card for card in cards_data if card['image'] in cards_files]

chats = {}

create_or_update_db()

def get_chat_key(id):
    return f'chat_{ENVIRONMENT.lower()}_{id}'

async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # print(update)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. {TAG_NAME}-{len(filtered_cards)}')

    chat_id = update.effective_chat.id
    chat_key = get_chat_key(chat_id)
    if chats.get(chat_key):
        await update.message.reply_text(chats[chat_key])

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # print(update)
    chat_id = update.effective_chat.id
    chat_key = get_chat_key(chat_id)
    if not chats.get(chat_key) or chats[chat_key]['pointer'] >= len(chats[chat_key]['cards_order']):
        sheet_data = get_or_create_chat_data(chat_key, {})
        current_set = sheet_data.get('current_set', False)
        if current_set and current_set.get('pointer', 0) < len(current_set.get('cards_order', [])):
            chats[chat_key] = current_set
        else:
            cards_order = list(range(0, len(filtered_cards) - 1))
            random.shuffle(cards_order)
            chats[chat_key] = { 'cards_order': cards_order[:20], 'pointer': 0 }

    current_chat = chats[chat_key]
    card_num = current_chat['cards_order'][current_chat['pointer']]
    next_card = filtered_cards[card_num]
    chats[chat_key]['pointer'] += 1

    filename = next_card['image']
    filepath = os.path.join(cards_path, filename)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Next', callback_data='next_card')]])

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=open(filepath, 'rb'),
        reply_markup=keyboard,
        caption=next_card['ru'],
        has_spoiler=True,
    )

    if update.message:
        user = update.message.from_user
    elif update.callback_query:
        user = update.callback_query.from_user

    if user:
        user_dict = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'language_code': user.language_code,
            'current_set': chats[chat_key],
        }
        data = get_or_create_chat_data(chat_key, user_dict)
        print('')
        print(data)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback, чтобы убрать часики ожидания на кнопке
    await send_card(update, context)

def main():
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler('hello', say_hello))
    app.add_handler(CommandHandler('card', send_card))

    app.add_handler(CallbackQueryHandler(button, pattern='^next_card$'))

    app.run_polling()

if __name__ == '__main__':
    main()
