from aiogram.fsm.state import StatesGroup, State


class DateTimeStates(StatesGroup):
    START_TIME = State()
    END_TIME = State()
    DATE = State()


class RegStates(StatesGroup):
    FULL_NAME = State()
    MOBILE_NUMBER = State()
    DEPARTMENT = State()


class EditStates(StatesGroup):
    EDIT_START_TIME = State()
    EDIT_END_TIME = State()
    DATE = State()
    USER_ID = State()


class CustomStates(StatesGroup):
    CUSTOM_START_DATE = State()
    CUSTOM_END_DATE = State()


class XlsxState(StatesGroup):
    START_PERIOD = State()
    END_PERIOD = State()


class EditKeyboardStates(StatesGroup):
    EDIT_END_TIME = State()
    DATE = State()
    USER_ID = State()
