import json
import re
import webbrowser

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process

from .command_base import Command


class OpenWebPageCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "OpenWebPageCommand",
            "description": "Открывает веб-страницу по указанному URL. Пользователь может сказать, например, 'открой YouTube', и команда откроет соответствующую страницу.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Полный URL веб-страницы, которую нужно открыть.",
                    }
                },
                "required": ["text"],
            },
            "returns": {
                "type": ["string", "null"],
                "description": "Сообщение об успешном открытии веб-страницы или о неудаче.",
            },
        },
    }

    @classmethod
    def execute(cls, text: str) -> None:
        webbrowser.open_new_tab(text)


class GoogleSearchCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "GoogleSearchCommand",
            "description": "Открывает поисковую страницу Google с указанным запросом. Пользователь может сказать, например, 'поиск в гугле котики', и команда сформирует и откроет ссылку для поиска в Google по запросу 'котики'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Поисковый запрос для google",
                    }
                },
                "required": ["text"],
            },
            "returns": {"type": "null", "description": "Нет возвращаемого значения."},
        },
    }

    @classmethod
    def execute(cls, text: str) -> None:
        url = f"https://www.google.com/search?q={text}"
        webbrowser.open_new_tab(url)


class YouTubePlayCommand(Command):
    command_description: dict = {
        "type": "function",
        "function": {
            "name": "YouTubePlayCommand",
            "description": "Выполняет поиск видео на YouTube по указанному запросу и открывает первое найденное видео. Пользователь может сказать, например, 'включи музыку', 'включи музончик', 'включи что-то на YouTube', и далее указать, что именно, например, 'hollywood undead city', и команда выполнит поиск и воспроизведение.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Запрос для поиска видео на YouTube.",
                    }
                },
                "required": ["text"],
            },
            "returns": {
                "type": ["string", "null"],
                "description": "Сообщение о результате операции или None в случае успеха.",
            },
        },
    }

    @classmethod
    def execute(cls, text: str) -> None | str:

        search_query = text

        search_url = f"https://www.youtube.com/results?search_query={search_query}"

        # Запрашиваем страницу с результатами поиска
        response = requests.get(search_url)
        if response.status_code != 200:
            return "Не удалось выполнить поиск на YouTube."

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", string=re.compile("var ytInitialData"))
        json_text = script_tag.string.split(" = ", 1)[1].rsplit(";", 1)[0]
        data = json.loads(json_text)

        # Поиск видео в структуре данных
        video_id = None
        for content in data["contents"]["twoColumnSearchResultsRenderer"][
            "primaryContents"
        ]["sectionListRenderer"]["contents"]:
            for item in content["itemSectionRenderer"]["contents"]:
                if "videoRenderer" in item:
                    video_id = item["videoRenderer"]["videoId"]
                    break
            if video_id:
                break
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # Открываем браузер с первым найденным видео
        webbrowser.open_new_tab(video_url)
