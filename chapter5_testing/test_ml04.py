
# ============================================================
# NeuroShield AI - ML-04
# Random Forest Feature Importance Evaluation
# ============================================================

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    PROJECT_ROOT / "models" /
    "random_forest_neuroshield.joblib"
)

FEATURE_PATH = (
    PROJECT_ROOT / "models" /
    "random_forest_features.json"
)

CSV_PATH = TEST_DIR / "ml04_feature_importance.csv"
CHART_PATH = TEST_DIR / "ml04_top10_features.png"

# ============================================================
# MAIN TEST
# ============================================================

def main():

    model = joblib.load(MODEL_PATH)

    with open(FEATURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        features = data
    elif isinstance(data, dict):
        features = (
            data.get("features")
            or data.get("feature_names")
        )
    else:
        raise ValueError("Invalid feature list format.")

    if not features:
        raise ValueError("Feature list is empty.")

    importances = np.asarray(
        model.feature_importances_,
        dtype=float
    )

    if len(features) != len(importances):
        raise ValueError(
            "Feature count does not match model importance count."
        )

    valid = (
        len(features) == 42
        and np.isfinite(importances).all()
        and (importances >= 0).all()
        and np.isclose(importances.sum(), 1.0)
    )

    df = pd.DataFrame({
        "Feature": features,
        "Importance": importances
    })

    df = df.sort_values(
        "Importance",
        ascending=False
    ).reset_index(drop=True)

    df.insert(
        0,
        "Rank",
        range(1, len(df) + 1)
    )

    # Save CSV outside original results folder
    df.to_csv(CSV_PATH, index=False)

    # ========================================================
    # TOP 10 FEATURE CHART
    # ========================================================

    top10 = df.head(10)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        top10["Feature"][::-1],
        top10["Importance"][::-1]
    )

    ax.set_xlabel("Feature Importance Score")
    ax.set_title(
        "NeuroShield AI - Top 10 Random Forest Features"
    )

    fig.tight_layout()
    fig.savefig(
        CHART_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # ========================================================
    # CLEAN TERMINAL OUTPUT
    # ========================================================

    print()
    print("=" * 65)
    print("              NeuroShield AI - ML-04")
    print("          Random Forest Feature Importance")
    print("=" * 65)

    print(f"\nTotal Features : {len(features)}")
    print(f"Importance Sum : {importances.sum():.6f}")
    print(f"Valid Values   : {valid}")

    print("\n" + "-" * 65)
    print("TOP 10 MOST IMPORTANT FEATURES")
    print("-" * 65)

    print(
        top10.to_string(
            index=False,
            formatters={
                "Importance": "{:.6f}".format
            }
        )
    )

    print("\n" + "-" * 65)
    print("OUTPUT FILES")
    print("-" * 65)

    print(f"CSV   : {CSV_PATH}")
    print(f"Chart : {CHART_PATH}")

    print("\nTest Status:", "PASS" if valid else "FAIL")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
