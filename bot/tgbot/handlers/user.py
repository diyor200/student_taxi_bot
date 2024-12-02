import logging

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from ..misc.states import Registration, DriverRegistration
from ..loader import db, config
from ..keyboards.reply import phone_button, user_main_menu_keyboard, start_keyboard
from ..services.broadcaster import broadcast
from ..config import load_config
from ..consts.consts import USER_TYPE, PASSENGER, ADD_CAR

user_router = Router()


# register
@user_router.message(F.text == PASSENGER)
async def begin_registration(message: types.Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.Name)


@user_router.message(Registration.Name)
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


@user_router.message(Registration.Surname)
async def get_name(message: types.Message, state: FSMContext):
    if message.content_type != ContentType.TEXT:
        await message.answer("❌ Faqat text ko'rinishida kiriting. Familyangizni qaytadan kiriting:")
        return await state.set_state(Registration.Name)

    surname = message.text
    await state.update_data({
        "surname": surname
    })
    await message.answer("Telefon raqamingizni kiriting:\nMisol: <b>+998901234567</b>",
                         reply_markup=phone_button())
    await state.set_state(Registration.Phone)


@user_router.message(Registration.Phone)
async def get_name(message: types.Message, state: FSMContext):
    phone = message.text

    if message.content_type == ContentType.CONTACT:
        phone = message.contact.phone_number
    else:
        await message.answer("❌ Noto'g'ri format. Qaytadan kiriting:\nTugmadan foydalaning")
        return await state.set_state(Registration.Phone)

    data = await state.get_data()
    name = data["name"]
    surname = data["surname"]
    username = message.from_user.username
    if username is None:
        username = str(message.from_user.id)


    try:
        await db.add_user(username=username, name=name, surname=surname, phone=phone,
                          telegram_id=message.from_user.id, user_type=USER_TYPE)
    except Exception as e:
        logging.exception(e)
        await message.answer(text="Ro'yhatdan o'tishda muammo yuzaga keldi", reply_markup=start_keyboard())
        await state.clear()
        return

    await message.answer(text="✅Ro'yhatdan muvaffaqiyatli o'tdingiz!", reply_markup=user_main_menu_keyboard())
    await state.clear()


@user_router.message(F.text == ADD_CAR)
async def add_car(message: types.Message, state: FSMContext):
    await message.answer("Mashina modelini kiriting:", reply_markup=types.ReplyKeyboardRemove())

    await state.update_data({
        "only_card_add": True
    })
    await state.set_state(DriverRegistration.CarModel)
