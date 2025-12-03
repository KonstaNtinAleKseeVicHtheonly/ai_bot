#логгирование
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(r'D:\vsc\projects\TG_BOTS\AI_API_BOT\logger\logs_history.log', encoding='utf-8')      # запись в файл
        ]
    )
    return logging.getLogger(__name__)
