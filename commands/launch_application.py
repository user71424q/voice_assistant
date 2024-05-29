import os
from fuzzywuzzy import process
from .command_base import Command
from utils import load_app_paths
import re

class LaunchApplicationCommand(Command):
    command_regexp = re.compile(r'(запусти|стартани)\s+(.+)', re.IGNORECASE)

    def execute(self) -> str:
        match = self.command_regexp.search(self.text)

        app_name_fragment = match.group(2).strip().lower()
        app_paths = load_app_paths()
        
        # Найти наилучшее совпадение для имени приложения
        best_match, score = process.extractOne(app_name_fragment, app_paths.keys())
        
        if score > 80:  # Порог совпадения для аргументов
            app_path = app_paths[best_match]
            os.startfile(app_path)
            return f"Запускаю {best_match}"
        else:
            return f"Приложение '{app_name_fragment}' не найдено"