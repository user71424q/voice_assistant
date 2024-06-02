import speech_recognition as sr
from commands import get_command
from tts_local import speak

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, phrase_time_limit=30)
        try:
            # TODO проверка голоса
            if True:
                text = recognizer.recognize_google(audio, language="ru-RU")
                print(f"Вы сказали: {text}")
                return text
            else:
                print("Голос не совпадает.")
                return None
        except sr.UnknownValueError:
            print("Не удалось распознать голос.")
            return None
        except sr.RequestError:
            print("Ошибка сервиса распознавания.")
            return None


if __name__ == "__main__":
    speak("Привет, Хозяин")
    while True:
        try:
            command_text = listen()
            if not command_text:
                continue

            command = get_command(command_text.lower())
            if not command:
                continue

            result_to_speak = command.execute()
            if result_to_speak:
                speak(result_to_speak)

        except Exception as e:
            print(e)
