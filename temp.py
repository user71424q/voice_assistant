import numpy as np
import librosa
from pydub import AudioSegment
from scipy.spatial.distance import cosine
import speech_recognition as sr

def audio_to_array(audio) -> np.ndarray:
    """
    Конвертирует аудио объект из speech_recognition в numpy массив.
    
    :param audio: Аудио объект из speech_recognition.
    :return: Кортеж из numpy массива и частоты дискретизации.
    """
    audio_data = audio.get_raw_data()
    audio_segment = AudioSegment(data=audio_data, sample_width=2, frame_rate=16000, channels=1)
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
    
    # Нормализация аудио данных
    samples = samples / np.iinfo(np.int16).max
    
    return samples, audio_segment.frame_rate

def is_voice_match(sample_audio: np.ndarray, sample_sr: int, input_audio: np.ndarray, input_sr: int, threshold: float = 0.5) -> bool:
    """
    Сравнивает два аудио по их голосовым отпечаткам и возвращает True, если они совпадают.

    :param sample_audio: Аудио массив образца голоса.
    :param sample_sr: Частота дискретизации образца голоса.
    :param input_audio: Аудио массив для аутентификации.
    :param input_sr: Частота дискретизации аудио для аутентификации.
    :param threshold: Пороговое значение косинусного расстояния для определения совпадения голосов.
    :return: True, если голоса совпадают, иначе False.
    """
    
    # Преобразуем аудио в мел-спектрограммы
    sample_mfcc = librosa.feature.mfcc(y=sample_audio, sr=sample_sr, n_mfcc=13)
    input_mfcc = librosa.feature.mfcc(y=input_audio, sr=input_sr, n_mfcc=13)

    # Усредняем MFCC по временной оси, чтобы получить голосовой отпечаток
    sample_mfcc_mean = np.mean(sample_mfcc, axis=1)
    input_mfcc_mean = np.mean(input_mfcc, axis=1)
    
    # Рассчитываем косинусное расстояние между голосовыми отпечатками
    similarity = 1 - cosine(sample_mfcc_mean, input_mfcc_mean)
    
    # Если сходство выше порогового значения, голоса считаются совпадающими
    return similarity #> threshold

# Пример использования функции
if __name__ == "__main__":
    # # Загрузка образца голоса
    # sample_audio_path = "config/sample.wav"
    # sample_audio, sample_sr = librosa.load(sample_audio_path, sr=None)
    
    # recognizer = sr.Recognizer()
    # recognizer.pause_threshold = 0.3
    # recognizer.non_speaking_duration = 0.3
    
    # while True:
    #     with sr.Microphone() as source:
    #         print("Listening...")
    #         audio = recognizer.listen(source, phrase_time_limit=10)
        
    #     input_audio, input_sr = audio_to_array(audio)
        
    #     # Проверка совпадения голосов
    #     match = is_voice_match(sample_audio, sample_sr, input_audio, input_sr)
    #     print(f"Голоса совпадают: {match}")
    import pyperclip
    content = pyperclip.paste()
    print(content)
