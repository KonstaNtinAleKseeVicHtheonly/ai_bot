from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
# фитры 
from aiogram.filters import CommandStart, CommandObject, Command
#FSM
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
# системыне утилиты
from logger.logger_configuration import setup_logging
from datetime import datetime
import asyncio
#vsegpt
from app.open_ai.vse_gpt import generate_text_request_async
#клавиаутра
from app.keyboards.base_keyboards import inline_keyboard, cancel_keyboard
# FSM
from aiogram.fsm.context import FSMContext
from app.FSM.states import ChatMode
# колбэки
from aiogram.types import CallbackQuery
# DB
from app.database.requests.user_requests import set_tg_user_optimized, get_tg_user,calculate_cost
from app.database.requests.models_requests import get_ai_model_by_name
#
from decimal import Decimal

logger = setup_logging()

user_handler = Router()



@user_handler.message(CommandStart())
async def start_process(message : Message, state:FSMContext):
    '''пока что активирует текстовый диалог с AI'''
    await state.clear()# на всякий случай сбрасываем состояние что бы начать заново
    await set_tg_user_optimized(user_id=message.from_user.id,user_name=message.from_user.username, created_at=datetime.now(),balance='0')# если юзера нет, в базе - добавить его
    await message.answer(f'''твой id{message.from_user.id}\n
                         твой ник{message.from_user.username} \n
                         тове полное имя {message.from_user.full_name}''')
    await message.answer("Для начала, выберите режим я",reply_markup=inline_keyboard)
    

@user_handler.message(Command('chat'))
async def start_chatting(message : Message, state:FSMContext):
    '''Активирует тесктовый диалог с AI если юзер есть в базе и у него не нулевыйо баланс'''
    current_user = await get_tg_user(message.from_user.id)
    if not current_user:
        await message.answer("Вас нет в базе,пожалуйста зарегестрируйтесь")
    elif Decimal(current_user.balance) <= 0:
        await message.answer("Недостаточно срдетсв на балансе, пожалуйста пополните его что бы начать разговор с чатом")
    else:
        await state.set_state(ChatMode.text)
        text_ai_model_info = await get_ai_model_by_name('openai/gpt-4o-mini', 1)
        await state.update_data(ai_model=text_ai_model_info.name)
        await state.update_data(ai_type=text_ai_model_info.ai_type)
        await message.answer("Активирован диалг с AI, задайте ваш вопрос")
        
@user_handler.message(Command('check_balance'))
async def check_yser_balance(message : Message):
    '''Выводит баланс зера в чат'''
    current_user = await get_tg_user(message.from_user.id)
    if not current_user:
        await message.answer("Вас нет в базе,пожалуйста зарегестрируйтесь")
    await message.answer(f"Вот ваш баланс : {current_user.balance}")

@user_handler.callback_query(F.data == 'cancel')
async def stop_dialog(message:Message, state:FSMContext):
    await state.clear()
    await message.answer("Вы вышли из режима диалога")
    await message.answer("Выберите нужный вам функционал", reply_markup=inline_keyboard)

@user_handler.callback_query(F.data == 'dialog_mod')
async def set_dialog_mod(callback : CallbackQuery, state:FSMContext):
    await state.set_state(ChatMode.text)
    await callback.message.answer("Введите ваш текстовый запрос")
    
@user_handler.message(F.text, StateFilter(ChatMode.text))
async def ai_text_chatting(message : Message, state : FSMContext):
    current_user = await get_tg_user(message.from_user.id)
    current_user_balance = current_user.balance
    if Decimal(current_user_balance) <= 0:
        await message.answer(f"Ваш баланс отрицателен или равен нулю : {current_user_balance}, пожалуйста пополните счет")
    else:
        model_data = await state.get_data()
        await message.answer("Ваш запрос принят, пожалуйста ожидайте")
        await state.set_state(ChatMode.waiting)
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)# какое действие происходит в чате сейча
        user_answer = await generate_text_request_async(message.text) # вернет сам ответ и затраченные токены
        await calculate_cost(message.from_user.id, user_answer['token_usage'],  model_data.get('ai_model'))
        await asyncio.sleep(1)
        await message.answer(f"Получен ответ на ваш запрос:\n{user_answer['response']}")
        await state.set_state(ChatMode.text)
        await message.answer("Введите следующий запрос либо выйдите из режима диалога, нажав кнопку отмены")
    
@user_handler.message(F.text, StateFilter(ChatMode.waiting))
async def wait_message(message : Message):
    await message.answer("Пожалуйста, подождите пока обрабтается ваш предыдущий запрос")
    
@user_handler.message(~F.text, StateFilter(ChatMode.text))
async def wrong_message_text_dialog(message : Message):
    await message.answer("Ебаный по голове, тебе же сказали, введие ваш текстовый запрос,хуль ты шляпу всякую отправляешь, занятьс нечем?")

async def ai_texting(callback : CallbackQuery, state:FSMContext):
    state.set(ChatMode.text)
    await callback.message.answer("Введите ваш запрос")
    
    
@user_handler.message(F.text.startswith('запрос:'))
async def make_api_request(message : Message):
    '''по сообщению от юзера  делает запрос на vsegpt'''
    logger.info(f"принят запрос от юзера {message.text[7:]}")
    await message.answer("Ваш запрос отправлен, пожалуйста подождите генерации ответа")
    ai_answer = await generate_text_request_async(message.text[7:])
    await message.answer(f"Лови ответ:\n{ai_answer}")
    

@user_handler.message(Command('show_me'))
async def show_user_info(message:Message):
    '''показывает юзеру инфу о нем из бд + баланс и прочее'''
    current_user = await get_tg_user(message.from_user.id)
    if not current_user:
        await message.answer("вы еще не зарегестрировались в канале")
    else:
        readable_var = current_user.__dict__.items()
        final_text = ''
        for k,v in readable_var:
            final_text += f"{k}-{v}\n"
        await message.answer(f"Вот инфа о тебе :\n{final_text}")