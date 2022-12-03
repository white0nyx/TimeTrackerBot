from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db
from tgbot.misc.work_with_text import get_statistic


async def statistic_button(message: Message, state: FSMContext):
    user_id = message.from_user.id

    user = get_user_from_json_db(user_id)

    if not user.get('categories'):
        await message.answer('Для получения статистики у вас должна быть установлена хотя бы одна категория')
        return

    categories = user.get('categories')

    text = get_statistic(categories)

    await message.answer(text=text)


def register_statistic_button(dp: Dispatcher):
    dp.register_message_handler(statistic_button, Text('📊 Статистика'), state=[None, States.my_categories])


def register_all_statistic(dp):
    register_statistic_button(dp)
