# ============================================================
# NeuroShield AI
# Developmental Impact Scoring Framework
# ============================================================

import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

NORMALIZATION_PATH = (
    BASE_DIR
    / "models"
    / "developmental_normalization.json"
)


# ============================================================
# LOAD NORMALIZATION CONFIGURATION
# ============================================================

with open(
    NORMALIZATION_PATH,
    "r",
    encoding="utf-8"
) as file:

    NORMALIZATION = json.load(file)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_feature(feature_name, value):
    """
    Normalize a feature to the range 0-1 using the
    training-data percentile bounds.

    Values outside the training bounds are clamped.
    """

    if feature_name not in NORMALIZATION:
        raise ValueError(
            f"No normalization configuration for: "
            f"{feature_name}"
        )

    bounds = NORMALIZATION[feature_name]

    lower = float(bounds["lower"])
    upper = float(bounds["upper"])

    value = float(value)

    normalized = (
        (value - lower)
        / (upper - lower)
    )

    # Clamp to 0-1
    normalized = max(
        0.0,
        min(1.0, normalized)
    )

    return normalized


# ============================================================
# COGNITIVE IMPACT
# ============================================================

def calculate_cognitive_score(features):

    motion = (
        normalize_feature(
            "motion_mean",
            features["motion_mean"]
        )
        +
        normalize_feature(
            "motion_spike_rate",
            features["motion_spike_rate"]
        )
    ) / 2

    scene_change = normalize_feature(
        "scene_rate",
        features["scene_rate"]
    )

    repetition = (
        normalize_feature(
            "loop_detection_score",
            features["loop_detection_score"]
        )
        +
        normalize_feature(
            "phrase_repetition",
            features["phrase_repetition"]
        )
    ) / 2

    visual_complexity = (
        normalize_feature(
            "avg_saturation",
            features["avg_saturation"]
        )
        +
        normalize_feature(
            "flicker_rate",
            features["flicker_rate"]
        )
    ) / 2

    cognitive_score = (
        0.30 * motion
        + 0.25 * scene_change
        + 0.25 * repetition
        + 0.20 * visual_complexity
    )

    return cognitive_score


# ============================================================
# BEHAVIOURAL RISK
# ============================================================

def calculate_behavioural_score(features):

    motion = normalize_feature(
        "motion_spike_rate",
        features["motion_spike_rate"]
    )

    audio_density = normalize_feature(
        "sound_density",
        features["sound_density"]
    )

    reward_cues = normalize_feature(
        "reward_cue_frequency",
        features["reward_cue_frequency"]
    )

    attention_resets = normalize_feature(
        "attention_reset_rate",
        features["attention_reset_rate"]
    )

    behavioural_score = (
        0.15 * motion
        + 0.15 * audio_density
        + 0.30 * reward_cues
        + 0.40 * attention_resets
    )

    return behavioural_score


# ============================================================
# EMOTIONAL STIMULATION
# ============================================================

def calculate_emotional_score(features):

    loudness = normalize_feature(
        "loudness",
        features["loudness"]
    )

    pitch_variation = normalize_feature(
        "pitch_variation",
        features["pitch_variation"]
    )

    arousal = normalize_feature(
        "emotion_arousal",
        features["emotion_arousal"]
    )

    stability = normalize_feature(
        "emotion_stability",
        features["emotion_stability"]
    )

    # Higher arousal and lower stability represent
    # stronger emotional stimulation.
    emotional_dynamics = (
        arousal
        +
        (1.0 - stability)
    ) / 2

    emotional_score = (
        0.30 * loudness
        + 0.25 * pitch_variation
        + 0.45 * emotional_dynamics
    )

    return emotional_score


# ============================================================
# OVERALL DEVELOPMENTAL IMPACT
# ============================================================

def calculate_developmental_scores(features):
    """
    Calculate all NeuroShield developmental scores.

    Internal calculations use 0-1.
    Returned values use 0-100 for the extension UI.
    """

    cognitive = calculate_cognitive_score(
        features
    )

    behavioural = calculate_behavioural_score(
        features
    )

    emotional = calculate_emotional_score(
        features
    )

    # Equal weighting across the three developmental
    # dimensions.
    overall = (
        cognitive
        + behavioural
        + emotional
    ) / 3

    return {
        "cognitive": round(
            cognitive * 100,
            2
        ),
        "behavioural": round(
            behavioural * 100,
            2
        ),
        "emotional": round(
            emotional * 100,
            2
        ),
        "overall": round(
            overall * 100,
            2
        ),
    }