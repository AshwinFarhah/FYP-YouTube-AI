# ============================================================
# NeuroShield AI
# Live YouTube Video Feature Analyzer
# ============================================================

from pathlib import Path
import json
import math

import cv2
import numpy as np
import pandas as pd


# ============================================================
# EXISTING NEUROSHIELD MODULES
# ============================================================

from modules.visual_features import (
    extract_visual_features
)

from modules.video_extractor import (
    extract_audio
)

from modules.audio_features import (
    extract_audio_features
)

from modules.emotional_features import (
    extract_emotional_features
)

from modules.whisper_features import (
    extract_transcript
)

from modules.text_features import (
    extract_text_features
)

from modules.behavioural_features import (
    extract_behavioural_features
)

from utils.text_cleaner import (
    clean_transcript
)

from utils.transcript_quality import (
    evaluate_transcript_quality
)

from backend.developmental_scoring import (
    calculate_developmental_scores
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURE_PATH = (
    BASE_DIR /
    "models" /
    "random_forest_features.json"
)

MEDIAN_PATH = (
    BASE_DIR /
    "models" /
    "deployment_feature_medians.json"
)


# ============================================================
# LOAD EXPECTED ML FEATURES
# ============================================================

with open(
    FEATURE_PATH,
    "r",
    encoding="utf-8"
) as file:

    feature_data = json.load(file)


if isinstance(feature_data, list):

    FEATURE_NAMES = feature_data

elif isinstance(feature_data, dict):

    if "features" in feature_data:

        FEATURE_NAMES = feature_data["features"]

    elif "feature_names" in feature_data:

        FEATURE_NAMES = feature_data["feature_names"]

    else:

        raise ValueError(
            "Could not find feature names."
        )

else:

    raise ValueError(
        "Unexpected feature file format."
    )


# ============================================================
# LOAD DEPLOYMENT MEDIANS
# ============================================================

with open(
    MEDIAN_PATH,
    "r",
    encoding="utf-8"
) as file:

    DEPLOYMENT_MEDIANS = json.load(file)


# ============================================================
# VIDEO DURATION
# ============================================================

def get_video_duration(video_path):

    cap = cv2.VideoCapture(
        str(video_path)
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    frame_count = cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )

    cap.release()


    if fps <= 0:

        return 0.0


    duration = (
        frame_count /
        fps
    )


    return float(duration)


# ============================================================
# SAFE NUMBER CONVERSION
# ============================================================

def safe_float(value):

    try:

        value = float(value)

        if math.isnan(value):

            return np.nan

        if math.isinf(value):

            return np.nan

        return value

    except (TypeError, ValueError):

        return np.nan


# ============================================================
# MEDIAN IMPUTATION
# ============================================================

def apply_deployment_medians(
    features
):

    cleaned_features = {}


    for feature in FEATURE_NAMES:

        value = features.get(
            feature,
            np.nan
        )

        value = safe_float(
            value
        )


        # ----------------------------------------------------
        # Missing / invalid value
        # ----------------------------------------------------

        if pd.isna(value):

            if feature not in DEPLOYMENT_MEDIANS:

                raise ValueError(
                    f"No deployment median found for: {feature}"
                )

            value = float(
                DEPLOYMENT_MEDIANS[
                    feature
                ]
            )


        cleaned_features[
            feature
        ] = float(value)


    return cleaned_features


# ============================================================
# MAIN VIDEO ANALYZER
# ============================================================

def analyze_video_features(
    video_path
):

    print()
    print("=" * 65)
    print("NeuroShield AI - Multimodal Feature Extraction")
    print("=" * 65)

    video_path = str(
        video_path
    )


    # ========================================================
    # 1. VIDEO DURATION
    # ========================================================

    print()
    print("[1/8] Reading video duration...")


    video_duration = (
        get_video_duration(
            video_path
        )
    )


    analysis_duration = min(
        video_duration,
        300.0
    )


    print(
        f"Video duration: {video_duration:.2f} seconds"
    )

    print(
        f"Analysis duration: {analysis_duration:.2f} seconds"
    )


    # ========================================================
    # 2. VISUAL FEATURES
    # ========================================================

    print()
    print("[2/8] Extracting visual features...")


    visual_features = (
        extract_visual_features(
            video_path
        )
    )


    if visual_features is None:

        raise RuntimeError(
            "Visual feature extraction failed."
        )


    print(
        "Visual feature extraction complete."
    )


    # ========================================================
    # 3. AUDIO EXTRACTION
    # ========================================================

    print()
    print("[3/8] Extracting audio...")


    audio_path = (
        extract_audio(
            video_path
        )
    )


    audio_available = (
        audio_path is not None
    )


    if audio_available:

        print(
            "Audio extraction complete."
        )

    else:

        print(
            "No usable audio was extracted."
        )


    # ========================================================
    # 4. AUDIO FEATURES
    # ========================================================

    print()
    print("[4/8] Extracting audio features...")


    audio_features = (
        extract_audio_features(
            audio_path
        )
    )


    print(
        "Audio feature extraction complete."
    )


    # ========================================================
    # 5. EMOTIONAL FEATURES
    # ========================================================

    print()
    print("[5/8] Calculating emotional features...")


    emotional_features = (
        extract_emotional_features(

            audio_features.get(
                "loudness",
                0
            ),

            audio_features.get(
                "pitch_variation",
                0
            ),

            audio_features.get(
                "tempo",
                0
            ),

            audio_features.get(
                "spectral_contrast",
                0
            )

        )
    )


    print(
        "Emotional feature extraction complete."
    )


    # ========================================================
    # ATTENTION SCORE
    # ========================================================

    attention_score = (

        0.4 * min(
            visual_features.get(
                "motion_spike_rate",
                0
            ),
            1
        )

        +

        0.3 * min(
            visual_features.get(
                "scene_rate",
                0
            ),
            1
        )

        +

        0.3 * min(
            audio_features.get(
                "sound_density",
                0
            ),
            1
        )

    )


    attention_score = float(
        np.clip(
            attention_score,
            0,
            1
        )
    )


    # ========================================================
    # 6. WHISPER TRANSCRIPTION
    # ========================================================

    print()
    print("[6/8] Running Whisper transcription...")


    raw_transcript = (
        extract_transcript(
            audio_path
        )
    )


    transcript = (
        clean_transcript(
            raw_transcript
        )
    )


    print(
        "Whisper transcription complete."
    )


    # ========================================================
    # 7. TRANSCRIPT QUALITY
    # ========================================================

    print()
    print("[7/8] Evaluating transcript quality...")


    transcript_quality = (
        evaluate_transcript_quality(
            transcript
        )
    )


    transcript_word_count = (
        transcript_quality.get(
            "transcript_word_count",
            0
        )
    )

    english_ratio = (
        transcript_quality.get(
            "english_ratio",
            0
        )
    )

    quality_score = (
        transcript_quality.get(
            "transcript_quality_score",
            0
        )
    )


    # --------------------------------------------------------
    # Same rejection rules used during dataset construction
    # --------------------------------------------------------

    transcript_rejected = (

        quality_score < 0.70

        or

        english_ratio < 0.75

        or

        transcript_word_count < 20

    )


    if transcript_rejected:

        print(
            "Transcript rejected for NLP feature extraction."
        )

        text_features = {

            "transcript_length":
                np.nan,

            "sentence_complexity":
                np.nan,

            "average_sentence_length":
                np.nan,

            "vocabulary_diversity":
                np.nan,

            "phrase_repetition":
                np.nan,

            "educational_word_ratio":
                np.nan,

            "reward_keyword_frequency":
                np.nan

        }


        # Behavioural calculations should not receive NaN.
        behavioural_text_features = {

            "reward_keyword_frequency":
                0.0

        }

    else:

        print(
            "Transcript accepted."
        )


        text_features = (
            extract_text_features(
                transcript
            )
        )


        behavioural_text_features = (
            text_features.copy()
        )


    # ========================================================
    # 8. BEHAVIOURAL FEATURES
    # ========================================================

    print()
    print("[8/8] Calculating behavioural features...")


    behavioural_visual_features = {

        "scene_rate":
            visual_features.get(
                "scene_rate",
                0
            ),

        "motion_std":
            visual_features.get(
                "motion_std",
                0
            ),

        "motion_spike_rate":
            visual_features.get(
                "motion_spike_rate",
                0
            ),

        "flicker_rate":
            visual_features.get(
                "flicker_rate",
                0
            )

    }


    behavioural_audio_features = {

        "audio_variation":
            audio_features.get(
                "audio_variation",
                0
            ),

        "audio_repetition":
            audio_features.get(
                "audio_repetition",
                0
            )

    }


    behavioural_features = (
        extract_behavioural_features(

            behavioural_visual_features,

            behavioural_audio_features,

            behavioural_text_features

        )
    )


    print(
        "Behavioural feature extraction complete."
    )


    # ========================================================
    # TRANSCRIPT LENGTH NORMALIZED
    # ========================================================

    transcript_length = (
        text_features.get(
            "transcript_length",
            np.nan
        )
    )


    if pd.isna(
        transcript_length
    ):

        transcript_length_normalized = (
            np.nan
        )

    else:

        transcript_length_normalized = (

            float(
                transcript_length
            )

            /

            max(
                video_duration,
                1.0
            )

        )


    # ========================================================
    # COMBINE ALL RAW FEATURES
    # ========================================================

    raw_features = {}


    # Visual
    raw_features.update(
        visual_features
    )


    # Audio
    raw_features.update(
        audio_features
    )


    # Attention
    raw_features[
        "attention_score"
    ] = attention_score


    # Behavioural
    raw_features.update(
        behavioural_features
    )


    # Text
    raw_features.update(
        text_features
    )


    # Transcript quality ML features
    raw_features[
        "transcript_word_count"
    ] = transcript_quality.get(
        "transcript_word_count",
        0
    )

    raw_features[
        "unique_word_ratio"
    ] = transcript_quality.get(
        "unique_word_ratio",
        0
    )

    raw_features[
        "repeated_word_ratio"
    ] = transcript_quality.get(
        "repeated_word_ratio",
        0
    )

    raw_features[
        "hallucination_score"
    ] = transcript_quality.get(
        "hallucination_score",
        0
    )

    raw_features[
        "english_ratio"
    ] = transcript_quality.get(
        "english_ratio",
        0
    )

    raw_features[
        "nonsense_ratio"
    ] = transcript_quality.get(
        "nonsense_ratio",
        0
    )


    # Emotion
    raw_features.update(
        emotional_features
    )


    # Video duration
    raw_features[
        "video_duration_seconds"
    ] = video_duration


    # Normalized transcript length
    raw_features[
        "transcript_length_normalized"
    ] = (
        transcript_length_normalized
    )


    # ========================================================
    # KEEP EXACT RANDOM FOREST FEATURES
    # ========================================================

    model_features = {}


    for feature in FEATURE_NAMES:

        model_features[
            feature
        ] = raw_features.get(
            feature,
            np.nan
        )


    # ========================================================
    # APPLY TRAINING MEDIANS
    # ========================================================

    clean_features = (
        apply_deployment_medians(
            model_features
        )
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if len(clean_features) != 42:

        raise RuntimeError(
            "Expected 42 ML features but "
            f"generated {len(clean_features)}."
        )


    missing_after_imputation = [

        feature

        for feature, value
        in clean_features.items()

        if pd.isna(value)

    ]


    if missing_after_imputation:

        raise RuntimeError(
            "Missing features remain after imputation: "
            + str(
                missing_after_imputation
            )
        )

    # ========================================================
    # DEVELOPMENTAL IMPACT SCORING
    # ========================================================

    developmental_scores = (
        calculate_developmental_scores(
            clean_features
        )
    )

    print()
    print("Developmental impact scores:")

    print(
        "  Cognitive:",
        developmental_scores["cognitive"]
    )

    print(
        "  Behavioural:",
        developmental_scores["behavioural"]
    )

    print(
        "  Emotional:",
        developmental_scores["emotional"]
    )

    print(
        "  Overall:",
        developmental_scores["overall"]
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 65)
    print("MULTIMODAL EXTRACTION COMPLETE")
    print("=" * 65)

    print(
        "ML features generated:",
        len(clean_features)
    )

    print(
        "Audio available:",
        audio_available
    )

    print(
        "Transcript words:",
        transcript_word_count
    )

    print(
        "Transcript quality:",
        round(
            quality_score,
            4
        )
    )

    print(
        "Transcript rejected:",
        transcript_rejected
    )

    print(
        "All features ready for Random Forest."
    )

    print(
        "=" * 65
    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "features":
            clean_features,

        "raw_features":
            model_features,

        "developmental_scores":
            developmental_scores,

        "video_duration":
            video_duration,

        "analysis_duration":
            analysis_duration,

        "audio_available":
            audio_available,

        "transcript":
            transcript,

        "transcript_rejected":
            bool(
                transcript_rejected
            ),

        "transcript_quality_score":
            float(
                quality_score
            ),

        "transcript_quality_label":
            transcript_quality.get(
                "transcript_quality_label",
                "unknown"
            )

    }