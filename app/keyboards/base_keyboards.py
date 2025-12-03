from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


reply_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Чат'),KeyboardButton(text='НАстройки')]
], resize_keyboard=True, input_field_placeholder="Выберите режим")

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Режим отправки сообщений", callback_data='dialog_mod')]
],resize_keyboard=True, input_field_placeholder="Выберите режим")

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена',callback_data='cancel')]])