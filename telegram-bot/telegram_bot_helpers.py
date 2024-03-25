from typing import Tuple, Dict

from telegram import Update

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

async def common_button_handler(update: Update) -> Tuple[Dict[str, any], int]:
    query = update.callback_query
    if query is not None:
        await query.answer()

    user = get_user_from_update(update)
    chat_id = update.effective_chat.id

    return (user, chat_id)
