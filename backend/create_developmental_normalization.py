# ============================================================
# NeuroShield AI
# Developmental Scoring Normalization Generator
# ============================================================

import json
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

X_TRAIN_PATH = BASE_DIR / "data" / "ml" / "X_train.csv"

OUTPUT_PATH = (
    BASE_DIR
    / "models"
    / "developmental_normalization.json"
)


# ============================================================
# DEVELOPMENTAL FEATURES
# ============================================================

DEVELOPMENTAL_FEATURES = [

    # Cognitive
    "motion_mean",
    "motion_spike_rate",
    "scene_rate",
    "loop_detection_score",
    "phrase_repetition",
    "avg_saturation",
    "flicker_rate",

    # Behavioural
    "sound_density",
    "reward_cue_frequency",
    "attention_reset_rate",

    # Emotional
    "loudness",
    "pitch_variation",
    "emotion_arousal",
    "emotion_stability",
]


# ============================================================
# NORMALIZATION SETTINGS
# ============================================================

LOWER_PERCENTILE = 0.05
UPPER_PERCENTILE = 0.95


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("NeuroShield AI - Developmental Normalization")
    print("=" * 65)

    # --------------------------------------------------------
    # Load training data
    # --------------------------------------------------------

    if not X_TRAIN_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {X_TRAIN_PATH}"
        )

    df = pd.read_csv(X_TRAIN_PATH)

    print(f"Training rows: {len(df)}")
    print(f"Training features: {len(df.columns)}")

    # --------------------------------------------------------
    # Validate required features
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in DEVELOPMENTAL_FEATURES
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing developmental features:\n"
            + "\n".join(missing_features)
        )

    # --------------------------------------------------------
    # Calculate normalization bounds
    # --------------------------------------------------------

    normalization = {}

    print()
    print("Normalization bounds:")
    print("-" * 65)

    for feature in DEVELOPMENTAL_FEATURES:

        values = pd.to_numeric(
            df[feature],
            errors="coerce"
        ).dropna()

        if values.empty:
            raise ValueError(
                f"No valid numeric values found for {feature}"
            )

        lower = float(
            values.quantile(LOWER_PERCENTILE)
        )

        upper = float(
            values.quantile(UPPER_PERCENTILE)
        )

        # Prevent division by zero later
        if upper <= lower:

            lower = float(values.min())
            upper = float(values.max())

        if upper <= lower:

            raise ValueError(
                f"Feature has no usable range: {feature}"
            )

        normalization[feature] = {
            "lower": lower,
            "upper": upper,
            "lower_percentile": LOWER_PERCENTILE,
            "upper_percentile": UPPER_PERCENTILE,
        }

        print(
            f"{feature:<30} "
            f"{lower:.6f} -> {upper:.6f}"
        )

    # --------------------------------------------------------
    # Save configuration
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            normalization,
            file,
            indent=4
        )

    print()
    print("=" * 65)
    print("Normalization configuration created successfully.")
    print(f"Features saved: {len(normalization)}")
    print(f"Output: {OUTPUT_PATH}")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()