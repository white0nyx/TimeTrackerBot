import os

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, MediaGroup, CallbackQuery

from tgbot.keyboards.inline import generate_statistic_time_keyboard
from tgbot.misc.analytics import get_plot_total_time, get_diagram_week_statistic, get_circle_diagram_sessions_durations, \
    is_possible_get_circle_diagram_sessions_durations, get_diagram_by_hours_in_day
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, fill_all_categories_past_date
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
    categories = user.get('categories')

    album = MediaGroup()
    text = get_statistic(user_id, categories, period_statistic)

    # График изменения количества общих часов
    get_plot_total_time(str(user_id))
    all_time_plot = InputFile(path_or_bytesio=f'data/{user_id}_total_time.png')
    album.attach_photo(all_time_plot)

    # Диаграмма со статистикой по дням
    get_diagram_week_statistic(str(user_id))
    diagram_week_statistic = InputFile(path_or_bytesio=f'data/{user_id}_week_statistic.png')
    album.attach_photo(diagram_week_statistic)

    # Круговая диаграмма по продолжительности сессий
    if is_possible_get_circle_diagram_sessions_durations(user_id):
        get_circle_diagram_sessions_durations(str(user_id))
        circle_diagram_sessions_durations = InputFile(
            path_or_bytesio=f'data/{user_id}_sessions_durations_statistic.png')
        album.attach_photo(circle_diagram_sessions_durations)

    # Диаграмма со статистикой по часам
    if is_possible_get_circle_diagram_sessions_durations(user_id):
        get_diagram_by_hours_in_day(str(user_id))
        sessions_hours = InputFile(
            path_or_bytesio=f'data/{user_id}_session_count_by_hour_in_day.png')
        album.attach_photo(sessions_hours)

    async with state.proxy() as data:
        data['message_img'] = await message.answer_media_group(album)
        data['message_text'] = await message.answer(text, reply_markup=generate_statistic_time_keyboard(user_id))

    os.remove(f'data/{user_id}_total_time.png')
    os.remove(f'data/{user_id}_week_statistic.png')

    if is_possible_get_circle_diagram_sessions_durations(user_id):
        os.remove(f'data/{user_id}_sessions_durations_statistic.png')
        os.remove(f'data/{user_id}_session_count_by_hour_in_day.png')


def register_statistic_button(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопку Статистика"""
    dp.register_message_handler(statistic_button, Text('📊 Статистика'),
                                state=[None, States.my_categories, States.category_menu])


async def changing_statistics_period(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопки смены периода статистики"""
    await call.answer(cache_time=10)
    async with state.proxy() as data:
        for img in data['message_img']:
            await img.delete()
        await data['message_text'].delete()


def register_changing_statistics_period(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопки смены периода статистики"""
    dp.register_callback_query_handler(callback=changing_statistics_period,
                                       text=['day', 'week', 'month', 'year', 'all_time'],
                                       state='*')


def register_all_statistic(dp):
    """Регистрация всех обработчиков связанных со статистикой"""
    register_statistic_button(dp)
    register_changing_statistics_period(dp)
