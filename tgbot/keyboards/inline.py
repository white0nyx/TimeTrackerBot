from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура с паузой и остановкой
pause_stop_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='⏸ Пауза', callback_data='pause'),
        InlineKeyboardButton(text='⏹ Стоп', callback_data='stop'),
    ]
])

# Клавиатура с продолжением и остановкой
resume_stop_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='▶ Продолжить', callback_data='resume'),
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


# Клавиатура меню категории
category_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='👀 Посмотреть сессии', callback_data='category_operations')
    ],
    [
        InlineKeyboardButton(text='➕ Добавить время', callback_data='add_time')
    ],
    [
        InlineKeyboardButton(text='✏ Изменить название', callback_data='change_title')
    ],
    [
        InlineKeyboardButton(text='❌ Удалить категорию', callback_data='delete_category')
    ],
])

# Кнопка Не добавлять
no_add_inline_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Не добавлять', callback_data='no_add')
    ]
])

# Кнопка Удалить операцию
delete_operation_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='🗑 Удалить операцию', callback_data='delete_operation')
    ]
])
