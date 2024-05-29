from RUTTS import TTS
from ruaccent import RUAccent
import json
# Инициализация движка синтеза речи

tts = TTS("TeraTTS/glados2-g2p-vits", add_time_to_end=0.8)
accentizer = RUAccent()
accentizer.load(omograph_model_size='turbo2', use_dictionary=True, workdir='C:\\pet\\voice\\model')

def speak(text: str):
    text = accentizer.process_all(text)
    tts(text, play=True, lenght_scale=1.3)

def load_app_paths():
    with open('config/app_paths.json', 'r', encoding='utf-8') as f:
        paths = json.load(f)
    # Преобразуем конфигурацию в удобный для поиска формат
    app_paths = {}
    for path, aliases in paths.items():
        for alias in aliases:
            app_paths[alias.lower()] = path
    return app_paths



def load_web_pages():
    with open('config/web_pages.json', 'r', encoding='utf-8') as f:
        pages = json.load(f)
    # Преобразуем конфигурацию в удобный для поиска формат
    web_pages = {}
    for url, aliases in pages.items():
        for alias in aliases:
            web_pages[alias.lower()] = url
    return web_pages