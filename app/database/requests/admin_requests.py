from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, update, delete
from logger.logger_configuration import setup_logging
logger = setup_logging()

           
async def delete_tg_user(user_id:id)->bool:
    '''удаляет юзера и вв=ернет True если он был в базе иначе верну False'''
    async with async_session() as session:
                try:
                    async with async_session() as session:
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