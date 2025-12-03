'''файл для генерации запросов от юзеров на AI платформу'''
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from logger.logger_configuration import setup_logging
import os
import httpx
from httpx_socks import AsyncProxyTransport

load_dotenv()
logger = setup_logging()



def generate_text_request(user_request:str)->str:
    '''передает указанно сообщение на отправку по api в текстовое AI, после - возвращает ответ на запрос'''
    try:
        client = OpenAI(
            api_key=os.getenv("VSE_GPT_API_KEY"), # ваш ключ в VseGPT после регистрации
            base_url="https://api.vsegpt.ru/v1",# ссылка на api сайта
            )
    
        messages = []
        #messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": user_request})

        logger.info(f"приступаю к отправке запроса {user_request}")
        response_big = client.chat.completions.create(
            model='openai/gpt-4o-mini', # id модели из списка моделей - можно использовать OpenAI, Anthropic и пр. меняя только этот параметр
            messages=messages,
            temperature=0.7,
            n=1,
            max_tokens=3000, # максимальное число ВЫХОДНЫХ токенов. Для большинства моделей не должно превышать 4096
            extra_headers={ "X-Title": "My App" }, # опционально - передача информация об источнике API-вызова
        )
        logger.info("Ответ успешно получен")
        #print("Response BIG:",response_big)
        response = response_big.choices[0].message.content
        return response
    except Exception as err:
        logger.error(f'Возника ошбка при отпрвке запроса на AI : {err}')
        return f"Ошибка в запросе : {err}"
    

proxy_transport = AsyncProxyTransport.from_url(
    os.getenv('PROXY_IP')
)# доп настройка под socks5 иначе при прокси на https использовать  http_client=httpx.AsyncClient(proxy='https://P7FQ8t:v9bpPd@168.81.236.73:8000',transport=httpx.HTTPTransport(local_address="0.0.0.0")),

async def generate_text_request_async(user_request:str)->dict[str:str]:
    '''передает указанно сообщение на отправку по api в текстовое AI, после - возвращает ответ на запрос'''
    try:
        client = AsyncOpenAI(
            api_key=os.getenv("VSE_GPT_API_KEY"), # ваш ключ в VseGPT после регистрации
            base_url="https://api.vsegpt.ru/v1",# ссылка на api сайта
            )
    
        messages = []
        messages.append({"role": "system", "content": "Отвечай лаконично и емко"})
        messages.append({"role": "user", "content": user_request})

        logger.info(f"приступаю к отправке запроса {user_request}")
        response_big = await client.chat.completions.create(
            model='openai/gpt-4o-mini', # id модели из списка моделей - можно использовать OpenAI, Anthropic и пр. меняя только этот параметр
            messages=messages,
            temperature=1,
            n=1,
            max_tokens=3000, # максимальное число ВЫХОДНЫХ токенов. Для большинства моделей не должно превышать 4096
            extra_headers={ "X-Title": "My App" }, # опционально - передача информация об источнике API-вызова
        )
        logger.info(f"Ответ успешно получен : {response_big}")

        response = response_big.choices[0].message.content
        return {'response':response, 'token_usage': response_big.usage.total_tokens}
    except Exception as err:
        if response:
            logger.error(f'Возника ошбка при отпрвке запроса на AI связанная с ответом: {err} {response}')
            return f"Ошибка в запросе : {err} {response}"
        logger.error(f'Возника ошбка при отпрвке запроса на AI : {err}')
        return f"Ошибка в запросе : {err} {response}"
    


async def generate_image_request_async(user_request:str)->str:
    '''передает указанно сообщение на отправку по api в текстовое AI, после - возвращает ответ на запрос'''
    try:
        client = AsyncOpenAI(
            api_key=os.getenv("VSE_GPT_API_KEY"), # ваш ключ в VseGPT после регистрации
            base_url="https://api.vsegpt.ru/v1",# ссылка на api сайта
            )
    
        messages = []
        messages.append({"role": "system", "content": "Отвечай лаконично и емко"})
        messages.append({"role": "user", "content": user_request})

        logger.info(f"приступаю к отправке запроса {user_request}")
        response_big = await client.chat.completions.create(
            model = "vis-openai/gpt-5-nano",
            messages=messages,
            temperature=1,
            n=1,
            max_tokens=3000, # максимальное число ВЫХОДНЫХ токенов. Для большинства моделей не должно превышать 4096
            extra_headers={ "X-Title": "My App" }, # опционально - передача информация об источнике API-вызова
        )
        logger.info("Ответ успешно получен")

        response = response_big.choices[0].message.content
        return response
    except Exception as err:
        if response:
            logger.error(f'Возника ошбка при отпрвке запроса на AI связанная с ответом: {err} {response}')
            return f"Ошибка в запросе : {err} {response}"
        logger.error(f'Возника ошбка при отпрвке запроса на AI : {err}')
        return f"Ошибка в запросе : {err} {response}"
    