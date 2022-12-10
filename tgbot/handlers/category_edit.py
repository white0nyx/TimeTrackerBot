from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.cancel import cancel_button
from tgbot.keyboards.inline import category_buttons, yes_no_keyboard
from tgbot.keyboards.reply import cancel_button, main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_date import get_day_of_week
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date, \
    possible_add_time, possible_sub_time
from tgbot.misc.work_with_text import get_category_info_message, convert_to_preferred_format, is_valid_time, \
    get_the_time_in_seconds


async def category_inline_button(call: CallbackQuery):
    """Обработка нажатия на Inline-кнопку категории в состоянии my_categories"""
    callback_data = call.data
    await call.answer(cache_time=10)

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
    await call.answer(cache_time=10)
    category_title = call.message.text.split('\n')[0]

    async with state.proxy() as data:
        data['changing_category'] = category_title

    if call.data == 'add_time':
        await call.message.answer(
            f'Введите время в формате чч:мм:сс, которое вы хотите добавить к категории {category_title}\n\n'
            f'Например: 01:20:03 или 1:20:3',
            reply_markup=cancel_button)
        await States.wait_add_time.set()

    elif call.data == 'subtract_time':
        await call.message.answer(
            f'Введите время в формате чч:мм:сс, которое вы хотите вычесть из категории {category_title}\n\n'
            f'Например: 01:20:03 или 1:20:3',
            reply_markup=cancel_button)
        await States.wait_sub_time.set()

    elif call.data == 'change_title':
        await call.message.answer(f'Введите новое название для категории {category_title}',
                                  reply_markup=cancel_button)
        await States.wait_new_title.set()

    elif call.data == 'delete_category':
        await call.message.answer(f'Вы уверены, что хотите удалить категорию {category_title}?',
                                  reply_markup=yes_no_keyboard)
        await States.confirm_delete_category.set()


def register_edit_category(dp: Dispatcher):
    dp.register_callback_query_handler(edit_category, state=[None, States.category_menu])


async def confirm_changing_time(message: Message, state: FSMContext):
    str_time = message.text

    if is_valid_time(str_time, for_edit_time=True) is not True:
        await message.answer(text=is_valid_time(str_time, for_edit_time=True), reply_markup=cancel_button)
        return

    user_id = message.from_user.id

    async with state.proxy() as data:
        category_title = data['changing_category']

    time_in_seconds = get_the_time_in_seconds(str_time)

    if await state.get_state() == States.wait_add_time.state:
        action = 'добавить'

        check_possible_add_time = possible_add_time(user_id, time_in_seconds, category_title)
        is_possible_add_time = check_possible_add_time.get('is_possible_add_time')
        seconds_today = check_possible_add_time.get('seconds_today')

        if not is_possible_add_time:
            await message.answer('⚠ Данные введены некорректно!\n\n'
                                 f'Вы не можете добавить такое количество времени, '
                                 f'поскольку иначе получится, что за эти сутки вы '
                                 f'уделили этой категории более 24 часов\n\n'
                                 f'Потрачено времени сегодня: {convert_to_preferred_format(seconds_today)}\n'
                                 f'Ещё можно добавить сегодня: {convert_to_preferred_format(86_400 - seconds_today)}',
                                 reply_markup=cancel_button)
            return

        await States.confirm_add_time.set()

    else:
        action = 'вычесть'

        check_possible_sub_time = possible_sub_time(user_id, time_in_seconds, category_title)
        is_possible_sub_time = check_possible_sub_time.get('is_possible_sub_time')
        seconds_today = check_possible_sub_time.get('seconds_today')

        if not is_possible_sub_time:
            await message.answer(f'⚠ Данные введены некорректно!\n\n'
                                 f'Вы не можете вычесть такое количество времени из этой категории, '
                                 f'поскольку сегодня ещё не потратили столько времени на неё\n\n'
                                 f'Потрачено времени сегодня: {convert_to_preferred_format(seconds_today)}',
                                 reply_markup=cancel_button)
            return

        await States.confirm_sub_time.set()

    async with state.proxy() as data:
        data['time_in_seconds'] = time_in_seconds

    await message.answer(f'Вы хотите {action} {convert_to_preferred_format(time_in_seconds)}?',
                         reply_markup=yes_no_keyboard)


def register_confirm_changing_time(dp: Dispatcher):
    dp.register_message_handler(confirm_changing_time, state=[States.wait_add_time, States.wait_sub_time])


async def change_time(call: CallbackQuery, state: FSMContext):
    if call.data == 'no':

        if await state.get_state() == States.confirm_add_time.state:
            action = 'добавление'
            state_again = States.wait_add_time

        else:
            action = 'вычитание'
            state_again = States.wait_sub_time

        async with state.proxy() as data:
            time_in_seconds = data.get('time_in_seconds')
        await call.message.delete()
        await call.message.answer(f'Вы отменили {action} {convert_to_preferred_format(time_in_seconds)}! '
                                  f'Введите новое число или нажмите отмену.', reply_markup=cancel_button)
        await state_again.set()

    else:

        action = 'добавлено' if await state.get_state() == States.confirm_add_time.state else 'вычтено'

        async with state.proxy() as data:
            category_title = data.get('changing_category')
            time_in_seconds = data.get('time_in_seconds')

        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)

        for category in user['categories']:
            if category['name'] == category_title:
                today = get_day_of_week(call)

                date_now = str(datetime.now()).split()[0]

                empty_day = {'date': date_now,
                             'start': None,
                             'end': None,
                             'seconds': None}

                if empty_day in category['operations']:
                    category['operations'].remove(empty_day)

                if await state.get_state() == States.confirm_add_time.state:
                    category['seconds'] += time_in_seconds
                    category[today] += time_in_seconds

                    category['operations'].append({'date': date_now,
                                                   'start': None,
                                                   'end': None,
                                                   'seconds': time_in_seconds})

                else:
                    category['seconds'] -= time_in_seconds
                    category[today] -= time_in_seconds

                    category['operations'].append({'date': date_now,
                                                   'start': None,
                                                   'end': None,
                                                   'seconds': 0 - time_in_seconds})

                break

        update_user_data(user_id, user)

        await call.message.delete()
        await call.message.answer(f'✅ Время {action}!', reply_markup=main_keyboard)
        await state.reset_state(with_data=True)


def register_change_time(dp: Dispatcher):
    dp.register_callback_query_handler(change_time, state=[States.confirm_add_time, States.confirm_sub_time])


async def ask_category_title(message: Message, state: FSMContext):
    new_title = message.text

    if len(new_title) > 32:
        await message.answer('⚠ Слишком длинное название\n\n'
                             'Вы можете указать название длиной до 32 символов\n\n'
                             'Пожалуйста, повторите ввод', reply_markup=cancel_button)
        return

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
        await call.message.answer('Введите другое название или воспользуйтесь отменой', reply_markup=cancel_button)
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

        await call.message.answer('✅ Название категории успешно изменено!', reply_markup=main_keyboard)
        await state.reset_state(with_data=True)


def register_confirm_new_category_title(dp: Dispatcher):
    dp.register_callback_query_handler(confirm_new_category_title, state=States.confirm_new_title)


async def confirm_delete_category(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)

    if call.data == 'no':
        await call.message.answer('Удаление категории отменено', reply_markup=main_keyboard)
        await call.message.delete()
        await state.reset_state(with_data=True)

    else:
        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)
        categories = user['categories']

        async with state.proxy() as data:
            category_name = data['changing_category']

        for index, category in enumerate(categories):
            if category['name'] == category_name:
                del categories[index]
                break

        update_user_data(user_id, user)

        await call.message.answer(f'✅ Категория {category_name} была удалена!', reply_markup=main_keyboard)
        await call.message.delete()
        await state.reset_state(with_data=True)


def register_confirm_delete_category(dp: Dispatcher):
    dp.register_callback_query_handler(confirm_delete_category, state=States.confirm_delete_category)


def register_all_category_edit(dp):
    register_category_inline_button(dp)
    register_edit_category(dp)
    register_confirm_changing_time(dp)
    register_change_time(dp)
    register_ask_category_title(dp)
    register_confirm_new_category_title(dp)
    register_confirm_delete_category(dp)
