from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import pause_stop_keyboard, generate_category_keyboard, yes_no_keyboard, \
    resume_stop_keyboard
from tgbot.keyboards.reply import main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date
from tgbot.misc.work_with_text import get_the_time_in_seconds, get_time_in_str_text


async def start_button(message: Message, state: FSMContext):
    """Обработка кнопки СТАРТ"""
    await message.answer(f'⏱ Время пошло!\n\n'
                         f'Прошло: 00:00:00', reply_markup=pause_stop_keyboard)

    user_id = message.from_user.id
    fill_all_categories_past_date(user_id)

    async with state.proxy() as data:
        data['last_start'] = message.date
        data['first_start'] = message.date
        data['all_time'] = 0
        data['pause'] = False


def register_start_button(dp: Dispatcher):
    """Регистрация обработчика кнопки СТАРТ"""
    dp.register_message_handler(start_button, Text('▶ Старт'), )


async def update_button(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки ОБНОВИТЬ"""
    await call.message.delete()

    async with state.proxy() as data:
        seconds_now = get_the_time_in_seconds(str(datetime.now() - data['last_start']).split('.')[0])
        time_now_str = get_time_in_str_text(data['all_time'] + seconds_now)

    await call.message.answer(f'⏱ Время пошло\n\n'
                              f'Прошло: {time_now_str}', reply_markup=pause_stop_keyboard)


def register_update_button(dp: Dispatcher):
    """Регистрация обработчика кнопки ОБНОВИТЬ"""
    dp.register_callback_query_handler(update_button,
                                       text='update',
                                       state=[None, States.my_categories, States.category_menu])


async def pause_button(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки ПАУЗА"""
    await call.answer(cache_time=10)
    await call.message.delete()

    async with state.proxy() as data:
        seconds_now = get_the_time_in_seconds(str(datetime.now() - data['last_start']).split('.')[0])
        data['all_time'] += seconds_now
        data['pause'] = True

        time_now_str = get_time_in_str_text(data['all_time'])

    await call.message.answer(f'⏸ Пауза\n\nПрошло: {time_now_str}', reply_markup=resume_stop_keyboard)


def register_pause_button(dp: Dispatcher):
    """Регистрация обработчика кнопки ПАУЗА"""
    dp.register_callback_query_handler(pause_button, text='pause', state=[None,
                                                                          States.my_categories,
                                                                          States.category_menu])


async def resume_button(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки ПРОДОЛЖИТЬ"""
    await call.answer(cache_time=10)
    await call.message.delete()

    async with state.proxy() as data:
        now = datetime.now()
        data['last_start'] = now
        data['pause'] = False

        time_now_str = get_time_in_str_text(data['all_time'])

    await call.message.answer(f'⏱ Время пошло\n'
                              f'Прошло: {time_now_str}', reply_markup=pause_stop_keyboard)


def register_resume_button(dp: Dispatcher):
    """Регистрация обработчика кнопки продолжить"""
    dp.register_callback_query_handler(resume_button, text='resume', state=[None,
                                                                            States.my_categories,
                                                                            States.category_menu])


async def stop_button(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки СТОП"""
    await call.answer(cache_time=60)
    await call.message.delete()

    async with state.proxy() as data:

        if data.get('end_time') is None:
            now = datetime.now()
            send_time = True
        else:
            now = data.get('end_time')
            send_time = False

        if not data['pause']:
            seconds_now = get_the_time_in_seconds(str(now - data['last_start']).split('.')[0])
            data['all_time'] += seconds_now

        all_time = get_time_in_str_text(data['all_time'])
        data['last_time'] = all_time
        data['end_time'] = now

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
    """Регистрация обработчика кнопки СТОП"""
    dp.register_callback_query_handler(stop_button, text='stop',
                                       state=[None, States.my_categories, States.category_menu])


async def no_add_time_button(call: CallbackQuery):
    """Обработка нажатия на кнопку отказа добавлять время (Кнопка НЕТ)"""
    await call.message.delete()
    await call.message.answer('Вы уверенны, что не хотите добавлять время к категории?',
                              reply_markup=yes_no_keyboard)


def register_no_add_time_button(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопку отказа добавлять время"""
    dp.register_callback_query_handler(no_add_time_button, state=[States.add_time_to_category,
                                                                  States.add_new_category_name,
                                                                  States.add_new_category_based_seconds], text='no_add')


async def confirm_no_add(call: CallbackQuery, state: FSMContext):
    """Обработка подтверждения отказа добавлять время"""
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
    """Регистрация обработчика подтверждения отказа добавлять время"""
    dp.register_callback_query_handler(confirm_no_add,
                                       state=[States.add_time_to_category,
                                              States.add_new_category_name,
                                              States.add_new_category_based_seconds],
                                       text=['yes', 'no'])


async def add_time_to_category(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку согласия добавления времени (Кнопка ДА)"""
    callback_data = call.data
    async with state.proxy() as data:
        state_data = data

    user_id = call.from_user.id
    user = get_user_from_json_db(user_id)

    time = state_data['last_time']

    category_name = None
    for category in user['categories']:
        if callback_data in category.values():
            category_name = category['name']
            time_in_seconds = get_the_time_in_seconds(state_data['last_time'])
            category['seconds'] += time_in_seconds

            date_now = str(datetime.now()).split()[0]
            start = str(state_data.get('first_start')).split()[-1].split('.')[0]
            end = str(state_data.get('end_time')).split()[-1].split('.')[0]
            seconds = get_the_time_in_seconds(state_data.get('last_time'))

            empty_day = {'date': date_now,
                         'start': None,
                         'end': None,
                         'seconds': None}

            if empty_day in category['operations']:
                category['operations'].remove(empty_day)

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
    """Регистрация обработчика нажатия на кнопку согласия добавления времени"""
    dp.register_callback_query_handler(add_time_to_category, Text(startswith='category_'),
                                       state=[States.add_time_to_category, States.add_new_category_name,
                                              States.add_new_category_based_seconds])


def register_all_timer(dp):
    """Регистрация всех обработчиков связанных с таймером"""
    register_start_button(dp)
    register_update_button(dp)
    register_pause_button(dp)
    register_resume_button(dp)
    register_stop_button(dp)
    register_no_add_time_button(dp)
    register_register_no_add_button(dp)
    register_add_time_to_category(dp)
