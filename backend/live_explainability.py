# ============================================================
# NeuroShield AI
# Live SHAP Explainability
# ============================================================

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap


# ============================================================
# PATHS
# ============================================================

BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "random_forest_neuroshield.joblib"
)

FEATURES_PATH = (
    BASE_DIR
    / "models"
    / "random_forest_features.json"
)


# ============================================================
# CLASS LABELS
# ============================================================

CLASS_NAMES = {
    0: "High Risk",
    1: "Low Risk",
    2: "Medium Risk"
}


# ============================================================
# PARENT-FRIENDLY FEATURE NAMES
# ============================================================

PARENT_FRIENDLY_NAMES = {

    "attention_score":
        "Attention-related activity",

    "attention_reset_rate":
        "Attention-reset patterns",

    "reward_cue_frequency":
        "Reward-related cues",

    "motion_spike_rate":
        "Sudden motion spikes",

    "motion_mean":
        "Overall visual motion",

    "motion_std":
        "Variation in motion",

    "avg_saturation":
        "Color saturation",

    "avg_brightness":
        "Brightness",

    "audio_variation":
        "Audio variation",

    "loudness":
        "Audio loudness",

    "flicker_rate":
        "Rapid visual changes",

    "scene_rate":
        "Scene changes",

    "loop_detection_score":
        "Repetitive content patterns",

    "emotion_arousal":
        "Emotional arousal",

    "emotion_valence":
        "Emotional tone",

    "emotion_stability":
        "Emotional stability",

    "transcript_length":
        "Transcript length",

    "transcript_word_count":
        "Transcript content",

    "vocabulary_diversity":
        "Vocabulary diversity",

    "phrase_repetition":
        "Phrase repetition",

    "educational_word_ratio":
        "Educational vocabulary",

    "reward_keyword_frequency":
        "Reward-related keywords",

    "average_sentence_length":
        "Average sentence length",

    "sentence_complexity":
        "Sentence complexity",

    "tempo":
        "Audio tempo"
}


# ============================================================
# LOAD MODEL + FEATURES ONCE
# ============================================================

MODEL = joblib.load(
    MODEL_PATH
)

with open(
    FEATURES_PATH,
    "r",
    encoding="utf-8"
) as file:

    FEATURE_NAMES = json.load(file)


# ============================================================
# CREATE SHAP EXPLAINER ONCE
# ============================================================

EXPLAINER = shap.TreeExplainer(
    MODEL
)


# ============================================================
# FRIENDLY FEATURE NAME
# ============================================================

def get_friendly_name(feature_name):

    return PARENT_FRIENDLY_NAMES.get(
        feature_name,
        feature_name.replace(
            "_",
            " "
        ).title()
    )


# ============================================================
# NORMALIZE SHAP OUTPUT
# ============================================================

def get_predicted_class_shap_values(
    shap_values,
    predicted_class
):

    shap_array = np.asarray(
        shap_values
    )


    # --------------------------------------------------------
    # SHAP format:
    #
    # samples x features x classes
    # --------------------------------------------------------

    if (
        shap_array.ndim == 3
        and
        shap_array.shape[0] == 1
        and
        shap_array.shape[1]
        == len(FEATURE_NAMES)
    ):

        return shap_array[
            0,
            :,
            predicted_class
        ]


    # --------------------------------------------------------
    # Alternative format:
    #
    # classes x samples x features
    # --------------------------------------------------------

    if (
        shap_array.ndim == 3
        and
        shap_array.shape[0]
        == len(CLASS_NAMES)
        and
        shap_array.shape[1] == 1
        and
        shap_array.shape[2]
        == len(FEATURE_NAMES)
    ):

        return shap_array[
            predicted_class,
            0,
            :
        ]


    # --------------------------------------------------------
    # Binary / two-dimensional fallback
    # --------------------------------------------------------

    if (
        shap_array.ndim == 2
        and
        shap_array.shape[0] == 1
        and
        shap_array.shape[1]
        == len(FEATURE_NAMES)
    ):

        return shap_array[0]


    raise ValueError(
        "Unexpected live SHAP output shape: "
        + str(shap_array.shape)
    )


# ============================================================
# GENERATE LIVE EXPLANATION
# ============================================================

def explain_prediction(
    features,
    predicted_class,
    top_n=5
):

    predicted_class = int(
        predicted_class
    )


    if predicted_class not in CLASS_NAMES:

        raise ValueError(
            "Unknown predicted class: "
            + str(predicted_class)
        )


    # --------------------------------------------------------
    # CREATE EXACT MODEL INPUT
    # --------------------------------------------------------

    input_row = pd.DataFrame(
        [
            [
                features[name]
                for name in FEATURE_NAMES
            ]
        ],
        columns=FEATURE_NAMES
    )


    # --------------------------------------------------------
    # CALCULATE SHAP
    # --------------------------------------------------------

    shap_values = (
        EXPLAINER.shap_values(
            input_row
        )
    )


    local_shap = (
        get_predicted_class_shap_values(
            shap_values,
            predicted_class
        )
    )


    # --------------------------------------------------------
    # BUILD CONTRIBUTION TABLE
    # --------------------------------------------------------

    contributions = []

    for index, feature_name in enumerate(
        FEATURE_NAMES
    ):

        shap_value = float(
            local_shap[index]
        )

        feature_value = float(
            input_row.iloc[
                0,
                index
            ]
        )


        if shap_value > 0:

            direction = "supports"

        elif shap_value < 0:

            direction = "opposes"

        else:

            direction = "neutral"


        contributions.append({

            "feature":
                feature_name,

            "friendly_name":
                get_friendly_name(
                    feature_name
                ),

            "feature_value":
                feature_value,

            "shap_value":
                shap_value,

            "absolute_shap":
                abs(shap_value),

            "direction":
                direction

        })


    # --------------------------------------------------------
    # SORT BY IMPORTANCE
    # --------------------------------------------------------

    contributions.sort(
        key=lambda item:
            item["absolute_shap"],
        reverse=True
    )


    # --------------------------------------------------------
    # KEEP ALL 42 RANKED FEATURE CONTRIBUTIONS
    # --------------------------------------------------------

    feature_contributions = [
        contribution.copy()
        for contribution in contributions
    ]


    top_contributors = (
        contributions[:top_n]
    )


    # --------------------------------------------------------
    # SUPPORTING FEATURES
    # --------------------------------------------------------

    supporting = [
        item
        for item in contributions
        if item["shap_value"] > 0
    ]

    supporting.sort(
        key=lambda item:
            item["shap_value"],
        reverse=True
    )


    # --------------------------------------------------------
    # OPPOSING FEATURES
    # --------------------------------------------------------

    opposing = [
        item
        for item in contributions
        if item["shap_value"] < 0
    ]

    opposing.sort(
        key=lambda item:
            item["shap_value"]
    )


    top_supporting = supporting[:3]

    top_opposing = opposing[:3]


    # --------------------------------------------------------
    # HUMAN-READABLE EXPLANATION
    # --------------------------------------------------------

    predicted_label = CLASS_NAMES[
        predicted_class
    ]


    if top_supporting:

        names = [
            item["friendly_name"]
            for item in top_supporting
        ]


        if len(names) == 1:

            factor_text = names[0]

        elif len(names) == 2:

            factor_text = (
                names[0]
                + " and "
                + names[1]
            )

        else:

            factor_text = (
                names[0]
                + ", "
                + names[1]
                + ", and "
                + names[2]
            )


        parent_explanation = (
            f"The model's {predicted_label} "
            f"prediction was mainly influenced "
            f"by {factor_text} detected in "
            f"the video."
        )

    else:

        parent_explanation = (
            f"The model classified this video "
            f"as {predicted_label} based on "
            f"the combined multimodal features."
        )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "predicted_class":
            predicted_class,

        "predicted_label":
            predicted_label,

        "parent_explanation":
            parent_explanation,

        "top_contributors":
            top_contributors,

        "supporting_factors":
            top_supporting,

        "opposing_factors":
            top_opposing,

        "feature_contributions":
            feature_contributions

    }