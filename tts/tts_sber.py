import io
import time
import uuid
import wave

import numpy as np
import requests
import sounddevice as sd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Token:
    authdata: str = (
        "ТОКЕН"
    )
    token: str | None = None
    expires_in: int | None = None

    @staticmethod
    def get_token() -> str:
        # Проверяем, если токен отсутствует или истекло время его действия, обновляем токен
        if Token.token is None or (
            Token.expires_in is not None
            and Token.expires_in < int(time.time() * 1000) - 2000
        ):
            Token.token, Token.expires_in = Token.__request_for_new_token__()
        return Token.token

    @staticmethod
    def __request_for_new_token__() -> tuple[str, int]:
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            "Authorization": f"Basic {Token.authdata}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"scope": "SALUTE_SPEECH_PERS"}  # Укажите необходимый scope здесь

        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            response_data = response.json()
            # expires_at указывает на Unix-время завершения действия Access Token в миллисекундах
            return response_data["access_token"], response_data["expires_at"]
        else:
            raise Exception("Failed to obtain token")


def speak(text: str):
    # Получаем токен из класса Token
    token = Token.get_token()

    # URL для синтеза речи
    url = "https://smartspeech.sber.ru/rest/v1/text:synthesize?voice=Ost_24000"

    # Заголовки запроса
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/text"}

    # Выполняем POST запрос
    response = requests.post(url, headers=headers, data=text, verify=False)

    # Проверяем успешность запроса
    if response.status_code == 200:
        with wave.open(io.BytesIO(response.content), "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            audio_data = wav_file.readframes(wav_file.getnframes())
            audio = np.frombuffer(audio_data, dtype=np.int16)
            sd.play(audio, samplerate=sample_rate)
    else:
        print(response)
        raise Exception("Failed to synthesize speech")
