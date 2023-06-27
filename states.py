from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    waiting_for_cryptocurrency = State()