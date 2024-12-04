import logging

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from ..keyboards.inline import change_user_info_by_type_keyboard, update_user_info_keyboard
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

    sent_message = await message.answer(text=text)
    await message.bot.edit_message_reply_markup(
        message_id=sent_message.message_id,
        chat_id=message.chat.id,
        reply_markup=change_user_info_by_type_keyboard(user['type'], sent_message.message_id)
    )


async def begin_update_user(call: types.CallbackQuery, state: FSMContext):
    text_parts = call.data.split(":")
    if text_parts not in ['name', 'phone', 'surname']:
        await call.message.answer(text="Nimani o'zgartirmoqchisiz:", reply_markup=update_user_info_keyboard())
        return

    name, surname, phone = None, None, None
    if text_parts == 'name':
        name = text_parts[1]
    elif text_parts == 'phone':
        phone = text_parts[1]
    elif text_parts == 'surname':
        surname = text_parts[1]
    else:
        await call.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return

    try:
        await db.update_user(name, surname, phone, call.from_user.id)
        await call.bot.answer_callback_query(text="✅Muvaffaqiyatli o'zgartirildi",
                                             callback_query_id=call.id,
                                             show_alert=True)
    except Exception as ex:
        logging.error(ex)
        await call.message.answer(text="Xatolik yuzaga keldi, qaytadan urinib ko'ring")
        await state.clear()
        return
