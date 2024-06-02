import json
import re, random, string
import pyperclip
from fuzzywuzzy import process
from .command_base import Command


def load_passwords():
    with open("config/passwords.json", "r", encoding="utf-8") as f:
        passwords = json.load(f)
    # Преобразуем конфигурацию в удобный для поиска формат
    res = {}
    for pas, aliases in passwords.items():
        for alias in aliases:
            res[alias.lower()] = pas
    return res


# Генерация пароля
def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


class CopyPasswordCommand(Command):
    command_regexp = re.compile(r"скопируй пароль (от|для)\s+(.+)", re.IGNORECASE)

    def execute(self) -> str:
        match = self.command_regexp.search(self.text)
        if not match:
            return "Команда не распознана"

        service_name = match.group(2).strip().lower()
        passwords = load_passwords()

        best_match, score = process.extractOne(service_name, passwords.keys())

        if score > 80:  # Порог совпадения
            password = passwords[best_match]
            pyperclip.copy(password)
            return "Пароль скопирован."
        else:
            return "Пароль не найден."


class GeneratePasswordCommand(Command):
    command_regexp = re.compile(r"новый пароль (от|для)\s+(.+)", re.IGNORECASE)

    def execute(self) -> str:
        match = self.command_regexp.search(self.text)

        service_name = match.group(2).strip().lower()
        passwords = load_passwords()

        if service_name in passwords.keys():
            return "Такой сервис уже есть."

        # Генерация пароля
        new_password = generate_password()

        # Обновление или добавление записи в JSON-файл
        with open("config/passwords.json", "r", encoding="utf-8") as f:
            full_passwords = json.load(f)
        full_passwords[new_password] = [service_name]
        with open("config/passwords.json", "w", encoding="utf-8") as f:
            json.dump(full_passwords, f, ensure_ascii=False, indent=4)

        # Копирование пароля в буфер обмена
        pyperclip.copy(new_password)
        return "Пароль сгенерирован."
