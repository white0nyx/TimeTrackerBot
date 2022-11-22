# Reply-клавиатуры и кнопки

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главная клавиатура
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='▶ Старт')
    ],
    [
        KeyboardButton(text='📓 Мои категории'),
        KeyboardButton(text='📊 Статистика'),
    ],
], resize_keyboard=True)