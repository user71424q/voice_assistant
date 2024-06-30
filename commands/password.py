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
        Создание таблиц credentials и services в базе данных, если они еще не созданы.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    credential_id INTEGER,
                    service_alias TEXT NOT NULL,
                    FOREIGN KEY (credential_id) REFERENCES credentials (id)
                )
            ''')
            conn.commit()

    def add_credential(self, login: str, password: str) -> int:
        """
        Добавление новых учетных данных в таблицу credentials.
        
        :param login: Логин.
        :param password: Пароль.
        :return: Идентификатор новых учетных данных.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO credentials (login, password) VALUES (?, ?)', (login, password))
            conn.commit()
            return cursor.lastrowid

    def delete_credential(self, credential_id: int) -> None:
        """
        Удаление учетных данных и связанных с ними сервисов.
        
        :param credential_id: Идентификатор учетных данных.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM services WHERE credential_id = ?', (credential_id,))
            cursor.execute('DELETE FROM credentials WHERE id = ?', (credential_id,))
            conn.commit()

    def add_service(self, credential_id: int, service_alias: str) -> int:
        """
        Добавление нового сервиса для учетных данных.
        
        :param credential_id: Идентификатор учетных данных.
        :param service_alias: Псевдоним сервиса.
        :return: Идентификатор нового сервиса.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO services (credential_id, service_alias) VALUES (?, ?)', (credential_id, service_alias))
            conn.commit()
            return cursor.lastrowid

    def delete_service(self, service_id: int) -> None:
        """
        Удаление сервиса.
        
        :param service_id: Идентификатор сервиса.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
            conn.commit()

    def get_credential(self, credential_id: int) -> Optional[Tuple[int, str, str]]:
        """
        Получение учетных данных по их идентификатору.
        
        :param credential_id: Идентификатор учетных данных.
        :return: Кортеж с учетными данными (id, login, password) или None, если учетные данные не найдены.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, login, password FROM credentials WHERE id = ?', (credential_id,))
            return cursor.fetchone()

    def get_services_by_credential(self, credential_id: int) -> List[Tuple[int, int, str]]:
        """
        Получение списка сервисов для учетных данных.
        
        :param credential_id: Идентификатор учетных данных.
        :return: Список кортежей с данными сервисов (id, credential_id, service_alias).
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, credential_id, service_alias FROM services WHERE credential_id = ?', (credential_id,))
            return cursor.fetchall()

    def get_all_credentials(self) -> List[Tuple[int, str, str]]:
        """
        Получение всех учетных данных.
        
        :return: Список кортежей с данными всех учетных данных (id, login, password).
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, login, password FROM credentials')
            return cursor.fetchall()

    def get_all_services(self) -> List[Tuple[int, int, str]]:
        """
        Получение всех сервисов.
        
        :return: Список кортежей с данными всех сервисов (id, credential_id, service_alias).
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, credential_id, service_alias FROM services')
            return cursor.fetchall()
        
    def get_credential_by_service(self, service_alias: str) -> Optional[Tuple[str, str]]:
        """
        Поиск учетных данных (email и password) для сервиса по его псевдониму.
        
        :param service_alias: Псевдоним сервиса.
        :return: Кортеж с данными (email, password) или None, если сервис не найден.
        """
        services = self.get_all_services()
        for service in services:
            if service[2] == service_alias:
                credential_id = service[1]
                credential = self.get_credential(credential_id)
                if credential:
                    return credential[1], credential[2]  # Возвращаем email и password
        return None




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
                        "description": "Название сервиса, для которого ищем пароль. Строго в имменительном падеже",
                    }
                },
                "required": ["service_name"],
            },
        },
    }

    @classmethod
    def execute(cls, service_name: str) -> str:
        credentials = cls.db.get_credential_by_service(service_name)
        if not credentials:
            return "Пароль не найден"

        clipboard.copy(credentials[1])
        time.sleep(0.5)
        clipboard.copy(credentials[0])
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
        if service_name in cls.db.get_all_services():
            return "Такой сервис уже есть"

        # Генерация пароля
        new_password = generate_password()
        login = clipboard.paste()
        if not login:
            return "Некорректное содержимое буфера обмена"
        
        credntial_id = cls.db.add_credential(login, new_password)
        alias_id = cls.db.add_service(credntial_id, service_name)
        if not alias_id:
            return "Ошибка добавления в БД"
        # Копирование пароля в буфер обмена
        clipboard.copy(new_password)
        return "Пароль сгенерирован"
