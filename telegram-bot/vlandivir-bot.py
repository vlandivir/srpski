from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Загружаем переменные окружения из файла .env, который находится на уровень выше
load_dotenv(".env")

# Получаем токен из переменных окружения
token = os.getenv("VLANDIVIR_BOT_TOKEN")

# Теперь переменная token содержит ваш токен
print(token)  # Просто для проверки, в продакшене лучше убрать

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update)
    print(context)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def main():
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("hello", hello))

    app.run_polling()

if __name__ == '__main__':
    main()
