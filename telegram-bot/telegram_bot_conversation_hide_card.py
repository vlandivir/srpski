import json
import re
import time
import io

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)

from postgres_db import update_user_card_response
from telegram_bot_helpers import get_user_from_update

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ConversationHandler, CallbackContext

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

CONFIRMATION = 1

async def ask_confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    file_id = query.data.split(':')[1]
    context.user_data['file_id'] = file_id

    keyboard = [[
        InlineKeyboardButton('❌ Hide', callback_data='confirm_delete'),
        InlineKeyboardButton('Отмена', callback_data='cancel_delete')
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Вы уверены, что хотите скрыть карточку навсегда?',
        reply_markup=reply_markup
    )

    return CONFIRMATION

async def confirm_delete(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user = get_user_from_update(update)
    update_user_card_response(user['id'], context.user_data['file_id'], 'button_hide')

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Карточка успешно скрыта.',
    )

    return ConversationHandler.END

async def cancel_delete(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Операция отменена.',
    )

    return ConversationHandler.END

def get_hide_card_conversation_handler():
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_confirmation, pattern='^button_hide:.+$')],
        states={
            CONFIRMATION: [
                CallbackQueryHandler(ask_confirmation, pattern='^button_hide:.+$'),
                CallbackQueryHandler(confirm_delete, pattern='^confirm_delete$'),
                CallbackQueryHandler(cancel_delete, pattern='^cancel_delete$'),
            ],
        },
        fallbacks=[],
    )

    return conversation_handler
