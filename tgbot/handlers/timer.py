import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import stop_timer_button, generate_category_keyboard, yes_no_keyboard
from tgbot.misc.states import States


async def start_button(message: Message, state: FSMContext):
    """Обработка кнопки СТАРТ"""
    await message.answer('Время пошло!', reply_markup=stop_timer_button)

    start_time = message.date

    async with state.proxy() as data:
        data['last_start'] = start_time


def register_start_button(dp: Dispatcher):
    dp.register_message_handler(start_button, Text('▶ Старт'))


async def stop_button(call: CallbackQuery, state: FSMContext):
    """Обработка кнопки СТОП"""
    await call.answer(cache_time=60)

    async with state.proxy() as data:

        if data.get('end_time') is None:
            now = datetime.datetime.now()
            send_time = True
        else:
            now = data.get('end_time')
            send_time = False

        all_time = str(now - data['last_start']).split('.')[0]
        data['last_time'] = all_time
        data['end_time'] = now

        categories = data.get('categories')

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
    dp.register_callback_query_handler(stop_button, text='stop')


async def no_add_button(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('Вы уверенны, что не хотите добавлять время к категории?',
                              reply_markup=yes_no_keyboard)


def register_no_add_button(dp: Dispatcher):
    dp.register_callback_query_handler(no_add_button, state=States.add_time_to_category, text='no_add')


async def confirm_no_add(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        time = data['last_time']

    if call.data == 'yes':
        await call.answer(f'Время {time} не было добавлено!')
        await state.reset_state(with_data=False)
        await call.message.delete()
        async with state.proxy() as data:
            data['state_time'] = None
            data['end_time'] = None
            data['last_start'] = None
            data['last_time'] = None

    elif call.data == 'no':
        await call.answer('Продолжите добавление времени', cache_time=1)
        await stop_button(call, state)
        await call.message.delete()


def register_register_no_add_button(dp: Dispatcher):
    dp.register_callback_query_handler(confirm_no_add, state=States.add_time_to_category, text=['yes', 'no'])


def register_all_timer(dp):
    register_start_button(dp)
    register_stop_button(dp)
    register_no_add_button(dp)
    register_register_no_add_button(dp)
