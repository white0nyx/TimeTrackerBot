from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from tgbot.misc.work_with_text import get_statistic


async def statistic_button(message: Message, state: FSMContext):

    async with state.proxy() as data:

        if data.get('categories') is None:
            await message.answer('Для получения статистики у вас должна быть установлена хотя бы одна категория')
            return

        categories = data.get('categories')

    text = get_statistic(categories)

    await message.answer(text=text)


def register_statistic_button(dp: Dispatcher):
    dp.register_message_handler(statistic_button, Text('📊 Статистика'))


def register_all_statistic(dp):
    register_statistic_button(dp)