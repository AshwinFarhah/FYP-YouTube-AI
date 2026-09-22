# ============================================================
# NeuroShield AI
# Hybrid Framework Analysis - Stage 4
#
# Hybrid Threshold Analysis
#
# Hybrid:
#
# H = 0.50(RF Risk Evidence)
#   + 0.50(Overall Developmental Impact)
#
# Purpose:
#   Estimate stable Low / Medium / High operational
#   thresholds using stratified cross-validation.
#
# IMPORTANT:
#   These are dataset-derived operational thresholds.
#   They are NOT clinical cut-offs.
# ============================================================

import os
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = os.path.join(
    "results",
    "hybrid_stage1_results.csv"
)

OUTPUT_PATH = os.path.join(
    "results",
    "hybrid_threshold_analysis.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

N_SPLITS = 5
RANDOM_STATE = 42

# Search thresholds from 0 to 100.
# 0.5 gives reasonably fine resolution without making
# the search unnecessarily large.

THRESHOLD_STEP = 0.5


# ============================================================
# LABEL ENCODING
# ============================================================

LABEL_TO_ORDINAL = {
    "Low Risk": 0,
    "Medium Risk": 1,
    "High Risk": 2
}

ORDINAL_TO_LABEL = {
    0: "Low Risk",
    1: "Medium Risk",
    2: "High Risk"
}


# ============================================================
# HYBRID CLASSIFICATION
# ============================================================

def classify_hybrid(scores, low_threshold, high_threshold):

    scores = np.asarray(scores)

    predictions = np.ones(
        len(scores),
        dtype=int
    )

    predictions[
        scores < low_threshold
    ] = 0

    predictions[
        scores >= high_threshold
    ] = 2

    return predictions


# ============================================================
# FIND BEST THRESHOLDS
# ============================================================

def find_best_thresholds(scores, labels):

    best_result = None

    candidates = np.arange(
        0.0,
        100.0 + THRESHOLD_STEP,
        THRESHOLD_STEP
    )

    for low_threshold in candidates:

        for high_threshold in candidates:

            if high_threshold <= low_threshold:
                continue

            predictions = classify_hybrid(
                scores,
                low_threshold,
                high_threshold
            )

            macro_f1 = f1_score(
                labels,
                predictions,
                average="macro",
                zero_division=0
            )

            accuracy = accuracy_score(
                labels,
                predictions
            )

            # Primary criterion:
            # highest macro F1.
            #
            # Tie-breaker:
            # highest accuracy.

            candidate_result = {
                "low_threshold":
                    low_threshold,

                "high_threshold":
                    high_threshold,

                "macro_f1":
                    macro_f1,

                "accuracy":
                    accuracy
            }

            if best_result is None:

                best_result = candidate_result

            elif (
                candidate_result["macro_f1"]
                >
                best_result["macro_f1"]
            ):

                best_result = candidate_result

            elif (
                np.isclose(
                    candidate_result["macro_f1"],
                    best_result["macro_f1"]
                )
                and
                candidate_result["accuracy"]
                >
                best_result["accuracy"]
            ):

                best_result = candidate_result

    return best_result


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 74)
    print("NeuroShield AI")
    print("Hybrid Framework Analysis - Stage 4")
    print("Hybrid Threshold Analysis")
    print("=" * 74)


    # ========================================================
    # LOAD DATA
    # ========================================================

    print()
    print("Loading Stage 1 results...")

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"Samples loaded: {len(df)}"
    )


    # ========================================================
    # CALCULATE LOCKED 50/50 HYBRID SCORE
    # ========================================================

    df["hybrid_score"] = (

        0.50
        * df["rf_risk_evidence"]

        +

        0.50
        * df[
            "overall_developmental_impact"
        ]

    )


    labels = (

        df["actual_label"]
        .map(
            LABEL_TO_ORDINAL
        )
        .to_numpy()

    )

    scores = (
        df["hybrid_score"]
        .to_numpy()
    )


    # ========================================================
    # SHOW SCORE DISTRIBUTION
    # ========================================================

    print()
    print("=" * 74)
    print("50/50 HYBRID SCORE DISTRIBUTION")
    print("=" * 74)
    print()

    print(
        df["hybrid_score"]
        .describe()
        .round(2)
    )


    print()
    print(
        "Hybrid score by actual class:"
    )

    print()

    class_distribution = (

        df
        .groupby(
            "actual_label"
        )["hybrid_score"]
        .agg(
            [
                "count",
                "mean",
                "std",
                "min",
                "median",
                "max"
            ]
        )
        .round(2)

    )

    print(
        class_distribution
    )


    # ========================================================
    # STRATIFIED CROSS-VALIDATION
    # ========================================================

    print()
    print("=" * 74)
    print("5-FOLD THRESHOLD CROSS-VALIDATION")
    print("=" * 74)
    print()


    skf = StratifiedKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE
    )


    fold_results = []

    all_validation_actual = []
    all_validation_predictions = []


    for fold_number, (
        train_index,
        validation_index
    ) in enumerate(
        skf.split(scores, labels),
        start=1
    ):

        train_scores = scores[
            train_index
        ]

        train_labels = labels[
            train_index
        ]

        validation_scores = scores[
            validation_index
        ]

        validation_labels = labels[
            validation_index
        ]


        # Find thresholds using only this fold's
        # threshold-training portion.

        best = find_best_thresholds(
            train_scores,
            train_labels
        )


        low_threshold = (
            best["low_threshold"]
        )

        high_threshold = (
            best["high_threshold"]
        )


        # Apply those thresholds to the unseen
        # validation portion of this fold.

        validation_predictions = (
            classify_hybrid(
                validation_scores,
                low_threshold,
                high_threshold
            )
        )


        accuracy = accuracy_score(
            validation_labels,
            validation_predictions
        )

        precision = precision_score(
            validation_labels,
            validation_predictions,
            average="macro",
            zero_division=0
        )

        recall = recall_score(
            validation_labels,
            validation_predictions,
            average="macro",
            zero_division=0
        )

        macro_f1 = f1_score(
            validation_labels,
            validation_predictions,
            average="macro",
            zero_division=0
        )


        fold_results.append({

            "fold":
                fold_number,

            "low_threshold":
                low_threshold,

            "high_threshold":
                high_threshold,

            "accuracy":
                accuracy,

            "macro_precision":
                precision,

            "macro_recall":
                recall,

            "macro_f1":
                macro_f1

        })


        all_validation_actual.extend(
            validation_labels
        )

        all_validation_predictions.extend(
            validation_predictions
        )


        print(
            f"Fold {fold_number}: "
            f"Low/Medium = {low_threshold:.1f}, "
            f"Medium/High = {high_threshold:.1f}, "
            f"Accuracy = {accuracy:.4f}, "
            f"Macro F1 = {macro_f1:.4f}"
        )


    fold_df = pd.DataFrame(
        fold_results
    )


    # ========================================================
    # THRESHOLD STABILITY
    # ========================================================

    print()
    print("=" * 74)
    print("THRESHOLD STABILITY")
    print("=" * 74)
    print()


    print(
        fold_df[
            [
                "low_threshold",
                "high_threshold"
            ]
        ]
        .describe()
        .round(2)
    )


    # ========================================================
    # CROSS-VALIDATED PERFORMANCE
    # ========================================================

    print()
    print("=" * 74)
    print("CROSS-VALIDATED PERFORMANCE")
    print("=" * 74)
    print()


    print(
        fold_df[
            [
                "accuracy",
                "macro_precision",
                "macro_recall",
                "macro_f1"
            ]
        ]
        .agg(
            [
                "mean",
                "std"
            ]
        )
        .round(4)
    )


    # ========================================================
    # OUT-OF-FOLD CONFUSION MATRIX
    # ========================================================

    print()
    print("=" * 74)
    print("OUT-OF-FOLD CONFUSION MATRIX")
    print("=" * 74)
    print()


    cm = confusion_matrix(
        all_validation_actual,
        all_validation_predictions,
        labels=[0, 1, 2]
    )


    cm_df = pd.DataFrame(
        cm,
        index=[
            "Actual Low",
            "Actual Medium",
            "Actual High"
        ],
        columns=[
            "Pred Low",
            "Pred Medium",
            "Pred High"
        ]
    )


    print(
        cm_df
    )


    # ========================================================
    # FINAL THRESHOLD ESTIMATE
    #
    # Median CV threshold is used because it is less affected
    # by one unusually high or low fold estimate.
    # ========================================================

    final_low_threshold = float(
        fold_df[
            "low_threshold"
        ].median()
    )

    final_high_threshold = float(
        fold_df[
            "high_threshold"
        ].median()
    )


    print()
    print("=" * 74)
    print("CROSS-VALIDATED THRESHOLD ESTIMATE")
    print("=" * 74)

    print()
    print(
        f"Low / Medium boundary: "
        f"{final_low_threshold:.2f}"
    )

    print(
        f"Medium / High boundary: "
        f"{final_high_threshold:.2f}"
    )


    # ========================================================
    # APPLY ESTIMATED THRESHOLDS FOR DESCRIPTIVE SUMMARY
    # ========================================================

    df[
        "hybrid_category"
    ] = classify_hybrid(
        scores,
        final_low_threshold,
        final_high_threshold
    )


    df[
        "hybrid_category_label"
    ] = (

        df["hybrid_category"]
        .map(
            ORDINAL_TO_LABEL
        )

    )


    print()
    print(
        "Category counts using estimated thresholds:"
    )

    print()

    print(
        df[
            "hybrid_category_label"
        ]
        .value_counts()
    )


    # ========================================================
    # SAVE
    # ========================================================

    fold_df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    print()
    print("=" * 74)

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print("=" * 74)

    print()
    print(
        "Stage 4 threshold analysis complete."
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()