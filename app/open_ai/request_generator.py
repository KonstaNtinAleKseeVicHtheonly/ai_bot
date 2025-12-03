'''файл для генерации запросов от юзеров на AI платформу'''
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv
from logger.logger_configuration import setup_logging
import os
import aiohttp
load_dotenv()
logger = setup_logging()



async def request_generator(user_message:str):
    logger.info("пошла обработка асинхронного запроса")
    current_headers = {
        "Authorization": os.getenv("VSE_GPT_API_KEY"),  # Замените на ваш ключ API
        "Content-Type": "application/json"}
    current_data = {
        "model": "sonet_3.7",  # Укажите нужную модель
        "prompt": user_message,
        "max_tokens": 1000,  # Настроить по необходимости
        "temperature": 0.7}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.vsegpt.ru/v1/chat/completions',
            json=current_data,
            headers=current_headers) as response:
            logger.info("ответ успешно получен")
            result = await response.text()
            logger.info(f"получен успешный ответ на запрос {user_message} : {result}")
            return result


