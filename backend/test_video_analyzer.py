# ============================================================
# NeuroShield AI
# Live Video Analysis + Random Forest Test
# ============================================================

from pathlib import Path
import json
import joblib
import pandas as pd

from backend.video_analyzer import (
    analyze_video_features
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

VIDEO_PATH = (
    BASE_DIR /
    "backend" /
    "temp" /
    "wXfcmS3SquY.mp4"
)

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "random_forest_neuroshield.joblib"
)

FEATURE_PATH = (
    BASE_DIR /
    "models" /
    "random_forest_features.json"
)


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("=" * 65)
print("NeuroShield AI - Live Prediction Test")
print("=" * 65)

print()
print("Loading Random Forest...")

model = joblib.load(
    MODEL_PATH
)

print(
    "Random Forest loaded."
)


# ============================================================
# LOAD FEATURE ORDER
# ============================================================

with open(
    FEATURE_PATH,
    "r",
    encoding="utf-8"
) as file:

    feature_data = json.load(
        file
    )


if isinstance(
    feature_data,
    list
):

    feature_names = (
        feature_data
    )

elif "features" in feature_data:

    feature_names = (
        feature_data["features"]
    )

else:

    feature_names = (
        feature_data["feature_names"]
    )


# ============================================================
# ANALYZE VIDEO
# ============================================================

print()
print(
    "Testing video:",
    VIDEO_PATH
)


analysis = (
    analyze_video_features(
        VIDEO_PATH
    )
)


features = (
    analysis["features"]
)


# ============================================================
# CREATE RANDOM FOREST INPUT
# ============================================================

X = pd.DataFrame(
    [features],
    columns=feature_names
)


print()
print(
    "Random Forest input shape:",
    X.shape
)


# ============================================================
# PREDICTION
# ============================================================

prediction = (
    model.predict(
        X
    )[0]
)

probabilities = (
    model.predict_proba(
        X
    )[0]
)


# ============================================================
# LABEL MAPPING
# ============================================================

LABEL_MAPPING = {

    0: "High Risk",

    1: "Low Risk",

    2: "Medium Risk"

}


risk_level = (
    LABEL_MAPPING.get(
        int(prediction),
        str(prediction)
    )
)


predicted_class_index = (
    list(
        model.classes_
    ).index(
        prediction
    )
)


confidence = float(
    probabilities[
        predicted_class_index
    ]
)


# ============================================================
# RESULT
# ============================================================

print()
print("=" * 65)
print("LIVE RANDOM FOREST RESULT")
print("=" * 65)

print(
    "Prediction:",
    int(prediction)
)

print(
    "Risk level:",
    risk_level
)

print(
    "Confidence:",
    f"{confidence:.4f}"
)

print()
print(
    "Class probabilities:"
)


for class_id, probability in zip(
    model.classes_,
    probabilities
):

    label = LABEL_MAPPING.get(
        int(class_id),
        str(class_id)
    )

    print(
        f"   {label:15s}: "
        f"{float(probability):.4f}"
    )


print()
print(
    "Input features:",
    X.shape[1]
)

print(
    "Transcript rejected:",
    analysis[
        "transcript_rejected"
    ]
)

print()
print("=" * 65)
print(
    "LIVE PREDICTION TEST COMPLETE"
)
print("=" * 65)