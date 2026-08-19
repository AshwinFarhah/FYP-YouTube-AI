import librosa
import numpy as np

from modules.config import *


# =====================================================
# LOAD AUDIO
# =====================================================

def load_audio(audio_path):

    if audio_path is None:

        return np.array([]), TARGET_SAMPLE_RATE

    try:

        y, sr = librosa.load(
            audio_path,
            sr=TARGET_SAMPLE_RATE,
            mono=True
        )

        return y, sr

    except Exception as e:

        print(
            "⚠️ Failed to load audio:",
            e
        )

        return np.array([]), TARGET_SAMPLE_RATE


# =====================================================
# AUDIO FEATURE EXTRACTION
# =====================================================

def extract_audio_features(audio_path):

    y, sr = load_audio(audio_path)

    # =================================================
    # No audio / failed audio
    # =================================================

    if len(y) == 0:

        print(
            "⚠️ Audio features set to zero."
        )

        return {

            "loudness": 0.0,

            "rms_energy": 0.0,

            "sound_density": 0.0,

            "tempo": 0.0,

            "avg_pitch": 0.0,

            "pitch_variation": 0.0,

            "audio_variation": 0.0,

            "spectral_centroid": 0.0,

            "spectral_bandwidth": 0.0,

            "spectral_rolloff": 0.0,

            "spectral_contrast": 0.0,

            "zero_crossing_rate": 0.0,

            "harmonic_ratio": 0.0,

            "percussive_ratio": 0.0,

            "audio_repetition": 0.0

        }

    # =================================================
    # Loudness
    # =================================================

    loudness = np.mean(
        librosa.feature.rms(y=y)
    )

    # =================================================
    # RMS Energy
    # =================================================

    rms = np.mean(
        librosa.feature.rms(y=y)
    )

    # =================================================
    # Tempo
    # =================================================

    try:

        tempo, _ = librosa.beat.beat_track(
            y=y,
            sr=sr
        )

        tempo = float(
            np.mean(tempo)
        )

    except Exception:

        tempo = 0.0

    # =================================================
    # Pitch
    # =================================================

    try:

        pitches, magnitudes = librosa.piptrack(
            y=y,
            sr=sr
        )

        pitch_values = pitches[
            pitches > 0
        ]

        if len(pitch_values):

            avg_pitch = np.mean(
                pitch_values
            )

            pitch_variation = np.std(
                pitch_values
            )

        else:

            avg_pitch = 0.0
            pitch_variation = 0.0

    except Exception:

        avg_pitch = 0.0
        pitch_variation = 0.0

    # =================================================
    # Audio Variation
    # =================================================

    audio_variation = np.std(y)

    # =================================================
    # Spectral Features
    # =================================================

    try:

        spectral_centroid = np.mean(
            librosa.feature.spectral_centroid(
                y=y,
                sr=sr
            )
        )

        spectral_bandwidth = np.mean(
            librosa.feature.spectral_bandwidth(
                y=y,
                sr=sr
            )
        )

        spectral_rolloff = np.mean(
            librosa.feature.spectral_rolloff(
                y=y,
                sr=sr
            )
        )

        spectral_contrast = np.mean(
            librosa.feature.spectral_contrast(
                y=y,
                sr=sr
            )
        )

        zero_crossing_rate = np.mean(
            librosa.feature.zero_crossing_rate(y)
        )

    except Exception:

        spectral_centroid = 0.0
        spectral_bandwidth = 0.0
        spectral_rolloff = 0.0
        spectral_contrast = 0.0
        zero_crossing_rate = 0.0

    # =================================================
    # Harmonic / Percussive
    # =================================================

    try:

        harmonic, percussive = librosa.effects.hpss(y)

        harmonic_energy = np.mean(
            np.abs(harmonic)
        )

        percussive_energy = np.mean(
            np.abs(percussive)
        )

        total = (
            harmonic_energy
            +
            percussive_energy
            +
            1e-8
        )

        harmonic_ratio = (
            harmonic_energy / total
        )

        percussive_ratio = (
            percussive_energy / total
        )

    except Exception:

        harmonic_ratio = 0.0
        percussive_ratio = 0.0

    # =================================================
    # Sound Density
    # =================================================

    try:

        onset_env = librosa.onset.onset_strength(
            y=y,
            sr=sr
        )

        sound_density = float(
            np.mean(onset_env)
        )

    except Exception:

        sound_density = 0.0

    # =================================================
    # Audio Repetition
    # =================================================

    try:

        chroma = librosa.feature.chroma_stft(
            y=y,
            sr=sr
        )

        similarity = np.corrcoef(
            chroma
        )

        repetition = float(
            np.mean(
                similarity > 0.95
            )
        )

    except Exception:

        repetition = 0.0

    # =================================================
    # RETURN FEATURES
    # =================================================

    return {

        "loudness":
            float(loudness),

        "rms_energy":
            float(rms),

        "sound_density":
            float(sound_density),

        "tempo":
            float(tempo),

        "avg_pitch":
            float(avg_pitch),

        "pitch_variation":
            float(pitch_variation),

        "audio_variation":
            float(audio_variation),

        "spectral_centroid":
            float(spectral_centroid),

        "spectral_bandwidth":
            float(spectral_bandwidth),

        "spectral_rolloff":
            float(spectral_rolloff),

        "spectral_contrast":
            float(spectral_contrast),

        "zero_crossing_rate":
            float(zero_crossing_rate),

        "harmonic_ratio":
            float(harmonic_ratio),

        "percussive_ratio":
            float(percussive_ratio),

        "audio_repetition":
            float(repetition)

    }