# Cтейты

from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    """Класс стейтов"""
    add_new_category_name = State()
    add_new_category_minutes = State()
    confirm_data = State()

