from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

add_new_category_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='➕ Новая категория', callback_data='new_category')
    ]
])

yes_no_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data='yes'),
        InlineKeyboardButton(text='Нет', callback_data='no')
    ]
])


def generate_category_keyboard(categories=()):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for i, category in enumerate(categories):
        name_category = category['name']
        callback_data = category['callback_data']
        keyboard.insert(InlineKeyboardButton(text=name_category, callback_data=callback_data))

    keyboard.insert(InlineKeyboardButton(text='➕ Новая категория', callback_data='new_category'))

    return keyboard
