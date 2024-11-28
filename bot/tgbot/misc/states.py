from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    Name = State()
    Surname = State()
    Phone = State()


class DriverRegistration(StatesGroup):
    Name = State()
    Surname = State()
    Phone = State()
    CarModel = State()
    CarNumber = State()
