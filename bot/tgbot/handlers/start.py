import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, Update

from ..consts.consts import DRIVER_TYPE
from ..keyboards.reply import start_keyboard, driver_main_menu_keyboard, user_main_menu_keyboard
from ..loader import db

start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message):
    try:
        user = await db.get_user_by_telegram_id(message.from_user.id)

        if user["type"] == DRIVER_TYPE:
            markup = driver_main_menu_keyboard
        else:
            markup = user_main_menu_keyboard
    except Exception as e:
        await message.reply("Assalomu alaykum botdan foydalanish uchun avval ro'yhatdan o'ting:",
                            reply_markup=start_keyboard())
        return

    await message.reply("Assalomu alaykum! Botimizga xush kelibsiz",
                        reply_markup=markup())


@start_router.message(Command("help"))
async def start_help(message: Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam",)

    return await message.answer(text="\n".join(text))
