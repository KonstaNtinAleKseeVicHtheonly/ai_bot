from app.database.models import User, AI_Model
from sqlalchemy import select, update, delete
from logger.logger_configuration import setup_logging
from decimal import Decimal, ROUND_HALF_UP
from app.utils.system_decorators import set_session_connection # декоратор подключения к сессии для взаимодейтсвия с БД

import os

logger = setup_logging()




        
        
@set_session_connection    
async def set_tg_user_optimized(session,user_id:int,**kwargs):
    '''создает юзера если его нет в бд иначе возрващает его'''
    try:
        user =  await session.scalar(select(User).where(User.tg_id == user_id))
        # если такого юзера нет, создаем нового юзера
        if not user:
            new_user_data = {'tg_id':user_id, **kwargs}
            new_user = User(**new_user_data)
            logger.warning(f"Юзера с tg_id {user_id} нет в БД, добавляем его")
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)  # ← ВАЖНО: обновляем объект из БД
            logger.info(f"Юзер tg_id {user_id} успешно создан")
            return new_user
        logger.info(f"Юзер с tg_id {user_id} успешно найдет")
        return user
    except Exception as err:
        logger.error(f"Ошибка при создании юзера в БД с параметрами id: {user_id}| {kwargs}:\n{err}")
    
@set_session_connection  
async def get_tg_user(session,user_id:int)->User|bool:
    '''выводит изера из базы по его tg_id если такого нет - вернт False'''
    try:
        user = await session.scalar(select(User).where(User.tg_id==user_id))
        if user:
            return user
        logger.warning(f"Юзера с данным tg_id {user_id} нет  в бд")
        return False
    except Exception as err:
        logger.error(f"Ошибка при выведении юзера с id {user_id} из БД: {err}")
        return False
    
@set_session_connection  
async def calculate_cost(session,user_tg_id:int, tokens_spent:int,  model_name:str):
    '''высчитывает сумма потраченную за 1 запрос'''
    try:
        logger.error(f"{user_tg_id}, {tokens_spent}, {model_name}")
        logger.warning(f"Модель {model_name}, затраченные токены {tokens_spent}")
        user = await session.scalar(select(User).where(User.tg_id==user_tg_id))
        ai_model = await session.scalar(select(AI_Model).where(AI_Model.name==model_name))
        logger.warning(f"текущий баланс : {user.balance},количество потраченных токенов {tokens_spent}, цена одного токена{ai_model.price}")
        request_cost_raw= (Decimal(ai_model.price) * Decimal(tokens_spent))* Decimal(os.getenv('INTEREST_RATE'))# сумма запроса на основе количества потраченных токенов и цены одного токена данной модели 1.5 это наша наценка
        request_cost_final = request_cost_raw.quantize(Decimal('0.001'),rounding=ROUND_HALF_UP)
        new_balance = Decimal(user.balance) - Decimal(request_cost_final)# сумма на балансе юзера после запроса
        await session.execute(update(User).where(User.id==user.id).values(balance=str(new_balance)))
        await session.commit()
    except Exception as err:
        logger.error(f"Ошибка при расчете стоимоисти запроса {err}")
        raise ValueError
   
@set_session_connection      
async def calculate_image_cost(session,user_tg_id:int, model_name:str, model_type:str):
    '''высчитывает сумма потраченную за 1 фотографи запрос(без токенов т.к цена в модели указана за генерацию одного изображения)'''
    try:
        user = await session.scalar(select(User).where(User.tg_id==user_tg_id))
        ai_model = await session.scalar(select(AI_Model).where(AI_Model.name==model_name, AI_Model.aimodel_type==model_type))
        request_cost_raw= Decimal(ai_model.price) * Decimal('2')# сумма запроса на основе количества потраченных токенов и цены одного токена данной модели 1.5 это наша наценка
        request_cost_final = request_cost_raw.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        logger.info(f"запрос от юзера {user.user_name} : {user.tg_id}, на сумму {ai_model.price}")
        new_balance = Decimal(user.balance) - Decimal(request_cost_final)# сумма на балансе юзера после запроса
        logger.info(f"был баланс : {user.balance}, стал баланс : {new_balance}")
        await session.execute(update(User).where(User.id==user.id).values(balance=str(new_balance)))
        await session.commit()
    except Exception as err:
        logger.error(f"Ошибка при расчете стоимости генерации изображения: {err}")
        raise ValueError(f"Произошла ошибка: {err}")
        


#метод если нужно загрузка фото на диск
# # Если у тебя есть путь к файлу
# async def send_image_to_user(message_obj:Message, image_path: str, caption: str = ""):
#     """
#     Отправляет изображение пользователю
#     """
#     try:
#         photo = FSInputFile(image_path)# вмксто менеджеа with открывает фотку по image_path
#         await message_obj.answer_photo(
#                 photo=photo,
#                 caption=caption,  # ✅ Добавляем заголовок
#                 parse_mode="HTML"
#             )
#         logger.info(f"Изображение отправлено пользователю {message_obj.from_user.id}")
        
#     except Exception as e:
#         logger.error(f"Ошибка при отправке изображения: {e}")
#         raise