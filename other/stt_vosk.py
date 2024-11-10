import vosk
import sounddevice as sd
import queue
import json

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))

def recognize(model_path='model/russian_small'):
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result).get('text', '')
            if text:
                print(f"Вы сказали: {text}")

if __name__ == "__main__":
    model_path = "model/russian_small"
    # Ensure the model directory exists
    import os
    if not os.path.exists(model_path):
        print(f"Model path {model_path} does not exist. Please download the model and place it in the correct directory.")
        exit(1)

    print("Запуск распознавания речи с использованием модели Vosk...")
    # Setup audio stream
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        recognize(model_path)
