#логгирование
import logging
import os
from pathlib import Path


def setup_logging():
    if os.path.exists('/.dockerenv'):
        # Мы в Docker контейнере - используем путь внутри контейнера
        # WORKDIR в Dockerfile = /app, поэтому используем относительный путь
        log_path = '/app/logger/logs_history.log'
        print(f"Docker environment detected. Using log path: {log_path}")
    elif os.path.exists("D:\vsc\projects\TG_BOTS\AI_API_BOT\logger\logs_history.log"):# локальный проект
        log_path = r'D:\vsc\projects\TG_BOTS\AI_API_BOT\logger\logs_history.log'
    else:
        # Мы на сервере (не в контейнере)
        log_path = '/root/bots/AI_API_BOT/logger/logs_history.log'
        print(f"Non-Docker environment. Using log path: {log_path}")
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(r'D:\vsc\projects\TG_BOTS\AI_API_BOT\logger\logs_history.log', encoding='utf-8')      # запись в файл
        ]
    )
    return logging.getLogger(__name__)
