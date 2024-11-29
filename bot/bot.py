import asyncio
import logging
import sys
import aiohttp
import betterlogging as bl
import fastapi
import json

from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram import Dispatcher, Bot, types
from pydantic import BaseModel

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.check_sub import CheckSubscription
from tgbot.loader import db, config
from tgbot.services import broadcaster
from datetime import datetime
from fastapi import FastAPI


async def on_startup(bot: Bot, admin_ids: list[int]):
    try:
        await db.create()
    except Exception as e:
        logging.error(e)
        await broadcaster.broadcast(bot, admin_ids, "can't create tables. Program is stopping.....")
        logging.error("can't create tables. Program is stopping.....")
        sys.exit(1)

    await broadcaster.broadcast(bot, admin_ids, "Bot ishga tushdi")


def register_global_middlewares(dp: Dispatcher, cfg: Config):
    middleware_types = [
        # CheckSubscription(config.tg_bot.channels[0]),
        ConfigMiddleware(cfg),
        # DatabaseMiddleware(session_pool),

    ]
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()

# app = FastAPI()
setup_logging()
storage = get_storage(config)
dp = Dispatcher(storage=storage)
dp.include_routers(*routers_list)
register_global_middlewares(dp, config)


# @app.on_event("startup")
# async def start_up():
#     if await bot.get_webhook_info():
#         await bot.delete_webhook()
#
#     await on_startup(bot, config.tg_bot.admin_ids)
#
#
# class Item(BaseModel):
#     teacher: str
#     image_url: str
#     text: str
#
#
# class RekData:
#     teacher: str
#     image_url: str
#     text: str
#     create_markup: bool
#
#
# @app.post("/test")
# async def process(item: Item):
#     rek = RekData()
#     rek.teacher = item.teacher
#     rek.image_url = item.image_url
#     rek.text = item.text
#     rek.create_markup = False
#
#     await send_homework_to_users(config.tg_bot.admin_ids, rek)
#     return {"Hello": "World"}
#
#
# async def send_homework_to_users(users: list[int], item: RekData):
#     count = 0
#     text = f"<b>Yangi uy vazifasi</b>\n<b>Sana:</b>\t<code>{datetime.now().date()}</code>\n<b>Ustoz:</b>\t{item.teacher}\n<b>Text</b>:\t{item.text}"
#
#     if item.create_markup:
#         markup = uz_subjects_list()
#     else:
#         markup = None
#
#     try:
#         for user_id in users:
#             if await bot.send_photo(
#                     chat_id=user_id,
#                     photo=item.image_url,
#                     caption=text,
#                     reply_markup=markup,
#             ):
#                 count += 1
#             await asyncio.sleep(
#                 0.05
#             )  # 20 messages per second (Limit: 30 messages per second)
#     finally:
#         logging.info(f"{count} messages successful sent.")
#
#     return count
#
#
# @app.post("/webhook")
# async def process_update(update: dict):
#     telegram_update = types.Update(**update)
#     await dp._process_update(bot, telegram_update)
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await broadcaster.broadcast(bot, config.tg_bot.admin_ids, "bot o'chdi")
#     await bot.session.close()
#     return


async def main():
    session = AiohttpSession(proxy="http://172.25.113.50:8085")
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'), session=session)
    await on_startup(bot, config.tg_bot.admin_ids)
    if await bot.get_webhook_info():
        await bot.delete_webhook()

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот був вимкнений!")
