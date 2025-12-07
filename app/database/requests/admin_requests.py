
from sqlalchemy import select, update, delete
from logger.logger_configuration import setup_logging
from app.database.models import User, AI_Model
from app.utils.system_decorators import set_session_connection # декоратор подключения к сессии для взаимодейтсвия с БД

logger = setup_logging()

@set_session_connection        
async def delete_tg_user(session,user_id:id)->bool:
    '''удаляет юзера и вв=ернет True если он был в базе иначе верну False'''
    try:
        
            user = await session.scalar(select(User).where(User.tg_id == user_id))
            
            if not user:
                logger.info(f"❌ Юзер {user_id} не найден")
                return False
            
            await session.delete(user)
            await session.commit()
            logger.info(f"✅ Юзер {user_id} удален")
            return True           
    except Exception as e:
            logger.error(f"❌ Ошибка удаления юзера {user_id}: {e}")
            return False
        
        

@set_session_connection        
async def get_all_models(session)->list[AI_Model]:
    '''Выводит все модели из БД'''
    try:
            result  = await session.scalars(select(AI_Model))
            return result.all()
                    
    except Exception as e:
            logger.error(f"❌ Ошибка при выводе всех доступных моделей : {e}")
            return False
        
        
@set_session_connection        
async def get_all_users(session)->list[AI_Model]:
    '''Выводиит всех членов данного tg канала'''
    try:
            result  = await session.scalars(select(User))
            return result.all()
                    
    except Exception as e:
            logger.error(f"❌ Ошибка при выводе всех доступных моделей : {e}")
            return False