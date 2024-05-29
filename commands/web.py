import re
import json
import webbrowser
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process
from .command_base import Command
from utils import load_web_pages

class OpenWebPageCommand(Command):
    command_regexp = re.compile(r'(открой)\s+(.+)', re.IGNORECASE)

    def execute(self) -> None | str:
        match = self.command_regexp.search(self.text)

        page_name = match.group(2).strip().lower()
        web_pages = load_web_pages()
        
        best_match = None
        best_score = 0

        # Ищем наилучшее совпадение для веб-страницы
        for alias, url in web_pages.items():
            match, score = process.extractOne(page_name, [alias])
            if score > best_score:
                best_score = score
                best_match = url
        
        if best_match and best_score > 80: 
            webbrowser.open_new_tab(best_match)
        else:
            return f"Веб-страница {page_name} не найдена"

class GoogleSearchCommand(Command):
    command_regexp = re.compile(r'(загугли)\s+(.+)', re.IGNORECASE)

    def execute(self) -> None:
        match = self.command_regexp.search(self.text)

        query = match.group(2).strip().lower()
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open_new_tab(url)


class YouTubePlayCommand(Command):
    command_regexp = re.compile(r'(включи музыку|музончик)\s+(.+)', re.IGNORECASE)

    def execute(self) -> None | str:
        match = self.command_regexp.search(self.text)

        search_query = match.group(2).strip().lower()
        
        search_url = f"https://www.youtube.com/results?search_query={search_query}"
        
        # Запрашиваем страницу с результатами поиска
        response = requests.get(search_url)
        if response.status_code != 200:
            return "Не удалось выполнить поиск на YouTube."

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', string=re.compile('var ytInitialData'))
        json_text = script_tag.string.split(' = ', 1)[1].rsplit(';', 1)[0]
        data = json.loads(json_text)

        # Поиск видео в структуре данных
        video_id = None
        for content in data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']:
            for item in content['itemSectionRenderer']['contents']:
                if 'videoRenderer' in item:
                    video_id = item['videoRenderer']['videoId']
                    break
            if video_id:
                break
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # Открываем браузер с первым найденным видео
        webbrowser.open_new_tab(video_url)
