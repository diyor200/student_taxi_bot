import logging
import re
from datetime import datetime

import asyncpg

from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType
from aiogram.types import ReplyKeyboardRemove

from ..consts.consts import (ROUTES, USER_TYPE, SEND_ROUTE_FORM, get_region_name_by_id, get_district_name_by_index,
                             SEND_MESSAGE_VIA_TELERGAM_TEXT, CANCEL_TEXT, NEXT_TEXT)
from ..keyboards.inline import get_regions_inline_keyboard, get_districts_by_region_id, write_to_driver_inline_button
from ..misc.states import RoutesState
from ..utils.common import get_user_link
from ..loader import db, config
from ..keyboards.reply import phone_button, driver_main_menu_keyboard, user_main_menu_keyboard, start_keyboard, next_cancel_keyboard
from ..services.broadcaster import broadcast

routes_router = Router()


# register
@routes_router.message(F.text == ROUTES)
async def begin_registration(message: types.Message, state: FSMContext):
    sent_message = await message.answer("Qaysi viloyatdan viloyatdan:", reply_markup=get_regions_inline_keyboard())

    await state.update_data({
        "message_id": sent_message.message_id
    })
    await state.set_state(RoutesState.FromRegion)


@routes_router.callback_query(RoutesState.FromRegion)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    region_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "from_region_id": region_id
    })

    await call.message.bot.edit_message_text(
        message_id=message_id,
        chat_id=call.from_user.id,
        text="Qaysi tumandan:",
        reply_markup=get_districts_by_region_id(region_id)
    )
    await state.set_state(RoutesState.FromDistrict)


@routes_router.callback_query(RoutesState.FromDistrict)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    district_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "from_district_id": district_id
    })

    await call.message.bot.edit_message_text(
        message_id=message_id,
        chat_id=call.from_user.id,
        text="Qaysi viloyatga:",
        reply_markup=get_regions_inline_keyboard()
    )
    await state.set_state(RoutesState.ToRegion)


@routes_router.callback_query(RoutesState.ToRegion)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    region_id = int(call.data)

    data = await state.get_data()
    message_id = data['message_id']

    await state.update_data({
        "to_region_id": region_id
    })

    await call.message.bot.edit_message_text(
        message_id=message_id,
        chat_id=call.from_user.id,
        text="Qaysi tumanga:",
        reply_markup=get_districts_by_region_id(region_id
                                                ))
    await state.set_state(RoutesState.ToDistrict)


@routes_router.callback_query(RoutesState.ToDistrict)
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    from_region_id = int(data["from_region_id"])
    from_district_id = int(data["from_district_id"])
    to_region_id = int(data["to_region_id"])
    to_district_id = int(call.data)
    message_id = data['message_id']

    user = await db.get_user_by_telegram_id(call.from_user.id)
    available_routes = await db.get_route(from_region_id, from_district_id, to_region_id, to_district_id)

    await call.message.bot.delete_message(chat_id=call.from_user.id, message_id=message_id)

    if user['type'] == USER_TYPE:
        markup = user_main_menu_keyboard()
    else:
        markup = driver_main_menu_keyboard()

    if len(available_routes) < 1:
        await call.message.answer("🤷‍♂️ Marshrutlar topilmadi", reply_markup=markup)
        await state.clear()
        return
    elif len(available_routes) >= 1:  # this is because we send only 5 datas at once
        if len(available_routes) <= 5:
            count = len(available_routes)
            await state.clear()
        else:
            count = 5
            markup = next_cancel_keyboard()

        for i in range(count):
            # get driver and car from db
            driver = await db.get_user_by_id(available_routes[i]['driver_id'])
            car = await db.get_car_by_driver_id(available_routes[i]['driver_id'])

            # prepare vars
            from_region_name = get_region_name_by_id(available_routes[i]['from_region_id'])
            from_district_name = get_district_name_by_index(available_routes[i]['from_region_id'],
                                                            available_routes[i]['from_district_id'])
            to_region_name = get_region_name_by_id(available_routes[i]['from_region_id'])
            to_district_name = get_district_name_by_index(available_routes[i]['to_region_id'],
                                                          available_routes[i]['to_district_id'])

            # prepare sending text
            text = SEND_ROUTE_FORM.format(
                from_region_name + " " + from_district_name,
                to_region_name + " " + to_district_name,
                available_routes[i]['start_time'],
                available_routes[i]['comment'],
                driver['name'] + " " + driver['surname'],
                car['model'],
                car['number'],
                driver['phone'],
            )

            # create send message to user inline button
            link = get_user_link(driver['username'], driver['telegram_id'])

            await call.message.answer(text=text,
                                      reply_markup=write_to_driver_inline_button(text=SEND_MESSAGE_VIA_TELERGAM_TEXT,
                                                                                 link=link))

    if len(available_routes) > 5:
        await state.update_data({"available_routes": available_routes[5:], "type": user['type']})
        await state.set_state(RoutesState.Next)
        await call.message.answer("Boshqalarni ko'rish", reply_markup=markup)

        return

    await state.clear()
    await call.message.answer("Bo'limni tanlang:", reply_markup=markup)


@routes_router.message(RoutesState.Next)
async def begin_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    available_routes = data['available_routes']
    usert_type = data['type']

    if usert_type == USER_TYPE:
        markup = user_main_menu_keyboard()
    else:
        markup = driver_main_menu_keyboard()

    # check message text to cancel
    if message.text == CANCEL_TEXT:
        await state.clear()
        await call.message.answer("Bo'limni tanlang:", reply_markup=markup)
        return

    if len(available_routes) <= 5:
        count = len(available_routes)
        await state.clear()
    else:
        count = 5
        markup = next_cancel_keyboard()

    for i in range(count):
        # get driver and car from db
        driver = await db.get_user_by_id(available_routes[i]['driver_id'])
        car = await db.get_car_by_driver_id(available_routes[i]['driver_id'])

        # prepare vars
        from_region_name = get_region_name_by_id(available_routes[i]['from_region_id'])
        from_district_name = get_district_name_by_index(available_routes[i]['from_region_id'],
                                                        available_routes[i]['from_district_id'])
        to_region_name = get_region_name_by_id(available_routes[i]['from_region_id'])
        to_district_name = get_district_name_by_index(available_routes[i]['to_region_id'],
                                                      available_routes[i]['to_district_id'])

        # prepare sending text
        text = SEND_ROUTE_FORM.format(
            from_region_name + " " + from_district_name,
            to_region_name + " " + to_district_name,
            available_routes[i]['start_time'],
            available_routes[i]['comment'],
            driver['name'] + " " + driver['surname'],
            car['model'],
            car['number'],
            driver['phone'],
            )

        # create send message to user inline button
        link = get_user_link(driver['username'], driver['telegram_id'])

        await message.answer(text=text,
                                  reply_markup=write_to_driver_inline_button(text=SEND_MESSAGE_VIA_TELERGAM_TEXT,
                                                                             link=link))

    if len(available_routes) > 5:
        await state.update_data({"available_routes": available_routes[5:]})
        await state.set_state(RoutesState.Next)
        await message.answer("Boshqalarni ko'rish", reply_markup=markup)

        return

    await state.clear()
    await message.answer("Bo'limni tanlang:", reply_markup=markup)

