import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile, Update



admin_router = Router()
# admin_router.message.filter(AdminFilter())
