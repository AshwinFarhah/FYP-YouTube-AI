# ============================================================
# NeuroShield AI
# Parent-Facing Feature Interpretation
#
# Converts extracted feature values into descriptive,
# dataset-relative interpretations.
#
# IMPORTANT:
# These descriptions are relative to NeuroShield's training
# dataset. They are NOT clinical thresholds.
# ============================================================

import json
import os


# ============================================================
# PATH
# ============================================================

REFERENCE_PATH = os.path.join(
    "models",
    "feature_reference_ranges.json"
)


# ============================================================
# LOAD REFERENCE RANGES
# ============================================================

with open(
    REFERENCE_PATH,
    "r",
    encoding="utf-8"
) as file:

    FEATURE_REFERENCE_RANGES = json.load(file)


# ============================================================
# FEATURES NOT SUITABLE FOR SIMPLE QUARTILE INTERPRETATION
# ============================================================

EXCLUDED_PARENT_FEATURES = {
    "educational_word_ratio",
    "hallucination_score",
    "english_ratio"
}


# ============================================================
# PARENT-FRIENDLY FEATURE NAMES
# ============================================================

FEATURE_DISPLAY_NAMES = {

    "avg_saturation":
        "Colour saturation",

    "avg_brightness":
        "Visual brightness",

    "motion_mean":
        "Overall motion",

    "motion_std":
        "Motion variation",

    "scene_rate":
        "Scene changes",

    "flicker_rate":
        "Visual flicker",

    "loudness":
        "Audio loudness",

    "sound_density":
        "Sound activity",

    "audio_variation":
        "Audio variation",

    "avg_pitch":
        "Average pitch",

    "pitch_variation":
        "Pitch variation",

    "tempo":
        "Audio tempo",

    "motion_spike_rate":
        "Sudden motion changes",

    "attention_score":
        "Attention-related activity",

    "loop_detection_score":
        "Repeated content patterns",

    "reward_cue_frequency":
        "Reward-related cues",

    "attention_reset_rate":
        "Attention resets",

    "sentence_complexity":
        "Sentence complexity",

    "average_sentence_length":
        "Sentence length",

    "vocabulary_diversity":
        "Vocabulary diversity",

    "phrase_repetition":
        "Phrase repetition",

    "reward_keyword_frequency":
        "Reward-related language",

    "unique_word_ratio":
        "Vocabulary variety",

    "repeated_word_ratio":
        "Repeated language",

    "nonsense_ratio":
        "Unclear or nonsensical language",

    "emotion_arousal":
        "Emotional intensity",

    "emotion_valence":
        "Emotional tone",

    "emotion_stability":
        "Emotional stability"
}


# ============================================================
# INTERPRET ONE FEATURE
# ============================================================

def interpret_feature(
    feature_name,
    value
):

    if feature_name in EXCLUDED_PARENT_FEATURES:

        return None


    reference = FEATURE_REFERENCE_RANGES.get(
        feature_name
    )


    if reference is None:

        return None


    try:

        numeric_value = float(value)

    except (TypeError, ValueError):

        return None


    p25 = float(reference["p25"])
    p75 = float(reference["p75"])


    # --------------------------------------------------------
    # COLLAPSED RANGE
    # --------------------------------------------------------

    if p25 == p75:

        return None


    # --------------------------------------------------------
    # DATASET-RELATIVE POSITION
    # --------------------------------------------------------

    if numeric_value < p25:

        level = "lower"

        label = "Lower than typical"

    elif numeric_value > p75:

        level = "higher"

        label = "Higher than typical"

    else:

        level = "typical"

        label = "Typical range"


    return {

        "feature":
            feature_name,

        "display_name":
            FEATURE_DISPLAY_NAMES.get(
                feature_name,
                feature_name.replace(
                    "_",
                    " "
                ).title()
            ),

        "value":
            numeric_value,

        "reference_level":
            level,

        "reference_label":
            label,

        "p25":
            p25,

        "p75":
            p75

    }


# ============================================================
# INTERPRET ALL AVAILABLE FEATURES
# ============================================================

def interpret_features(
    features
):

    interpretations = {}


    if not isinstance(features, dict):

        return interpretations


    for feature_name, value in features.items():

        interpretation = interpret_feature(
            feature_name,
            value
        )


        if interpretation is not None:

            interpretations[
                feature_name
            ] = interpretation


    return interpretations