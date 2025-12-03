from aiogram.fsm.state import State, StatesGroup

class ChatMode(StatesGroup):
    text = State()
    waiting = State()