import os
import asyncio
from telethon.sync import TelegramClient
from dotenv import load_dotenv
from .command_base import Command
import nest_asyncio

nest_asyncio.apply()

# Загружаем переменные окружения
load_dotenv(dotenv_path="config/.env")

users = {
        "алина": "id63638",
        "алине": "id63638",
        "арине": "id63638",
        "арина": "id63638",
        # Добавьте другие соответствия имени и chat id здесь
    }

class MessageToTelegramCommand(Command):

    command_description: dict = {
        "type": "function",
        "function": {
            "name": "MessageToTelegramCommand",
            "description": "Отправляет сообщение указанному пользователю в Telegram. Пользователь может сказать, например, 'Напиши алине привет' или `спроси у алины`, если хочет задать вопрос.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Текст сообщения, которое нужно отправить. Тебе КАТЕГОРИЧЕСКИ запрещено менять текст который тебя просят отправить, за исключением максимум знаков препинания. Никакой перестановки слов или изменения смысла",
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Имя адресата сообщения строго в именительном падеже.",
                    },
                },
                "required": ["text", "recipient"],
            },
            "returns": {
                "type": ["string", "null"],
                "description": "Сообщение об успешной отправке сообщения или о неудаче.",
            },
        },
    }


    @staticmethod
    async def send_message_async(api_id, api_hash, text, recipient):
        async with TelegramClient('config/bot', api_id, api_hash, device_model="desktop app", app_version="5.1.5", system_version="windows 12") as client:
            if recipient.lower() in users:
                user_id = users[recipient.lower()]
                await client.send_message(user_id, text)
                return "Сообщение успешно отправлено."
            else:
                return f"Пользователь с именем {recipient} не найден."

    @classmethod
    def execute(cls, text: str, recipient: str) -> None | str:
        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")
        #phone = os.getenv("TELEGRAM_PHONE")
        #password = os.getenv("TELEGRAM_PASSWORD")
            

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(cls.send_message_async(api_id, api_hash, text, recipient))
        
        return result


class GetRecentTelegramMessages(Command):
    

    command_description: dict = {
        "type": "function",
        "function": {
            "name": "GetRecentTelegramMessages",
            "description": "Получает последние сообщения от указанного пользователя в Telegram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Имя пользователя для получения сообщений строго в именительном падеже.",
                    },
                },
                "required": ["recipient"],
            },
            "returns": {
                "type": ["string", "null"],
                "description": "Последние сообщения от указанного пользователя или сообщение о неудаче.",
            },
        },
    }

    @staticmethod
    async def get_messages_async(api_id, api_hash, recipient, limit = 5):
        async with TelegramClient('config/bot', api_id, api_hash, device_model="desktop app", app_version="5.1.5", system_version="windows 12") as client:
            if recipient.lower() in users:
                username = users[recipient.lower()]
                user = await client.get_entity(username)
                messages = await client.get_messages(user, limit=limit)
                return ".\n".join([message.message for message in messages[::-1]])
            else:
                return f"Пользователь с именем {recipient} не найден."

    @classmethod
    def execute(cls, recipient: str) -> None | str:
        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")
        # phone = os.getenv("TELEGRAM_PHONE")
        # password = os.getenv("TELEGRAM_PASSWORD")

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(cls.get_messages_async(api_id, api_hash, recipient))

        return result