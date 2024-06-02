import json
import librosa
import numpy as np
from scipy.spatial.distance import cdist

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



def get_mfcc(audio_path):
    y, sr = librosa.load(audio_path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_scaled = np.mean(mfcc.T, axis=0)
    return mfcc_scaled

def is_voice_match(sample_path, test_audio, threshold=50):
    # Получаем MFCC для образца
    sample_mfcc = get_mfcc(sample_path)
    
    # Получаем MFCC для тестового аудио
    with open("temp_audio.wav", "wb") as f:
        f.write(test_audio.get_wav_data())
    test_mfcc = get_mfcc("temp_audio.wav")
    
    # Сравниваем MFCC с использованием евклидова расстояния
    distance = cdist([sample_mfcc], [test_mfcc], metric='euclidean')[0][0]
    print(distance)
    return distance < threshold

