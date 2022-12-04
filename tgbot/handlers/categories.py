from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import yes_no_keyboard, generate_category_keyboard
from tgbot.keyboards.reply import cancel_button, main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data
from tgbot.misc.work_with_text import get_the_time_in_seconds


async def my_categories_button(message: Message, state: FSMContext):
    """Обработка нажатия на кнопку КАТЕГОРИИ"""

    user_id = str(message.from_user.id)

    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    if not categories:
        await message.answer('У вас пока нет ни одной добавленной категории.\n\n'
                             'Чтобы добавить категорию воспользуйтесь кнопкой ниже.',
                             reply_markup=generate_category_keyboard())

    else:
        await message.answer('📓 Ваши категории', reply_markup=generate_category_keyboard(categories))

    await States.my_categories.set()


def register_my_categories_button(dp: Dispatcher):
    """Регистрация обработчика кнопки КАТЕГОРИИ"""
    dp.register_message_handler(my_categories_button, Text('📓 Мои категории'), state=[None, States.my_categories])


async def add_new_category(call: CallbackQuery):
    """Обработка кнопки НОВАЯ КАТЕГОРИЯ"""
    await call.answer(cache_time=60)
    await States.add_new_category_name.set()
    await call.message.answer('Введите название категории:', reply_markup=cancel_button)


def register_add_new_category(dp: Dispatcher):
    """Регистрация обработки кнопки НОВАЯ КАТЕГОРИЯ"""
    dp.register_callback_query_handler(add_new_category, text='new_category', state=[None,
                                                                                     States.add_time_to_category,
                                                                                     States.my_categories])


async def save_name_new_category(message: Message, state: FSMContext):
    """Сохранение названия категории и запрос потраченного времени"""
    category_name = message.text

    async with state.proxy() as data:
        data['suspect_category'] = {}
        data['suspect_category']['name'] = category_name

    await message.answer(f'Укажите количество потраченных минут на неё', reply_markup=cancel_button)
    await States.add_new_category_based_minutes.set()


def register_save_name_new_category(dp: Dispatcher):
    """Регистрация обработчика сохранения названия категории"""
    dp.register_message_handler(save_name_new_category, state=[States.add_new_category_name])


async def save_based_minutes_new_category(message: Message, state: FSMContext):
    """Сохранение количества потраченных минут и запрос подтверждения данных"""
    minutes = message.text

    async with state.proxy() as data:
        data['suspect_category']['based_minutes'] = int(minutes)
        data['suspect_category']['seconds'] = int(minutes) * 60
        data['suspect_category']['monday'] = 0
        data['suspect_category']['tuesday'] = 0
        data['suspect_category']['wednesday'] = 0
        data['suspect_category']['thursday'] = 0
        data['suspect_category']['friday'] = 0
        data['suspect_category']['saturday'] = 0
        data['suspect_category']['sunday'] = 0
        data['suspect_category']['operations'] = {}

    async with state.proxy() as data:
        category_name = data['suspect_category']['name']
        category_minutes = data['suspect_category']['based_minutes']

    await message.answer(f'Подтвердите введённые данные: \n\n'
                         f'Категория: {category_name}\n'
                         f'Потрачено минут: {category_minutes}', reply_markup=yes_no_keyboard)

    await States.confirm_data.set()


def register_save_minutes_new_category(dp: Dispatcher):
    """Регистрация обработчика сохранения потраченных минут"""
    dp.register_message_handler(save_based_minutes_new_category, state=[States.add_new_category_based_minutes])


async def confirm_data(call: CallbackQuery, state: FSMContext):
    """Подтверждение пользователем данных и их сохранение"""
    await call.answer(cache_time=60)
    await call.message.delete()
    user_id = call.from_user.id
    if call.data == 'yes':

        user = get_user_from_json_db(user_id)
        async with state.proxy() as data:

            suspect_category = data['suspect_category']

            suspect_category['callback_data'] = 'category_' + str(len(user['categories']) + 1)
            user['categories'].append(suspect_category)

            if data.get('last_time') is not None:
                new_time = get_the_time_in_seconds(data.get('last_time'))

                old_time = int(user['categories'][-1]['based_minutes']) * 60

                user['categories'][-1]['seconds'] = old_time + new_time

                day_index = data['day_index']
                days = {0: 'monday',
                        1: 'tuesday',
                        2: 'wednesday',
                        3: 'thursday',
                        4: 'friday',
                        5: 'saturday',
                        6: 'sunday'}

                user['categories'][-1][days[day_index]] = new_time

                date_now = str(datetime.now()).split()[0]
                if user['categories'][-1]['operations'].get(date_now) is None:
                    user['categories'][-1]['operations'][date_now] = new_time
                else:
                    user['categories'][-1]['operations'][date_now] += new_time

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
    dp.register_callback_query_handler(confirm_data, text=['yes', 'no'], state=States.confirm_data)


def register_all_categories_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков категорий"""
    register_my_categories_button(dp)
    register_add_new_category(dp)
    register_save_name_new_category(dp)
    register_save_minutes_new_category(dp)
    register_confirm_data(dp)
