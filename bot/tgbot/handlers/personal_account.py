import logging

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from ..misc.states import Registration, DriverRegistration
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

    await message.answer(text=text, reply_markup=markup)
