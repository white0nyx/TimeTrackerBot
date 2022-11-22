from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from tgbot.keyboards.reply import main_keyboard
from tgbot.misc.states import States


async def cancel_button(message: Message, state: FSMContext):
    """Обработка нажатия на кнопку отмены"""
    await state.reset_state(with_data=False)
    async with state.proxy() as data:
        data['suspect_category'] = {}
    await message.answer('Вы вернулись в главное меню', reply_markup=main_keyboard)


def register_cancel_button(dp: Dispatcher):
    """Регистрация обработчика кнопки отмена"""
    dp.register_message_handler(cancel_button, Text('↩ Отмена'), state=[States.add_new_category_name,
                                                                        States.add_new_category_minutes])
