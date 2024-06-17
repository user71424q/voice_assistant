import io
import json

import librosa
import numpy as np
from scipy.spatial.distance import euclidean


def load_app_paths():
    with open("config/app_paths.json", "r", encoding="utf-8") as f:
        paths = json.load(f)
    # Преобразуем конфигурацию в удобный для поиска формат
    app_paths = {}
    for path, aliases in paths.items():
        for alias in aliases:
            app_paths[alias.lower()] = path
    return app_paths


def is_voice_match(audio_data: bytes, sample_path: str, threshold: float = 100) -> bool:
    pass
