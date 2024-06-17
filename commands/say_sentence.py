import re

from .command_base import Command


class SaySentenceCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "SaySentenceCommand",
            "description": "Функция, которая обрабатывает твой ответ на вопрос или просьбу пользователя",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "твой ответ на текстовый запрос или вопрос пользователя",
                    }
                },
                "required": ["text"],
            },
            "returns": {"type": "string", "description": "Та же самая строка"},
        },
    }

    @classmethod
    def execute(cls, text: str) -> str:
        return text
