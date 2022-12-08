from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import stop_timer_button, generate_category_keyboard, yes_no_keyboard
from tgbot.keyboards.reply import main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date, \
    get_all_dates_operations
from tgbot.misc.work_with_text import get_the_time_in_seconds


async def start_button(message: Message, state: FSMContext):
    """Обработка кнопки СТАРТ"""
    await message.answer('Время пошло!', reply_markup=stop_timer_button)

    start_time = message.date

    user_id = message.from_user.id
    fill_all_categories_past_date(user_id)

    async with state.proxy() as data:
        data['last_start'] = start_time


def register_start_button(dp: Dispatcher):
    dp.register_message_handler(start_button, Text('▶ Старт'), state=[None, States.my_categories, States.category_menu])


async def stop_button(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки СТОП"""
    await call.answer(cache_time=60)

    async with state.proxy() as data:

        if data.get('end_time') is None:
            now = datetime.now()
            send_time = True
        else:
            now = data.get('end_time')
            send_time = False

        all_time = str(now - data['last_start']).split('.')[0]
        data['last_time'] = all_time
        data['end_time'] = now
        data['day_index'] = datetime.weekday(call.message.date)

        data['call_time'] = call
        data['state_time'] = state

    user_id = call.from_user.id
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    if send_time:
        await call.message.answer(f'⏱ Прошло {all_time}')

    if categories:
        await call.message.answer(text=f'К какой категории добавить это время?',
                                  reply_markup=generate_category_keyboard(categories, no_add_button=True))

    else:
        await call.message.answer(text='У вас пока нет ни одной категории.\n\n'
                                       'Чтобы создать новую категорию воспользуйтесь кнопкой ниже.',
                                  reply_markup=generate_category_keyboard(no_add_button=True))

    await States.add_time_to_category.set()


def register_stop_button(dp: Dispatcher):
    dp.register_callback_query_handler(stop_button, text='stop',
                                       state=[None, States.my_categories, States.category_menu])


async def no_add_button(call: CallbackQuery, state: FSMContext):
    # if await state.get_state() in (States.add_new_category_name.state, States.add_new_category_based_seconds.state):
    #
    #     async with state.proxy() as data:
    #         time = data['last_time']
    #
    #     await call.message.answer(f'Время {time} не было добавлено!', reply_markup=main_keyboard)
    #     await state.reset_state(with_data=True)
    #     await call.message.delete()
    #     return

    await call.message.delete()
    await call.message.answer('Вы уверенны, что не хотите добавлять время к категории?',
                              reply_markup=yes_no_keyboard)


def register_no_add_button(dp: Dispatcher):
    dp.register_callback_query_handler(no_add_button, state=[States.add_time_to_category,
                                                             States.add_new_category_name,
                                                             States.add_new_category_based_seconds], text='no_add')


async def confirm_no_add(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        time = data['last_time']

    if call.data == 'yes':
        await call.message.answer(f'Время {time} не было добавлено!', reply_markup=main_keyboard)
        await state.reset_state(with_data=True)
        await call.message.delete()

    elif call.data == 'no':
        await call.answer('Продолжите добавление времени', cache_time=1)
        await stop_button(call, state)
        await call.message.delete()


def register_register_no_add_button(dp: Dispatcher):
    dp.register_callback_query_handler(confirm_no_add,
                                       state=[States.add_time_to_category,
                                              States.add_new_category_name,
                                              States.add_new_category_based_seconds],
                                       text=['yes', 'no'])


async def add_time_to_category(call: CallbackQuery, state: FSMContext):
    callback_data = call.data
    async with state.proxy() as data:

        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)

        time = data['last_time']

        for category in user['categories']:
            if callback_data in category.values():
                category_name = category['name']
                time_in_seconds = get_the_time_in_seconds(data['last_time'])
                category['seconds'] += time_in_seconds

                day_index = data['day_index']

                days = {0: 'monday',
                        1: 'tuesday',
                        2: 'wednesday',
                        3: 'thursday',
                        4: 'friday',
                        5: 'saturday',
                        6: 'sunday'}

                category[days[day_index]] += time_in_seconds

                date_now = str(datetime.now()).split()[0]
                start = str(data.get('last_start'))
                end = str(data.get('end_time'))
                seconds = get_the_time_in_seconds(data.get('last_time'))

                category['operations'].append({'date': date_now,
                                               'start': start,
                                               'end': end,
                                               'seconds': seconds})

        update_user_data(user_id, user)

    await state.reset_state(with_data=True)
    await call.answer(cache_time=30)

    await call.message.answer(f'✅ Время {time} успешно добавлено в категорию {category_name}',
                              reply_markup=main_keyboard)
    await call.message.delete()


def register_add_time_to_category(dp: Dispatcher):
    dp.register_callback_query_handler(add_time_to_category, Text(startswith='category_'),
                                       state=[States.add_time_to_category, States.add_new_category_name,
                                              States.add_new_category_based_seconds])


def register_all_timer(dp):
    register_start_button(dp)
    register_stop_button(dp)
    register_no_add_button(dp)
    register_register_no_add_button(dp)
    register_add_time_to_category(dp)
