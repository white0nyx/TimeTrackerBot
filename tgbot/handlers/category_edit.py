from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.inline import category_buttons, yes_no_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_date import get_day_of_week
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data
from tgbot.misc.work_with_text import get_category_info_message


async def category_inline_button(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на Inline-кнопку категории в состоянии my_categories"""
    callback_data = call.data
    await call.answer(cache_time=5)

    user_id = call.from_user.id
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    text = get_category_info_message(callback_data, categories)
    await call.message.delete()
    await call.message.answer(text=text, reply_markup=category_buttons)

    await States.category_menu.set()


def register_category_inline_button(dp: Dispatcher):
    dp.register_callback_query_handler(category_inline_button, state=[None, States.my_categories])


async def edit_category(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=3)
    category_title = call.message.text.split('\n')[0]

    async with state.proxy() as data:
        data['changing_category'] = category_title

    if call.data == 'add_time':
        await call.message.answer(
            f'Введите время в минутах, которое вы хотите добавить к категории {category_title}:')
        await States.wait_add_minutes.set()

    elif call.data == 'subtract_time':
        await call.message.answer(
            f'Введите время в минутах, которое вы хотите вычесть из категории {category_title}:')
        await States.wait_sub_minutes.set()

    elif call.data == 'change_title':
        await call.message.answer(f'Введите новое название для категории {category_title}:')
        await States.wait_new_title.set()

    elif call.data == 'delete_category':
        await call.message.answer(f'Вы уверены, что хотите удалить категорию {category_title}?',
                                  reply_markup=yes_no_keyboard)
        await States.delete_category_confirm.set()


def register_edit_category(dp: Dispatcher):
    dp.register_callback_query_handler(edit_category, state=[None, States.category_menu])


async def confirm_adding_time(message: Message, state: FSMContext):
    time_in_minutes = int(message.text)

    async with state.proxy() as data:
        data['time_in_minutes'] = time_in_minutes

    await message.answer(f'Вы хотите добавить {time_in_minutes} минут?', reply_markup=yes_no_keyboard)
    await States.confirm_add_minutes.set()


def register_confirm_adding_time(dp: Dispatcher):
    dp.register_message_handler(confirm_adding_time, state=[States.wait_add_minutes])


async def add_time(call: CallbackQuery, state: FSMContext):
    if call.data == 'no':

        async with state.proxy() as data:
            time_in_minutes = data.get('time_in_minutes')

        await call.message.delete()
        await call.message.answer(f'Вы отменили добавление {time_in_minutes} минут!'
                                  f'Введите новое число или нажмите отмену.')
        await States.wait_add_minutes.set()

    else:

        async with state.proxy() as data:
            category_title = data.get('changing_category')
            time_in_minutes = data.get('time_in_minutes')

        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)

        for category in user['categories']:
            if category['name'] == category_title:
                today = get_day_of_week(call)
                category['seconds'] += time_in_minutes * 60
                category[today] += time_in_minutes * 60

                date_now = str(datetime.now()).split()[0]
                if category['operations'].get(date_now) is None:
                    category['operations'][date_now] = time_in_minutes * 60
                else:
                    category['operations'][date_now] += time_in_minutes * 60

                break

        update_user_data(user_id, user)

        await call.message.delete()
        await call.message.answer('Время добавлено!')
        await state.reset_state(with_data=True)


def register_add_time(dp: Dispatcher):
    dp.register_callback_query_handler(add_time, state=[States.confirm_add_minutes])


def register_all_category_edit(dp):
    register_category_inline_button(dp)
    register_edit_category(dp)
    register_confirm_adding_time(dp)
    register_add_time(dp)
