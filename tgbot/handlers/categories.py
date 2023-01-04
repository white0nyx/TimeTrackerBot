from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import yes_no_keyboard, generate_category_keyboard
from tgbot.keyboards.reply import cancel_button, main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date, \
    get_all_category_names
from tgbot.misc.work_with_text import get_the_time_in_seconds, is_valid_time, get_time_in_str_text


async def my_categories_button(message: Message):
    """Обработка нажатия на кнопку КАТЕГОРИИ"""

    user_id = str(message.from_user.id)

    user = get_user_from_json_db(user_id)
    categories = user.get('categories')
    fill_all_categories_past_date(user_id)
    if not categories:
        await message.answer('У вас пока нет ни одной добавленной категории.\n\n'
                             'Чтобы добавить категорию воспользуйтесь кнопкой ниже.',
                             reply_markup=generate_category_keyboard())

    else:
        await message.answer('📓 Ваши категории', reply_markup=generate_category_keyboard(categories))

    await States.my_categories.set()


def register_my_categories_button(dp: Dispatcher):
    """Регистрация обработчика кнопки КАТЕГОРИИ"""
    dp.register_message_handler(my_categories_button,
                                Text('📓 Мои категории'),
                                state=[None, States.my_categories, States.category_menu])


async def add_new_category(call: CallbackQuery):
    """Обработка кнопки НОВАЯ КАТЕГОРИЯ"""
    await call.message.delete()
    await call.answer(cache_time=60)
    await States.add_new_category_name.set()
    await call.message.answer('Введите название для новой категории', reply_markup=cancel_button)


def register_add_new_category(dp: Dispatcher):
    """Регистрация обработки кнопки НОВАЯ КАТЕГОРИЯ"""
    dp.register_callback_query_handler(add_new_category,
                                       text='new_category',
                                       state=[None,
                                              States.add_time_to_category,
                                              States.my_categories,
                                              States.add_new_category_name,
                                              States.add_new_category_based_seconds])


async def save_name_new_category(message: Message, state: FSMContext):
    """Сохранение названия категории и запрос потраченного времени"""
    category_name = message.text
    user_id = message.from_user.id

    if len(category_name) > 32:
        await message.answer('⚠ Слишком длинное название\n\n'
                             'Вы можете указать название длиной до 32 символов\n\n'
                             'Пожалуйста, повторите ввод', reply_markup=cancel_button)
        return

    if category_name in get_all_category_names(user_id):
        await message.answer('⚠ Категория с таким названием уже существует\n\n'
                             'Пожалуйста, повторите ввод', reply_markup=cancel_button)
        return

    async with state.proxy() as data:
        data['suspect_category'] = {}
        data['suspect_category']['name'] = category_name

    await message.answer(f'Укажите количество потраченного времени на эту категорию до начала использования бота '
                         f'в формате чч:мм:сс\n\n'
                         f'Например: 01:20:03 или 1:20:3\n\n'
                         f'Вы можете отправить 0, если не хотите добавлять время', reply_markup=cancel_button)
    await States.add_new_category_based_seconds.set()


def register_save_name_new_category(dp: Dispatcher):
    """Регистрация обработчика сохранения названия категории"""
    dp.register_message_handler(save_name_new_category, state=[States.add_new_category_name])


async def save_based_minutes_new_category(message: Message, state: FSMContext):
    """Сохранение количества потраченных минут и запрос подтверждения данных"""
    str_time = message.text

    if is_valid_time(str_time) is not True:
        await message.answer(text=is_valid_time(str_time), reply_markup=cancel_button)
        return

    seconds = get_the_time_in_seconds(str_time)
    async with state.proxy() as data:
        data['suspect_category']['based_seconds'] = int(seconds)
        data['suspect_category']['seconds'] = int(seconds)
        data['suspect_category']['operations'] = []

    async with state.proxy() as data:
        category_name = data['suspect_category']['name']
        category_seconds = data['suspect_category']['based_seconds']
        category_time = get_time_in_str_text(category_seconds)

    await message.answer(f'Подтвердите введённые данные: \n\n'
                         f'Категория: {category_name}\n'
                         f'Потрачено времени: {category_time}', reply_markup=yes_no_keyboard)

    await States.confirm_data.set()


def register_save_minutes_new_category(dp: Dispatcher):
    """Регистрация обработчика сохранения потраченных минут"""
    dp.register_message_handler(save_based_minutes_new_category, state=[States.add_new_category_based_seconds])


async def confirm_data(call: CallbackQuery, state: FSMContext):
    """Подтверждение пользователем данных и их сохранение"""
    await call.answer(cache_time=60)
    await call.message.delete()
    user_id = call.from_user.id
    if call.data == 'yes':

        user = get_user_from_json_db(user_id)
        async with state.proxy() as data:

            suspect_category = data['suspect_category']

            if len(user['categories']) == 0:
                new_number = 0

            else:
                new_number = int(user['categories'][-1]['callback_data'].split('category_')[-1]) + 1

            suspect_category['callback_data'] = 'category_' + str(new_number)
            user['categories'].append(suspect_category)

            if data.get('last_time') is not None:
                new_time = get_the_time_in_seconds(data.get('last_time'))

                old_time = int(user['categories'][-1]['based_seconds'])

                user['categories'][-1]['seconds'] = old_time + new_time

                date_now = str(datetime.now()).split()[0]
                start = str(data.get('last_start')).split()[-1]
                end = str(data.get('end_time')).split()[-1].split('.')[0]
                seconds = get_the_time_in_seconds(data.get('last_time'))
                user['categories'][-1]['operations'].append({'date': date_now,
                                                             'start': start,
                                                             'end': end,
                                                             'seconds': seconds})

            update_user_data(user_id, user)

        await call.message.answer('✅ Категория добавлена', reply_markup=main_keyboard)

        await state.reset_state(with_data=True)

    elif call.data == 'no':
        async with state.proxy() as data:
            data['suspect_category'] = {}

        await call.message.answer('❌ Произведена отмена', reply_markup=main_keyboard)
        await state.reset_state(with_data=True)


def register_confirm_data(dp: Dispatcher):
    """Регистрация обработчика подтверждения данных"""
    dp.register_callback_query_handler(confirm_data, text=['yes', 'no'], state=[States.confirm_data])


def register_all_categories_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков категорий"""
    register_my_categories_button(dp)
    register_add_new_category(dp)
    register_save_name_new_category(dp)
    register_save_minutes_new_category(dp)
    register_confirm_data(dp)
