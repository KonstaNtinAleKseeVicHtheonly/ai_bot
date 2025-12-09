from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, update, delete
from logger.logger_configuration import setup_logging
from app.database.models import AI_Model, Order

logger = setup_logging()






# async def create_ai_type_wrong_var(ai_type:str):
#     if not isinstance(ai_type, str):
#         logger.warning("Нужно ввести тип ai  в строковом варианте")
#         return False
#     try:
#         async with async_session() as session:
#             result = await check_ai_type(session, ai_type)
#             if result is not None:
#                 logger.info("данный тип AI модели уже сущестует")
#                 return False
#             logger.info("Создание типа AI")
#             new_ai_type = AI_type(name=ai_type)
#             await session.add(new_ai_type)
#             await session.commit()
#             return new_ai_type
#     except Exception as err:
#         logger.error(f"ошибка произошла при создании типа AI : {err}")
#         return False
    
# async def create_ai_type_hz(ai_type: str):
#     """Создает тип AI если его нет"""
#     if not isinstance(ai_type, str):
#         logger.warning("❌ Нужно ввести тип AI в строковом варианте")
#         return None  # ⬅️ возвращаем None, не False
#     async with async_session() as session:
#             try:
#                 # Проверяем существование
#                 existing = await session.scalar(
#                     select(AI_type).where(AI_type.name == ai_type)
#                 )
#                 if existing:
#                     logger.info(f"ℹ️ Тип AI '{ai_type}' уже существует")
#                     return False
#                 # Создаем новый
#                 logger.info(f"СОздание нового AI_type : {ai_type}")
#                 new_ai_type = AI_type(name=ai_type)
#                 session.add(new_ai_type)
#                 await session.commit()
#                 logger.info(f"✅ Тип AI '{ai_type}' создан, ID: {new_ai_type.id}")
#                 return new_ai_type
#             except Exception as err:
#                 logger.error(f"❌ Ошибка создания типа AI '{ai_type}': {err}")
#                 return None  # ⬅️ возвращаем None при ошибке
            
    
# async def check_ai_type(current_session,ai_type:str)->bool|AI_type:
#     '''если такой тип уже есть в БД - вернет данную строку из БД иначе False'''
#     # Проверяем существование
#     existing = await current_session.scalar(
#             select(AI_type).where(AI_type.name == ai_type)) 
#     if existing:
#             logger.info(f"ℹ️ Тип AI '{ai_type}' уже существует")
#             return existing
#     logger.info("Не существует указанного типа AI")
#     return False

    
    
async def create_ai_model_2(ai_model_name: str, ai_type_name: str, ai_model_price:str):
    """Создает новую AI модель"""
    try:
        async with async_session() as session:
            # 1. Проверяем существование типа AI
            # 2. Проверяем, не существует ли уже такая модель
            existing_model = await session.scalar(
                select(AI_Model).where(AI_Model.name == ai_model_name, AI_Model.aimodel_type == ai_type_name)
            )
            if existing_model:
                logger.warning(f"⚠️ Модель AI '{ai_model_name}' уже существует")
                return False  # или None/False
            # 3. Создаем новую модель (БЕЗ AWAIT!)
            new_ai_model = AI_Model(
                name=ai_model_name,
                aimodel_type=ai_type_name,
                price = ai_model_price
            )
            session.add(new_ai_model)  # без await!
            # 4. Сохраняем в БД
            await session.commit()
            await session.refresh(new_ai_model)
            
            logger.info(f"✅ Новая AI модель '{ai_model_name}' успешно создана")
            return new_ai_model         
    except ValueError as err:
        # Ловим исключение из check_ai_type
        logger.error(f"❌ Ошибка проверки типа AI: {err}")
        return None
    except Exception as err:
        logger.error(f"❌ Ошибка создания модели AI '{ai_model_name}': {err}")
        # Сессия уже закрыта контекстным менеджером, rollback не нужен
        return None
    
   
    
async def get_ai_model_by_name(ai_name:str,ai_type:str): # вынести проверку на существование строки в БД в отдельный метод потом!!!
    '''из БД возвращает объект класса AI_Models по ее названию и названию типа ai'''
    async with async_session() as session:
        try:
            
            existing_ai = await session.scalar(select(AI_Model).where(AI_Model.name==ai_name, AI_Model.aimodel_type==ai_type))
            if not existing_ai:
                logger.info(f"МОдели AI с именем {ai_name} нет в БД")
                return False
            logger.info(f"строка с именем {ai_name} имеется в БД")
            return existing_ai
        except Exception as err:
            logger.info(f"Общая ошибка при получнии объекта AI_Model : {err}")
            return err
        
