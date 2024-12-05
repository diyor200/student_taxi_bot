from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from ..consts.consts import ROUTES, NEXT_TEXT, CANCEL_TEXT, CREATE_ROUTE, MY_ROUTES, PERSONAL_ACCOUNT_TEXT


def start_keyboard():
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="👨 Yo'lovchi"),
        KeyboardButton(text="🚖 Haydovchi")
    ]],
        resize_keyboard=True)
    return markup


def phone_button() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Telefon raqam yuborish", request_contact=True)]],
      resize_keyboard=True)
    return markup


def user_main_menu_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text=ROUTES),
        KeyboardButton(text="👤 Shaxsiy kabinet")],
        [KeyboardButton(text="🚖 Mashina qo'shish")]
    ], resize_keyboard=True)

    return markup


def driver_main_menu_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text=ROUTES),
        KeyboardButton(text=PERSONAL_ACCOUNT_TEXT)],
        [KeyboardButton(text=CREATE_ROUTE)],
        [KeyboardButton(text=MY_ROUTES)],
    ], resize_keyboard=True)

    return markup


def next_cancel_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text=NEXT_TEXT),
        KeyboardButton(text=CANCEL_TEXT),
    ]], resize_keyboard=True
    )

    return markup
