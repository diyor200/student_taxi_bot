from datetime import datetime, timedelta

from ..consts.consts import get_region_name_by_id, GROUP_ID
from ..misc.db_api.postgres import Database

from aiogram import Bot


def get_user_link(username, telegram_id) -> str:
    if username:
        # Link to the user by username
        return f"https://t.me/{username}"
    else:
        # Link to the user by user ID
        return f"tg://user?id={telegram_id}"


def get_route_date_range() -> list:
    return [datetime.now(), datetime.now() + timedelta(days=2)]


async def get_or_create_topic_id(from_region_id: int, bot: Bot, db: Database):
    topic = await db.get_topic_by_region_id(from_region_id)
    if topic is None:
        topic_name = get_region_name_by_id(from_region_id)
        topic = await bot.create_forum_topic(chat_id=GROUP_ID, name=topic_name)
        await db.add_topic(from_region_id, topic.message_thread_id, topic.name)
        topic = await db.get_topic_by_region_id(from_region_id)

    return topic