from dotenv import load_dotenv
from logger.logger_configuration import setup_logging
import os
import aiohttp
from openai import OpenAI
load_dotenv()
logger = setup_logging()





def base_request():
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Как твои дела?"},
        ],
        stream=False
    )
    return response.choices[0].message.content


async def check_balance():
    headers = {
        "Authorization": os.getenv("DEEPSEEK_API_KEY")
    }
    logger.info("запрос отправлен")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://api.deepseek.com/user/balance',
            headers=headers
        ) as response:
            if response.status == 200:
                logger.info("успешно получен ответ")
                balance_info = await response.json()
                logger.warning(f"инфа о балансе {balance_info}")
                return balance_info
            else:
                return f"Ошибка: {response.status}"
            
async def test_api_key():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=data
        ) as response:
            return await response.json()