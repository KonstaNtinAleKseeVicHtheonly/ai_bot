from aiogram.fsm.state import State, StatesGroup

class ChatMode(StatesGroup):
    text = State()
    image = State()
    waiting = State()
    vision = State()
    
class NewsLetter(StatesGroup):
    '''класс, Отвечающий за рассылку новостей'''
    sending_message = State() # сам сообщени е которое нужн разослать всем юзерам