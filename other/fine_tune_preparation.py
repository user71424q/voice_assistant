import json
import os

import openai
from dotenv import load_dotenv

from commands import FUNCTIONS, TOOLS

load_dotenv("config/.env")
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Ты являешься голосовым ассистентом и отвечаешь строго в формате JSON. "
    "Твоя задача - качественно определять намерения пользователя и предоставлять соответствующие вызовы команд в ответ. Твои входные данные являются транскрибированным голосом и могут быть слегка искажены. "
    "Так же ты поддерживаешь обычный разговор с пользователем.  "
    "В случае если ты решаешь дать свой собственный ответ ты обязательно вызываешь SaySentenceCommand и передаешь в нее свой ответ. Ко мне обращаться как Хозяин"
)


function_list = TOOLS.copy()


def remove_descriptions(function_list: list) -> list:
    """Удаляет описания параметров и возвращаемые значения из функций для экономии токенов

    Args:
        function_list list: список описаний функций

    Returns:
        list: измененный список функций
    """    
    for function in function_list:
        func = function["function"]
        # if "description" in func:
        #    del func["description"]

        params = func["parameters"]
        if "properties" in params:
            for param in params["properties"].values():
                if "description" in param:
                    del param["description"]
        if "returns" in func:
            del func["returns"]

    return function_list


modified_function_list = remove_descriptions(function_list)
all_function_names = FUNCTIONS.keys()

def get_tool_calls(function_name: str, argument: list | None = None) -> dict:
    """Возвращает форматированные под реальные tool calls объекты по заданной функции и листу аргументов

    Args:
        function_name (str): название функции. Должно принадлежать all_function_names
        argument (list | None, optional): список аргументов, подставляемых в вызов. Defaults to None.

    Returns:
        dict: словарь представляющий собой вызов от gpt api
    """
    assert function_name in all_function_names, "Неправльное имя функции"
    arguments = {}
    for tool in TOOLS:
        if tool["function"]["name"] == function_name:
            argument_names = tool["function"]["parameters"]["properties"]
            if not argument_names:
                assert (
                    argument is None
                ), "Подано лишнее значение аргумента в функцию без аргументов"
            else:
                assert len(argument) == len(argument_names.keys())
                iteration = 0
                for argument_name in argument_names.keys():
                    arguments[argument_name] = argument[iteration]
                    iteration += 1
    return [
        {
            "id": "call_id",
            "type": "function",
            "function": {
                "name": function_name,
                "arguments": json.dumps(arguments, ensure_ascii=False),
            },
        }
    ]


training_list = []


def append_training_entry(prompt: str, function_name: str, arguments: list | None) -> None:
    """Функция с помощью которой можно быстро добавлять записи

    Args:
        prompt (str): команда
        function_name (str): имя функции которая должна быть вызвана
        arguments (list | None): аргументы функции
    """
    global SYSTEM_PROMPT
    training_list.append(
        {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls(function_name, arguments),
                },
            ],
            "tools": modified_function_list,
        }
    )


append_training_entry(
    "спроси у алины как у нее дела", "MessageToTelegramCommand", ["Как дела?", "Алина"]
)
append_training_entry("че там мне алина пишет", "GetRecentTelegramMessages", ["Алина"])
append_training_entry(
    "напиши Алине Что я сделал все домашние дела И теперь буду чилить",
    "MessageToTelegramCommand",
    ["Я сделал все домашние дела, и теперь буду чилить.", "Алина"],
)
append_training_entry("открой телеграм", "LaunchApplicationCommand", ["Telegram"])
append_training_entry(
    "напиши Алине че как там у тебя",
    "MessageToTelegramCommand",
    ["Че как там у тебя?", "Алина"],
)
append_training_entry("нужен новый пароль от почты гугл", "GeneratePasswordCommand", ["Gmail"])
append_training_entry("сгенерируй пароль для киберфорума", "GeneratePasswordCommand", ["киберфорум"])
append_training_entry("сгенерируй мне пароль для моего хс аккаунта", "GeneratePasswordCommand", ["hearthstone"])
append_training_entry("найди сколько стоит последний айфон", "GoogleSearchCommand", ["iphone цена"])
ALL_SERVICE_NAMES_EXAMPLE = [('Vk',), ('Telegram',), ('Google play',), ('Ютуб',), ('hearthstone',)]

training_list.append(
    {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "выдай пароль от телеги"},
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls("get_all_service_names", None),
                },
                { "role": "tool", 
                                            "content": json.dumps({"result": ALL_SERVICE_NAMES_EXAMPLE}, ensure_ascii=False),
                                            "tool_call_id": "call_id"
                                            },
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls("CopyPasswordCommand", ["Telegram"]),
                }
                
            ],
            "tools": modified_function_list,
        }
)
training_list.append(
    {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "скопируй пароль от моего хс аккаунта"},
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls("get_all_service_names", None),
                },
                { "role": "tool", 
                                            "content": json.dumps({"result": ALL_SERVICE_NAMES_EXAMPLE}, ensure_ascii=False),
                                            "tool_call_id": "call_id"
                                            },
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls("CopyPasswordCommand", ["hearthstone"]),
                }
                
            ],
            "tools": modified_function_list,
        }
)
append_training_entry(
    "Приведи несколько способов как можно в питоне отсортировать массив чисел по чётности",
    "SaySentenceCommand",
    [
        "Первый способ - отсортировать массив с помощью sorted с lambda выражением х%2, второй способ - разделить массив на части, отсортировать и затем объединить"
    ],
)
append_training_entry(
    "как варить рис",
    "SaySentenceCommand",
    [
        "Чтобы варить рис, возьмите соотношение 1:2 риса и воды. Промойте рис в холодной воде, затем добавьте его в кастрюлю с водой. Доведите воду до кипения, уменьшите огонь и варите рис под крышкой 15 минут."
    ],
)
append_training_entry(
    "комп в сон хотя стоп я передумал отмена",
    "SaySentenceCommand",
    ["Хозяин, ваш запрос команды был отменен."],
)
append_training_entry("найди как варить рис", "GoogleSearchCommand", ["как варить рис"])
append_training_entry("открой ютуб", "OpenWebPageCommand", ["https://youtube.com"])
append_training_entry("вруби мне hollywoood undead city", "YouTubePlayCommand", ["Hollywood Undead - City [lyrics video]"])
append_training_entry("включи fall out boy young volcanoes", "YouTubePlayCommand", ["fall out boy - young volcanoes [lyrics video]"])
append_training_entry("включи мне despacito", "YouTubePlayCommand", ["despacito"])
append_training_entry("включи первое видео с канала better voice", "YouTubePlayCommand", ["better voice"])
training_file = "config/training_file.jsonl"
with open(training_file, "w", encoding="utf-8") as f:
    for item in training_list:
        json_str = json.dumps(item, ensure_ascii=False)
        f.write(f"{json_str}\n")
# Генерируем валидационные данные
training_list = []
append_training_entry(
    "Спроси у алины скоро ли она", "MessageToTelegramCommand", ["Ты скоро?", "Алина"]
)
# append_training_entry(
#     "пж закрой гребаный хс", "CloseApplicationCommand", ["hearthstone"]
# )
append_training_entry(
    "ну что стартуй стелларис", "LaunchApplicationCommand", ["stellaris"]
)
append_training_entry("сгенерируй мне пароль для моего аккаунта рокет лиги", "GeneratePasswordCommand", ["rocket league"])
append_training_entry("включи на ютубе hollywoood undead day of the dead", "YouTubePlayCommand", ["Hollywood Undead - Day of the dead [lyrics video]"])
append_training_entry("включи на ютубе данза кудуро", "YouTubePlayCommand", ["данза кудуро"])
append_training_entry("пк в сон", "SleepPCCommand", None)
append_training_entry("комп в сон", "SleepPCCommand", None)
append_training_entry("открой гугл", "OpenWebPageCommand", ["https://google.com"])
training_list.append(
    {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "хей красавица, мне нужен пароль для ютубчика"},
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls("get_all_service_names", None),
                },
                { "role": "tool", 
                                            "content": json.dumps({"result": ALL_SERVICE_NAMES_EXAMPLE}, ensure_ascii=False),
                                            "tool_call_id": "call_id"
                                            },
                {
                    "role": "assistant",
                    "tool_calls": get_tool_calls("CopyPasswordCommand", ["Ютуб"]),
                }
                
            ],
            "tools": modified_function_list,
        }
)
validation_file = "config/validation_file.jsonl"
with open(validation_file, "w", encoding="utf-8") as f:
    for item in training_list:
        json_str = json.dumps(item, ensure_ascii=False)
        f.write(f"{json_str}\n")

client = openai.OpenAI()
file = client.files.create(
    file=open(training_file, "rb"),
    purpose="fine-tune",
)
file_id = file.id
print(f"train FileID: {file_id}")
file = client.files.create(
    file=open(validation_file, "rb"),
    purpose="fine-tune",
)
file_id = file.id
print(f"valid FileID: {file_id}")
# ft = client.fine_tuning.jobs.create(
#     model="gpt-3.5-turbo",
#     training_file=file_id,
#     validation_file=...
# )
# print(f"Fine-tuning job created: {ft}")
