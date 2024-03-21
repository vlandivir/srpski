import os
import json

from dotenv import load_dotenv

from do_space import file_exists_in_do_space
from postgres_db import get_or_create_user, update_user_current_set, get_all_cards, update_user_card_response, get_new_cards_pack, get_user_stats
from postgres_create_or_update_db import create_or_update_db

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

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
    cards_order_with_weight = get_new_cards_pack(user['id'])
    cards_order =  [x[0] for x in cards_order_with_weight]

    current_set = {
        'cards_order': cards_order,
        'cards_order_with_weight': cards_order_with_weight,
        'pointer': 0,
    }

    print(current_set)

    update_user_current_set(user, current_set)
    return current_set

async def new_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_update(update)
    if not user:
        return None

    chat_id = update.effective_chat.id
    chat_key = get_chat_key(chat_id)
    chats[chat_key] = create_new_set(user)
    await update.message.reply_text(chats[chat_key])

def progress_bar(weight):
    red_square = '🟥'
    yellow_square = '🟨'
    green_square = '🟩'
    blue_square = '🟦'
    black_square = '⬛'

    squares = [red_square] * 2 + [yellow_square] * 3 + [green_square] * 3 + [blue_square] * 2

    if weight > 1024:
        return red_square + black_square * 9
    elif weight == 0:
        return black_square * 10
    elif 0 < weight <= 1:
        return ''.join(squares)
    else:
        painted_squares = min(10, max(1, 10 - int(weight).bit_length() + 1))
        return ''.join(squares[:painted_squares]) + black_square * (10 - painted_squares)

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
        await context.bot.send_message(chat_id=chat_id, text=prepare_user_stats(user['id']))

    current_set = chats[chat_key]

    card_weight = None
    if (current_set.get('cards_order_with_weight')):
        card_num, card_weight = current_set['cards_order_with_weight'][current_set['pointer']]
    else:
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
            # InlineKeyboardButton('❌ Skip', callback_data=f'button_next'),
            InlineKeyboardButton('⏩ Skip', callback_data=f'button_next'),
            InlineKeyboardButton('⬇️ More', callback_data=f'button_more'),
        ]
    ])

    if not file_exists_in_do_space('vlandivir', f'srpski/{filename}'):
        await send_card(update, context)
        return

    caption = f"{progress_bar(card_weight)}\n" if card_weight is not None else ''
    caption += next_card['ru']

    await context.bot.send_photo(
        chat_id=chat_id,
        photo = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/srpski/{filename}',
        reply_markup=keyboard,
        caption=caption,
        has_spoiler=True,
    )

async def button_next_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback, чтобы убрать часики ожидания на кнопке
    await send_card(update, context)

async def button_card_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback, чтобы убрать часики ожидания на кнопке

    user = get_user_from_update(update)
    data = query.data.split(':')
    update_user_card_response(user['id'], data[1], data[0])
    await send_card(update, context)

def prepare_user_stats(user_id: str) -> str:
    return '\n'.join([
        f"{s.get('response_date','')} 🔴 {s.get('complex','')}  🟡 {s.get('hard','')} 🟢 {s.get('ok','')} 🔵 {s.get('easy','')}"
        for s in get_user_stats(user_id)
    ])

async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_update(update)
    if not user:
        return None

    await update.message.reply_text(prepare_user_stats(user['id']))

async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user_from_update(update)
    if not user:
        return None

    chat_id = update.effective_chat.id

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

def main():
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler('hello', say_hello))
    app.add_handler(CommandHandler('card', send_card))
    app.add_handler(CommandHandler('update', update_cards))
    app.add_handler(CommandHandler('new', new_cards))
    app.add_handler(CommandHandler('stats', user_stats))

    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_complex:'))
    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_hard:'))
    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_ok:'))
    app.add_handler(CallbackQueryHandler(button_card_response, pattern='^button_easy:'))
    app.add_handler(CallbackQueryHandler(button_next_card, pattern='^button_next$'))

    app.add_handler(CallbackQueryHandler(oops_handler, pattern='^button_help$'))
    app.add_handler(CallbackQueryHandler(oops_handler, pattern='^button_more$'))

    app.add_handler(MessageHandler(filters.ALL, default_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
