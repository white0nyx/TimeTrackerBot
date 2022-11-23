# Cтейты

from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    """Класс стейтов"""

    # Добавление новой категории
    add_new_category_name = State()
    add_new_category_based_minutes = State()
    confirm_data = State()

    # Добавление времени к категории
    add_time_to_category = State()
