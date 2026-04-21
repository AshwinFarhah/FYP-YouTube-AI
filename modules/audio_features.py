import librosa
import numpy as np

def load_audio(audio_path):
    y, sr = librosa.load(audio_path)
    return y, sr


def compute_loudness(y):
    rms = librosa.feature.rms(y=y)
    return np.mean(rms)


def compute_sound_density(y, sr):
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    duration = len(y) / sr
    return len(onsets) / duration