from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..consts.consts import regions


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
    builder.row(InlineKeyboardButton(text=text, url=link))
    builder.adjust(1)

    return builder.as_markup()
