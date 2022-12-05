# Cтейты

from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    """Класс стейтов"""

    # Добавление новой категории
    my_categories = State()
    add_new_category_name = State()
    add_new_category_based_seconds = State()
    confirm_data = State()

    # Добавление времени к категории
    add_time_to_category = State()

    # Меню категории
    category_menu = State()

    # Ожидание и подтверждение времени для добавления
    wait_add_time = State()
    confirm_add_time = State()

    # Ожидание и подтверждение времени для вычитания
    wait_sub_time = State()
    confirm_sub_time = State()

    # Ожидание и подтверждение нового названия
    wait_new_title = State()
    confirm_new_title = State()

    # Подтверждение удаления категории
    confirm_delete_category = State()
