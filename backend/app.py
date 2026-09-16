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