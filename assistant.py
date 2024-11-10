import asyncio
import concurrent.futures
from time import sleep
import queue
import json
import io
import sounddevice as sd
import speech_recognition as sr
import numpy as np
import whisper
import vosk
from dotenv import load_dotenv

from commands import execute_command
from tts.tts_salute import speak

env_path = "config/.env"
load_dotenv(dotenv_path=env_path)


class SpeechRecognizer:
    def __init__(self, model_path='model/russian_small', pause_threshold=0.25):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.non_speaking_duration = pause_threshold
        self.executor = concurrent.futures.ThreadPoolExecutor()

        # Vosk specific initialization
        self.q = queue.Queue()
        self.model_path = model_path
        self.model = vosk.Model(model_path)
        self.vosk_recognizer = vosk.KaldiRecognizer(self.model, 16000)

    def audio_callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def start_listening(self):
        # Start audio stream with Vosk
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=self.audio_callback, device=self.microphone.device_index):
            self.listen()

    def listen(self):
        audio_buffer = io.BytesIO()
        while True:
            data = self.q.get()
            audio_buffer.write(data)
            if self.vosk_recognizer.AcceptWaveform(data):
                if self.extract_command(self.vosk_recognizer.Result()):
                    audio_buffer.seek(0)  # Rewind to the beginning of the buffer
                    audio_data = sr.AudioData(audio_buffer.read(), sample_rate=16000, sample_width=2)
                
                    self.executor.submit(self.recognize_and_process, audio_data)
                    
                audio_buffer.seek(0)
                audio_buffer.truncate(0)  # Clear the buffer for next audio

    def recognize_and_process(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {text}")
            self.process_command(text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass

    def process_command(self, command_text: str):
        if not command_text:
            return
        command = self.extract_command(command_text)
        if command:
            result_to_speak = asyncio.run(execute_command(command))
            if result_to_speak:
                self.executor.submit(speak, result_to_speak)

    def extract_command(self, command_text: str, assistant_name="Клара"):
        command_text = command_text.lower()
        assistant_name = assistant_name.lower()
        if assistant_name in command_text:
            return command_text.split(assistant_name, 1)[1].strip()
        return ""


if __name__ == "__main__":
    speak("Привет Хозяин")
    recognizer = SpeechRecognizer()
    recognizer.start_listening()

    try:
        while True:
            sleep(1)  # Основной поток продолжает работу
    except KeyboardInterrupt:
        print("Программа завершена.")
