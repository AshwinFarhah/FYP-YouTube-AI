# ============================================================
# NeuroShield AI
# FastAPI Backend - Random Forest Prediction
# ============================================================

from pathlib import Path
import json
import joblib
import pandas as pd
import uuid
import threading
import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.youtube_downloader import download_youtube_video
from backend.video_analyzer import analyze_video_features


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

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
# ANALYSIS CACHE CONFIGURATION
# ============================================================

CACHE_DIR = (
    BASE_DIR
    / "backend"
    / "cache"
)

CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("NeuroShield AI - Backend")
print("=" * 60)

print("\nLoading Random Forest model...")

model = joblib.load(MODEL_PATH)

print(
    "Random Forest model loaded successfully."
)


# ============================================================
# LOAD FEATURE NAMES
# ============================================================

print("Loading ML feature list...")

with open(
    FEATURES_PATH,
    "r",
    encoding="utf-8"
) as file:

    feature_data = json.load(file)


if isinstance(feature_data, list):

    feature_names = feature_data

elif isinstance(feature_data, dict):

    if "features" in feature_data:

        feature_names = (
            feature_data["features"]
        )

    elif "feature_names" in feature_data:

        feature_names = (
            feature_data["feature_names"]
        )

    else:

        raise ValueError(
            "Could not find feature names "
            "in random_forest_features.json"
        )

else:

    raise ValueError(
        "Unexpected format in "
        "random_forest_features.json"
    )


print(
    "Feature list loaded successfully."
)

print(
    f"Number of expected features: "
    f"{len(feature_names)}"
)


# ============================================================
# LABEL MAPPING
# ============================================================

LABEL_MAPPING = {
    0: "High Risk",
    1: "Low Risk",
    2: "Medium Risk"
}
# ============================================================
# ANALYSIS CACHE HELPERS
# ============================================================

def extract_youtube_video_id(
    youtube_url
):

    patterns = [

        r"(?:v=)([A-Za-z0-9_-]{11})",

        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",

        r"(?:shorts/)([A-Za-z0-9_-]{11})"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            youtube_url
        )


        if match:

            return match.group(1)


    return None


def get_cache_path(
    video_id
):

    return (
        CACHE_DIR
        / f"{video_id}.json"
    )


def load_cached_result(
    video_id
):

    if not video_id:

        return None


    cache_path = (
        get_cache_path(
            video_id
        )
    )


    if not cache_path.exists():

        return None


    try:

        with open(
            cache_path,
            "r",
            encoding="utf-8"
        ) as file:

            cached_result = (
                json.load(file)
            )


        print(
            "NeuroShield AI: Cached result found:",
            video_id
        )


        return cached_result


    except Exception as error:

        print(
            "NeuroShield AI: Could not read cached result:",
            error
        )


        return None


def save_cached_result(
    video_id,
    result
):

    if not video_id:

        return


    cache_path = (
        get_cache_path(
            video_id
        )
    )


    try:

        with open(
            cache_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )


        print(
            "NeuroShield AI: Analysis result cached:",
            cache_path
        )


    except Exception as error:

        print(
            "NeuroShield AI: Could not save analysis cache:",
            error
        )

# ============================================================
# ANALYSIS JOB STORAGE
# ============================================================
#
# Each long-running video analysis is stored here.
#
# IMPORTANT:
# This is intentionally an in-memory job store for the current
# local FYP deployment.
#
# The Chrome extension no longer needs to keep one HTTP request
# open for the entire analysis.
# ============================================================

analysis_jobs = {}

analysis_jobs_lock = threading.Lock()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="NeuroShield AI API",
    description=(
        "Backend API for NeuroShield AI "
        "machine learning analysis."
    ),
    version="1.1.0"
)


# ============================================================
# REQUEST MODELS
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
def predict(
    request: PredictionRequest
):

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
                "error":
                    "Missing required features",

                "missing_features":
                    missing_features
            }
        )


    # --------------------------------------------------------
    # Create feature row in exact training order
    # --------------------------------------------------------

    feature_row = {
        feature:
            request.features[feature]

        for feature in feature_names
    }


    X = pd.DataFrame(
        [feature_row],
        columns=feature_names
    )


    # --------------------------------------------------------
    # Make prediction
    # --------------------------------------------------------

    prediction = (
        model.predict(X)[0]
    )


    probabilities = (
        model.predict_proba(X)[0]
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


    # --------------------------------------------------------
    # Convert numerical label
    # --------------------------------------------------------

    risk_level = (
        LABEL_MAPPING.get(
            int(prediction),
            str(prediction)
        )
    )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "prediction":
            int(prediction),

        "risk_level":
            risk_level,

        "confidence":
            confidence
    }


# ============================================================
# RUN VIDEO ANALYSIS JOB
# ============================================================
#
# This function performs the same real analysis that the old
# /analyze-video endpoint performed.
#
# The difference is that it runs independently after the
# endpoint has already returned the job ID.
# ============================================================

def run_video_analysis_job(
    job_id,
    youtube_url
):

    try:

        # ----------------------------------------------------
        # MARK JOB AS PROCESSING
        # ----------------------------------------------------

        with analysis_jobs_lock:

            analysis_jobs[job_id][
                "status"
            ] = "processing"


        print()
        print("=" * 65)

        print(
            "NeuroShield AI - "
            "Background Video Analysis"
        )

        print("=" * 65)

        print(
            "Job ID:",
            job_id
        )

        print(
            "Received URL:",
            youtube_url
        )


        # ====================================================
        # 1. DOWNLOAD YOUTUBE VIDEO
        # ====================================================

        download_result = (
            download_youtube_video(
                youtube_url
            )
        )


        video_id = (
            download_result[
                "video_id"
            ]
        )


        video_path = (
            download_result[
                "video_path"
            ]
        )


        # ----------------------------------------------------
        # SAVE VIDEO ID INTO JOB
        # ----------------------------------------------------

        with analysis_jobs_lock:

            analysis_jobs[job_id][
                "video_id"
            ] = video_id


        # ====================================================
        # 2. MULTIMODAL FEATURE EXTRACTION
        # ====================================================

        analysis = (
            analyze_video_features(
                video_path
            )
        )


        features = (
            analysis[
                "features"
            ]
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


        for (
            class_id,
            probability
        ) in zip(
            model.classes_,
            probabilities
        ):

            label = (
                LABEL_MAPPING.get(
                    int(class_id),
                    str(class_id)
                )
            )


            class_probabilities[
                label
            ] = float(
                probability
            )


        # ====================================================
        # 6. BUILD RESULT
        # ====================================================

        result = {

            "status":
                "analysis_complete",

            "video_id":
                video_id,

            "prediction":
                int(prediction),

            "risk_level":
                risk_level,

            "confidence":
                confidence,

            "class_probabilities":
                class_probabilities,

            "feature_count":
                len(features),

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

        # ====================================================
        # CACHE COMPLETED ANALYSIS
        # ====================================================

        result[
            "analysis_source"
        ] = "live"


        save_cached_result(
            video_id,
            result
        )


        # ====================================================
        # 7. STORE COMPLETED RESULT
        # ====================================================

        with analysis_jobs_lock:

            analysis_jobs[job_id][
                "status"
            ] = "complete"

            analysis_jobs[job_id][
                "result"
            ] = result


        # ====================================================
        # TERMINAL OUTPUT
        # ====================================================

        print()
        print("=" * 65)

        print(
            "NeuroShield AI - "
            "Analysis Complete"
        )

        print("=" * 65)


        print(
            "Job ID:",
            job_id
        )


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


    except Exception as error:

        print()
        print(
            "NeuroShield AI - "
            "Background Analysis Error:",
            error
        )


        # ====================================================
        # SAVE ERROR IN JOB
        # ====================================================

        with analysis_jobs_lock:

            if job_id in analysis_jobs:

                analysis_jobs[job_id][
                    "status"
                ] = "failed"

                analysis_jobs[job_id][
                    "error"
                ] = str(
                    error
                )


# ============================================================
# START YOUTUBE VIDEO ANALYSIS
# ============================================================

@app.post("/analyze-video")
def analyze_video(
    request: VideoAnalysisRequest
):

    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    youtube_url = (
        request.youtube_url.strip()
    )


    if not youtube_url:

        raise HTTPException(
            status_code=400,
            detail="YouTube URL is required."
        )

    # --------------------------------------------------------
    # CHECK FOR PREVIOUSLY COMPLETED ANALYSIS
    # --------------------------------------------------------

    video_id = (
        extract_youtube_video_id(
            youtube_url
        )
    )


    cached_result = (
        load_cached_result(
            video_id
        )
    )


    if cached_result is not None:

        job_id = str(
            uuid.uuid4()
        )


        cached_result[
            "analysis_source"
        ] = "cached"


        with analysis_jobs_lock:

            analysis_jobs[job_id] = {

                "job_id":
                    job_id,

                "status":
                    "complete",

                "youtube_url":
                    youtube_url,

                "video_id":
                    video_id,

                "result":
                    cached_result,

                "error":
                    None

            }


        print()
        print("=" * 65)

        print(
            "NeuroShield AI - Cached Analysis"
        )

        print("=" * 65)

        print(
            "Video ID:",
            video_id
        )

        print(
            "Job ID:",
            job_id
        )

        print(
            "Result loaded from cache."
        )

        print("=" * 65)


        return {

            "status":
                "processing",

            "job_id":
                job_id,

            "message":
                "Cached analysis available."

        }


    # --------------------------------------------------------
    # Generate unique job ID
    # --------------------------------------------------------

    job_id = str(
        uuid.uuid4()
    )


    # --------------------------------------------------------
    # Create job record
    # --------------------------------------------------------

    with analysis_jobs_lock:

        analysis_jobs[job_id] = {

            "job_id":
                job_id,

            "status":
                "queued",

            "youtube_url":
                youtube_url,

            "video_id":
                None,

            "result":
                None,

            "error":
                None

        }


    # --------------------------------------------------------
    # Start background analysis thread
    # --------------------------------------------------------

    worker = threading.Thread(
        target=run_video_analysis_job,
        args=(
            job_id,
            youtube_url
        ),
        daemon=True
    )


    worker.start()


    print()
    print("=" * 65)

    print(
        "NeuroShield AI - "
        "Analysis Job Created"
    )

    print("=" * 65)

    print(
        "Job ID:",
        job_id
    )

    print(
        "URL:",
        youtube_url
    )

    print("=" * 65)


    # --------------------------------------------------------
    # IMPORTANT:
    # Return immediately.
    # --------------------------------------------------------

    return {

        "status":
            "processing",

        "job_id":
            job_id,

        "message":
            "Video analysis started."

    }


# ============================================================
# ANALYSIS STATUS ENDPOINT
# ============================================================

@app.get(
    "/analysis-status/{job_id}"
)
def analysis_status(
    job_id: str
):

    # --------------------------------------------------------
    # Find job
    # --------------------------------------------------------

    with analysis_jobs_lock:

        job = (
            analysis_jobs.get(
                job_id
            )
        )


        if job is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Analysis job "
                    "not found."
                )
            )


        status = (
            job[
                "status"
            ]
        )


        video_id = (
            job.get(
                "video_id"
            )
        )


        result = (
            job.get(
                "result"
            )
        )


        error = (
            job.get(
                "error"
            )
        )


    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    if status == "complete":

        return {

            "status":
                "complete",

            "job_id":
                job_id,

            "video_id":
                video_id,

            "result":
                result

        }


    # --------------------------------------------------------
    # FAILED
    # --------------------------------------------------------

    if status == "failed":

        return {

            "status":
                "failed",

            "job_id":
                job_id,

            "video_id":
                video_id,

            "error":
                error

        }


    # --------------------------------------------------------
    # STILL RUNNING
    # --------------------------------------------------------

    return {

        "status":
            status,

        "job_id":
            job_id,

        "video_id":
            video_id

    }