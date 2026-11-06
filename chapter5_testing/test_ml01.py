
# ============================================================
# NeuroShield AI - ML-01
# Random Forest Classification Accuracy Test
# ============================================================

import os
import json
import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# ============================================================
# FILE PATHS
# ============================================================

MODEL_PATH = "../models/random_forest_neuroshield.joblib"
FEATURE_PATH = "../models/random_forest_features.json"

X_TEST_PATH = "../data/ml/X_test.csv"
Y_TEST_PATH = "../data/ml/y_test.csv"

# ============================================================
# LOAD MODEL AND DATA
# ============================================================

def main():

    model = joblib.load(MODEL_PATH)

    X_test = pd.read_csv(X_TEST_PATH)
    y_test = pd.read_csv(Y_TEST_PATH).iloc[:, 0]

    with open(FEATURE_PATH, "r", encoding="utf-8") as file:
        feature_data = json.load(file)

    # Support feature list stored as a list or dictionary
    if isinstance(feature_data, list):
        feature_names = feature_data
    elif isinstance(feature_data, dict):
        feature_names = (
            feature_data.get("features")
            or feature_data.get("feature_names")
        )
    else:
        raise ValueError("Unsupported feature list format.")

    if not feature_names:
        raise ValueError("Feature names could not be loaded.")

    missing = [
        feature for feature in feature_names
        if feature not in X_test.columns
    ]

    if missing:
        raise ValueError(
            f"Missing test features: {missing}"
        )

    X_test = X_test[feature_names]

    # ========================================================
    # PREDICTION
    # ========================================================

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(
        y_test, y_pred,
        average="weighted",
        zero_division=0
    )
    recall = recall_score(
        y_test, y_pred,
        average="weighted",
        zero_division=0
    )
    f1 = f1_score(
        y_test, y_pred,
        average="weighted",
        zero_division=0
    )

    correct = (y_test.to_numpy() == y_pred).sum()
    total = len(y_test)

    # ========================================================
    # CLEAN OUTPUT
    # ========================================================

    print("\n" + "=" * 55)
    print("         NeuroShield AI - ML-01")
    print("       Random Forest Classification")
    print("=" * 55)

    print(f"\nTesting Samples : {total}")
    print(f"Features Used   : {len(feature_names)}")
    print(f"Correct Results : {correct}")
    print(f"Wrong Results   : {total - correct}")

    print("\n" + "-" * 55)
    print("PERFORMANCE METRICS")
    print("-" * 55)

    print(f"Accuracy        : {accuracy * 100:.2f}%")
    print(f"Precision       : {precision * 100:.2f}%")
    print(f"Recall          : {recall * 100:.2f}%")
    print(f"F1-Score        : {f1 * 100:.2f}%")

    print("\n" + "-" * 55)
    print("CLASSIFICATION REPORT")
    print("-" * 55)

    print(classification_report(
        y_test,
        y_pred,
        zero_division=0
    ))

    print("=" * 55)
    print("ML-01 EXECUTION: COMPLETE")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
