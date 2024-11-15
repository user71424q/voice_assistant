import importlib
import json
import os
import pkgutil
import re
from inspect import isclass
from typing import Optional, Type

import httpx
from openai import AsyncOpenAI

from commands.command_base import Command

COMMANDS_DIR = os.path.dirname(__file__)
TOOLS: list = []
FUNCTIONS: dict = {}
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
            command_name = attribute.command_description["function"]["name"]
            # Проверка, что имя функции соответствует шаблону
            if not re.match(r"^[a-zA-Z0-9_-]+$", command_name):
                raise ValueError(f"Invalid function name: {command_name}")
            TOOLS.append(attribute.command_description)
            FUNCTIONS[attribute.command_description["function"]["name"]] = (
                attribute.execute
            )


system_message = [
    {
        "role": "system",
        "content": (
            "Ты являешься голосовым ассистентом и отвечаешь строго в формате JSON. "
            "Твоя задача - качественно определять намерения пользователя и предоставлять соответствующие вызовы команд в ответ. "
            "Так же ты поддерживаешь обычный разговор с пользователем. "
            "В случае если ты решаешь дать свой собственный ответ ты обязательно вызываешь SaySentenceCommand и передаешь в нее свой ответ."
        ),
    }
]


async def execute_command(text: str) -> Optional[str]:
    """Отправляет запрос в gpt для определения вызова команды, затем выполняет вызов нужной команды

    Args:
        text (str): текст команды

    Returns:
        Optional[str]: результат выполнения команды
    """
    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    messages = system_message + [{"role": "user", "content": text}]
    while True:
        try:
            response = await client.chat.completions.create(
                model="ft:gpt-4o-mini-2024-07-18:personal::A1tzSTN0",
                messages=messages,
                tools=TOOLS,
                tool_choice="required",  # как минимум 1 функция вызывается
            )
            response_message = response.choices[0].message
            print(response_message)
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = FUNCTIONS[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(**function_args)
                    if not "Command" in function_name:
                        messages.append(response_message)
                        messages.append({ "role": "tool", 
                                            "content": json.dumps({"result": function_response}, ensure_ascii=False),
                                            "tool_call_id": tool_call.id
                                            }
                                        )
                    else:
                        return function_response
        except Exception as e:
            print(f"Ошибка при выполнении команды: {e}")
            return None
