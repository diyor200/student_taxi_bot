import logging
import re
from datetime import datetime, timedelta

import asyncpg

from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType
from aiogram.types import ReplyKeyboardRemove

from ..consts.consts import DRIVER_TYPE, DRIVER, CREATE_ROUTE, SEND_ROUTE_FORM, get_region_name_by_id, \
    get_district_name_by_index, DIRECTION_STATUS_ACTIVE, SEND_MESSAGE_VIA_TELERGAM_TEXT, GROUP_ID, DIRECTION_STATUS_TEXT
from ..keyboards.inline import get_regions_inline_keyboard, get_districts_by_region_id, create_cancel_full_button, \
    write_to_driver_inline_button
from ..misc.states import DriverRegistration, RouteState
from ..loader import db, config
from ..keyboards.reply import phone_button, driver_main_menu_keyboard, user_main_menu_keyboard, start_keyboard
from ..utils.common import get_route_date_range, get_user_link

driver_router = Router()


@driver_router.message(Command('group'))
async def begin_registration(message: types.Message, state: FSMContext):
    print(f"{message.chat.id=}")
    topic = message.message_thread_id

    await message.answer("Ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DriverRegistration.Name)


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

    await message.answer(text="✅Ro'yhatdan muvaffaqiyatli o'tdingiz!", reply_markup=driver_main_menu_keyboard())
    await state.clear()


@driver_router.message(F.text == CREATE_ROUTE)
async def begin_registration(message: types.Message, state: FSMContext):
    sent_message = await message.answer("Qaysi viloyatdan:", reply_markup=get_regions_inline_keyboard())

    await state.update_data({
        "message_id": sent_message.message_id
    })
    await state.set_state(RouteState.FromRegion)


@driver_router.callback_query(RouteState.FromRegion)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    region_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "from_region_id": region_id
    })

    await call.message.bot.edit_message_text(text="Qaysi tumanga:",
                                             chat_id=call.from_user.id,
                                             message_id=message_id,
                                             reply_markup=get_districts_by_region_id(region_id))
    await state.set_state(RouteState.FromDistrict)


@driver_router.callback_query(RouteState.FromDistrict)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    district_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "from_district_id": district_id
    })

    await call.message.bot.edit_message_text(text="Qaysi viloyatga:",
                                             message_id=message_id,
                                             chat_id=call.from_user.id,
                                             reply_markup=get_regions_inline_keyboard())
    await state.set_state(RouteState.ToRegion)


@driver_router.callback_query(RouteState.ToRegion)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    region_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "to_region_id": region_id
    })

    await call.message.bot.edit_message_text(text="Qaysi tumanga:",
                                             message_id=message_id,
                                             chat_id=call.from_user.id,
                                             reply_markup=get_districts_by_region_id(region_id))
    await state.set_state(RouteState.ToDistrict)


@driver_router.callback_query(RouteState.ToDistrict)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    to_district_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "to_district_id": to_district_id
    })

    date_range = get_route_date_range()
    await call.message.bot.edit_message_text(
        text=f"Yurish sanasini kiriting:\nMisol: <b>{date_range[0].strftime('%d.%m.%Y')}</b>\n"
             f"Eslatma: kiritilayotgan sana {date_range[0].strftime('%d.%m.%Y')}"
             f" va {date_range[1].strftime('%d.%m.%Y')} oralig'ida bo'lishi kerak",
        message_id=message_id,
        chat_id=call.from_user.id,
        reply_markup=None)
    await state.set_state(RouteState.StartDate)


@driver_router.message(RouteState.StartDate)
async def begin_registration(message: types.Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        date_range = get_route_date_range()
        if start_date < datetime.today().date() or start_date > datetime.today().date() + timedelta(days=3):
            await message.answer(text=f"✖️ Noto'g'ri format, iltimos qaytadan kiriting:\nMisol: <b>31.12.2024</b>\n"
                                      f"Eslatma: kiritilayotgan sana {date_range[0].strftime('%d.%m.%Y')}"
                                      f" va {date_range[1].strftime('%d.%m.%Y')} oralig'ida bo'lishi kerak")
            await state.set_state(RouteState.StartDate)
            return
    except Exception as ex:
        logging.error(ex)
        await message.answer(text="✖️ Noto'g'ri format, iltimos qaytadan kiriting:")
        await state.set_state(RouteState.StartDate)
        return

    await state.update_data({
        "start_date": start_date
    })

    await message.answer("Yurish vaqtini kiriting:\nMisol: <b>08:00</b>",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.StartTime)


@driver_router.message(RouteState.StartTime)
async def begin_registration(message: types.Message, state: FSMContext):
    try:
        start_time = datetime.strptime(message.text, "%H:%M").time()
    except Exception as ex:
        logging.error(ex)
        await message.answer(text="✖️ Noto'g'ri format, iltimos qaytadan kiriting:")
        await state.set_state(RouteState.StartTime)
        return

    await state.update_data({
        "start_time": start_time
    })

    await message.answer("Bo'sh joylar soni(faqat son kiriting):\nMisol: <b>4</b>",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.Seats)


@driver_router.message(RouteState.Seats)
async def begin_registration(message: types.Message, state: FSMContext):
    try:
        seats = int(message.text)
    except Exception as ex:
        logging.error(ex)
        await message.answer(text="✖️ Noto'g'ri format, iltimos qaytadan kiriting:")
        await state.set_state(RouteState.Seats)
        return

    await state.update_data({
        "seats": seats
    })

    await message.answer("Narxini kiriting(faqat son):\nMisol: <b>20000</b>",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(RouteState.Price)


@driver_router.message(RouteState.Price)
async def begin_registration(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except Exception as ex:
        logging.error(ex)
        await message.answer(text="✖️ Noto'g'ri format, iltimos qaytadan kiriting:\nMisol: <b>20000</b>")
        await state.set_state(RouteState.Price)
        return

    await state.update_data({
        "price": price
    })

    await message.answer("📄 Qo'shimcha ma'lumot kiriting:\nMisol: <b>Andijon shahar Boburshox ko'chasi, Hamkorbank "
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
    start_date = data["start_date"]
    start_time = datetime.combine(start_date, data["start_time"])
    seats = data["seats"]
    price = data["price"]
    comment = message.text

    await state.clear()

    user = await db.get_user_by_telegram_id(message.from_user.id)

    # except Exception as ex:
    #     logging.error(ex)
    #     await message.answer(text="✖️Ma'lumot yaratishda xatolik ro'y berdi, iltimos qaytadan urinib ko'ring")

    car = await db.get_car_by_driver_id(user['id'])

    # prepare vars
    from_region_name = get_region_name_by_id(from_region_id)
    from_district_name = get_district_name_by_index(from_region_id, from_district_id)
    to_region_name = get_region_name_by_id(from_region_id)
    to_district_name = get_district_name_by_index(to_region_id, to_district_id)

    text = SEND_ROUTE_FORM.format(
        from_region_name + " " + from_district_name,
        to_region_name + " " + to_district_name,
        start_time,
        price,
        comment,
        user['name'] + " " + user['surname'],
        car['model'],
        car['number'],
        user['phone'],
        DIRECTION_STATUS_TEXT[DIRECTION_STATUS_ACTIVE]
    )

    # send to topic
    topic = await db.get_topic_by_region_id(from_region_id)
    sent_message = await message.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=topic['topic_id'],
        text=text,
        reply_markup=write_to_driver_inline_button(text=SEND_MESSAGE_VIA_TELERGAM_TEXT,
                                                   link=get_user_link(message.from_user.username, message.from_user.id))
    )

    route = await db.add_route(driver_id=user['id'], from_region_id=from_region_id, from_district_id=from_district_id,
                               to_region_id=to_region_id, to_district_id=to_district_id,
                               message_id=sent_message.message_id,
                               start_time=start_time, seats=seats, price=price, comment=comment,
                               status=DIRECTION_STATUS_ACTIVE)
    await message.answer(text=text, reply_markup=create_cancel_full_button(f"{route['id']}"))

    await message.answer(text="✅Muvaffaqiyatli yaratildi!",
                         reply_markup=driver_main_menu_keyboard())
