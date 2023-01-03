import os

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, MediaGroup, CallbackQuery

from tgbot.keyboards.inline import generate_statistic_period_keyboard
from tgbot.misc.analytics import get_plot_total_time, get_diagram_week_statistic, get_circle_diagram_sessions_durations, \
    is_possible_get_graphics, get_diagram_by_hours_in_day
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date
from tgbot.misc.work_with_text import get_statistic


async def statistic_button(message: Message, state: FSMContext):
    """Обработка нажатия на кнопку Статистика"""
    user_id = message.from_user.id

    fill_all_categories_past_date(user_id)
    user = get_user_from_json_db(user_id)

    if not user.get('categories'):
        await message.answer('Для получения статистики у вас должна быть установлена хотя бы одна категория')
        return

    period_statistic = user.get('period_statistic')

    if period_statistic == 'day':
        period_statistic_in_days = 1

    elif period_statistic == 'week':
        period_statistic_in_days = 7

    elif period_statistic == 'month':
        period_statistic_in_days = 30

    elif period_statistic == 'year':
        period_statistic_in_days = 365

    else:
        period_statistic_in_days = None

    categories = user.get('categories')

    album = MediaGroup()
    text = get_statistic(user_id, categories, period_statistic)

    if text[0] == '⚠':
        await message.answer(text)
        return

    # График изменения количества общих часов
    get_plot_total_time(str(user_id), period_statistic_in_days)
    all_time_plot = InputFile(f'data/{user_id}_total_time.png')
    album.attach_photo(all_time_plot)

    # Диаграмма со статистикой по дням
    get_diagram_week_statistic(str(user_id), period_statistic_in_days)
    diagram_week_statistic = InputFile(f'data/{user_id}_week_statistic.png')
    album.attach_photo(diagram_week_statistic)

    # Круговая диаграмма по продолжительности сессий
    get_circle_diagram_sessions_durations(str(user_id))
    circle_diagram_sessions_durations = InputFile(f'data/{user_id}_sessions_durations_statistic.png')
    album.attach_photo(circle_diagram_sessions_durations)

    # Диаграмма со статистикой по часам
    get_diagram_by_hours_in_day(str(user_id))
    sessions_hours = InputFile(f'data/{user_id}_session_count_by_hour_in_day.png')
    album.attach_photo(sessions_hours)

    async with state.proxy() as data:
        data['message'] = message
        data['message_img'] = await message.answer_media_group(album)
        data['message_text'] = await message.answer(text, reply_markup=generate_statistic_period_keyboard(user_id))

    os.remove(f'data/{user_id}_total_time.png')
    os.remove(f'data/{user_id}_week_statistic.png')
    os.remove(f'data/{user_id}_sessions_durations_statistic.png')
    os.remove(f'data/{user_id}_session_count_by_hour_in_day.png')


def register_statistic_button(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопку Статистика"""
    dp.register_message_handler(statistic_button, Text('📊 Статистика'),
                                state=[None, States.my_categories, States.category_menu])


async def changing_statistics_period_button(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку ИЗМЕНИТЬ ПЕРИОД СТАТИСТИКИ"""
    user_id = call.from_user.id
    await call.answer(cache_time=1)
    async with state.proxy() as data:
        for img in data['message_img']:
            await img.delete()
        await data['message_text'].delete()
    await call.message.answer('Выберите период, за который хотите увидеть статистику',
                              reply_markup=generate_statistic_period_keyboard(user_id))


def register_changing_statistics_period_button(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопку ИЗМЕНИТЬ ПЕРИОД СТАТИСТИКИ"""
    dp.register_callback_query_handler(changing_statistics_period_button, text='change_period', state='*')


async def period_selection(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопки смены периода статистики"""
    user_id = call.from_user.id

    await call.answer(cache_time=10)

    user = get_user_from_json_db(user_id)
    user['period_statistic'] = call.data
    update_user_data(user_id, user)

    async with state.proxy() as data:
        message = data['message']

    await statistic_button(message, state)


def register_period_selection(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопки смены периода статистики"""
    dp.register_callback_query_handler(callback=period_selection,
                                       text=['day', 'week', 'month', 'year', 'all_time'],
                                       state='*')


def register_all_statistic(dp):
    """Регистрация всех обработчиков связанных со статистикой"""
    register_statistic_button(dp)
    register_changing_statistics_period_button(dp)
    register_period_selection(dp)
