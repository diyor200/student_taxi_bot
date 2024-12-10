from aiogram import Router, Bot
from aiogram.types import Update
from aiogram.types import ContentType
from aiogram import F

forum_router = Router()

@forum_router.message(content_types=ContentType.FORUM_TOPIC_CLOSED)
async def handle_forum_topic_delete(update: Update, bot: Bot):
    chat_id = update.chat.id
    topic_id = update.chat_delete_forum_topic.message_thread_id

    # Log or perform an action
    print(f"Forum topic deleted in chat {chat_id}, topic ID: {topic_id}")

    # Optional notification
    await bot.send_message(chat_id, f"A forum topic (ID: {topic_id}) was deleted.")
