import logging

from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, Update

from ..consts.consts import CREATE_TOPIC, GROUP_ID
from ..filters.admin import AdminFilter
from ..keyboards.inline import get_regions_inline_keyboard
from ..misc.states import CreateTopic
from ..loader import db, config


admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command(CREATE_TOPIC))
async def begin_registration(message: types.Message, state: FSMContext):
    await message.answer("Topic nomini kiriting:")
    await state.set_state(CreateTopic.Name)


@admin_router.message(CreateTopic.Name)
async def begin_registration(message: types.Message, state: FSMContext):
    name = message.text
    sent_message = await message.answer("Viloyatni tanlang kiriting:", reply_markup=get_regions_inline_keyboard())

    await state.update_data({
        "name": name,
        "message_id": sent_message.message_id
    })

    await state.set_state(CreateTopic.Region)


@admin_router.callback_query(CreateTopic.Region)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    message_id = data["message_id"]
    name = data["name"]
    region_id = int(call.data)

    topic = await call.bot.create_forum_topic(chat_id=GROUP_ID, name=name)
    try:
        await db.add_topic(region_id, topic.message_thread_id, topic.name)
    except Exception as ex:
        logging.error(ex)
        await call.message.bot.edit_message_text(
            text="Topic yaratishda muammo yuzaga keldi",
            chat_id=call.from_user.id,
            message_id=message_id,
            reply_markup=None,
        )

        await state.clear()
        return

    await call.message.bot.edit_message_text(
        text="✅Muvaffaqiyatli yaratildi",
        chat_id=call.from_user.id,
        message_id=message_id,
        reply_markup=None,
    )

    await state.clear()

