# Обработчики простых команд
import datetime
import json

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

    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    with open('data/users.json', 'r+', encoding='utf-8') as db:
        users = json.load(db)

        if str(user_id) not in users.keys():
            users[user_id] = {'user_data': {'id': user_id, 'username': username, 'full_name': full_name},
                              'categories': []}

        db.seek(0)
        json.dump(users, db, indent=4, ensure_ascii=False)


async def help_command(message: Message):
    """Обработка команды /help"""
    await message.answer('Когда-нибудь я напишу здесь сообщение, которое будет помогать пользователям')


async def my_data_command(message: Message, state: FSMContext):
    """Вывод всех сохранных данных из стейта"""
    async with state.proxy() as data:
        await message.answer(str(dict(data)).replace("'", '"').replace('None', 'null'))


def register_all_simple_commands(dp: Dispatcher):
    """Регистрация всех простых команд"""
    dp.register_message_handler(start_command, Command('start'), state=[None, States.my_categories])
    dp.register_message_handler(help_command, Command('help'), state=[None, States.my_categories])
    dp.register_message_handler(my_data_command, Command('my_data'), state=[None, States.my_categories])
