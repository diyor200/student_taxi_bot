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

from .personal_account import begin_update_user, begin_update_car
from ..consts.consts import DRIVER_TYPE, DRIVER, CREATE_ROUTE, SEND_ROUTE_FORM, get_region_name_by_id, \
    get_district_name_by_index, DIRECTION_STATUS_ACTIVE, SEND_MESSAGE_VIA_TELERGAM_TEXT, GROUP_ID, DIRECTION_STATUS_TEXT
from ..keyboards.inline import get_regions_inline_keyboard, get_districts_by_region_id, create_cancel_full_button, \
    write_to_driver_inline_button
from ..misc.states import DriverRegistration, RouteState
from ..loader import db, config
from ..keyboards.reply import phone_button, driver_main_menu_keyboard, user_main_menu_keyboard, start_keyboard
from ..utils.common import get_route_date_range, get_user_link

inline_router = Router()


@inline_router.callback_query()
async def begin_registration(call: types.CallbackQuery, state: FSMContext):
    text = call.data
    text_parts = text.split(':')

    match text_parts[0]:
        case 'cancel_route' | 'full_route':
            if text_parts[0] == 'cancel_route':
                status = DIRECTION_STATUS_TEXT[3]
            else:
                status = DIRECTION_STATUS_TEXT[2]

            route = await db.get_route_by_id(int(text_parts[1]))
            user = await db.get_user_by_id(route['driver_id'])
            car = await db.get_car_by_driver_id(route['driver_id'])

            from_region_name = get_region_name_by_id(route["from_region_id"])
            from_district_name = get_district_name_by_index(route['from_region_id'], route['from_district_id'])
            to_region_name = get_region_name_by_id(route['to_region_id'])
            to_district_name = get_district_name_by_index(route['to_region_id'], route['to_district_id'])

            text = SEND_ROUTE_FORM.format(
                from_region_name + " " + from_district_name,
                to_region_name + " " + to_district_name,
                route['start_time'],
                route['price'],
                route['comment'],
                user['name'] + " " + user['surname'],
                car['model'],
                car['number'],
                user['phone'],
                status
            )

            logging.info("editing message")
            await call.bot.edit_message_text(
                chat_id=GROUP_ID,
                message_id=route['message_id'],
                text=text,
                reply_markup=None
            )

            await call.message.answer(text="Bekor qilindi ✖️")
            await call.bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)

        case 'change_user':
            message_id = int(text_parts[1])
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=message_id)
            await begin_update_user(call, state, call.message.message_id)
        case 'change_car':
            message_id = int(text_parts[1])
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=message_id)
            await begin_update_car(call, state, call.message.message_id)
        case 'update_user_info':
            await begin_update_user(call, state, call.message.message_id)
        case 'update_car_info':
            await begin_update_car(call, state, call.message.message_id)