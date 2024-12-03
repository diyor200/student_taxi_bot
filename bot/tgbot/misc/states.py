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
    StartDate = State()
    StartTime = State()
    Seats = State()
    Price = State()
    Comment = State()


# Topic
class CreateTopic(StatesGroup):
    Name = State()
    Region = State()


class RoutesState(StatesGroup):
    FromRegion = State()
    FromDistrict = State()
    ToRegion = State()
    ToDistrict = State()
    Date = State()
    Next = State()
