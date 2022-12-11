import os

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, MediaGroup

from tgbot.misc.analytics import get_plot_total_time, get_diagram_week_statistic
from tgbot.misc.states import States
from tgbot.misc.work_with_json import get_user_from_json_db, fill_all_categories_past_date
from tgbot.misc.work_with_text import get_statistic


async def statistic_button(message: Message):
    user_id = message.from_user.id

    fill_all_categories_past_date(user_id)
    user = get_user_from_json_db(user_id)

    if not user.get('categories'):
        await message.answer('Для получения статистики у вас должна быть установлена хотя бы одна категория')
        return

    categories = user.get('categories')

    text = get_statistic(user_id, categories)

    get_plot_total_time(str(user_id))
    all_time_plot = InputFile(path_or_bytesio=f'data/{user_id}_total_time.png')

    get_diagram_week_statistic(str(user_id))
    diagram_week_statistic = InputFile(path_or_bytesio=f'data/{user_id}_week_statistic.png')

    # await message.bot.send_photo(user_id, all_time_plot, caption=text)

    album = MediaGroup()
    album.attach_photo(all_time_plot, caption=text)
    album.attach_photo(diagram_week_statistic)

    await message.answer_media_group(album)
    os.remove(f'data/{user_id}_total_time.png')
    os.remove(f'data/{user_id}_week_statistic.png')


def register_statistic_button(dp: Dispatcher):
    dp.register_message_handler(statistic_button, Text('📊 Статистика'),
                                state=[None, States.my_categories, States.category_menu])


def register_all_statistic(dp):
    register_statistic_button(dp)
