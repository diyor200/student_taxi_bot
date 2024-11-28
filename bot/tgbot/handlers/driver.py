import logging
import re
import asyncpg

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType
from aiogram.types import ReplyKeyboardRemove

from ..consts.consts import DRIVER_TYPE
from ..misc.states import DriverRegistration
from ..loader import db, config
from ..keyboards.reply import phone_button, driver_main_menu_keyboard, user_main_menu_keyboard
from ..services.broadcaster import broadcast

driver_router = Router()


# register
@driver_router.message(F.text == "🚖 Haydovchi")
async def begin_registration(message: types.Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DriverRegistration.Name)


@driver_router.message(DriverRegistration.Name)
async def get_name(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("❌ Faqat text ko'rinishida kiriting. Ismingizni qaytadan kiriting:")
        return await state.set_state(DriverRegistration.Name)

    name = message.text
    await state.update_data({
        "name": name
    })

    await message.answer("Familyangizni kiriting:")
    await state.set_state(DriverRegistration.Surname)


@driver_router.message(DriverRegistration.Surname)
async def get_name(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("❌ Faqat text ko'rinishida kiriting. Familyangizni qaytadan kiriting:")
        return await state.set_state(DriverRegistration.Name)

    surname = message.text
    await state.update_data({
        "surname": surname
    })
    await message.answer("Telefon raqamingizni kiriting:\nMisol: <b>+998901234567</b>",
                         reply_markup=phone_button())
    await state.set_state(DriverRegistration.Phone)


@driver_router.message(DriverRegistration.Phone)
async def get_name(message: types.Message, state: FSMContext):
    phone = message.text

    if message.content_type == ContentType.TEXT or message.content_type == ContentType.CONTACT:
        if message.content_type == ContentType.CONTACT:
            phone = message.contact.phone_number
    else:
        await message.answer("❌ Noto'g'ri format. Qaytadan kiriting:\nTugmadan foydalaning")
        return await state.set_state(DriverRegistration.Phone)

    await state.update_data({
        "phone": phone
    })

    await message.answer(text="Mashina modelini kiriting:\nMisol: <b>Gentra</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(DriverRegistration.CarModel)


@driver_router.message(DriverRegistration.CarModel)
async def get_name(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("❌ Faqat text ko'rinishida kiriting. Ismingizni qaytadan kiriting:")
        return await state.set_state(DriverRegistration.CarModel)

    model = message.text
    await state.update_data({
        "model": model
    })

    await message.answer("Raqamini kiriting:\nMisol: <b>01 Z 001 ZZ</b>")
    await state.set_state(DriverRegistration.CarNumber)


@driver_router.message(DriverRegistration.CarNumber)
async def get_name(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("❌ Faqat text ko'rinishida kiriting. Ismingizni qaytadan kiriting:")
        return await state.set_state(DriverRegistration.CarNumber)

    data = await state.get_data()
    name = data.get('name')
    surname = data.get("surname")
    phone = data.get("phone")
    car_model = data.get("model")
    only_card_add = data.get("only_card_add")
    car_number = message.text

    if only_card_add:
        try:
            user = await db.get_user_by_telegram_id(telegram_id=message.from_user.id)
            await db.add_car(user_id=user['id'], car_model=car_model, car_number=car_number)
            await db.update_user_type(telegram_id=user['telegram_id'], user_type=DRIVER_TYPE)
        except Exception as e:
            logging.exception(e)
            await message.answer(text="Ro'yhatdan o'tishda muammo yuzaga keldi", reply_markup=user_main_menu_keyboard())
            return
    else:
        try:
            user_id = await db.add_user(username=message.from_user.username, name=name, surname=surname, phone=phone,
                                        telegram_id=message.from_user.id, user_type=DRIVER_TYPE)
            await db.add_car(user_id=user_id[0], car_model=car_model, car_number=car_number)
        except Exception as e:
            logging.exception(e)
            await message.answer(text="Ro'yhatdan o'tishda muammo yuzaga keldi",
                                 reply_markup=types.ReplyKeyboardRemove())
            return

    await message.answer(text="Ro'yhatdan muvaffaqiyatli o'tdingiz!", reply_markup=driver_main_menu_keyboard())
    await state.clear()


@driver_router.message(F.text == "🚕 Marshrut yaratish")
async def begin_registration(message: types.Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DriverRegistration.Name)