import os
import random

from dotenv import load_dotenv

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Загружаем переменные окружения из файла .env, который находится на уровень выше
load_dotenv(".env")

# Получаем токен из переменных окружения
token = os.getenv("VLANDIVIR_BOT_TOKEN")

# Теперь переменная token содержит ваш токен
print(token)  # Просто для проверки, в продакшене лучше убрать

async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update)
    print(context)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(current_dir, '..', 'chat-gpt', 'language-cards', 'result-images')
    filename = random.choice(os.listdir(directory))
    filepath = os.path.join(directory, filename)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Next", callback_data='next_card')]])
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(filepath, 'rb'), reply_markup=keyboard)

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
