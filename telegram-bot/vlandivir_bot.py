import os

from dotenv import load_dotenv

from do_space import file_exists_in_do_space
from postgres_db import get_or_create_user, update_user_current_set, get_all_cards, update_user_card_response, get_new_cards_pack
from postgres_create_or_update_db import create_or_update_db

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

load_dotenv('.env')
TAG_NAME = os.getenv('TAG_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')
POSTGRES_CONNECTION_STRING = os.getenv('POSTGRES_CONNECTION_STRING')

token = os.getenv('VLANDIVIR_BOT_TOKEN')
token = os.getenv('TEST_BOT_TOKEN', token) # for local run python3 telegram-bot/vlandivir_bot.py

create_or_update_db()

cards_data = get_all_cards()
cards_index = {}
for card in cards_data:
    cards_index[card['generated_at']] = card

chats = {}

def get_chat_key(id):
    return f'chat_{ENVIRONMENT.lower()}_{id}'

async def update_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global cards_data, cards_index
    cards_data = get_all_cards()
    cards_index = {}
    for card in cards_data:
        cards_index[card['generated_at']] = card

    await update.message.reply_text(f'Hello {update.effective_user.first_name}. {TAG_NAME}-{len(cards_data)}')

async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. {TAG_NAME}-{len(cards_data)}')

    chat_id = update.effective_chat.id
    chat_key = get_chat_key(chat_id)
    if chats.get(chat_key):
        await update.message.reply_text(chats[chat_key])

def get_user_from_update(update: Update):
    if update.message:
        user = update.message.from_user
    elif update.callback_query:
        user = update.callback_query.from_user

    if not user:
        return None

    return {
        'id': str(user.id),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'language_code': user.language_code,
    }

def create_new_set(user):
    card_ids = get_new_cards_pack(user['id'])
    current_set = { 'cards_order': card_ids, 'pointer': 0 }
    update_user_current_set(user, current_set)
    return current_set

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_update(update)
    if not user:
        return None

    chat_id = update.effective_chat.id
    chat_key = get_chat_key(chat_id)

    if not chats.get(chat_key):
        user = get_or_create_user(user)
        if not user:
            return None

        if user.get('current_set'):
            chats[chat_key] = user.get('current_set')
        else:
            chats[chat_key] = create_new_set(user)

    if chats[chat_key]['pointer'] >= len(chats[chat_key]['cards_order']):
        chats[chat_key] = create_new_set(user)

    current_set = chats[chat_key]
    card_num = current_set['cards_order'][current_set['pointer']]
    next_card = cards_index.get(
        card_num,
        cards_data[card_num if card_num < len(cards_data) else 0]
    )
    chats[chat_key]['pointer'] += 1
    update_user_current_set(user, current_set)

    filename = next_card['image']
    fileid = next_card.get('generated_at', 0)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('🔴 ???', callback_data=f'button_complex:{fileid}'),
            InlineKeyboardButton('🟡 Hard ', callback_data=f'button_hard:{fileid}'),
            InlineKeyboardButton('🟢 Ok', callback_data=f'button_ok:{fileid}'),
            InlineKeyboardButton('🔵 Easy', callback_data=f'button_easy:{fileid}'),
        ],
        [
            InlineKeyboardButton('Skip', callback_data=f'button_next'),
        ]
    ])

    if not file_exists_in_do_space('vlandivir', f'srpski/{filename}'):
        await send_card(update, context)
        return

    await context.bot.send_photo(
        chat_id=chat_id,
        photo = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/srpski/{filename}',
        reply_markup=keyboard,
        caption=next_card['ru'],
        has_spoiler=True,
    )

async def button_next_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback, чтобы убрать часики ожидания на кнопке
    await send_card(update, context)

async def button_next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback, чтобы убрать часики ожидания на кнопке

    user = get_user_from_update(update)
    data = query.data.split(':')
    update_user_card_response(user['id'], data[1], data[0])
    await send_card(update, context)

def main():
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler('hello', say_hello))
    app.add_handler(CommandHandler('card', send_card))
    app.add_handler(CommandHandler('update', update_cards))

    app.add_handler(CallbackQueryHandler(button_next, pattern='^button_complex:'))
    app.add_handler(CallbackQueryHandler(button_next, pattern='^button_hard:'))
    app.add_handler(CallbackQueryHandler(button_next, pattern='^button_ok:'))
    app.add_handler(CallbackQueryHandler(button_next, pattern='^button_easy:'))

    app.add_handler(CallbackQueryHandler(button_next_card, pattern='^button_next$'))

    app.run_polling()

if __name__ == '__main__':
    main()
