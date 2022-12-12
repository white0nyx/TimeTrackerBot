from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.keyboards.inline import generate_category_keyboard
from tgbot.keyboards.reply import main_keyboard
from tgbot.misc.work_with_json import get_user_from_json_db


async def press_cancel_button(message: Message, state: FSMContext):
    """Обработка нажатия на кнопку отмены"""

    async with state.proxy() as data:
        if data.get('last_time') is not None:

            user_id = message.from_user.id
            user = get_user_from_json_db(user_id)
            categories = user.get('categories')

            time = data.get('last_time')
            await message.answer(text=f'⚠ Вы отменили создание новой категории.\n\n',
                                 reply_markup=generate_category_keyboard(categories, no_add_button=True))

            await message.answer(text=f'Выберите, в какую категорию добавить {time}', reply_markup=ReplyKeyboardRemove())
            return

    await state.reset_state(with_data=True)
    await message.answer('Вы вернулись в главное меню', reply_markup=main_keyboard)


def register_cancel_button(dp: Dispatcher):
    """Регистрация обработчика кнопки отмена"""
    dp.register_message_handler(press_cancel_button, Text('↩ Отмена'), state='*')
