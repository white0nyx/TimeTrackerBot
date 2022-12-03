import asyncio
import json
import logging
import os.path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import BotCommand

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.cancel import register_cancel_button
from tgbot.handlers.categories import register_all_categories_handlers
from tgbot.handlers.simple_commands import register_all_simple_commands
from tgbot.handlers.statistic import register_all_statistic
from tgbot.handlers.timer import register_all_timer

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    pass


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_all_simple_commands(dp)
    register_cancel_button(dp)
    register_all_timer(dp)
    register_all_categories_handlers(dp)
    register_all_statistic(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    if not os.path.exists('data/users.json'):
        with open('data/users.json', 'w', encoding='utf-8') as db:
            json.dump({}, db, indent=4, ensure_ascii=False)

    await dp.bot.set_my_commands([BotCommand('start', 'Запустить бота'),
                                  BotCommand('help', 'Помощь'),
                                  BotCommand('my_data', 'Получить данные')])
    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
