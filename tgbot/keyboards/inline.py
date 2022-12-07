from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Кнопка остановки секундомера
stop_timer_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='⏹ Стоп', callback_data='stop'),
    ]
])

# Клавиатура с кнопками - да / нет
yes_no_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data='yes'),
        InlineKeyboardButton(text='Нет', callback_data='no')
    ]
])


def generate_category_keyboard(categories=(), no_add_button=False):
    """Создание клавиатуры с категориями"""
    keyboard = InlineKeyboardMarkup(row_width=1)

    for i, category in enumerate(categories):
        name_category = category['name']
        callback_data = category['callback_data']
        keyboard.insert(InlineKeyboardButton(text=name_category, callback_data=callback_data))

    keyboard.insert(InlineKeyboardButton(text='➕ Новая категория', callback_data='new_category'))

    if no_add_button:
        keyboard.insert(InlineKeyboardButton(text='Не добавлять', callback_data='no_add'))

    return keyboard


category_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='➕ Добавить время', callback_data='add_time'),
        InlineKeyboardButton(text='➖ Вычесть время', callback_data='subtract_time'),
    ],
    [
        InlineKeyboardButton(text='✏ Изменить название', callback_data='change_title')
    ],
    [
        InlineKeyboardButton(text='❌ Удалить категорию', callback_data='delete_category')
    ],
])

no_add_inline_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Не добавлять', callback_data='no_add')
    ]
])