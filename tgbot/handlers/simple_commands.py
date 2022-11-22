# Обработчики простых команд

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message


async def start_command(message: Message):
    """Обработка команды /start"""
    await message.answer('👋')

    await message.answer('Добро пожаловать в бота, который поможет '
                         'вам вести статистику вашего потраченного времени!\n\n'
                         'Чтобы лучше понять, что делает этот бот, воспользуйтесь командой <b><i>/help</i></b>.')


async def help_command(message: Message):
    """Обработка команды /help"""
    await message.answer('Когда-нибудь я напишу здесь сообщение, которое будет помогать пользователям')


def register_all_simple_commands(dp: Dispatcher):
    """Регистрация всех простых команд"""
    dp.register_message_handler(start_command, Command('start'))
    dp.register_message_handler(help_command, Command('help'))
