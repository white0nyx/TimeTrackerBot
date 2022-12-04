from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.inline import category_buttons, yes_no_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_date import get_day_of_week
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date
from tgbot.misc.work_with_text import get_category_info_message, get_word_end_vp, get_word_end_rp


async def category_inline_button(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на Inline-кнопку категории в состоянии my_categories"""
    callback_data = call.data
    await call.answer(cache_time=5)

    user_id = call.from_user.id
    user = get_user_from_json_db(user_id)

    categories = user.get('categories')
    fill_all_categories_past_date(user_id)

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


async def confirm_changing_time(message: Message, state: FSMContext):
    time_in_minutes = int(message.text)
    if await state.get_state() == States.wait_add_minutes.state:
        action = 'добавить'
        await States.confirm_add_minutes.set()

    else:
        action = 'вычесть'
        await States.confirm_sub_minutes.set()

    async with state.proxy() as data:
        data['time_in_minutes'] = time_in_minutes

    minutes = get_word_end_vp(time_in_minutes)

    await message.answer(f'Вы хотите {action} {time_in_minutes} {minutes}?', reply_markup=yes_no_keyboard)


def register_confirm_changing_time(dp: Dispatcher):
    dp.register_message_handler(confirm_changing_time, state=[States.wait_add_minutes, States.wait_sub_minutes])


async def change_time(call: CallbackQuery, state: FSMContext):
    if call.data == 'no':

        if await state.get_state() == States.confirm_add_minutes.state:
            action = 'добавление'
            state_again = States.wait_add_minutes

        else:
            action = 'вычитание'
            state_again = States.wait_sub_minutes

        async with state.proxy() as data:
            time_in_minutes = data.get('time_in_minutes')
            minutes_text = get_word_end_rp(time_in_minutes)
        await call.message.delete()
        await call.message.answer(f'Вы отменили {action} {time_in_minutes} {minutes_text}! '
                                  f'Введите новое число или нажмите отмену.')
        await state_again.set()

    else:

        action = 'добавлено' if await state.get_state() == States.confirm_add_minutes.state else 'вычтено'

        async with state.proxy() as data:
            category_title = data.get('changing_category')
            time_in_minutes = data.get('time_in_minutes')

        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)

        for category in user['categories']:
            if category['name'] == category_title:
                today = get_day_of_week(call)

                if await state.get_state() == States.confirm_add_minutes.state:
                    category['seconds'] += time_in_minutes * 60
                    category[today] += time_in_minutes * 60

                    date_now = str(datetime.now()).split()[0]
                    category['operations'][date_now] += time_in_minutes * 60

                else:
                    category['seconds'] -= time_in_minutes * 60
                    category[today] -= time_in_minutes * 60

                    date_now = str(datetime.now()).split()[0]
                    category['operations'][date_now] += time_in_minutes * 60

                break

        update_user_data(user_id, user)

        await call.message.delete()
        await call.message.answer(f'Время {action}!')
        await state.reset_state(with_data=True)


def register_change_time(dp: Dispatcher):
    dp.register_callback_query_handler(change_time, state=[States.confirm_add_minutes, States.confirm_sub_minutes])


async def ask_category_title(message: Message, state: FSMContext):
    new_title = message.text

    async with state.proxy() as data:
        data['new_category_title'] = new_title

    await message.answer(f'Вы уверены, что хотите изменить название категории на "{new_title}"?',
                         reply_markup=yes_no_keyboard)

    await States.confirm_new_title.set()


def register_ask_category_title(dp: Dispatcher):
    dp.register_message_handler(ask_category_title, state=[States.wait_new_title])


async def confirm_new_category_title(call: CallbackQuery, state: FSMContext):

    await call.answer(cache_time=10)

    if call.data == 'no':
        await call.message.delete()
        await call.message.answer('Введите другое название или воспользуйтесь отменой')
        await States.wait_new_title.set()

    else:

        async with state.proxy() as data:
            new_category_title = data['new_category_title']
            old_category_title = data['changing_category']

        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)
        categories = user['categories']

        for category in categories:
            if category['name'] == old_category_title:
                category['name'] = new_category_title
                break

        update_user_data(user_id, user)

        await call.message.answer('Название категории успешно изменено!')
        await state.reset_state(with_data=True)


def register_confirm_new_category_title(dp: Dispatcher):
    dp.register_callback_query_handler(confirm_new_category_title, state=States.confirm_new_title)


def register_all_category_edit(dp):
    register_category_inline_button(dp)
    register_edit_category(dp)
    register_confirm_changing_time(dp)
    register_change_time(dp)
    register_ask_category_title(dp)
    register_confirm_new_category_title(dp)
