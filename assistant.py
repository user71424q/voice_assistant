import concurrent.futures
import asyncio
from time import sleep
import speech_recognition as sr
from dotenv import load_dotenv
from commands import execute_command
from tts.tts_salute import speak

env_path = "config/.env"
load_dotenv(dotenv_path=env_path)

class SpeechRecognizer:
    def __init__(self, energy_threshold=300, pause_threshold=0.20):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.non_speaking_duration = pause_threshold
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def start_listening(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        self.executor.submit(self.listen)

    def listen(self):
        while True:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, phrase_time_limit=10)
                self.executor.submit(self.recognize_and_process, audio)
    
    def recognize_and_process(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {text}")
            self.process_command(text)
        except sr.UnknownValueError:
            print("Не удалось распознать голос.")
        except sr.RequestError:
            print("Ошибка сервиса распознавания.")
    
    def process_command(self, command_text):
        if not command_text or not self.is_assistant_called(command_text):
            return
        command = self.extract_command(command_text)
        if command:
            result_to_speak = asyncio.run(execute_command(command))
            if result_to_speak:
                self.executor.submit(speak, result_to_speak)

    def is_assistant_called(self, command_text, assistant_name="Клара"):
        return assistant_name.lower() in command_text.lower()

    def extract_command(self, command_text, assistant_name="Клара"):
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
            sleep(1) # Основной поток продолжает работу
    except KeyboardInterrupt:
        print("Программа завершена.")
