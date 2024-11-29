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


class RouteState(StatesGroup):
    FromRegion = State()
    FromDistrict = State()
    ToRegion = State()
    ToDistrict = State()
    StartTime = State()
    Seats = State()
    Price = State()
    Comment = State()
