# Обработчики простых команд
import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from tgbot.keyboards.reply import main_keyboard
from tgbot.misc.states import States


async def start_command(message: Message):
    """Обработка команды /start"""
    await message.answer('👋')

    await message.answer('Добро пожаловать в бота, который поможет '
                         'вам вести статистику вашего потраченного времени!\n\n'
                         'Чтобы лучше понять, что делает этот бот, воспользуйтесь командой <b><i>/help</i></b>.',
                         reply_markup=main_keyboard)


async def help_command(message: Message):
    """Обработка команды /help"""
    await message.answer('Когда-нибудь я напишу здесь сообщение, которое будет помогать пользователям')


async def my_data_command(message: Message, state: FSMContext):
    """Вывод всех сохранных данных из стейта"""
    async with state.proxy() as data:
        await message.answer(str(dict(data)))
        x = '"'
        print(str(dict(data)).replace("'", x).replace('None', 'null'))


def register_all_simple_commands(dp: Dispatcher):
    """Регистрация всех простых команд"""
    dp.register_message_handler(start_command, Command('start'), state=[None, States.my_categories])
    dp.register_message_handler(help_command, Command('help'), state=[None, States.my_categories])
    dp.register_message_handler(my_data_command, Command('my_data'), state=[None, States.my_categories])
