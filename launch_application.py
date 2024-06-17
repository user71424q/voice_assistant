import os
import re
import subprocess

from fuzzywuzzy import process

from utils import load_app_paths

from .command_base import Command


class LaunchApplicationCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "LaunchApplicationCommand",
            "description": "Запускает приложение по указанному имени. Пользователь может сказать, например, 'запусти/открой калькулятор', и команда найдет и запустит приложение.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Имя приложения, которое нужно запустить.",
                    }
                },
                "required": ["text"],
            },
            "returns": {
                "type": "string",
                "description": "Сообщение об успешном запуске приложения или о том, что приложение не найдено.",
            },
        },
    }

    @classmethod
    def execute(cls, text: str) -> str:

        app_name = text
        app_paths = load_app_paths()

        # Найти наилучшее совпадение для имени приложения
        best_match, score = process.extractOne(app_name, app_paths.keys())

        if score > 80:  # Порог совпадения для аргументов
            app_path = app_paths[best_match]
            work_dir = os.path.dirname(app_path)
            subprocess.Popen([app_path], cwd=work_dir)
            return f"Запускаю {best_match}"
        else:
            return f"Приложение '{app_name}' не найдено"
