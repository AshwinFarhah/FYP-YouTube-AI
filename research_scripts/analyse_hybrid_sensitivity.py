# ============================================================
# NeuroShield AI
# Hybrid Framework Analysis - Stage 2
#
# Weight Sensitivity Analysis
#
# This script DOES NOT modify the model, backend, dataset,
# developmental scoring framework, or browser extension.
# ============================================================

import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_PATH = os.path.join(
    "../results",
    "hybrid_stage1_results.csv"
)

OUTPUT_PATH = os.path.join(
    "../results",
    "hybrid_sensitivity_results.csv"
)


# ============================================================
# CANDIDATE WEIGHTS
# ============================================================

WEIGHT_CONFIGURATIONS = {

    "RF30_DEV70": (0.30, 0.70),

    "RF40_DEV60": (0.40, 0.60),

    "RF50_DEV50": (0.50, 0.50),

    "RF60_DEV40": (0.60, 0.40),

    "RF70_DEV30": (0.70, 0.30),

}


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 72)
    print("NeuroShield AI")
    print("Hybrid Framework Analysis - Stage 2")
    print("Weight Sensitivity Analysis")
    print("=" * 72)


    # --------------------------------------------------------
    # LOAD STAGE 1 RESULTS
    # --------------------------------------------------------

    print()
    print("Loading Stage 1 results...")

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"Samples loaded: {len(df)}"
    )


    required_columns = [

        "rf_risk_evidence",
        "overall_developmental_impact"

    ]


    for column in required_columns:

        if column not in df.columns:

            raise ValueError(
                f"Missing required column: {column}"
            )


    # --------------------------------------------------------
    # CALCULATE EACH HYBRID CONFIGURATION
    # --------------------------------------------------------

    print()
    print("Calculating candidate hybrid scores...")


    hybrid_columns = []


    for name, weights in WEIGHT_CONFIGURATIONS.items():

        rf_weight, dev_weight = weights

        column_name = (
            f"hybrid_{name.lower()}"
        )


        df[column_name] = (

            rf_weight
            * df["rf_risk_evidence"]

            +

            dev_weight
            * df[
                "overall_developmental_impact"
            ]

        )


        hybrid_columns.append(
            column_name
        )


    print("Hybrid scores calculated.")


    # --------------------------------------------------------
    # DISTRIBUTION SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("HYBRID SCORE DISTRIBUTIONS")
    print("=" * 72)


    summary = (

        df[
            hybrid_columns
        ]
        .describe()
        .loc[
            [
                "mean",
                "std",
                "min",
                "25%",
                "50%",
                "75%",
                "max"
            ]
        ]
        .T
        .round(2)

    )


    print()
    print(summary)


    # --------------------------------------------------------
    # SCORE CORRELATION BETWEEN CONFIGURATIONS
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("CORRELATION BETWEEN WEIGHT CONFIGURATIONS")
    print("=" * 72)
    print()


    correlation_matrix = (

        df[
            hybrid_columns
        ]
        .corr()
        .round(4)

    )


    print(
        correlation_matrix
    )


    # --------------------------------------------------------
    # MEAN HYBRID SCORE BY ACTUAL CLASS
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("MEAN HYBRID SCORE BY ACTUAL CLASS")
    print("=" * 72)
    print()


    actual_summary = (

        df
        .groupby(
            "actual_label"
        )[
            hybrid_columns
        ]
        .mean()
        .round(2)

    )


    print(
        actual_summary
    )


    # --------------------------------------------------------
    # MEAN HYBRID SCORE BY RF PREDICTED CLASS
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print("MEAN HYBRID SCORE BY RF PREDICTED CLASS")
    print("=" * 72)
    print()


    predicted_summary = (

        df
        .groupby(
            "predicted_label"
        )[
            hybrid_columns
        ]
        .mean()
        .round(2)

    )


    print(
        predicted_summary
    )


    # --------------------------------------------------------
    # DIFFERENCE FROM 50/50 REFERENCE
    # --------------------------------------------------------

    reference_column = (
        "hybrid_rf50_dev50"
    )


    print()
    print("=" * 72)
    print("CHANGE RELATIVE TO 50/50 CONFIGURATION")
    print("=" * 72)
    print()


    difference_results = []


    for column in hybrid_columns:

        difference = (

            df[column]
            -
            df[reference_column]

        ).abs()


        difference_results.append({

            "configuration":
                column,

            "mean_absolute_change":
                difference.mean(),

            "median_absolute_change":
                difference.median(),

            "maximum_change":
                difference.max()

        })


    difference_df = pd.DataFrame(
        difference_results
    )


    print(

        difference_df
        .round(2)
        .to_string(
            index=False
        )

    )


    # --------------------------------------------------------
    # RANGE ACROSS ALL WEIGHT CONFIGURATIONS
    # --------------------------------------------------------

    df[
        "hybrid_weight_range"
    ] = (

        df[
            hybrid_columns
        ].max(
            axis=1
        )

        -

        df[
            hybrid_columns
        ].min(
            axis=1
        )

    )


    print()
    print("=" * 72)
    print("PER-VIDEO WEIGHT SENSITIVITY")
    print("=" * 72)
    print()


    print(

        df[
            "hybrid_weight_range"
        ]
        .describe()
        .round(2)

    )


    # --------------------------------------------------------
    # LARGEST SENSITIVITY CASES
    # --------------------------------------------------------

    print()
    print(
        "10 videos most affected by "
        "weight selection:"
    )

    print()


    sensitive_cases = (

        df[
            [
                "sample_index",
                "actual_label",
                "predicted_label",
                "rf_risk_evidence",
                "overall_developmental_impact",
                "hybrid_weight_range"
            ]
        ]
        .sort_values(
            "hybrid_weight_range",
            ascending=False
        )
        .head(10)
        .round(2)

    )


    print(
        sensitive_cases.to_string(
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
        "Stage 2 sensitivity analysis complete."
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()