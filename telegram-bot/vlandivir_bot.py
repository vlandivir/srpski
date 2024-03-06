import os
import json
import random

from dotenv import load_dotenv

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

load_dotenv(".env")
token = os.getenv("VLANDIVIR_BOT_TOKEN")
token = os.getenv("TEST_BOT_TOKEN", token) # for local run python3 telegram-bot/vlandivir_bot.py
current_dir = os.path.dirname(os.path.abspath(__file__))

cards_path = os.path.join(current_dir, 'release-cards')
cards_file = os.path.join(current_dir, 'language-images.json')

with open(cards_file, 'r', encoding='utf-8') as file:
    cards_data = json.load(file)

async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update)
    print(context)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    random_card = random.choice(cards_data)
    filename = random_card['image']
    filepath = os.path.join(cards_path, filename)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Next', callback_data='next_card')]])

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(filepath, 'rb'),
        reply_markup=keyboard,
        caption=random_card['ru'],
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
