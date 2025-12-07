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
import uuid
import os
#vsegpt
from app.open_ai.vse_gpt import generate_text_request_async, generate_image_request_async, generate_vision
#клавиаутра
from app.keyboards.base_keyboards import inline_keyboard, cancel_keyboard
# FSM
from aiogram.fsm.context import FSMContext
from app.FSM.states import ChatMode
# колбэки
from aiogram.types import CallbackQuery
# DB
from app.database.requests.user_requests import set_tg_user_optimized, get_tg_user,calculate_cost, calculate_image_cost
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
    

# @user_handler.message(Command('chat'))
# async def start_chatting(message : Message, state:FSMContext):
#     '''Активирует тесктовый диалог с AI если юзер есть в базе и у него не нулевыйо баланс'''
#     current_user = await get_tg_user(message.from_user.id)
#     if not current_user:
#         await message.answer("Вас нет в базе,пожалуйста зарегестрируйтесь")
#     elif Decimal(current_user.balance) <= 0:
#         await message.answer("Недостаточно срдетсв на балансе, пожалуйста пополните его что бы начать разговор с чатом")
#     else:
#         await state.set_state(ChatMode.text)
#         text_ai_model_info = await get_ai_model_by_name('openai/gpt-4o-mini', 'text')
#         logger.critical(f"модель для текста {text_ai_model_info.name} : {text_ai_model_info.ai_type}")
#         await state.update_data(ai_model=text_ai_model_info.name)
#         await state.update_data(ai_type=text_ai_model_info.ai_type)
#         await message.answer("Активирован диалг с AI, задайте ваш вопрос")
        
@user_handler.message(Command('check_balance'))
async def check_yser_balance(message : Message):
    '''Выводит баланс зера в чат'''
    current_user = await get_tg_user(message.from_user.id)
    if not current_user:
        await message.answer("Вас нет в базе,пожалуйста зарегестрируйтесь")
    await message.answer(f"Вот ваш баланс : {current_user.balance}")

@user_handler.callback_query(F.data == 'cancel')
async def stop_dialog(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Текущий диалог отменени✅ ")
    await callback.message.answer("Выберите нужный вам функционал", reply_markup=inline_keyboard)
    

@user_handler.callback_query(F.data == 'dialog_mod')
async def set_dialog_mod(callback : CallbackQuery, state:FSMContext):
    current_user = await get_tg_user(callback.from_user.id)
    if not current_user:
        await callback.message.answer("Вас нет в базе,пожалуйста зарегестрируйтесь")
    elif Decimal(current_user.balance) <= 0:
        await callback.message.answer("Недостаточно срдетсв на балансе, пожалуйста пополните его что бы начать разговор с чатом")
    else:
        await state.set_state(ChatMode.text)
        text_ai_model_info = await get_ai_model_by_name('openai/gpt-4o-mini', 'text')
        logger.critical(f"модель для текста {text_ai_model_info.name} : {text_ai_model_info.ai_type}")
        await state.update_data(ai_model=text_ai_model_info.name)
        await state.update_data(ai_type=text_ai_model_info.ai_type)
        await callback.message.answer("Активирован диалг с AI, задайте ваш вопрос")
    
    

@user_handler.callback_query(F.data == 'generate_image_mod')
async def set_image_mod(callback : CallbackQuery, state:FSMContext):
    await state.set_state(ChatMode.image)
    image_ai_model_info =  await get_ai_model_by_name('img-flux/flux-2', 'image')
    await state.update_data(ai_model=image_ai_model_info.name)
    await state.update_data(ai_type=image_ai_model_info.ai_type)
    await callback.message.answer("Введите ваш текстовый запрос")
    
@user_handler.callback_query(F.data == 'vision_mod')
async def set_vision_mod(callback : CallbackQuery, state:FSMContext):
    current_user = await get_tg_user(callback.from_user.id)
    if not current_user:
        await callback.message.answer("Вас нет в базе,пожалуйста зарегестрируйтесь")
    elif Decimal(current_user.balance) <= 0:
        await callback.message.answer("Недостаточно срдетсв на балансе, пожалуйста пополните его что бы начать разговор с чатом")
    else:
        await state.set_state(ChatMode.vision)
        text_ai_model_info = await get_ai_model_by_name('vis-z-ai/glm-4.5v', 'vision')
        logger.warning(f"Выбрана модель для генерации текста по фото {text_ai_model_info.name} : {text_ai_model_info.ai_type}")
        await state.update_data(ai_model=text_ai_model_info.name)
        await state.update_data(ai_type=text_ai_model_info.ai_type)
        await state.update_data(local_path_to_load=r"D:\vsc\projects\TG_BOTS\AI_API_BOT\app\downloads\visions") # потом допилить как разберусь с подпиской
        await callback.message.answer("Активирован диалг с AI, отправьте вашу фотографию и описание к ней")
    
@user_handler.message(F.photo, StateFilter(ChatMode.vision))
async def ai_generate_text_by_image(message : Message, state : FSMContext):
    '''принимиает описание картинки и генерирует ее'''
    current_user = await get_tg_user(message.from_user.id)
    current_user_balance = current_user.balance
    if Decimal(current_user_balance) <= 0:
        await message.answer(f"Ваш баланс отрицателен или равен нулю : {current_user_balance}, пожалуйста пополните счет")
    else:
        model_data = await state.get_data()# для передачи в метод расчета имени модели
        await message.answer("Ваш запрос принят, пожалуйста ожидайте")
        await state.set_state(ChatMode.waiting)
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)# какое действие происходит в чате сейча
        # достаем id и путь до фотки от юзера
        user_image = await message.bot.get_file(message.photo[-1].file_id)
        logger.warning(f"вот путь до файла от юзера в хэндлере{user_image.file_path}")
        user_image_name = f"{str(uuid.uuid4())}.jpeg"
        local_path_to_load_image = rf"D:\vsc\projects\TG_BOTS\AI_API_BOT\app\downloads\visions\{user_image_name}" # путь для скачивания фото в проет
        await message.bot.download_file(file_path=user_image.file_path,destination=local_path_to_load_image)
        user_answer = await generate_vision(local_path_to_load_image, message.caption, model_data['ai_model'])# вернет ссылку на сгенерированое изображение
        os.remove(local_path_to_load_image) # удаление фотки от юзера после получения ответного запроса что бы память не засорять
        if user_answer:
            await calculate_cost(message.from_user.id,model_data.get('ai_model'), model_data.get('ai_type'))
            await asyncio.sleep(1)
            await message.answer_photo(photo=user_answer, caption=f"Сгенерировано по запросу : {message.caption}")
            await state.set_state(ChatMode.vision)
            await message.answer("Введите следующий запрос либо выйдите из режима",reply_markup=cancel_keyboard)
        else:
            await message.answer("По вашему запросы вышла ошибка пожалуйста повторите запрос")
        
    
@user_handler.message(F.text, StateFilter(ChatMode.image))
async def ai_generate_image(message : Message, state : FSMContext):
    '''принимиает описание картинки и генерирует ее'''
    current_user = await get_tg_user(message.from_user.id)
    current_user_balance = current_user.balance
    if Decimal(current_user_balance) <= 0:
        await message.answer(f"Ваш баланс отрицателен или равен нулю : {current_user_balance}, пожалуйста пополните счет")
    else:
        model_data = await state.get_data()# для передачи в метод расчета имени модели
        await message.answer("Ваш запрос принят, пожалуйста ожидайте")
        await state.set_state(ChatMode.waiting)
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)# какое действие происходит в чате сейча
        user_answer = await generate_image_request_async(message.text,model_data.get('ai_model')) # вернет ссылку на сгенерированое изображение
        if user_answer:
            await calculate_image_cost(message.from_user.id,model_data.get('ai_model'), model_data.get('ai_type'))
            await asyncio.sleep(1)
            await message.answer(f"Фотография по запросу {message.text} успешно сгененрирована")
            await message.answer_photo(photo=user_answer, caption=f"Сгенерировано по запросу : {message.text}")
            await state.set_state(ChatMode.image)
            await message.answer("Введите следующий запрос либо выйдите из режима",reply_markup=cancel_keyboard)
        else:
            await message.answer("По вашему запросы вышла ошибка пожалуйста повторите запрос")
        
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
    
@user_handler.message(~F.text, StateFilter(ChatMode.image))
async def wrong_image_text_dialog(message : Message):
    await message.answer("Ебаный по голове, тебе же сказали, введие ваш текстовый запрос,хуль ты шляпу всякую отправляешь, занятьс нечем?")

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