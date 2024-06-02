from RUTTS import TTS
from ruaccent import RUAccent

tts = TTS("TeraTTS/glados2-g2p-vits", add_time_to_end=0.8)
accentizer = RUAccent()
accentizer.load(
    omograph_model_size="turbo2", use_dictionary=True, workdir="C:\\pet\\voice\\model"
)


def speak(text: str):
    text = accentizer.process_all(text)
    tts(text, play=True, lenght_scale=1.3)
