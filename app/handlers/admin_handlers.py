from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, Message
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject
#FSM
from aiogram.fsm.context import FSMContext
# системыне утилиты
import asyncio
from logger.logger_configuration import setup_logging
#API
from app.open_ai.deepseek_api import check_balance, test_api_key, base_request
import os
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import check_admin
# DB
from app.database.requests.admin_requests import delete_tg_user
from app.database.requests.models_requests import create_ai_type_hz, create_ai_model_2

load_dotenv()

logger = setup_logging()

admin_handler = Router()
admin_handler.message.filter(check_admin)

@admin_handler.message(Command('show_balance'))
async def show_deepseek_token_balance(message: Message):
    await message.answer("Запрос отправлен")
    balance = base_request()
    await message.answer(f"твой баланс составляет {balance}")


@admin_handler.message(Command('delete_user'))
async def delete_user_by_id(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("Пожалуйста укажите в команде id юзера которого нужно удалить")
        return
    try:
        user_id = int(command.args)
        delete_action = await delete_tg_user(user_id)
        if delete_action:
            await message.answer(f"Юзер с id : {user_id} успешно удален")
        else:
            await message.answer(f"Юзера с id : {user_id} нет в базе данных!")
    except ValueError:
        await message.answer("Необходимо указать числовое значение юзера")
        return
    except Exception as err:
        await message.answer(f"общая ошибка произошла при удалении :{err}")
        return 

@admin_handler.message(Command('create_ai_type'))
async def create_new_ai_type(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("Пожалуйста укажите текстовый тип AI юзера которого нужно удалить")
        return
    try:
        new_ai_type = command.args.strip()
        result = await create_ai_type_hz(new_ai_type)
        if result:
            await message.answer(f"Новый тип AI : {new_ai_type} успешно создан")
        else:
            await message.answer(f"Скорее данный тип AI {new_ai_type} уже существует, либо указано неверный тип")
    except Exception as err:
        await message.answer(f"Общая ошибка при создании типа AI : {err}")
        

@admin_handler.message(Command('create_ai_model'))
async def create_new_ai_model(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("Пожалуйста укажите текстовый тип AI юзера которого нужно удалить")
        return
    try:
        new_ai_model_name, new_ai_type = command.args.strip().split(' ')
        result = await create_ai_model_2(new_ai_model_name, new_ai_type)
        if result:
            await message.answer(f"Новая модель AI : {new_ai_type} успешно создаа")
        else:
            await message.answer("Скорее всего какая то шляпа произошла")
    except Exception as err:
        await message.answer(f"Общая ошибка при создании типа AI : {err}")
        

