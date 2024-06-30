import os
import re
import subprocess

import psutil
from fuzzywuzzy import process
from transliterate import translit

from commands.command_base import Command
from utils import load_app_paths


class CloseApplicationCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "CloseApplicationCommand",
            "description": "Закрывает приложение по указанному имени. Пользователь может сказать, например, 'закрой браузер', и команда найдет и закроет приложение.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Имя приложения, которое нужно закрыть.",
                    }
                },
                "required": ["app_name"],
            },
        },
    }

    @classmethod
    def execute(cls, app_name: str) -> str:
        """
        Закрывает программу на компьютере по её названию.

        Args:
            app_name (str): Название программы, которую необходимо закрыть.

        Returns:
            str: Сообщение о результате выполнения.
        """
        # Получаем список всех активных процессов
        all_processes = {p.info['name']: p.info['name'] for p in psutil.process_iter(['name'])}

        # Добавляем транслитерацию для обработки русских названий
        transliterated_name = translit(app_name, 'ru', reversed=True)

        # Нечеткий поиск наилучшего совпадения по оригинальному и транслитерированному имени
        candidates = list(all_processes.keys())
        best_match, best_score = process.extractOne(app_name, candidates)
        trans_best_match, trans_best_score = process.extractOne(transliterated_name, candidates)

        # Выбираем лучшее совпадение из обоих вариантов
        if trans_best_score > best_score:
            best_match, best_score = trans_best_match, trans_best_score

        if best_match and best_score > 90:  # Порог совпадения для аргументов
            try:
                # Закрываем все процессы с найденным именем
                subprocess.run(["taskkill", "/f", "/im", best_match], check=True)
                return "Закрываю"
            except subprocess.CalledProcessError:
                return "Не удалось закрыть"
        else:
            return "Приложение не найдено"
