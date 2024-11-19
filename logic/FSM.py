from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class Reg(StatesGroup):
    name = State()
    time_to_message = State()
    city = State()