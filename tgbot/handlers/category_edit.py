from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.inline import category_menu_keyboard, yes_no_keyboard, delete_operation_inline_keyboard
from tgbot.keyboards.reply import cancel_button, main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, update_user_data, fill_all_categories_past_date, \
    possible_add_time, get_operation_by_serial_number_from_the_end, \
    get_all_not_none_category_operations, delete_operation_from_db
from tgbot.misc.work_with_text import get_category_info_message, get_time_in_str_text, is_valid_time, \
    get_the_time_in_seconds, get_text_category_operations


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
    await call.message.answer(text=text, reply_markup=category_menu_keyboard)

    await States.category_menu.set()


def register_category_inline_button(dp: Dispatcher):
    """Регистрация обработчика нажатия на Inline-кнопку категории"""
    dp.register_callback_query_handler(category_inline_button, state=[None, States.my_categories])


async def see_category_operations(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку 'Посмотреть сессии'"""
    await call.answer(cache_time=10)
    user_id = call.from_user.id
    category_name = call.message.text.split('\n\n')[0]

    operations = get_all_not_none_category_operations(user_id, category_name)
    text = get_text_category_operations(operations)

    if len(operations) == 0:
        await call.message.answer('У вас пока нет ни одной операции в данной категории')
        return

    async with state.proxy() as data:
        data['category_name'] = category_name
        data['last_operations'] = operations

    await call.message.answer(text, reply_markup=delete_operation_inline_keyboard)


def register_see_category_operations(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопку 'Посмотреть сессии'"""
    dp.register_callback_query_handler(see_category_operations, state=[States.category_menu],
                                       text='category_operations')


async def press_button_delete_operation(call: CallbackQuery):
    """Обработка нажатия на кнопку 'Удалить операцию'"""
    await call.answer(cache_time=10)
    await call.message.answer('Для удаления операции введите её порядковый номер', reply_markup=cancel_button)
    await States.delete_operation_state.set()


def register_delete_operation_press_button(dp: Dispatcher):
    """Регистрация обработчика нажатия на кнопку 'Удалить операцию'"""
    dp.register_callback_query_handler(press_button_delete_operation, text='delete_operation',
                                       state=[None, States.category_menu])


async def receiving_serial_number_operation_to_delete(message: Message, state: FSMContext):
    """Обработка получения серийного номера операции"""
    user_id = message.from_user.id
    serial_number = message.text

    async with state.proxy() as data:
        last_operations = data['last_operations']

    if not serial_number.isdigit() or int(serial_number) < 1 or int(serial_number) > len(last_operations):
        await message.answer(f'⚠ Данные введены некорректно!\n\n'
                             f'Неверно указан порядковый номер операции.'
                             f'Вам необходимо передать число от 1 до {len(last_operations)} включительно.\n'
                             f'Вы можете узнать порядковый номер операции из сообщения выше.\n\n'
                             f'Пожалуйста, повторите ввод', reply_markup=cancel_button)
        return

    async with state.proxy() as data:
        category_name = data.get('category_name')

    operation_data = get_operation_by_serial_number_from_the_end(user_id, category_name, serial_number)
    operation = get_text_category_operations([operation_data], serial_number).strip()
    async with state.proxy() as data:
        data['operation'] = operation_data

    await message.answer(f'Вы уверены, что хотите удалить операцию\n\n'
                         f'{operation}\n\n'
                         f'Отменить удаление будет невозможно', reply_markup=yes_no_keyboard)

    await States.confirm_delete_operation_state.set()


def register_receiving_serial_number_operation_to_delete(dp: Dispatcher):
    """Регистрация обработчика получения серийного номера операции"""
    dp.register_message_handler(receiving_serial_number_operation_to_delete, state=States.delete_operation_state)


async def confirm_delete_operation(call: CallbackQuery, state: FSMContext):
    """Обработка подтверждения удаления операции"""
    answer = call.data
    user_id = call.from_user.id

    if answer == 'no':
        await call.message.answer('Удаление операции отменено', reply_markup=main_keyboard)

    elif answer == 'yes':

        async with state.proxy() as data:
            category_name = data['category_name']
            operation = data['operation']

        delete_operation_from_db(user_id, category_name, operation)
        await call.message.answer('Сессия была удалена', reply_markup=main_keyboard)

    await call.message.delete()
    await state.reset_state()


def register_confirm_delete_operation(dp: Dispatcher):
    """Регистрация обработчика подтверждения удаления операции"""
    dp.register_callback_query_handler(confirm_delete_operation, state=States.confirm_delete_operation_state)


async def edit_category(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопки редактирования категории и добавления времени"""
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

    elif call.data == 'change_title':
        await call.message.answer(f'Введите новое название для категории {category_title}',
                                  reply_markup=cancel_button)
        await States.wait_new_title.set()

    elif call.data == 'delete_category':
        await call.message.answer(f'Вы уверены, что хотите удалить категорию {category_title}?',
                                  reply_markup=yes_no_keyboard)
        await States.confirm_delete_category.set()


def register_edit_category(dp: Dispatcher):
    """Обработка нажатия на кнопки редактирования категории и добавления времени"""
    dp.register_callback_query_handler(edit_category, state=[None, States.category_menu])


async def receiving_time_to_adding_time(message: Message, state: FSMContext):
    """Обработка получения времени для добавления"""
    str_time = message.text

    if is_valid_time(str_time, for_edit_time=True) is not True:
        await message.answer(text=is_valid_time(str_time, for_edit_time=True), reply_markup=cancel_button)
        return

    user_id = message.from_user.id

    async with state.proxy() as data:
        category_title = data['changing_category']

    time_in_seconds = get_the_time_in_seconds(str_time)

    check_possible_add_time = possible_add_time(user_id, time_in_seconds, category_title)
    is_possible_add_time = check_possible_add_time.get('is_possible_add_time')
    seconds_today = check_possible_add_time.get('seconds_today')

    if not is_possible_add_time:
        await message.answer('⚠ Данные введены некорректно!\n\n'
                             f'Вы не можете добавить такое количество времени, '
                             f'поскольку иначе получится, что за эти сутки вы '
                             f'уделили этой категории более 24 часов\n\n'
                             f'Потрачено времени сегодня: {get_time_in_str_text(seconds_today)}\n'
                             f'Ещё можно добавить сегодня: {get_time_in_str_text(86_400 - seconds_today)}',
                             reply_markup=cancel_button)
        return

    await States.confirm_add_time.set()

    async with state.proxy() as data:
        data['time_in_seconds'] = time_in_seconds

    await message.answer(f'Вы хотите добавить {get_time_in_str_text(time_in_seconds)}?',
                         reply_markup=yes_no_keyboard)


def register_receiving_time_to_adding_time(dp: Dispatcher):
    """Регистрация обработчика получения времени для добавления"""
    dp.register_message_handler(receiving_time_to_adding_time, state=[States.wait_add_time])


async def confirm_adding_time(call: CallbackQuery, state: FSMContext):
    """Обработка подтверждения добавления времени"""
    if call.data == 'no':

        async with state.proxy() as data:
            time_in_seconds = data.get('time_in_seconds')

        await call.message.delete()
        await call.message.answer(f'Вы отменили добавление {get_time_in_str_text(time_in_seconds)}! '
                                  f'Введите новое число или нажмите отмену.', reply_markup=cancel_button)

        await States.wait_add_time.set()

    elif call.data == 'yes':

        async with state.proxy() as data:
            category_title = data.get('changing_category')
            time_in_seconds = data.get('time_in_seconds')

        user_id = call.from_user.id
        user = get_user_from_json_db(user_id)

        for category in user['categories']:
            if category['name'] == category_title:

                date_now = str(datetime.now()).split()[0]
                time_start = str(datetime.now()).split()[-1].split('.')[0]

                empty_day = {'date': date_now,
                             'start': None,
                             'end': None,
                             'seconds': None}

                if empty_day in category['operations']:
                    category['operations'].remove(empty_day)

                category['seconds'] += time_in_seconds

                category['operations'].append({'date': date_now,
                                               'start': time_start,
                                               'end': None,
                                               'seconds': time_in_seconds})

                break

        update_user_data(user_id, user)

        await call.message.delete()
        await call.message.answer(f'✅ Время добавлено!', reply_markup=main_keyboard)
        await state.reset_state(with_data=True)


def register_confirm_adding_time(dp: Dispatcher):
    """Регистрация обработчика подтверждения добавления времени"""
    dp.register_callback_query_handler(confirm_adding_time, state=[States.confirm_add_time])


async def ask_category_title(message: Message, state: FSMContext):
    """Обработка получения нового названия для категории"""
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
    """Регистрация обработчика получения нового названия для категории"""
    dp.register_message_handler(ask_category_title, state=[States.wait_new_title])


async def confirm_new_category_title(call: CallbackQuery, state: FSMContext):
    """Обработка подтверждения нового названия для категории"""
    await call.answer(cache_time=10)

    if call.data == 'no':
        await call.message.delete()
        await call.message.answer('Введите другое название или воспользуйтесь отменой', reply_markup=cancel_button)
        await States.wait_new_title.set()

    elif call.data == 'yes':

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
    """Регистрация обработчика подтверждения нового названия для категории"""
    dp.register_callback_query_handler(confirm_new_category_title, state=States.confirm_new_title)


async def confirm_delete_category(call: CallbackQuery, state: FSMContext):
    """Обработка подтверждения удаления категории"""
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
    """Регистрация обработчика подтверждения удаления категории"""
    dp.register_callback_query_handler(confirm_delete_category, state=States.confirm_delete_category)


def register_all_category_edit(dp):
    """Регистрация всех обработчиков связанных с редактированием категории"""
    register_category_inline_button(dp)
    register_see_category_operations(dp)
    register_delete_operation_press_button(dp)
    register_receiving_serial_number_operation_to_delete(dp)
    register_confirm_delete_operation(dp)
    register_edit_category(dp)
    register_receiving_time_to_adding_time(dp)
    register_confirm_adding_time(dp)
    register_ask_category_title(dp)
    register_confirm_new_category_title(dp)
    register_confirm_delete_category(dp)
