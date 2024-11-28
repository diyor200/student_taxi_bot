from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


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
        KeyboardButton(text="Marshrutlar"),
        KeyboardButton(text="👤 Shaxsiy kabinet")],
        [KeyboardButton(text="🚖 Mashina qo'shish")]
    ], resize_keyboard=True)

    return markup


def driver_main_menu_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Marshrutlar"),
        KeyboardButton(text="👤 Shaxsiy kabinet")],
        [KeyboardButton(text="🚕 Marshrut yaratish")]
    ], resize_keyboard=True)

    return markup
