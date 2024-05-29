import re
import os
import subprocess
from fuzzywuzzy import process
from .command_base import Command
from utils import load_app_paths

class CloseApplicationCommand(Command):
    command_regexp = re.compile(r'(закрой)\s+(.+)', re.IGNORECASE)

    def execute(self) -> str:
        match = self.command_regexp.search(self.text)
        if not match:
            return "Команда не распознана"

        app_name = match.group(2).strip().lower()
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
                subprocess.run(['taskkill', '/f', '/im', app_name_to_kill], check=True)
                return "Закрываю"
            except subprocess.CalledProcessError:
                return "Не удалось закрыть"
        else:
            return "Приложение не найдено"
