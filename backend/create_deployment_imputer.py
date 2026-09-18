# ============================================================
# NeuroShield AI
# Create Deployment Median Values
# ============================================================

from pathlib import Path
import json

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

X_TRAIN_PATH = (
    BASE_DIR /
    "data" /
    "ml" /
    "X_train.csv"
)

OUTPUT_PATH = (
    BASE_DIR /
    "models" /
    "deployment_feature_medians.json"
)


# ============================================================
# LOAD TRAINING DATA
# ============================================================

print()
print("=" * 60)
print("NeuroShield AI - Deployment Median Generator")
print("=" * 60)

print(
    "Loading:",
    X_TRAIN_PATH
)

X_train = pd.read_csv(
    X_TRAIN_PATH
)


# ============================================================
# CALCULATE MEDIANS
# ============================================================

medians = (
    X_train
    .median()
    .to_dict()
)


# Convert numpy values to normal Python floats
medians = {
    feature: float(value)
    for feature, value in medians.items()
}


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        medians,
        file,
        indent=4
    )


print()
print(
    "Features:",
    len(medians)
)

print(
    "Saved:",
    OUTPUT_PATH
)

print()
print(
    "Deployment median values created successfully."
)