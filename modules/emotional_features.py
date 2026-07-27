import numpy as np


def extract_emotional_features(
        loudness,
        pitch_variation,
        tempo,
        spectral_contrast
):

    # -----------------------------
    # Emotional arousal
    # High energy = higher arousal
    # -----------------------------

    arousal = (
        0.35 * min(loudness,1)
        +
        0.35 * min(pitch_variation / 2000,1)
        +
        0.30 * min(tempo / 200,1)
    )


    # -----------------------------
    # Emotional valence
    # Positive sound proxy
    # -----------------------------

    valence = (
        0.5 * min(spectral_contrast / 50,1)
        +
        0.5 * (1 - min(pitch_variation / 2000,1))
    )


    # -----------------------------
    # Emotional stability
    # Low variation = stable emotion
    # -----------------------------

    stability = 1 - min(
        pitch_variation / 2000,
        1
    )


    return {

        "emotion_arousal":
            float(arousal),

        "emotion_valence":
            float(valence),

        "emotion_stability":
            float(stability)

    }