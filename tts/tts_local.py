import sounddevice as sd
import torch

device = torch.device("cpu")
torch.set_num_threads(4)
local_file = "model/ru_v3_1.pt"  # или ru_v3, ru_v4
model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)
sample_rate = 24000
speaker = "kseniya"


def speak(text: str):
    audio = model.apply_tts(text=text, speaker=speaker, sample_rate=sample_rate)
    audio_np = audio.cpu().numpy()
    sd.play(audio_np, sample_rate)
