from app.database.models import async_session# подключение к моделям через сессию
import functools

def set_session_connection(func):
    @functools.wraps(func)
    async def wrapper(*args,**kwargs):
        """автоматические открывает сессию"""
        async with async_session() as session:
            return await func(session,*args, **kwargs)    
    return wrapper
        