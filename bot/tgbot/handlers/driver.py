import logging
import re
from datetime import datetime

import asyncpg

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType
from aiogram.types import ReplyKeyboardRemove

from ..consts.consts import DRIVER_TYPE, DRIVER, CREATE_ROUTE
from ..keyboards.inline import get_regions_inline_keyboard, get_districts_by_region_id
from ..misc.states import DriverRegistration, RouteState
from ..loader import db, config
from ..keyboards.reply import phone_button, driver_main_menu_keyboard, user_main_menu_keyboard, start_keyboard
from ..services.broadcaster import broadcast

driver_router = Router()


# register
@driver_router.message(F.text == DRIVER)
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
    username = message.from_user.username
    if username is None:
        username = str(message.from_user.id)

    if only_card_add:
        try:
            user = await db.get_user_by_telegram_id(telegram_id=message.from_user.id)
            await db.add_car(user_id=user['id'], car_model=car_model, car_number=car_number)
            await db.update_user_type(telegram_id=user['telegram_id'], user_type=DRIVER_TYPE)
        except Exception as e:
            logging.exception(e)
            await message.answer(text="Ro'yhatdan o'tishda muammo yuzaga keldi", reply_markup=start_keyboard())
            await state.clear()
            return
    else:
        try:
            user_id = await db.add_user(username=username, name=name, surname=surname, phone=phone,
                                        telegram_id=message.from_user.id, user_type=DRIVER_TYPE)
            await db.add_car(user_id=user_id[0], car_model=car_model, car_number=car_number)
        except Exception as e:
            logging.exception(e)
            await message.answer(text="Ro'yhatdan o'tishda muammo yuzaga keldi",
                                 reply_markup=start_keyboard())
            await state.clear()
            return

    await message.answer(text="Ro'yhatdan muvaffaqiyatli o'tdingiz!", reply_markup=driver_main_menu_keyboard())
    await state.clear()


@driver_router.message(F.text == CREATE_ROUTE)
async def begin_registration(message: types.Message, state: FSMContext):
    await message.answer("Viloyatni tanlang:", reply_markup=get_regions_inline_keyboard())
    await state.set_state(RouteState.FromRegion)


@driver_router.callback_query(RouteState.FromRegion)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    region_id = int(call.data)

    await state.update_data({
        "from_region_id": region_id
    })

    await call.message.answer("Tumanni tanlang:", reply_markup=get_districts_by_region_id(region_id))
    await state.set_state(RouteState.FromDistrict)


@driver_router.callback_query(RouteState.FromDistrict)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    district_id = int(call.data)

    await state.update_data({
        "from_district_id": district_id
    })

    await call.message.answer("Viloyatni tanlang:", reply_markup=get_regions_inline_keyboard())
    await state.set_state(RouteState.ToRegion)


@driver_router.callback_query(RouteState.ToRegion)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    region_id = int(call.data)

    await state.update_data({
        "to_region_id": region_id
    })

    await call.message.answer("Tumanni tanlang:", reply_markup=get_districts_by_region_id(region_id))
    await state.set_state(RouteState.ToDistrict)


@driver_router.callback_query(RouteState.ToDistrict)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    to_district_id = int(call.data)

    await state.update_data({
        "to_district_id": to_district_id
    })

    await call.message.answer("Yurish vaqtini kiriting:\nMisol: <b>31.12.2024 08:00</b>",
                              reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.StartTime)


@driver_router.message(RouteState.StartTime)
async def begin_registration(message: types.Message, state: FSMContext):
    start_time = message.text

    await state.update_data({
        "start_time": start_time
    })

    await message.answer("Bo'sh joylar soni(faqat son kiriting):\nMisol: <b>4</b>",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.Seats)


@driver_router.message(RouteState.Seats)
async def begin_registration(message: types.Message, state: FSMContext):
    seats = message.text

    await state.update_data({
        "seats": seats
    })

    await message.answer("Narxini kiriting(faqat son):\nMisol: <b>20000</b>",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.Price)


@driver_router.message(RouteState.Price)
async def begin_registration(message: types.Message, state: FSMContext):
    price = message.text

    await state.update_data({
        "price": price
    })

    await message.answer("Izoh kiriting:\nMisol: <b>Andijon shahar Boburshox ko'chasi, Hamkorbank "
                         "bosh office oldidan yuramiz</b>",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.Comment)


@driver_router.message(RouteState.Comment)
async def begin_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    from_region_id = int(data["from_region_id"])
    from_district_id = int(data["from_district_id"])
    to_region_id = int(data["to_region_id"])
    to_district_id = int(data["to_district_id"])
    start_time = datetime.strptime(data["start_time"], "%d.%m.%Y %H:%M")
    seats = int(data["seats"])
    price = int(data["price"])
    comment = message.text

    user = await db.get_user_by_telegram_id(message.from_user.id)
    await db.add_route(driver_id=user['id'], from_region_id=from_region_id, from_district_id=from_district_id,
                       to_region_id=to_region_id, to_district_id=to_district_id, start_time=start_time,
                       seats=seats,
                       price=price, comment=comment)

    await message.answer("Muvaffaqiyatli yaratildi!",
                         reply_markup=driver_main_menu_keyboard())
    await state.set_state(RouteState.Price)
