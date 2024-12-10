from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..consts.consts import regions, CANCEL_TEXT, FULL_TEXT, DRIVER_TYPE


def get_regions_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for region in regions:
        builder.row()
        builder.row(InlineKeyboardButton(text=region['name'], callback_data=str(region['id'])))

    builder.adjust(1)

    return builder.as_markup()


def get_districts_by_region_id(region_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for region in regions:
        if region['id'] == region_id:
            for i, district in enumerate(region['districts']):
                builder.row(InlineKeyboardButton(text=district, callback_data=str(i)))

    builder.adjust(1)

    return builder.as_markup()


def write_to_driver_inline_button(text, link) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, url=link,
                                     switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                                         query="kak dela",
                                         allow_user_chats=True
                                     )))
    builder.adjust(1)

    return builder.as_markup()


def create_cancel_full_button(callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=CANCEL_TEXT, callback_data=f"cancel_route:{callback_data}"),
        InlineKeyboardButton(text=FULL_TEXT, callback_data=f"full_route:{callback_data}"),
    )

    return builder.as_markup()


def change_user_info_by_type_keyboard(user_type, message_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Foydalanuvchi ma'lumotlarini o'zgartirish", callback_data=f"change_user:{message_id}")
    )

    if user_type == DRIVER_TYPE:
        builder.add(
            InlineKeyboardButton(text="Mashina ma'lumotlarini o'zgartirish", callback_data=f"change_car:{message_id}")
        )

    builder.adjust(1)
    return builder.as_markup()


def update_user_info_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Ism", callback_data=f"update_user_info:name"),
        InlineKeyboardButton(text="Familiya", callback_data=f"update_user_info:surname"),
        InlineKeyboardButton(text="Telefon raqam", callback_data=f"update_user_info:phone"),
    )
    builder.adjust(1)

    return builder.as_markup()


def update_car_info_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Mashina modeli", callback_data=f"update_car_info:car_model"),
        InlineKeyboardButton(text="Mashina raqami", callback_data=f"update_car_info:car_number"),
    )
    builder.adjust(1)

    return builder.as_markup()
