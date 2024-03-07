import os
import json
import random

from dotenv import load_dotenv

from google_db_load_cards import get_cards

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

load_dotenv(".env")
TAG_NAME = os.getenv("TAG_NAME")

token = os.getenv("VLANDIVIR_BOT_TOKEN")
token = os.getenv("TEST_BOT_TOKEN", token) # for local run python3 telegram-bot/vlandivir_bot.py
current_dir = os.path.dirname(os.path.abspath(__file__))

cards_path = os.path.join(current_dir, 'release-cards')
cards_files = os.listdir(cards_path)
cards_data = get_cards()
filtered_cards = [card for card in cards_data if card['image'] in cards_files]

chats = {}

async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update)
    print(context)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. {TAG_NAME}-{len(filtered_cards)}')
    chat_key = f'chat_{update.effective_chat.id}'
    if chats.get(chat_key):
        await update.message.reply_text(f'{chats[chat_key]}')

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    chat_key = f'chat_{chat_id}'
    if not chats.get(chat_key) or chats[chat_key]["pointer"] >= len(filtered_cards):
        cards_order = list(range(0, len(filtered_cards) - 1))
        random.shuffle(cards_order)
        chats[chat_key] = {"cards_order": cards_order, "pointer": 0}

    current_chat = chats[chat_key]
    card_num = current_chat["cards_order"][current_chat["pointer"]]
    next_card = filtered_cards[card_num]
    chats[chat_key]["pointer"] += 1

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

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback, чтобы убрать часики ожидания на кнопке
    await send_card(update, context)

def main():
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("hello", say_hello))
    app.add_handler(CommandHandler("card", send_card))

    app.add_handler(CallbackQueryHandler(button, pattern='^next_card$'))

    app.run_polling()

if __name__ == '__main__':
    main()
