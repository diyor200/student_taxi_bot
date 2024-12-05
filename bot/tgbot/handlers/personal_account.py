import logging
from pyexpat.errors import messages

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from ..keyboards.inline import change_user_info_by_type_keyboard, update_user_info_keyboard, update_car_info_keyboard
from ..misc.states import Registration, DriverRegistration, UpdateUserData, UpdateCarData
from ..loader import db, config
from ..keyboards.reply import phone_button, user_main_menu_keyboard, start_keyboard, driver_main_menu_keyboard
from ..services.broadcaster import broadcast
from ..config import load_config
from ..consts.consts import USER_TYPE, PERSONAL_ACCOUNT_TEXT, PERSONAL_ACCOUNT_INFO_FORM, PERSONAL_ACCOUNT_CAR_INFO_FORM

account_router = Router()


# get account info
@account_router.message(F.text == PERSONAL_ACCOUNT_TEXT)
async def begin_registration(message: types.Message):
    # collect user data
    user = await db.get_user_by_telegram_id(message.from_user.id)
    try:
        car = await db.get_car_by_driver_id(user['id'])
    except Exception as e:
        logging.error(e)
        car = None

    if user['type'] == USER_TYPE:
        markup = user_main_menu_keyboard()
    else:
        markup = driver_main_menu_keyboard()

    # generate text
    text = PERSONAL_ACCOUNT_INFO_FORM.format(
        user['name'],
        user['surname'],
        user['phone'],
        "faol"
    )

    if car is not None:
        text += PERSONAL_ACCOUNT_CAR_INFO_FORM.format(
            car['model'],
            car['number']
        )

    sent_message = await message.answer(text=text)
    await message.bot.edit_message_reply_markup(
        message_id=sent_message.message_id,
        chat_id=message.chat.id,
        reply_markup=change_user_info_by_type_keyboard(user['type'], sent_message.message_id)
    )


async def begin_update_user(call: types.CallbackQuery, state: FSMContext, message_id):
    text_parts = call.data.split(":")
    print(f"{text_parts=}")
    if text_parts[1] not in ['name', 'phone', 'surname']:
        await call.message.answer(text="Nimani o'zgartirmoqchisiz:", reply_markup=update_user_info_keyboard())
        return

    print(f"{text_parts=}")
    if text_parts[1] == 'name':
        text = "Yangi ism kiriting"
        cache_data = {"change": "name"}
    elif text_parts[1] == 'phone':
        text = "Yangi teleforn raqam kiriting"
        cache_data = {"change": "phone"}
    elif text_parts[1] == 'surname':
        text = "Yangi familiya kiriting"
        cache_data = {"change": "surname"}
    else:
        await call.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return

    await call.bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=call.message.chat.id,
        reply_markup=None
    )

    await state.set_data(cache_data)
    await state.set_state(UpdateUserData.Field)


@account_router.message(UpdateUserData.Field)
async def update_user_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(f"{data=}")
    name, surname, phone = None, None, None
    if 'name' == data.get('change'):
        name = message.text
    elif 'surname' == data.get('change'):
        surname = message.text
    elif 'phone' == data.get('change'):
        phone = message.text
    else:
        await message.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return

    try:
        await db.update_user(name, surname, phone, message.from_user.id)
        await state.clear()
        await message.answer(text="✅Muvaffaqiyatli o'zgartirildi")
    except Exception as ex:
        logging.error(ex)
        await message.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return


async def begin_update_car(call: types.CallbackQuery, state: FSMContext, message_id):
    text_parts = call.data.split(":")
    if text_parts[1] not in ['car_model', 'car_number']:
        await call.message.answer(text="Nimani o'zgartirmoqchisiz:", reply_markup=update_car_info_keyboard())
        return

    if text_parts[1] == 'car_model':
        text = "Yangi avtomobil modelini kiriting"
        cache_data = {"change": "car_model"}
    elif text_parts[1] == 'car_number':
        text = "Yangi avtomobil raqamini kiriting"
        cache_data = {"change": "car_number"}
    else:
        await call.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return

    await call.bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=call.message.chat.id,
        reply_markup=None
    )

    await state.set_data(cache_data)
    await state.set_state(UpdateCarData.Field)


@account_router.message(UpdateCarData.Field)
async def update_user_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("car data", data)
    car_model, car_number = None, None
    if 'car_model' == data.get('change'):
        car_model = message.text
    elif 'car_number' == data.get('change'):
        car_number = message.text
    else:
        await message.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return

    try:
        await db.update_car(car_model, car_number, message.from_user.id)
        await state.clear()
        await message.answer(text="✅Muvaffaqiyatli o'zgartirildi")
    except Exception as ex:
        logging.error(ex)
        await message.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return
