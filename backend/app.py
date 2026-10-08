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
import time
import re
import os
import tempfile
from backend.cache_crypto import (
    FORMAT as ENCRYPTED_CACHE_FORMAT,
    encrypt_result, decrypt_result, validate_cache_key,
)
from urllib.parse import urlparse, parse_qs

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StrictStr, ConfigDict

from backend.youtube_downloader import download_youtube_video
from backend.video_analyzer import analyze_video_features

from backend.live_explainability import (
    explain_prediction
)
from backend.hybrid_assessment import (
    calculate_hybrid_assessment
)

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

# Fail closed rather than silently writing unencrypted analysis results.
validate_cache_key()

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

def extract_youtube_video_id(youtube_url: str):
    try:
        parsed = urlparse(youtube_url.strip())

        # Only allow HTTPS YouTube links.
        if parsed.scheme != "https":
            return None

        # Reject credentials and nonstandard ports.
        if parsed.username or parsed.password:
            return None

        try:
            if parsed.port is not None:
                return None
        except ValueError:
            return None

        hostname = (parsed.hostname or "").lower()

        allowed_hosts = {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
            "www.youtu.be",
        }

        if hostname not in allowed_hosts:
            return None

        video_id = None

        if hostname in {"youtu.be", "www.youtu.be"}:
            parts = parsed.path.strip("/").split("/")

            if len(parts) == 1:
                video_id = parts[0]

        else:
            path = parsed.path.rstrip("/")

            if path == "/watch":
                query = parse_qs(parsed.query)
                ids = query.get("v", [])

                if len(ids) == 1:
                    video_id = ids[0]

            elif path.startswith(("/shorts/", "/embed/", "/live/")):
                parts = path.strip("/").split("/")

                if len(parts) == 2:
                    video_id = parts[1]

        if video_id and re.fullmatch(
                r"[A-Za-z0-9_-]{11}",
                video_id
        ):
            return video_id

    except (TypeError, ValueError, AttributeError):
        pass

    return None


def get_cache_path(
        video_id
):
    return (
            CACHE_DIR
            / f"{video_id}.json"
    )


def _atomic_cache_write(cache_path, payload):
    """Replace a cache file atomically; never expose a partial JSON file."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=CACHE_DIR,
                prefix=".cache-", suffix=".tmp", delete=False
        ) as file:
            temp_path = Path(file.name)
            json.dump(payload, file, separators=(",", ":"))
            file.flush()
            os.fsync(file.fileno())
        # Restrict access to the temporary encrypted cache file
        # before replacing the destination.
        if os.name == "posix":
            os.chmod(temp_path, 0o600)

        os.replace(temp_path, cache_path)

        # Restrict access to the completed cache file.
        if os.name == "posix":
            os.chmod(cache_path, 0o600)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def validate_legacy_cache_result(video_id, result):
    """
    Validate the minimum structure of an existing
    plaintext analysis result before encryption.
    """

    if not isinstance(result, dict):
        return False

    required_fields = {
        "video_id",
        "prediction",
        "risk_level",
        "confidence",
        "class_probabilities",
        "hybrid_assessment",
        "developmental_scores",
        "explainability",
    }

    if not required_fields.issubset(result.keys()):
        return False

    if result["video_id"] != video_id:
        return False

    if type(result["prediction"]) is not int:
        return False

    if result["prediction"] not in LABEL_MAPPING:
        return False

    if not isinstance(result["risk_level"], str):
        return False

    if not isinstance(result["confidence"], (int, float)):
        return False

    for field in (
            "class_probabilities",
            "hybrid_assessment",
            "developmental_scores",
            "explainability",
    ):
        if not isinstance(result[field], dict):
            return False

    return True


def load_cached_result(video_id):
    if not video_id:
        return None

    cache_path = get_cache_path(video_id)
    if not cache_path.exists():
        return None

    try:
        with cache_path.open("r", encoding="utf-8") as file:
            stored = json.load(file)

        if isinstance(stored, dict) and stored.get("format") == ENCRYPTED_CACHE_FORMAT:
            result = decrypt_result(video_id, stored)
        elif isinstance(stored, dict) and "format" in stored:
            # Unknown or corrupted encrypted format: never treat it as plaintext.
            raise ValueError("Unrecognized cache envelope")
        elif validate_legacy_cache_result(video_id, stored):
            # One-time migration of legacy plaintext caches on first access.
            result = stored
            _atomic_cache_write(cache_path, encrypt_result(video_id, result))
            print("NeuroShield AI: Legacy cache migrated.")
        else:
            raise ValueError("Invalid legacy cache structure")

        print("NeuroShield AI: Cached result loaded.")
        return result
    except Exception as error:
        print("NeuroShield AI: Could not load authenticated cache:", type(error).__name__)
        # Do not overwrite corrupted or undecryptable cache with new analysis.
        raise RuntimeError("Encrypted analysis cache could not be read") from error


def save_cached_result(video_id, result):
    if not video_id:
        return

    cache_path = get_cache_path(video_id)
    try:
        _atomic_cache_write(cache_path, encrypt_result(video_id, result))
        print("NeuroShield AI: Encrypted result cached.")
    except Exception as error:
        print("NeuroShield AI: Could not save encrypted cache:", type(error).__name__)
        raise RuntimeError("Encrypted analysis cache could not be saved") from error


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
# SECURITY - ANALYSIS JOB RETENTION
# ============================================================

# Retain completed and failed jobs for 24 hours.

JOB_RETENTION_SECONDS = 86400


def cleanup_expired_analysis_jobs():
    current_time = time.time()

    with analysis_jobs_lock:

        expired_job_ids = []

        for job_id, job in analysis_jobs.items():

            if job.get("status") not in (
                    "complete",
                    "failed"
            ):
                continue

            completed_at = job.get(
                "completed_at"
            )

            if completed_at is None:
                continue

            if (
                    current_time - completed_at
                    >= JOB_RETENTION_SECONDS
            ):
                expired_job_ids.append(
                    job_id
                )

        for job_id in expired_job_ids:
            analysis_jobs.pop(
                job_id,
                None
            )

    if expired_job_ids:
        print(
            "NeuroShield AI: Cleaned up",
            len(expired_job_ids),
            "expired analysis jobs."
        )


# ============================================================
# SECURITY - CONCURRENT ANALYSIS LIMIT
# ============================================================

MAX_CONCURRENT_ANALYSES = 2

analysis_semaphore = threading.BoundedSemaphore(
    value=MAX_CONCURRENT_ANALYSES
)

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


# ============================================================
# SECURITY - VIDEO ANALYSIS REQUEST VALIDATION
# ============================================================

class VideoAnalysisRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    youtube_url: StrictStr = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Valid HTTPS YouTube video URL."
    )


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
            "NeuroShield AI: Video analysis request received."
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
        # HYBRID DEVELOPMENTAL ASSESSMENT
        # ====================================================

        print()
        print(
            "Calculating Hybrid Developmental Assessment..."
        )

        developmental_scores = (
            analysis[
                "developmental_scores"
            ]
        )

        hybrid_assessment = (
            calculate_hybrid_assessment(

                probability_low=(
                    class_probabilities[
                        "Low Risk"
                    ]
                ),

                probability_medium=(
                    class_probabilities[
                        "Medium Risk"
                    ]
                ),

                probability_high=(
                    class_probabilities[
                        "High Risk"
                    ]
                ),

                overall_developmental_impact=(
                    developmental_scores[
                        "overall"
                    ]
                )

            )
        )

        print(
            "Hybrid Developmental Assessment:",
            hybrid_assessment[
                "score"
            ],
            "/ 100 -",
            hybrid_assessment[
                "category"
            ]
        )

        # ========================================================
        # EXPLAINABLE AI - SHAP
        # ========================================================

        print()
        print(
            "Generating SHAP explanation..."
        )

        explainability = explain_prediction(
            features,
            int(prediction)
        )

        print(
            "SHAP explanation generated."
        )

        print(
            "NeuroShield AI: Explainability output generated."
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

            "hybrid_assessment":
                hybrid_assessment,

            "developmental_scores":
                developmental_scores,

            "explainability":
                explainability,

            "feature_interpretations":
                analysis[
                    "feature_interpretations"
                ],

            "multimedia_features": {

                "visual": {
                    "motion_mean":
                        float(features["motion_mean"]),

                    "scene_rate":
                        float(features["scene_rate"]),

                    "avg_brightness":
                        float(features["avg_brightness"]),

                    "avg_saturation":
                        float(features["avg_saturation"]),

                    "flicker_rate":
                        float(features["flicker_rate"])
                },

                "audio": {
                    "loudness":
                        float(features["loudness"]),

                    "pitch_variation":
                        float(features["pitch_variation"]),

                    "tempo":
                        float(features["tempo"]),

                    "sound_density":
                        float(features["sound_density"])
                },

                "text": {
                    "phrase_repetition":
                        float(features["phrase_repetition"]),

                    "sentence_complexity":
                        float(features["sentence_complexity"]),

                    "vocabulary_diversity":
                        float(features["vocabulary_diversity"]),

                    "educational_word_ratio":
                        float(features["educational_word_ratio"])
                },

                "engagement": {
                    "reward_cue_frequency":
                        float(features["reward_cue_frequency"]),

                    "attention_reset_rate":
                        float(features["attention_reset_rate"]),

                    "loop_detection_score":
                        float(features["loop_detection_score"]),

                    "motion_spike_rate":
                        float(features["motion_spike_rate"]),

                    "attention_score":
                        float(features["attention_score"])
                }

            },

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

            analysis_jobs[job_id][
                "completed_at"
            ] = time.time()

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
            "Video ID: [redacted]"
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
            "NeuroShield AI - Background Analysis Error:",
            type(error).__name__
        )

        # ====================================================
        # SECURITY - SAFE ERROR RESPONSE
        # ====================================================

        # Keep detailed errors in backend logs.

        # Do not expose Python exception details through the API.

        with analysis_jobs_lock:

            if job_id in analysis_jobs:
                analysis_jobs[job_id]["status"] = "failed"

                analysis_jobs[job_id]["error"] = (

                    "Video analysis could not be completed. "

                    "Please try again."

                )

                analysis_jobs[job_id]["completed_at"] = (

                    time.time()

                )


# ============================================================
# SECURITY - PROTECTED ANALYSIS WORKER
# ============================================================

def run_protected_analysis_job(job_id, youtube_url):
    try:
        run_video_analysis_job(
            job_id,
            youtube_url
        )

    except Exception as error:

        print(
            "NeuroShield AI - Protected worker error:",
            type(error).__name__
        )

        with analysis_jobs_lock:

            if job_id in analysis_jobs:
                analysis_jobs[job_id]["status"] = "failed"

                analysis_jobs[job_id]["error"] = (
                    "Video analysis failed."
                )

                analysis_jobs[job_id]["completed_at"] = (
                    time.time()
                )

    finally:
        # Always release the analysis slot.
        analysis_semaphore.release()


# ============================================================
# START YOUTUBE VIDEO ANALYSIS
# ============================================================

@app.post("/analyze-video")
def analyze_video(
        request: VideoAnalysisRequest
):
    # --------------------------------------------------------
    # SECURITY - CLEAN UP EXPIRED ANALYSIS JOBS
    # --------------------------------------------------------

    cleanup_expired_analysis_jobs()

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
    if video_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported YouTube video URL."
        )

    try:
        cached_result = load_cached_result(video_id)

    except RuntimeError:
        print(
            "NeuroShield AI: Secure cache retrieval failed."
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "The saved video analysis is temporarily "
                "unavailable. Please contact the system "
                "administrator."
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
                    None,

                "completed_at":
                    time.time()

            }

        print()
        print("=" * 65)

        print(
            "NeuroShield AI - Cached Analysis"
        )

        print("=" * 65)

        print(
            "Video ID: [redacted]"
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
    # SECURITY - CHECK AVAILABLE ANALYSIS CAPACITY
    # --------------------------------------------------------

    if not analysis_semaphore.acquire(blocking=False):
        raise HTTPException(
            status_code=429,
            detail=(
                "NeuroShield AI is currently processing "
                "the maximum number of videos. "
                "Please try again shortly."
            )
        )
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

    try:
        worker = threading.Thread(
            target=run_protected_analysis_job,
            args=(
                job_id,
                youtube_url
            ),
            daemon=True
        )

        worker.start()

    except Exception:
        analysis_semaphore.release()

        with analysis_jobs_lock:
            analysis_jobs.pop(job_id, None)

        raise HTTPException(
            status_code=500,
            detail="Unable to start video analysis."
        )

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
        "NeuroShield AI: Analysis job queued."
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
    # SECURITY - CLEAN UP EXPIRED ANALYSIS JOBS
    # --------------------------------------------------------

    cleanup_expired_analysis_jobs()
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
