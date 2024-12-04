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

from tgbot.consts.consts import get_region_name_by_id, get_district_name_by_index, SEND_ROUTE_FORM, \
    DIRECTION_STATUS_TEXT, GROUP_ID
from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.check_sub import CheckSubscription
from tgbot.loader import db, config
from tgbot.services import broadcaster
from datetime import datetime, timedelta
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

async def run_bot(tgbot: Bot):
    # session = AiohttpSession(proxy="http://172.25.113.50:8085")
    await on_startup(tgbot, config.tg_bot.admin_ids)
    if await tgbot.get_webhook_info():
        await tgbot.delete_webhook()

    await dp.start_polling(tgbot)


async def schedular(tgbot: Bot):
    while True:
        now = datetime.now()
        target_time = now.replace(hour=1, minute=0, second=0, microsecond=0)

        # If target time is in the past today, schedule it for tomorrow
        if target_time <= now:
            target_time += timedelta(days=1)

        # Calculate sleep duration until target time
        wait_time = (target_time - now).total_seconds()
        logging.info(f"[{now}] Waiting for {wait_time} seconds until {target_time}...")
        # await asyncio.sleep(wait_time)  # Sleep until the scheduled time
        await asyncio.sleep(100)  # Sleep until the scheduled time

        # Run the task
        try:
            # get expired ids
            logging.info("getting ids to expire")
            expired_ids = await db.get_expired_direction_message_ids_for_passive()
            logging.info("changing statuses to passive ")
            await db.passive_expired_directions()

            for i in expired_ids:
                from_region_name = get_region_name_by_id(i["from_region_id"])
                from_district_name = get_district_name_by_index(i['from_region_id'], i['from_district_id'])
                to_region_name = get_region_name_by_id(i['to_region_id'])
                to_district_name = get_district_name_by_index(i['to_region_id'], i['to_district_id'])

                text = SEND_ROUTE_FORM.format(
                    from_region_name + " " + from_district_name,
                    to_region_name + " " + to_district_name,
                    i['start_time'],
                    i['price'],
                    i['comment'],
                    i['name'] + " " + i['surname'],
                    i['model'],
                    i['number'],
                    i['phone'],
                    DIRECTION_STATUS_TEXT[3]
                )

                logging.info("editing message")
                await tgbot.edit_message_text(
                    chat_id=GROUP_ID,
                    message_id=i['message_id'],
                    text=text,
                    reply_markup=None
                )

                logging.info("sending message to admin")
                await asyncio.sleep(0.03)

            await broadcaster.broadcast(tgbot, config.tg_bot.admin_ids, "Job run successfully!")
        except Exception as ex:
            logging.error(ex)


async def main():
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))#, session=session)
    await asyncio.gather(run_bot(bot), schedular(bot))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot o'chdi!")
