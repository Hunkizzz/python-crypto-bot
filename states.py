from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    default = State()
    authenticated = State()
    waiting_for_cryptocurrency = State()
