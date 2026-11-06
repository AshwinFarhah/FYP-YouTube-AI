# ============================================================
# NeuroShield AI
# Hybrid Framework Analysis - Stage 1
#
# Purpose:
#   1. Load the existing Random Forest test dataset.
#   2. Generate RF class probabilities.
#   3. Convert probabilities into continuous RF Risk Evidence.
#   4. Calculate the existing developmental impact scores.
#   5. Save the combined results for later sensitivity analysis.
#
# IMPORTANT:
#   This script DOES NOT retrain or modify the model.
# ============================================================

import os
import json
import joblib
import pandas as pd
import numpy as np

from backend.developmental_scoring import (
    calculate_developmental_scores
)


# ============================================================
# PATHS
# ============================================================

X_TEST_PATH = "../data/ml/X_test.csv"
Y_TEST_PATH = "../data/ml/y_test.csv"

MODEL_PATH = "../models/random_forest_neuroshield.joblib"
FEATURE_PATH = "../models/random_forest_features.json"

RESULTS_DIR = "../results"

OUTPUT_PATH = os.path.join(
    RESULTS_DIR,
    "hybrid_stage1_results.csv"
)


# ============================================================
# RANDOM FOREST CLASS MAPPING
# ============================================================
#
# Existing LabelEncoder mapping:
#
#   0 = High Risk
#   1 = Low Risk
#   2 = Medium Risk
#
# Risk severity mapping used for continuous RF evidence:
#
#   Low Risk    = 0.0
#   Medium Risk = 0.5
#   High Risk   = 1.0
#
# Therefore:
#
# RF Risk Evidence =
#
#   P(Low)    * 0.0
# + P(Medium) * 0.5
# + P(High)   * 1.0
#
# The result is multiplied by 100.
#
# IMPORTANT:
# RF Risk Evidence is NOT model confidence.
# ============================================================

CLASS_LABELS = {
    0: "High Risk",
    1: "Low Risk",
    2: "Medium Risk"
}

RISK_SEVERITY = {
    "Low Risk": 0.0,
    "Medium Risk": 0.5,
    "High Risk": 1.0
}


# ============================================================
# LOAD FEATURE LIST
# ============================================================

def load_feature_list():

    with open(
        FEATURE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        features = json.load(file)

    return features


# ============================================================
# CALCULATE RF RISK EVIDENCE
# ============================================================

def calculate_rf_risk_evidence(
    class_probabilities,
    model_classes
):

    probability_map = {}

    for class_id, probability in zip(
        model_classes,
        class_probabilities
    ):

        label = CLASS_LABELS[int(class_id)]

        probability_map[label] = float(probability)


    p_low = probability_map.get(
        "Low Risk",
        0.0
    )

    p_medium = probability_map.get(
        "Medium Risk",
        0.0
    )

    p_high = probability_map.get(
        "High Risk",
        0.0
    )


    rf_risk_evidence = (

        p_low
        * RISK_SEVERITY["Low Risk"]

        +

        p_medium
        * RISK_SEVERITY["Medium Risk"]

        +

        p_high
        * RISK_SEVERITY["High Risk"]

    ) * 100.0


    return (
        rf_risk_evidence,
        p_low,
        p_medium,
        p_high
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("NeuroShield AI")
    print("Hybrid Framework Analysis - Stage 1")
    print("=" * 70)


    # ========================================================
    # LOAD RANDOM FOREST
    # ========================================================

    print()
    print("Loading Random Forest model...")

    model = joblib.load(
        MODEL_PATH
    )

    print("Random Forest loaded.")


    # ========================================================
    # LOAD FEATURE LIST
    # ========================================================

    print()
    print("Loading model feature list...")

    feature_names = load_feature_list()

    print(
        f"Expected features: "
        f"{len(feature_names)}"
    )


    # ========================================================
    # LOAD TEST DATA
    # ========================================================

    print()
    print("Loading ML test dataset...")

    X_test = pd.read_csv(
        X_TEST_PATH
    )

    y_test = pd.read_csv(
        Y_TEST_PATH
    )


    # Handle one-column y_test safely

    if y_test.shape[1] == 1:

        y_values = y_test.iloc[:, 0]

    else:

        raise ValueError(
            "Unexpected y_test structure."
        )


    print(
        f"Test samples: "
        f"{len(X_test)}"
    )


    # ========================================================
    # VALIDATE FEATURES
    # ========================================================

    missing_features = [

        feature

        for feature in feature_names

        if feature not in X_test.columns

    ]


    if missing_features:

        raise ValueError(

            "Missing model features in X_test: "
            + ", ".join(
                missing_features
            )

        )


    X_model = X_test[
        feature_names
    ].copy()


    print(
        f"Features used: "
        f"{X_model.shape[1]}"
    )


    # ========================================================
    # RANDOM FOREST PREDICTIONS
    # ========================================================

    print()
    print(
        "Generating Random Forest "
        "probabilities..."
    )


    predictions = model.predict(
        X_model
    )


    probabilities = model.predict_proba(
        X_model
    )


    print(
        "RF probabilities generated."
    )


    # ========================================================
    # BUILD HYBRID ANALYSIS DATA
    # ========================================================

    print()
    print(
        "Calculating RF risk evidence "
        "and developmental scores..."
    )


    results = []


    for index in range(
        len(X_model)
    ):

        feature_row = (
            X_model
            .iloc[index]
            .to_dict()
        )


        # ----------------------------------------------------
        # RF RISK EVIDENCE
        # ----------------------------------------------------

        (
            rf_risk,
            p_low,
            p_medium,
            p_high

        ) = calculate_rf_risk_evidence(

            probabilities[index],
            model.classes_

        )


        predicted_class = int(
            predictions[index]
        )


        predicted_label = (
            CLASS_LABELS[
                predicted_class
            ]
        )


        model_confidence = float(
            np.max(
                probabilities[index]
            )
        ) * 100.0


        # ----------------------------------------------------
        # DEVELOPMENTAL FRAMEWORK
        # ----------------------------------------------------

        developmental = (
            calculate_developmental_scores(
                feature_row
            )
        )


        cognitive = float(
            developmental[
                "cognitive"
            ]
        )

        behavioural = float(
            developmental[
                "behavioural"
            ]
        )

        emotional = float(
            developmental[
                "emotional"
            ]
        )

        overall = float(
            developmental[
                "overall"
            ]
        )


        # ----------------------------------------------------
        # STORE RESULT
        # ----------------------------------------------------

        results.append({

            "sample_index":
                index,

            "actual_class":
                int(
                    y_values.iloc[index]
                ),

            "actual_label":
                CLASS_LABELS[
                    int(
                        y_values.iloc[index]
                    )
                ],

            "predicted_class":
                predicted_class,

            "predicted_label":
                predicted_label,

            "model_confidence":
                model_confidence,

            "probability_low":
                p_low,

            "probability_medium":
                p_medium,

            "probability_high":
                p_high,

            "rf_risk_evidence":
                rf_risk,

            "cognitive_impact":
                cognitive,

            "behavioural_risk":
                behavioural,

            "emotional_stimulation":
                emotional,

            "overall_developmental_impact":
                overall

        })


    results_df = pd.DataFrame(
        results
    )


    # ========================================================
    # SAVE
    # ========================================================

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )


    results_df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("STAGE 1 RESULTS")
    print("=" * 70)


    print()
    print(
        "RF Risk Evidence:"
    )

    print(
        results_df[
            "rf_risk_evidence"
        ].describe().round(2)
    )


    print()
    print(
        "Overall Developmental Impact:"
    )

    print(
        results_df[
            "overall_developmental_impact"
        ].describe().round(2)
    )


    # ========================================================
    # CORRELATION
    # ========================================================

    correlation = (

        results_df[
            [
                "rf_risk_evidence",
                "overall_developmental_impact"
            ]
        ]
        .corr()
        .iloc[0, 1]

    )


    print()
    print(
        "Correlation between RF Risk Evidence "
        "and Overall Developmental Impact:"
    )

    print(
        round(
            correlation,
            4
        )
    )


    # ========================================================
    # MEAN DEVELOPMENTAL SCORE BY RF CLASS
    # ========================================================

    print()
    print(
        "Mean scores by RF predicted class:"
    )

    class_summary = (

        results_df
        .groupby(
            "predicted_label"
        )[
            [
                "rf_risk_evidence",
                "overall_developmental_impact"
            ]
        ]
        .mean()
        .round(2)

    )

    print(
        class_summary
    )


    # ========================================================
    # FIRST FIVE SAMPLES
    # ========================================================

    print()
    print(
        "First five samples:"
    )

    print(

        results_df[
            [
                "predicted_label",
                "model_confidence",
                "rf_risk_evidence",
                "overall_developmental_impact"
            ]
        ]
        .head()
        .round(2)

    )


    print()
    print("=" * 70)

    print(
        "Saved:"
    )

    print(
        OUTPUT_PATH
    )

    print("=" * 70)

    print()
    print(
        "Stage 1 complete."
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()