import logging

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from tgbot.misc.states import Registration
from tgbot.loader import db, config
from tgbot.keyboards.reply import markup, builder, adminKeyboards
from tgbot.services.broadcaster import broadcast
from tgbot.config import load_config

contest_router = Router()

config = load_config(".env")

# register
@contest_router.message(F.text == '📝 Konkursda qatnashish')
async def begin_registration(message: types.Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.Name)


@contest_router.message(Registration.Name)
async def get_name(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("❌ Faqat text ko'rinishida kiriting. Ismingizni qaytadan kiriting:")
        return await state.set_state(Registration.Name)

    name = message.text
    await state.update_data({
        "name": name
    })
    await message.answer("Familyangizni kiriting:")
    await state.set_state(Registration.Surname)