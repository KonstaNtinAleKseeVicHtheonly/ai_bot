
from aiogram.types import Message
import os
from dotenv import load_dotenv

load_dotenv()



async def check_admin(message:Message)->bool:
    '''проверка юзера на админа по его id'''
    return message.from_user.id == int(os.getenv('ADMIN_ID'))