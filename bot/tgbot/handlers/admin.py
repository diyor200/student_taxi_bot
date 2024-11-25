from datetime import datetime
import logging

import xlsxwriter
import os

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile, Update

from tgbot.filters.admin import AdminFilter
from tgbot.loader import db
from tgbot.keyboards.reply import adminKeyboards


admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.reply("Assalomu alaykum. Siz adminsiz!\n Buruqlarni ko'rish uchun /help buyrug'ini kiriting:",
                        reply_markup=adminKeyboards())


# @admin_router.message(Command("help"))
async def admin_help(message: Message):
    print(message.model_dump_json())
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam",)
            # "/get_registration_info - ro'yhatdan o'tganlar",
            # "/get_contest_info - konkurs qatnashchilar ro'yhati")
    return await message.answer(text="\n".join(text))


@admin_router.message(Command("help"))
async def admin_help(update: Update):
    print(update)

@admin_router.message(F.text == "Konkurs ishtirokchilari")
async def get_contest_info(message: Message):
    try:
        all_data = await db.get_all_registration_data()
    except Exception as ex:
        logging.warning(ex)
        await message.answer(
            "ma'lumotlarni olishda maummo yuzaga keldi.\nIltimos qaytadan urinib ko'ring yoki dasturchi bilan bog'laning",
            reply_markup=adminKeyboards())
    file = xlsxwriter.Workbook('contest_info.xlsx')
    workbook = file.add_worksheet("users")

    workbook.write("A1", "№")
    workbook.write("B1", "Ism")
    workbook.write("C1", "Familya")
    workbook.write("D1", "Yoshi")
    workbook.write("E1", "Til")
    workbook.write("F1", "Manzil")
    workbook.write("G1", "Telefon raqam")
    workbook.write("H1", "Sana")

    
    # Iterate over the data and write it out row by row.
    for i in range(len(all_data)):
        workbook.write(f"A{i + 2}", i + 1)
        workbook.write(f"B{i + 2}", all_data[i][1])
        workbook.write(f"C{i + 2}", all_data[i][2])
        workbook.write(f"D{i + 2}", all_data[i][3])
        workbook.write(f"E{i + 2}", all_data[i][4])
        workbook.write(f"F{i + 2}", all_data[i][5])
        workbook.write(f"G{i + 2}", all_data[i][6])
        logging.info(type(all_data[i][7]))
        workbook.write(f"H{i + 2}", all_data[i][7].strftime("%Y-%m-%d %H:%M:%S"))
    file.close()
    document = FSInputFile("contest_info.xlsx")
    await message.answer_document(document, caption="ro'yxatdan o'tgan barcha ishtirokchilar",
                                  reply_markup=adminKeyboards())
    os.remove("contest_info.xlsx")


@admin_router.message(F.text == "Ro'yhatdan o'tganlar")
async def get_contest_info(message: Message):
    try:
        all_data = await db.get_all_subject_registration_data()
        print(all_data)
    except Exception as ex:
        logging.warning(ex)
        await message.answer(
            "ma'lumotlarni olishda maummo yuzaga keldi.\nIltimos qaytadan urinib ko'ring yoki dasturchi bilan bog'laning",
            reply_markup=adminKeyboards())
    file = xlsxwriter.Workbook('registration_info.xlsx')
    workbook = file.add_worksheet("users")

    workbook.write("A1", "№")
    workbook.write("B1", "Ism")
    workbook.write("C1", "Familya")
    workbook.write("D1", "Yoshi")
    workbook.write("E1", "Til")
    workbook.write("F1", "Manzil")
    workbook.write("G1", "Telefon raqam")
    workbook.write("H1", "Fan")
    workbook.write("I1", "Sana")

    # Iterate over the data and write it out row by row.
    for i in range(len(all_data)):
        workbook.write(f"A{i + 2}", i + 1)
        workbook.write(f"B{i + 2}", all_data[i][1])
        workbook.write(f"C{i + 2}", all_data[i][2])
        workbook.write(f"D{i + 2}", all_data[i][3])
        workbook.write(f"E{i + 2}", all_data[i][4])
        workbook.write(f"F{i + 2}", all_data[i][5])
        workbook.write(f"G{i + 2}", all_data[i][6])
        workbook.write(f"H{i + 2}", all_data[i][7])
        workbook.write(f"I{i + 2}", all_data[i][8].strftime("%Y-%m-%d %H:%M:%S"))
    file.close()
    document = FSInputFile("registration_info.xlsx")
    await message.answer_document(document, caption="ro'yxatdan o'tgan barcha ishtirokchilar",
                                  reply_markup=adminKeyboards())
    os.remove("registration_info.xlsx")


# @user_router.message(F.text == "Konkurs ishtirokchilari")
# async def about_contest(message: Message):
#     await message.answer_photo(
#         photo="https://telegra.ph/file/9d19f625ff5734cedbb17.jpg",
#         caption="Konkurs haqida ma'lumot"
#     )


# @user_router.message(F.text == "Ro'yhatdan o'tganlar")
# async def about_contest(message: Message):
#     await message.answer_photo(
#         photo="https://telegra.ph/file/9d19f625ff5734cedbb17.jpg",
#         caption="Konkurs shartlari haqida ma'lumot")