from .command_base import Command
import os, importlib, pkgutil
from inspect import isclass
from typing import List, Type, Optional

COMMANDS_DIR = os.path.dirname(__file__)
ALL_COMMANDS: List[Type[Command]] = []
# Динамическое сканирование папки и импорт модулей
for module_info in pkgutil.iter_modules([COMMANDS_DIR]):
    if module_info.ispkg:
        continue
    module = importlib.import_module(f"commands.{module_info.name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        # Проверка, что это класс и он является наследником Command
        if (
            isclass(attribute)
            and issubclass(attribute, Command)
            and attribute is not Command
        ):
            ALL_COMMANDS.append(attribute)


def get_command(text: str) -> Optional[Type[Command]]:
    for command_class in ALL_COMMANDS:
        if command_class.command_regexp.search(text):
            return command_class(text)
    return None
