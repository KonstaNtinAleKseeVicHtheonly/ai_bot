from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, Message
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command, CommandObject
#FSM
from aiogram.fsm.context import FSMContext
from app.FSM.states import NewsLetter
from aiogram.filters import StateFilter
# системыне утилиты
import asyncio
import os
from dotenv import load_dotenv
#фильтры
from app.filters.admin_filters import AdminFilter
# DB
from app.database.requests.admin_requests import delete_tg_user, get_all_models, get_all_users
from app.database.requests.models_requests import  create_ai_model_2
#логгер
from logger.logger_configuration import setup_logging

load_dotenv()

logger = setup_logging()

admin_handler = Router()
admin_handler.message.filter(AdminFilter())



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

        

@admin_handler.message(Command('create_ai_model'))
async def create_new_ai_model(message: Message, command:CommandObject):
    '''по команде создает новую ai_model по имени модели и типу модели и цене переданные через пробел после
    команды /create_ai_model'''
    if not command.args:
        await message.answer("Пожалуйста укажите текстовый тип AI юзера которого нужно удалить")
        return
    try:
        new_ai_model_name, new_ai_type,ai_model_price = command.args.strip().split(' ')
        result = await create_ai_model_2(new_ai_model_name, new_ai_type, ai_model_price)
        if result:
            await message.answer(f"Новая модель AI : {new_ai_type} успешно создаа")
        else:
            await message.answer("Скорее всего какая то шляпа произошла")
    except Exception as err:
        await message.answer(f"Общая ошибка при создании типа AI : {err}")
        
@admin_handler.message(Command('show_all_models'))
async def show_all_ai_model(message: Message):
    '''по команде создает выводит в чат все AI модели из БД'''

    try:
        result = await get_all_models()
        if result:
            general_text = ''
            for model in result:
                general_text += f"Название: {model.name}, тип:{model.aimodel_type}, цена: {model.price}\n"
            await message.answer(f"Список всех акутальных моделей:\n{general_text}")
        else:
            await message.answer("Скорее всего какая то шляпа произошла")
    except Exception as err:
        await message.answer(f"Общая ошибка выводе всех моделей : {err}")
        



@admin_handler.message(Command('newsletter'))
async def activate_sending_mode(message:Message, state:FSMContext):
    '''рассылка сообщения от админа всем членам канала'''
    await state.set_state(NewsLetter.sending_message)
    await message.answer("Активирован режим рассылки сообщений.Введиет сообщеие которое хотите отправить пользователям")
    
@admin_handler.message(StateFilter(NewsLetter.sending_message))
async def send_message_to_chat_members(message:Message, state:FSMContext):
    '''принимает сообщение которое нужно отправить всем юзерам'''
    all_tg_members = await get_all_users()
    error_counter = 0
    for current_member in all_tg_members:
        try:
            await message.send_copy(chat_id=current_member.tg_id)
        except Exception as err:
            logger.warning(f'''При рассылке сообщения {message}, юзеру {current_member.user_name} с tg{current_member.tg_id}
                           произошла ошибка {err}''')
            error_counter += 1
            continue
    logger.info(f"РАссылка сообщения {message} юзера мтг канала успешно завершена")
    await message.answer(f"Сообщение успешно отправлено всем доступным пользователям за исключением {error_counter} пользователей")
    await message.answer("Для выхода из режима рассылки напищите /cancel, для активации режима рассылки пропишите еще раз newsletter")
    await state.clear()
    
@admin_handler.message(Command('cancel'))
async def cancel_processes(message:Message, state:FSMContext):
    '''Команда отмены и выхода их всех FSM'''
    await state.clear()
    await message.answer("Вы вышли из текущего режима")
