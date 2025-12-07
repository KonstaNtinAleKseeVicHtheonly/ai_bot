'''файл для генерации запросов от юзеров на AI платформу'''
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from logger.logger_configuration import setup_logging
import os
import httpx
from httpx_socks import AsyncProxyTransport
from app.database.models import async_session
import base64
from datetime import datetime
import uuid
import aiohttp
import aiofiles
from aiogram.types import BufferedInputFile


load_dotenv()
logger = setup_logging()

client = AsyncOpenAI(
            api_key=os.getenv("VSE_GPT_API_KEY"), # ваш ключ в VseGPT после регистрации
            base_url="https://api.vsegpt.ru/v1",# ссылка на api сайта
            )
#proxy_transport = AsyncProxyTransport.from_url(
#     os.getenv('PROXY_IP')
# )# доп настройка под socks5 иначе при прокси на https использовать  http_client=httpx.AsyncClient(proxy='https://P7FQ8t:v9bpPd@168.81.236.73:8000',transport=httpx.HTTPTransport(local_address="0.0.0.0")),

    
def generate_text_request(user_request:str)->str:
    '''передает указанно сообщение на отправку по api в текстовое AI, после - возвращает ответ на запрос'''
    try:
    
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
    

async def generate_text_request_async(user_request:str)->dict[str:str]:
    '''передает указанно сообщение на отправку по api в текстовое AI, после - возвращает ответ на запрос'''
    try:
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
    
    
async def generate_image_request_async(user_request:str, ai_model_name:str)->str:
    '''передает описание картинки на отправку в post запрос после чего возвращает объект 
      Фотографии(обработанной в BufferedInputFile) для дальнейшей отправки юзеру'''
    
    try:
        logger.info(f"начало формирование фотографии по запросу {user_request}")
        # Get API key from environment variable
        api_key = os.environ.get("VSE_GPT_API_KEY")
        if not api_key:
            logger.warning("указан неверный API KEy с сайта VSE GPT либо срок действия истек")
            raise ValueError("VSE_GPT_API_KEY environment variable is not set")

        # Prepare request data
        payload = {
            "model": ai_model_name,
            "prompt": user_request,
            "size": "1024x1024",
            "n": 1,
            "response_format": "b64_json",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Title": "MCP image gen standard 1024x1024"
        }

        url = "https://api.vsegpt.ru/v1/images/generations"
        async with aiohttp.ClientSession(headers=headers) as session:
            logger.info('Отправка запроса на генерацию изображения')
            
            async with session.post(url, json=payload) as response:
                # Check if request was successful
                if response.status == 200:
                    logger.info("Запрос успешен, обработка ответа")
                    
                    # Parse response
                    response_json = await response.json()
                    
                    # Validate response structure
                    if not response_json.get("data") or len(response_json["data"]) == 0:
                        raise ValueError("Некорректный ответ от API: отсутствует data")
                    
                    b64_data = response_json["data"][0].get("b64_json")
                    if not b64_data:
                        raise ValueError("Некорректный ответ от API: отсутствует b64_json")
                    image_bytes = base64.b64decode(b64_data)
                    
                    photo = BufferedInputFile(
                        file=image_bytes,
                        filename="generated_image.png"
                    )
                    return photo
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {response.status} - {error_text}")
                    return False          
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к API: {e}")
        raise Exception(f"Сетевая ошибка: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при генерации изображения: {e}")
        raise Exception(f"Ошибка генерации: {e}")

# async def generate_text_by_image(user_image,user_prompt:str, ai_model):
#     logger.info("приступаю к генерации текста по изображению от юзера")
#     response = await client.chat.completions.create(
#         model=ai_model,
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": user_prompt},
#                     {
#                         "type": "image_url",
#                         "image_url": "https://img-s-msn-com.akamaized.net/tenant/amp/entityid/AA18Lnc8.img?w=1920&h=1080&q=60&m=2&f=jpg",
#                     },
#                 ],
#             }
#         ],
#         max_tokens=400)
#     if response:
    
#     response = response.choices[0]
#     logger.info(f"Ответ успешно получен: {response}")
#     return response
async def encode_image(image_path):
    '''асинхронно'''
    async with aiofiles.open(image_path, 'rb') as image_file:
        image_bytes = await image_file.read()  # читаем bytes
        base64_bytes = base64.b64encode(image_bytes)  # кодируем в base64 bytes
        return base64_bytes.decode('utf-8')

async def generate_vision(path_to_get_image:str, user_request:str, ai_model_name:str)->str:
    '''Преобразует фотку в b64 формат для отправки в post запрос на сервер(безопаснее чем генерить ссылку)'''
    logger.info(f"подготовка отправки запроса по фотке и промпту {user_request}, с AI моделью {ai_model_name}")
    try:
        base_64_image = await encode_image(path_to_get_image)
        # Get API key from environment variable
        api_key = os.environ.get("VSE_GPT_API_KEY")
        if not api_key:
            raise ValueError("VSE_GPT_API_KEY environment variable is not set")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-Title": "MCP image gen standard 1024x1024"
        }

        # Prepare request data
        payload = {
        "model": ai_model_name,  # или "gpt-4-turbo"
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_request
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base_64_image}" # преобразовали каритнку в безопасную b64 кодировку для отправки на сайт
                        }
                    }
                ]
            }
        ],
        "max_tokens": 400}
    
        url = "https://api.vsegpt.ru/v1/images/generations"
        url_2 = "https://api.vsegpt.ru/v1/chat/completions"
        url_3 = "https://api.vsegpt.ru/v1/completions"

        async with aiohttp.ClientSession(headers=headers) as session:
            logger.info('Отправка запроса на генерацию изображения')
            
            async with session.post(url_2, json=payload) as response:
                # Check if request was successful
                if response.status == 200:
                    logger.info("Запрос успешен, обработка ответа")
                    
                    # Parse response
                    response_json = await response.json()
                    if not len(response_json):
                        logger.error(f"вернулся пустой щапрос при vision генерации по запросу :{user_request}")
                        return False
                    logger.warning(f"получен запрос по генерации текста из иозображения : {response_json}")
                    return {'response' : response_json['choices'][0]['message']['content'].strip(), 
                            "token_usage" : response_json['usage']['total_tokens']}
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {response.status} - {error_text}")   
                    return False          
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к API: {e}")
        raise Exception(f"Сетевая ошибка: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при генерации изображения: {e}")
        raise Exception(f"Ошибка генерации: {e}")
                    # рудимент к generate_vision
                    # # Validate response structure
                    # if not response_json.get("data") or len(response_json["data"]) == 0:
                    #     raise ValueError("Некорректный ответ от API: отсутствует data")
                    
                    # b64_data = response_json["data"][0].get("b64_json")
                    # if not b64_data:
                    #     raise ValueError("Некорректный ответ от API: отсутствует b64_json")
                    
                    # # Generate unique filename
                    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    # unique_id = str(uuid.uuid4())[:8]
                    # filename = f"generated_{timestamp}_{unique_id}.png"
                    # filepath = os.path.join(
                    #     rf"D:\vsc\projects\TG_BOTS\AI_API_BOT\app\downloads\pictures\user_{user_tg_id}",
                    #     filename
                    # )
                    # # Ensure directory exists
                    # os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    # # Decode and save image
                    # logger.info(f"Сохранение изображения: {filename}")
                    # try:
                    #     image_data = base64.b64decode(b64_data)
                    #     with open(filepath, "wb") as img_file:
                    #         img_file.write(image_data)
                    # except base64.binascii.Error as e:
                    #     raise ValueError(f"Ошибка декодирования base64: {e}")
                    # logger.warning(f"вот финальный запрос : {response_json}")
                    # # Return both response data and filepath
                    # return {
                    #     "filepath": filepath,
                    #     "filename": filename
                    # }

# метод ессли нужно сохранить сгенерированную фотку на диск:
# async def generate_image_request_async(user_tg_id:int,user_request:str, ai_model_name:str)->str:
#     '''передает описание картинки на отправку по api в текстовое AI, после - сгенерированную по описанию картинку'''
#     try:
#         # Get API key from environment variable
#         api_key = os.environ.get("VSE_GPT_API_KEY")
#         if not api_key:
#             raise ValueError("VSE_GPT_API_KEY environment variable is not set")

#         # Prepare request data
#         payload = {
#             "model": ai_model_name,
#             "prompt": user_request,
#             "size": "1024x1024",
#             "n": 1,
#             "response_format": "b64_json",
#         }

#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {api_key}",
#             "X-Title": "MCP image gen standard 1024x1024"
#         }

#         url = "https://api.vsegpt.ru/v1/images/generations"

#         async with aiohttp.ClientSession(headers=headers) as session:
#             logger.info('Отправка запроса на генерацию изображения')
            
#             async with session.post(url, json=payload) as response:
#                 # Check if request was successful
#                 if response.status == 200:
#                     logger.info("Запрос успешен, обработка ответа")
                    
#                     # Parse response
#                     response_json = await response.json()
                    
#                     # Validate response structure
#                     if not response_json.get("data") or len(response_json["data"]) == 0:
#                         raise ValueError("Некорректный ответ от API: отсутствует data")
                    
#                     b64_data = response_json["data"][0].get("b64_json")
#                     if not b64_data:
#                         raise ValueError("Некорректный ответ от API: отсутствует b64_json")
                    
#                     # Generate unique filename
#                     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                     unique_id = str(uuid.uuid4())[:8]
#                     filename = f"generated_{timestamp}_{unique_id}.png"
#                     filepath = os.path.join(
#                         rf"D:\vsc\projects\TG_BOTS\AI_API_BOT\app\downloads\pictures\user_{user_tg_id}",
#                         filename
#                     )
#                     # Ensure directory exists
#                     os.makedirs(os.path.dirname(filepath), exist_ok=True)
#                     # Decode and save image
#                     logger.info(f"Сохранение изображения: {filename}")
#                     try:
#                         image_data = base64.b64decode(b64_data)
#                         with open(filepath, "wb") as img_file:
#                             img_file.write(image_data)
#                     except base64.binascii.Error as e:
#                         raise ValueError(f"Ошибка декодирования base64: {e}")
#                     logger.warning(f"вот финальный запрос : {response_json}")
#                     # Return both response data and filepath
#                     return {
#                         "filepath": filepath,
#                         "filename": filename
#                     }
#                 else:
#                     error_text = await response.text()
#                     logger.error(f"Ошибка API: {response.status} - {error_text}")
#                     return False          
#     except aiohttp.ClientError as e:
#         logger.error(f"Ошибка сети при запросе к API: {e}")
#         raise Exception(f"Сетевая ошибка: {e}")
#     except Exception as e:
#         logger.error(f"Неожиданная ошибка при генерации изображения: {e}")
#         raise Exception(f"Ошибка генерации: {e}")