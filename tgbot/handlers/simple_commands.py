# Обработчики простых команд
import datetime
import json

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from tgbot.keyboards.reply import main_keyboard
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, fill_all_categories_past_date


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

    fill_all_categories_past_date(user_id)


async def help_command(message: Message):
    """Обработка команды /help"""
    await message.answer('Когда-нибудь я напишу здесь сообщение, которое будет помогать пользователям')


async def my_data_command(message: Message):
    """Вывод всех сохранных данных из стейта"""
    user_id = message.from_user.id
    user_info = str(get_user_from_json_db(user_id))
    await message.answer(f"""<code>{user_info.replace("'", '"')}</code>""")


def register_all_simple_commands(dp: Dispatcher):
    """Регистрация всех простых команд"""
    dp.register_message_handler(start_command, Command('start'), state=[None, States.my_categories])
    dp.register_message_handler(help_command, Command('help'), state=[None, States.my_categories])
    dp.register_message_handler(my_data_command, Command('my_data'), state=[None, States.my_categories])
