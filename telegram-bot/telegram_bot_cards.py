import os
import json

from dotenv import load_dotenv
from datetime import datetime

from do_space import file_exists_in_do_space, add_text_to_image_do

from postgres_db import (
    get_or_create_user, update_user_current_set, get_all_cards, update_user_card_response,
    get_new_cards_pack, get_user_stats
)
from postgres_db_cards import update_card

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from telegram_bot_helpers import common_button_handler
from telegram_bot_messages import create_progress_bar

load_dotenv('.env')
TAG_NAME = os.getenv('TAG_NAME')

cards_index = {}
chats = {}
cards_data = {}

def init_cards_cache():
    global cards_data, cards_index
    cards_data = get_all_cards()
    for card in cards_data:
        cards_index[card['id']] = card

def get_chat_key(id):
    return f'chat_{id}'

def get_card_by_id(card_id):
    return cards_index.get(card_id, None)

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

def prepare_user_stats(user_id: str) -> str:
    return '\n'.join([
        f"{s.get('response_date','')} 🔴 {s.get('complex','')}  🟡 {s.get('hard','')} 🟢 {s.get('ok','')} 🔵 {s.get('easy','')}"
        for s in get_user_stats(user_id)
    ])

async def send_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat_id = await common_button_handler(update)

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
        await context.bot.send_message(
            chat_id=chat_id,
            text=prepare_user_stats(user['id']),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⏩ Continue', callback_data=f'button_next')]])
        )
        return

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
    file_id = next_card.get('id', 0)

    keyboard_markup = [
        [
            InlineKeyboardButton('🔴 ???', callback_data=f'button_complex:{file_id}'),
            InlineKeyboardButton('🟡 Hard ', callback_data=f'button_hard:{file_id}'),
            InlineKeyboardButton('🟢 Ok', callback_data=f'button_ok:{file_id}'),
            InlineKeyboardButton('🔵 Easy', callback_data=f'button_easy:{file_id}'),
        ]
    ]

    second_row = [
        InlineKeyboardButton('❌ Hide', callback_data=f'button_hide:{file_id}'),
        InlineKeyboardButton('⏩ Skip', callback_data=f'button_next'),
    ]

    if (user['id'] == '150847737'):
        keyboard_markup.append([
            InlineKeyboardButton('🔄 Ref', callback_data=f'button_new_cards'),
            InlineKeyboardButton('➕ Add', callback_data=f'button_add_card'),
            InlineKeyboardButton('♻️ Up', callback_data=f'button_update_image:{file_id}'),
        ])

    keyboard_markup.append(second_row)
    keyboard = InlineKeyboardMarkup(keyboard_markup)

    if not file_exists_in_do_space('vlandivir', f'srpski/{filename}'):
        await send_card(update, context)
        return

    caption = f"{create_progress_bar(card_weight)}\n" if card_weight is not None else ''
    caption += next_card['ru']

    upts = str(int(next_card['updated_at'].timestamp())) if isinstance(next_card['updated_at'], datetime) else ''

    await context.bot.send_photo(
        chat_id=chat_id,
        photo = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/srpski/{filename}?upts={upts}',
        reply_markup=keyboard,
        caption=caption,
        has_spoiler=True,
    )

# HANDLERS

async def update_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    init_cards_cache()
    await update.message.reply_text(f'{TAG_NAME}-{len(cards_data)}')

async def say_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. {TAG_NAME}-{len(cards_data)}')

    chat_id = update.effective_chat.id
    chat_key = get_chat_key(chat_id)
    if chats.get(chat_key):
        await update.message.reply_text(json.dumps(chats[chat_key], indent=2))

async def button_next_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await send_card(update, context)

async def button_card_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user, chat_id = await common_button_handler(update)
    data = query.data.split(':')
    update_user_card_response(user['id'], data[1], data[0])
    await send_card(update, context)

async def button_new_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat_id = await common_button_handler(update)

    chat_key = get_chat_key(chat_id)
    chats[chat_key] = create_new_set(user)

    await context.bot.send_message(
        chat_id=chat_id,
        text=json.dumps(chats[chat_key], indent=2)
    )

async def button_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat_id = await common_button_handler(update)

    text = prepare_user_stats(user['id'])

    await context.bot.send_message(
        chat_id=chat_id,
        text=text or 'Ответьте на несколько карточек, чтобы получить статистику'
    )

async def button_update_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user, chat_id = await common_button_handler(update)

    data = query.data.split(':')
    card_id = int(data[1])
    card = get_card_by_id(card_id)
    if card is not None:
        data = {'sr': str(card['sr']), 'ru': str(card['ru']), 'en': str(card['en'])}
        image = update_card(card_id, data)

        print(image)
        if image:
            add_text_to_image_do(
                'vlandivir', 'srpski-sources/', 'srpski/', image, {'image': image, **data}
            )

            upts = str(int(card['updated_at'].timestamp())) if isinstance(card['updated_at'], datetime) else ''

            await context.bot.send_photo(
                chat_id=chat_id,
                photo = f'https://vlandivir.fra1.cdn.digitaloceanspaces.com/srpski/{card['image']}?upts={upts}',
            )
