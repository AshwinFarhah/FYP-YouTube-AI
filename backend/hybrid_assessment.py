# ============================================================
# NeuroShield AI
# Hybrid Developmental Assessment
# ============================================================
#
# Combines:
#
#   1. Random Forest probability-weighted risk evidence
#   2. Overall developmental impact score
#
# SHAP is NOT included in the numerical hybrid score.
# SHAP remains the explainability layer for the RF prediction.
#
# Locked formulation:
#
#   RF Risk Evidence:
#
#       R = 100 * (
#           0.0 * P(Low)
#         + 0.5 * P(Medium)
#         + 1.0 * P(High)
#       )
#
#   Hybrid Score:
#
#       H = 0.50 * R
#         + 0.50 * D
#
#   where:
#
#       D = Overall Developmental Impact
#
# Locked operational thresholds:
#
#       Low     : H < 28.0
#       Medium  : 28.0 <= H < 68.5
#       High    : H >= 68.5
#
# IMPORTANT:
# The Hybrid Developmental Assessment is a project-defined
# analytical indicator. It is NOT a probability of harm and
# NOT a clinical assessment.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

RF_WEIGHT = 0.50
DEVELOPMENTAL_WEIGHT = 0.50

LOW_MEDIUM_THRESHOLD = 28.0
MEDIUM_HIGH_THRESHOLD = 68.5


# ============================================================
# RF RISK EVIDENCE
# ============================================================

def calculate_rf_risk_evidence(
    probability_low,
    probability_medium,
    probability_high
):
    """
    Convert the Random Forest class-probability distribution
    into continuous ordinal risk evidence on a 0-100 scale.

    Ordered class encoding:

        Low Risk    = 0.0
        Medium Risk = 0.5
        High Risk   = 1.0

    This value is NOT model confidence.
    """

    probability_low = float(probability_low)
    probability_medium = float(probability_medium)
    probability_high = float(probability_high)

    rf_risk_evidence = 100.0 * (

        (0.0 * probability_low)

        +

        (0.5 * probability_medium)

        +

        (1.0 * probability_high)

    )

    return float(rf_risk_evidence)


# ============================================================
# HYBRID CATEGORY
# ============================================================

def get_hybrid_category(
    hybrid_score
):
    """
    Convert the continuous Hybrid Developmental Assessment
    score into the dataset-derived operational category.
    """

    hybrid_score = float(
        hybrid_score
    )

    if hybrid_score < LOW_MEDIUM_THRESHOLD:

        return "Low"

    if hybrid_score < MEDIUM_HIGH_THRESHOLD:

        return "Medium"

    return "High"


# ============================================================
# HYBRID DEVELOPMENTAL ASSESSMENT
# ============================================================

def calculate_hybrid_assessment(
    probability_low,
    probability_medium,
    probability_high,
    overall_developmental_impact
):
    """
    Calculate the complete Hybrid Developmental Assessment.

    H = 0.50(RF Risk Evidence)
      + 0.50(Overall Developmental Impact)
    """

    rf_risk_evidence = (
        calculate_rf_risk_evidence(
            probability_low,
            probability_medium,
            probability_high
        )
    )

    developmental_impact = float(
        overall_developmental_impact
    )

    hybrid_score = (

        RF_WEIGHT
        * rf_risk_evidence

        +

        DEVELOPMENTAL_WEIGHT
        * developmental_impact

    )


    # Defensive bounds.
    #
    # Both inputs are designed to be on 0-100 scales,
    # therefore the weighted result should also remain
    # within 0-100.

    hybrid_score = max(
        0.0,
        min(
            100.0,
            hybrid_score
        )
    )


    hybrid_category = (
        get_hybrid_category(
            hybrid_score
        )
    )


    return {

        "score":
            round(
                hybrid_score,
                2
            ),

        "category":
            hybrid_category,

        "rf_risk_evidence":
            round(
                rf_risk_evidence,
                2
            ),

        "developmental_impact":
            round(
                developmental_impact,
                2
            ),

        "rf_weight":
            RF_WEIGHT,

        "developmental_weight":
            DEVELOPMENTAL_WEIGHT,

        "low_medium_threshold":
            LOW_MEDIUM_THRESHOLD,

        "medium_high_threshold":
            MEDIUM_HIGH_THRESHOLD

    }