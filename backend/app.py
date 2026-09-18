# ============================================================
# NeuroShield AI
# FastAPI Backend - Random Forest Prediction
# ============================================================

from pathlib import Path
import json
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.youtube_downloader import download_youtube_video
from backend.video_analyzer import analyze_video_features

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "random_forest_neuroshield.joblib"
FEATURES_PATH = BASE_DIR / "models" / "random_forest_features.json"


# ============================================================
# LOAD MODEL
# ============================================================

print("============================================================")
print("NeuroShield AI - Backend")
print("============================================================")

print("\nLoading Random Forest model...")

model = joblib.load(MODEL_PATH)

print("Random Forest model loaded successfully.")


# ============================================================
# LOAD FEATURE NAMES
# ============================================================

print("Loading ML feature list...")

with open(FEATURES_PATH, "r", encoding="utf-8") as file:
    feature_data = json.load(file)


if isinstance(feature_data, list):
    feature_names = feature_data

elif isinstance(feature_data, dict):

    if "features" in feature_data:
        feature_names = feature_data["features"]

    elif "feature_names" in feature_data:
        feature_names = feature_data["feature_names"]

    else:
        raise ValueError(
            "Could not find feature names in random_forest_features.json"
        )

else:
    raise ValueError(
        "Unexpected format in random_forest_features.json"
    )


print(f"Feature list loaded successfully.")
print(f"Number of expected features: {len(feature_names)}")


# ============================================================
# LABEL MAPPING
# ============================================================

LABEL_MAPPING = {
    0: "High Risk",
    1: "Low Risk",
    2: "Medium Risk"
}


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="NeuroShield AI API",
    description="Backend API for NeuroShield AI machine learning analysis.",
    version="1.0.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class PredictionRequest(BaseModel):
    features: dict[str, float]


class VideoAnalysisRequest(BaseModel):
    youtube_url: str


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "system": "NeuroShield AI",
        "status": "online",
        "model": "Random Forest",
        "features": len(feature_names)
    }


# ============================================================
# MODEL STATUS ENDPOINT
# ============================================================

@app.get("/model-status")
def model_status():

    return {
        "model_loaded": True,
        "model_type": type(model).__name__,
        "feature_count": len(feature_names),
        "feature_names": feature_names
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict(request: PredictionRequest):

    # --------------------------------------------------------
    # Check that all expected features are provided
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in feature_names
        if feature not in request.features
    ]

    if missing_features:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing required features",
                "missing_features": missing_features
            }
        )


    # --------------------------------------------------------
    # Create feature row in the exact training order
    # --------------------------------------------------------

    feature_row = {
        feature: request.features[feature]
        for feature in feature_names
    }

    X = pd.DataFrame(
        [feature_row],
        columns=feature_names
    )


    # --------------------------------------------------------
    # Make prediction
    # --------------------------------------------------------

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    predicted_class_index = list(model.classes_).index(prediction)

    confidence = float(
        probabilities[predicted_class_index]
    )


    # --------------------------------------------------------
    # Convert numerical label to readable label
    # --------------------------------------------------------

    risk_level = LABEL_MAPPING.get(
        int(prediction),
        str(prediction)
    )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "prediction": int(prediction),
        "risk_level": risk_level,
        "confidence": confidence
    }

# ============================================================
# YOUTUBE VIDEO ANALYSIS ENDPOINT
# ============================================================

@app.post("/analyze-video")
def analyze_video(request: VideoAnalysisRequest):

    try:

        print()
        print("=" * 65)
        print("NeuroShield AI - Video Analysis Request")
        print("=" * 65)

        print(
            "Received URL:",
            request.youtube_url
        )


        # ====================================================
        # 1. DOWNLOAD YOUTUBE VIDEO
        # ====================================================

        download_result = (
            download_youtube_video(
                request.youtube_url
            )
        )


        video_id = (
            download_result["video_id"]
        )

        video_path = (
            download_result["video_path"]
        )


        # ====================================================
        # 2. MULTIMODAL FEATURE EXTRACTION
        # ====================================================

        analysis = (
            analyze_video_features(
                video_path
            )
        )


        features = (
            analysis["features"]
        )


        # ====================================================
        # 3. CREATE RANDOM FOREST INPUT
        # ====================================================

        X = pd.DataFrame(
            [features],
            columns=feature_names
        )


        # ====================================================
        # 4. RANDOM FOREST PREDICTION
        # ====================================================

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


        risk_level = (
            LABEL_MAPPING.get(
                int(prediction),
                str(prediction)
            )
        )


        # ====================================================
        # 5. CLASS PROBABILITIES
        # ====================================================

        class_probabilities = {}


        for class_id, probability in zip(
            model.classes_,
            probabilities
        ):

            label = LABEL_MAPPING.get(
                int(class_id),
                str(class_id)
            )


            class_probabilities[
                label
            ] = float(
                probability
            )


        # ====================================================
        # 6. RESPONSE
        # ====================================================

        print()
        print("=" * 65)
        print("NeuroShield AI - Analysis Complete")
        print("=" * 65)

        print(
            "Video ID:",
            video_id
        )

        print(
            "Risk level:",
            risk_level
        )

        print(
            "Confidence:",
            round(
                confidence,
                4
            )
        )

        print("=" * 65)


        return {

            "status":
                "analysis_complete",

            "video_id":
                video_id,

            "prediction":
                int(
                    prediction
                ),

            "risk_level":
                risk_level,

            "confidence":
                confidence,

            "class_probabilities":
                class_probabilities,

            "feature_count":
                len(
                    features
                ),

            "video_duration_seconds":
                analysis[
                    "video_duration"
                ],

            "analysis_duration_seconds":
                analysis[
                    "analysis_duration"
                ],

            "audio_available":
                analysis[
                    "audio_available"
                ],

            "transcript_rejected":
                analysis[
                    "transcript_rejected"
                ],

            "transcript_quality_score":
                analysis[
                    "transcript_quality_score"
                ],

            "transcript_quality_label":
                analysis[
                    "transcript_quality_label"
                ]

        }


    except Exception as error:

        print()
        print(
            "NeuroShield AI - Analysis Error:",
            error
        )


        raise HTTPException(
            status_code=500,
            detail=str(
                error
            )
        )