
# ============================================================
# NeuroShield AI - ML-02
# Random Forest Confusion Matrix Evaluation
# ============================================================

from pathlib import Path
import json
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score
)

# ============================================================
# PATH CONFIGURATION
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

X_TEST_PATH = PROJECT_ROOT / "data/ml/X_test.csv"
Y_TEST_PATH = PROJECT_ROOT / "data/ml/y_test.csv"

OUTPUT_PATH = TEST_DIR / "ml02_confusion_matrix.png"

# ============================================================
# MAIN TEST
# ============================================================

def main():

    model = joblib.load(MODEL_PATH)

    X_test = pd.read_csv(X_TEST_PATH)
    y_test = pd.read_csv(Y_TEST_PATH).iloc[:, 0]

    with open(FEATURE_PATH, "r", encoding="utf-8") as file:
        feature_data = json.load(file)

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
        raise ValueError(f"Missing features: {missing}")

    X_test = X_test[feature_names]

    # Generate predictions
    y_pred = model.predict(X_test)

    # Use the actual labels found in the model and test data
    labels = sorted(set(y_test) | set(y_pred))

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=labels
    )

    # ========================================================
    # SAVE CONFUSION MATRIX
    # ========================================================

    fig, ax = plt.subplots(figsize=(8, 6))

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=[str(label) for label in labels]
    )

    display.plot(
        ax=ax,
        cmap="Blues",
        values_format="d",
        colorbar=False
    )

    ax.set_title(
        "NeuroShield AI - Random Forest Confusion Matrix",
        fontsize=13,
        pad=15
    )

    ax.set_xlabel("Predicted Class")
    ax.set_ylabel("Actual Class")

    fig.tight_layout()

    fig.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    # ========================================================
    # CLEAN TERMINAL OUTPUT
    # ========================================================

    correct = int(cm.trace())
    total = int(cm.sum())
    incorrect = total - correct
    accuracy = accuracy_score(y_test, y_pred)

    print()
    print("=" * 55)
    print("          NeuroShield AI - ML-02")
    print("        Confusion Matrix Evaluation")
    print("=" * 55)

    print(f"\nTesting Samples  : {total}")
    print(f"Features Used    : {len(feature_names)}")
    print(f"Correct Results  : {correct}")
    print(f"Wrong Results    : {incorrect}")
    print(f"Accuracy         : {accuracy * 100:.2f}%")

    print("\n" + "-" * 55)
    print("CONFUSION MATRIX")
    print("-" * 55)

    print(
        pd.DataFrame(
            cm,
            index=[f"Actual {x}" for x in labels],
            columns=[f"Predicted {x}" for x in labels]
        ).to_string()
    )

    print("\n" + "-" * 55)
    print("OUTPUT")
    print("-" * 55)

    print(f"Saved Figure : {OUTPUT_PATH}")
    print("Original results folder : NOT MODIFIED")

    print("\nML-02 EXECUTION: COMPLETE")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
