"""
===========================================================
FYP CONFIGURATION
Multimodal Explainable AI Framework
===========================================================
"""

# ==========================================================
# VIDEO SETTINGS
# ==========================================================

FRAME_SAMPLE_RATE = 1           # Sample one frame every second
MAX_VIDEO_SECONDS = 300         # Maximum duration to analyse
RESIZE_WIDTH = 160
RESIZE_HEIGHT = 120

# ==========================================================
# VISUAL THRESHOLDS
# ==========================================================

SCENE_THRESHOLD = 0.50
FLICKER_THRESHOLD = 30
MOTION_SPIKE_THRESHOLD = 2.5

# ==========================================================
# AUDIO SETTINGS
# ==========================================================

TARGET_SAMPLE_RATE = 22050

# ==========================================================
# DEVELOPMENTAL WEIGHTS
# ==========================================================

VISUAL_WEIGHT = 0.35
AUDIO_WEIGHT = 0.30
TEXT_WEIGHT = 0.20
BEHAVIOURAL_WEIGHT = 0.15

# ==========================================================
# RANDOM FOREST
# ==========================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20

# ==========================================================
# OUTPUT
# ==========================================================

DATASET_FILE = "data/dataset_v2.csv"

MODEL_FILE = "models/random_forest.pkl"

SHAP_FOLDER = "results/shap"

# ==========================================================
# TEXT FEATURES
# ==========================================================

MIN_SENTENCE_LENGTH = 4

COMMON_EDUCATIONAL_WORDS = [
    "number",
    "numbers",
    "letter",
    "letters",
    "shape",
    "shapes",
    "colour",
    "color",
    "animal",
    "animals",
    "count",
    "counting",
    "learn",
    "learning",
    "alphabet",
    "phonics",
    "math",
    "music",
    "story",
    "stories"
]