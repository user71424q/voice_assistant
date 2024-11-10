import random
import sqlite3
import string
import time
from typing import List, Optional, Tuple

import clipboard

from commands.command_base import Command


class PasswordManager:
    def __init__(self, db_name: str):
        """
        Инициализация PasswordManager с именем базы данных.
        
        :param db_name: Имя SQLite файла базы данных.
        """
        self.db_name = db_name
        self._create_tables()

    def _create_tables(self):
        """
        Создание таблицы credentials в базе данных, если она еще не создана.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    service_name TEXT PRIMARY KEY,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_credential(self, service_name: str, login: str, password: str) -> int:
        """
        Добавление новых учетных данных в таблицу credentials.
        
        :param service_name: Название сервиса.
        :param login: Логин.
        :param password: Пароль.
        :return: Идентификатор новых учетных данных.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO credentials (service_name, login, password) VALUES (?, ?, ?)', (service_name, login, password))
            conn.commit()
            return cursor.lastrowid

    def delete_credential(self, service_name: str) -> None:
        """
        Удаление учетных данных.
        
        :param service_name: Идентификатор учетных данных.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM credentials WHERE service_name = ?', (service_name,))
            conn.commit()

    def get_credential_by_service_name(self, service_name: str) -> Optional[Tuple[str, str, str]]:
        """
        Получение учетных данных по их идентификатору (названию сервиса).
        
        :param service_name: Идентификатор учетных данных.
        :return: Кортеж с учетными данными (service_name, login, password) или None, если учетные данные не найдены.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT service_name, login, password FROM credentials WHERE service_name = ?', (service_name,))
            return cursor.fetchone()

    def get_all_credentials(self) -> List[Tuple[str, str, str]]:
        """
        Получение всех учетных данных.
        
        :return: Список кортежей с данными всех учетных данных (id, login, password).
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT service_name, login, password FROM credentials')
            return cursor.fetchall()

    def get_all_service_names(self) -> List[Tuple[str]]:
        """
        Получение всех сервисов.
        
        :return: Список кортежей с названиями всех сервисов (service_name).
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT service_name FROM credentials')
            return cursor.fetchall()
        




# Генерация пароля
def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


class CopyPasswordCommand(Command):
    db = PasswordManager("config/passwords.db")
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "CopyPasswordCommand",
            "description": "Ищет сохраненный пароль для указанного сервиса",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Название сервиса, для которого ищем пароль. Подается СТРОГО ключ, существующий в базе данных, без проверки метод не вызывается",
                    }
                },
                "required": ["service_name"],
            },
        },
    }

    @classmethod
    def execute(cls, service_name: str) -> str:
        credentials = cls.db.get_credential_by_service_name(service_name)
        if not credentials:
            return "Пароль не найден"

        clipboard.copy(credentials[2])
        time.sleep(0.5)
        clipboard.copy(credentials[1])
        return "Пароль скопирован"


class GeneratePasswordCommand(Command):
    db = PasswordManager("config/passwords.db")
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "GeneratePasswordCommand",
            "description": "Генерирует пароль для указанного сервиса",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Название сервиса, для которого генерируем пароль. Строго в имменительном падеже",
                    }
                },
                "required": ["service_name"],
            },
        },
    }

    @classmethod
    def execute(cls, service_name: str) -> str:

        # Генерация пароля
        new_password = generate_password()
        login = clipboard.paste()
        if not login:
            return "Некорректное содержимое буфера обмена"
        
        credential_id = cls.db.add_credential(service_name, login, new_password)
        if not credential_id:
            return "Ошибка добавления в БД"
        if credential_id == 0:
            return "Такой сервис уже существует, пароль не сгенерирован"
        # Копирование пароля в буфер обмена
        clipboard.copy(new_password)
        return "Пароль сгенерирован"
    
    
class ListServiceNames(Command):
    db = PasswordManager("config/passwords.db")
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "get_all_service_names",
            "description": "Возвращает список всех названий сервисов (ключей БД с паролями)",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }

    @classmethod
    def execute(cls) -> list:
        credentials = cls.db.get_all_service_names()
        return credentials
