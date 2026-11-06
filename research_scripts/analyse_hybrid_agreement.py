# ============================================================
# NeuroShield AI
# Hybrid Framework Analysis - Stage 3
#
# RF / Developmental Agreement Analysis
#
# Purpose:
#   Examine agreement and disagreement between:
#
#       RF Risk Evidence
#       Overall Developmental Impact
#
# No hybrid weights or thresholds are selected here.
# ============================================================

import os
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = os.path.join(
    "../results",
    "hybrid_stage1_results.csv"
)

OUTPUT_PATH = os.path.join(
    "../results",
    "hybrid_agreement_results.csv"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 72)
    print("NeuroShield AI")
    print("Hybrid Framework Analysis - Stage 3")
    print("RF / Developmental Agreement Analysis")
    print("=" * 72)


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    print()
    print("Loading Stage 1 results...")

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"Samples loaded: {len(df)}"
    )


    # --------------------------------------------------------
    # CALCULATE DIFFERENCES
    # --------------------------------------------------------

    df["rf_dev_difference"] = (

        df["rf_risk_evidence"]
        -
        df["overall_developmental_impact"]

    )


    df["absolute_rf_dev_difference"] = (

        df["rf_dev_difference"]
        .abs()

    )


    # --------------------------------------------------------
    # BASIC DIFFERENCE STATISTICS
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("ABSOLUTE RF / DEVELOPMENTAL DIFFERENCE")
    print("=" * 72)
    print()


    print(

        df[
            "absolute_rf_dev_difference"
        ]
        .describe()
        .round(2)

    )


    # --------------------------------------------------------
    # DIRECTION OF DIFFERENCE
    # --------------------------------------------------------

    rf_higher = (
        df["rf_dev_difference"] > 0
    ).sum()

    dev_higher = (
        df["rf_dev_difference"] < 0
    ).sum()

    equal = (
        np.isclose(
            df["rf_dev_difference"],
            0
        )
    ).sum()


    print()
    print("=" * 72)
    print("DIRECTION OF DIFFERENCE")
    print("=" * 72)

    print()
    print(
        f"RF evidence higher:       "
        f"{rf_higher} "
        f"({rf_higher / len(df) * 100:.2f}%)"
    )

    print(
        f"Developmental higher:     "
        f"{dev_higher} "
        f"({dev_higher / len(df) * 100:.2f}%)"
    )

    print(
        f"Approximately equal:      "
        f"{equal} "
        f"({equal / len(df) * 100:.2f}%)"
    )


    # --------------------------------------------------------
    # DIFFERENCE MAGNITUDE BANDS
    #
    # These are descriptive analysis bands only.
    # They are NOT risk thresholds.
    # --------------------------------------------------------

    difference = (
        df["absolute_rf_dev_difference"]
    )


    bands = {

        "< 5 points":
            (difference < 5),

        "5 - <10 points":
            (
                (difference >= 5)
                &
                (difference < 10)
            ),

        "10 - <20 points":
            (
                (difference >= 10)
                &
                (difference < 20)
            ),

        "20 - <30 points":
            (
                (difference >= 20)
                &
                (difference < 30)
            ),

        ">= 30 points":
            (difference >= 30)

    }


    print()
    print("=" * 72)
    print("DIFFERENCE MAGNITUDE")
    print("=" * 72)
    print()


    for name, condition in bands.items():

        count = int(
            condition.sum()
        )

        percentage = (
            count
            /
            len(df)
            *
            100
        )

        print(
            f"{name:<18} "
            f"{count:>4} "
            f"({percentage:>6.2f}%)"
        )


    # --------------------------------------------------------
    # DIFFERENCE BY ACTUAL CLASS
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("MEAN DIFFERENCE BY ACTUAL CLASS")
    print("=" * 72)
    print()


    actual_summary = (

        df
        .groupby(
            "actual_label"
        )
        .agg(

            mean_rf=(
                "rf_risk_evidence",
                "mean"
            ),

            mean_dev=(
                "overall_developmental_impact",
                "mean"
            ),

            mean_signed_difference=(
                "rf_dev_difference",
                "mean"
            ),

            mean_absolute_difference=(
                "absolute_rf_dev_difference",
                "mean"
            )

        )
        .round(2)

    )


    print(
        actual_summary
    )


    # --------------------------------------------------------
    # DIFFERENCE BY PREDICTED CLASS
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("MEAN DIFFERENCE BY RF PREDICTED CLASS")
    print("=" * 72)
    print()


    predicted_summary = (

        df
        .groupby(
            "predicted_label"
        )
        .agg(

            mean_rf=(
                "rf_risk_evidence",
                "mean"
            ),

            mean_dev=(
                "overall_developmental_impact",
                "mean"
            ),

            mean_signed_difference=(
                "rf_dev_difference",
                "mean"
            ),

            mean_absolute_difference=(
                "absolute_rf_dev_difference",
                "mean"
            )

        )
        .round(2)

    )


    print(
        predicted_summary
    )


    # --------------------------------------------------------
    # MOST DISAGREEMENT
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("15 LARGEST RF / DEVELOPMENTAL DIFFERENCES")
    print("=" * 72)
    print()


    largest = (

        df[
            [
                "sample_index",
                "actual_label",
                "predicted_label",
                "model_confidence",
                "rf_risk_evidence",
                "overall_developmental_impact",
                "rf_dev_difference",
                "absolute_rf_dev_difference"
            ]
        ]
        .sort_values(
            "absolute_rf_dev_difference",
            ascending=False
        )
        .head(15)
        .round(2)

    )


    print(
        largest.to_string(
            index=False
        )
    )


    # --------------------------------------------------------
    # RF HIGHER CASES
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("LARGEST CASES WHERE RF > DEVELOPMENTAL")
    print("=" * 72)
    print()


    rf_dominant = (

        df[
            df["rf_dev_difference"] > 0
        ][
            [
                "sample_index",
                "actual_label",
                "predicted_label",
                "rf_risk_evidence",
                "overall_developmental_impact",
                "rf_dev_difference"
            ]
        ]
        .sort_values(
            "rf_dev_difference",
            ascending=False
        )
        .head(10)
        .round(2)

    )


    print(
        rf_dominant.to_string(
            index=False
        )
    )


    # --------------------------------------------------------
    # DEVELOPMENTAL HIGHER CASES
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("LARGEST CASES WHERE DEVELOPMENTAL > RF")
    print("=" * 72)
    print()


    dev_dominant = (

        df[
            df["rf_dev_difference"] < 0
        ][
            [
                "sample_index",
                "actual_label",
                "predicted_label",
                "rf_risk_evidence",
                "overall_developmental_impact",
                "rf_dev_difference"
            ]
        ]
        .sort_values(
            "rf_dev_difference",
            ascending=True
        )
        .head(10)
        .round(2)

    )


    print(
        dev_dominant.to_string(
            index=False
        )
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    print()
    print("=" * 72)

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print("=" * 72)

    print()
    print(
        "Stage 3 agreement analysis complete."
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()