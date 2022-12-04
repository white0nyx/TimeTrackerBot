# Cтейты

from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    """Класс стейтов"""

    # Добавление новой категории
    my_categories = State()
    add_new_category_name = State()
    add_new_category_based_minutes = State()
    confirm_data = State()

    # Добавление времени к категории
    add_time_to_category = State()

    # Меню категории
    category_menu = State()

    # Ожидание минут для добавления
    wait_add_minutes = State()
    confirm_add_minutes = State()

    # Ожидание минут для вычитания
    wait_sub_minutes = State()
    confirm_sub_minutes = State()

    # Ожидание нового названия
    wait_new_title = State()

    # Подтверждение удаления категории
    delete_category_confirm = State()
