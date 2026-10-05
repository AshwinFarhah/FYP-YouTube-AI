# ============================================================
# NeuroShield AI
# Feature Reference Range Generator
#
# Purpose:
# Creates descriptive reference ranges for the 42 ML features
# using ONLY the training dataset.
#
# These ranges are used for parent-facing descriptions such as:
#
#   Lower than typical
#   Typical range
#   Higher than typical
#
# IMPORTANT:
# These are dataset-relative descriptive ranges.
# They are NOT clinical or developmental cut-offs.
# ============================================================

import json
import os

import pandas as pd


# ============================================================
# PATHS
# ============================================================

X_TRAIN_PATH = os.path.join(
    "data",
    "ml",
    "X_train.csv"
)

FEATURE_LIST_PATH = os.path.join(
    "models",
    "random_forest_features.json"
)

OUTPUT_PATH = os.path.join(
    "models",
    "feature_reference_ranges.json"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("NeuroShield AI - Feature Reference Range Generator")
    print("=" * 65)
    print()


    # --------------------------------------------------------
    # LOAD TRAINING FEATURES
    # --------------------------------------------------------

    print("Loading training dataset...")

    X_train = pd.read_csv(
        X_TRAIN_PATH
    )

    print(
        f"Training rows: {len(X_train)}"
    )

    print(
        f"Training columns: {len(X_train.columns)}"
    )


    # --------------------------------------------------------
    # LOAD EXPECTED MODEL FEATURES
    # --------------------------------------------------------

    print()
    print("Loading Random Forest feature list...")

    with open(
        FEATURE_LIST_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        feature_names = json.load(file)


    print(
        f"Expected model features: {len(feature_names)}"
    )


    # --------------------------------------------------------
    # VALIDATE FEATURES
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in feature_names
        if feature not in X_train.columns
    ]


    if missing_features:

        raise ValueError(
            "Missing features in X_train.csv: "
            + ", ".join(missing_features)
        )


    # --------------------------------------------------------
    # CREATE REFERENCE RANGES
    # --------------------------------------------------------
    #
    # We use:
    #
    # 25th percentile = lower reference boundary
    # 75th percentile = upper reference boundary
    #
    # Therefore:
    #
    # value < P25
    #     Lower than typical
    #
    # P25 <= value <= P75
    #     Typical range
    #
    # value > P75
    #     Higher than typical
    #
    # This is descriptive relative to the training data.
    # It is NOT a clinical classification.
    # --------------------------------------------------------

    print()
    print("Calculating feature reference ranges...")
    print()


    reference_ranges = {}


    for feature in feature_names:

        values = pd.to_numeric(
            X_train[feature],
            errors="coerce"
        ).dropna()


        if values.empty:

            print(
                f"WARNING: No valid values for {feature}"
            )

            continue


        p05 = float(
            values.quantile(0.05)
        )

        p25 = float(
            values.quantile(0.25)
        )

        median = float(
            values.quantile(0.50)
        )

        p75 = float(
            values.quantile(0.75)
        )

        p95 = float(
            values.quantile(0.95)
        )


        reference_ranges[feature] = {

            "p05": p05,

            "p25": p25,

            "median": median,

            "p75": p75,

            "p95": p95

        }


        print(
            f"{feature:<32} "
            f"P25={p25:.6f}  "
            f"Median={median:.6f}  "
            f"P75={p75:.6f}"
        )


    # --------------------------------------------------------
    # VALIDATE OUTPUT
    # --------------------------------------------------------

    if len(reference_ranges) != len(
        feature_names
    ):

        raise ValueError(
            "Reference range generation did not "
            "produce all expected features."
        )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )


    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            reference_ranges,
            file,
            indent=4
        )


    print()
    print("=" * 65)
    print("REFERENCE RANGE GENERATION COMPLETE")
    print("=" * 65)

    print(
        f"Saved to: {OUTPUT_PATH}"
    )

    print(
        f"Features saved: {len(reference_ranges)}"
    )

    print()
    print(
        "Interpretation:"
    )

    print(
        "  value < P25       -> Lower than typical"
    )

    print(
        "  P25 to P75        -> Typical range"
    )

    print(
        "  value > P75       -> Higher than typical"
    )

    print()
    print(
        "These ranges describe the NeuroShield "
        "training-data distribution only."
    )

    print(
        "They are NOT clinical thresholds."
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()