from aiogram import Bot,Dispatcher
from logger.logger_configuration import setup_logging
import os
from dotenv import load_dotenv
import asyncio
# роутеры
from app.handlers.admin_handlers import admin_handler
from app.handlers.user_handlers import user_handler
# редис
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis
#DB
from app.database.models import async_db_main


load_dotenv()

logger = setup_logging()



async def on_startup(dispatcher):
    '''метод создающий таблицы и устанавлаивающий связь в СУБД при запуске БОТА'''
    logger.info("Подключение к СУБД Postgrsql")
    try:
        await async_db_main()
        logger.info("Подключение успешно")
    except Exception as err:
        logger.error(f"Ошибка при подлкючениик СУБД Postgre : {err}")
        return False



async def main():
    redis = await aioredis.from_url("redis://localhost:6379/0")
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=RedisStorage(redis))
    dp.include_routers(user_handler,admin_handler)
    dp.startup.register(on_startup)# подключение к БД
    await bot.delete_webhook(drop_pending_updates=True) # сброс предыдущих апдейтов при перезапуске бота
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    try:
        logger.info("запуск основного цикла main")
        asyncio.run(main()) # отравка запроаса на сервре телеграма на наличеи новых сообщений, обнволений в нашем боте,если ответов нет то функция просто ожидает новых сообщений
        logger.info("окончание работы основного цикла main")
    except KeyboardInterrupt:
        logger.warning("Работа бота была остановлена через скрипт и ctrl + C")
    except Exception as err:
        logger.critical(f"сработала ошибка {err} в теле основного цикла main")

    