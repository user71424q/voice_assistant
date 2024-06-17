import os
import re
import subprocess

from fuzzywuzzy import process

from utils import load_app_paths

from .command_base import Command


class CloseApplicationCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "CloseApplicationCommand",
            "description": "Закрывает приложение по указанному имени. Пользователь может сказать, например, 'закрой браузер', и команда найдет и закроет приложение.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Имя приложения, которое нужно закрыть.",
                    }
                },
                "required": ["text"],
            },
            "returns": {
                "type": "string",
                "description": "Сообщение об успешном закрытии приложения, неудачной попытке или о том, что приложение не найдено.",
            },
        },
    }

    @classmethod
    def execute(cls, text) -> str:

        app_name = text
        app_paths = load_app_paths()

        best_match = None
        best_score = 0

        # Найти наилучшее совпадение для имени приложения
        for alias, path in app_paths.items():
            match, score = process.extractOne(app_name, [alias])
            if score > best_score:
                best_score = score
                best_match = path

        if best_match and best_score > 80:  # Порог совпадения для аргументов
            try:
                # Закрываем процесс
                app_name_to_kill = os.path.basename(best_match)
                subprocess.run(["taskkill", "/f", "/im", app_name_to_kill], check=True)
                return "Закрываю"
            except subprocess.CalledProcessError:
                return "Не удалось закрыть"
        else:
            return "Приложение не найдено"
