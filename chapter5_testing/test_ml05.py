
# ============================================================
# NeuroShield AI - ML-05
# Risk Classification Consistency
# ============================================================

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models/random_forest_neuroshield.joblib"
FEATURE_PATH = PROJECT_ROOT / "models/random_forest_features.json"
X_TEST_PATH = PROJECT_ROOT / "data/ml/X_test.csv"


def main():
    model = joblib.load(MODEL_PATH)

    with open(FEATURE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        features = data
    else:
        features = data.get("features") or data.get("feature_names")

    if not features:
        raise ValueError("Feature list could not be loaded.")

    X_test = pd.read_csv(X_TEST_PATH)[features]

    # Predict twice using the same model and dataset
    first = model.predict(X_test)
    second = model.predict(X_test)

    identical = np.array_equal(first, second)
    differences = int(np.sum(first != second))

    passed = (
        identical
        and len(first) == len(second)
        and differences == 0
    )

    print()
    print("=" * 55)
    print("             NeuroShield AI - ML-05")
    print("          Risk Classification Consistency")
    print("=" * 55)

    print(f"\nTesting Samples       : {len(X_test)}")
    print(f"Features Used         : {len(features)}")
    print(f"First Predictions     : {len(first)}")
    print(f"Second Predictions    : {len(second)}")
    print(f"Different Predictions : {differences}")
    print(f"Predictions Identical : {identical}")

    print("\n" + "-" * 55)
    print("Test Status:", "PASS" if passed else "FAIL")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
