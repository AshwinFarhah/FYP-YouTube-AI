# ============================================================
# NeuroShield AI
# Random Forest Training & Evaluation
# ============================================================

import os
import json
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


# ============================================================
# CONFIGURATION
# ============================================================

X_TRAIN_PATH = "../data/ml/X_train.csv"
X_TEST_PATH = "../data/ml/X_test.csv"

Y_TRAIN_PATH = "../data/ml/y_train.csv"
Y_TEST_PATH = "../data/ml/y_test.csv"

MODEL_DIR = "../models"
RESULTS_DIR = "../results"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_neuroshield.joblib"
)

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_features.json"
)

FEATURE_IMPORTANCE_PATH = os.path.join(
    RESULTS_DIR,
    "random_forest_feature_importance.csv"
)

CONFUSION_MATRIX_PATH = os.path.join(
    RESULTS_DIR,
    "random_forest_confusion_matrix.png"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("NEUROSHIELD AI - RANDOM FOREST TRAINING & EVALUATION")
    print("=" * 65)


    # ========================================================
    # CREATE DIRECTORIES
    # ========================================================

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)


    # ========================================================
    # LOAD DATA
    # ========================================================

    print()
    print("📂 Loading training and testing data...")

    X_train = pd.read_csv(X_TRAIN_PATH)
    X_test = pd.read_csv(X_TEST_PATH)

    y_train = pd.read_csv(Y_TRAIN_PATH)
    y_test = pd.read_csv(Y_TEST_PATH)

    print("✅ Data loaded successfully.")


    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    print()
    print("=" * 65)
    print("DATASET INFORMATION")
    print("=" * 65)

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")
    print(f"ML features:      {X_train.shape[1]}")


    # ========================================================
    # CONVERT TARGET TO 1D
    # ========================================================

    y_train = y_train.iloc[:, 0]
    y_test = y_test.iloc[:, 0]


    # ========================================================
    # FEATURE VALIDATION
    # ========================================================

    print()
    print("=" * 65)
    print("FEATURE VALIDATION")
    print("=" * 65)

    train_features = list(X_train.columns)
    test_features = list(X_test.columns)

    if train_features != test_features:

        print(
            "❌ ERROR: Training and testing features "
            "do not match."
        )

        raise ValueError(
            "Training and testing feature sets "
            "must be identical."
        )

    print("✅ Training and testing features match.")


    # ========================================================
    # MISSING VALUE CHECK
    # ========================================================

    print()
    print("=" * 65)
    print("MISSING VALUE CHECK")
    print("=" * 65)

    train_missing = X_train.isnull().sum().sum()
    test_missing = X_test.isnull().sum().sum()

    print(
        f"Training missing values: {train_missing}"
    )

    print(
        f"Testing missing values:  {test_missing}"
    )

    if train_missing > 0 or test_missing > 0:

        raise ValueError(
            "Missing values detected. "
            "Please run prepare_ml_dataset.py again."
        )

    print("✅ No missing values detected.")


    # ========================================================
    # TARGET DISTRIBUTION
    # ========================================================

    print()
    print("=" * 65)
    print("TARGET CLASS DISTRIBUTION")
    print("=" * 65)

    print("\nTraining:")
    print(y_train.value_counts())

    print("\nTesting:")
    print(y_test.value_counts())


    # ========================================================
    # RANDOM FOREST TRAINING
    # ========================================================

    print()
    print("=" * 65)
    print("RANDOM FOREST TRAINING")
    print("=" * 65)

    print()
    print("🌲 Initializing Random Forest...")

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )

    print("🌲 Training model...")

    model.fit(
        X_train,
        y_train
    )

    print("✅ Random Forest training completed.")


    # ========================================================
    # MODEL INFORMATION
    # ========================================================

    print()
    print("=" * 65)
    print("MODEL INFORMATION")
    print("=" * 65)

    print(
        "Algorithm: Random Forest Classifier"
    )

    print(
        f"Number of trees: {model.n_estimators}"
    )

    print(
        f"Number of features: {X_train.shape[1]}"
    )

    print(
        f"Classes: {list(model.classes_)}"
    )


    # ========================================================
    # PREDICTIONS
    # ========================================================

    print()
    print("=" * 65)
    print("MODEL PREDICTION")
    print("=" * 65)

    print()
    print("🔍 Generating predictions...")

    y_pred = model.predict(X_test)

    print("✅ Predictions generated.")


    # ========================================================
    # MODEL EVALUATION
    # ========================================================

    print()
    print("=" * 65)
    print("MODEL EVALUATION")
    print("=" * 65)

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    print()
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")


    # ========================================================
    # CLASSIFICATION REPORT
    # ========================================================

    print()
    print("=" * 65)
    print("CLASSIFICATION REPORT")
    print("=" * 65)

    print()

    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )


    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    print()
    print("=" * 65)
    print("CONFUSION MATRIX")
    print("=" * 65)

    class_names = [
        "High Risk",
        "Low Risk",
        "Medium Risk"
    ]

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1, 2]
    )

    print()
    print("Rows = Actual class")
    print("Columns = Predicted class")

    print()

    print(
        pd.DataFrame(
            cm,
            index=[
                "Actual High Risk",
                "Actual Low Risk",
                "Actual Medium Risk"
            ],
            columns=[
                "Predicted High Risk",
                "Predicted Low Risk",
                "Predicted Medium Risk"
            ]
        )
    )


    # ========================================================
    # CONFUSION MATRIX VISUALIZATION
    # ========================================================

    print()
    print(
        "📊 Generating confusion matrix visualization..."
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names
    )

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    display.plot(
        ax=ax,
        values_format="d"
    )

    ax.set_title(
        "NeuroShield AI - Random Forest Confusion Matrix"
    )

    ax.set_xlabel(
        "Predicted Risk Level"
    )

    ax.set_ylabel(
        "Actual Risk Level"
    )

    plt.tight_layout()

    plt.savefig(
        CONFUSION_MATRIX_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"✅ Confusion matrix saved:"
        f"\n   {CONFUSION_MATRIX_PATH}"
    )


    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    print()
    print("=" * 65)
    print("FEATURE IMPORTANCE")
    print("=" * 65)

    feature_importance = pd.DataFrame({
        "feature": X_train.columns,
        "importance": model.feature_importances_
    })

    feature_importance = feature_importance.sort_values(
        by="importance",
        ascending=False
    )

    print()
    print("Top 15 features:")

    for _, row in feature_importance.head(15).iterrows():

        print(
            f"{row['feature']:<35}"
            f"{row['importance']:.6f}"
        )


    # ========================================================
    # SAVE FEATURE IMPORTANCE
    # ========================================================

    feature_importance.to_csv(
        FEATURE_IMPORTANCE_PATH,
        index=False
    )

    print()

    print(
        f"✅ Feature importance saved:"
        f"\n   {FEATURE_IMPORTANCE_PATH}"
    )


    # ========================================================
    # SAVE MODEL
    # ========================================================

    print()
    print("=" * 65)
    print("SAVING MODEL")
    print("=" * 65)

    joblib.dump(
        model,
        MODEL_PATH
    )

    print()

    print(
        f"✅ Model saved:"
        f"\n   {MODEL_PATH}"
    )


    # ========================================================
    # SAVE FEATURE ORDER
    # ========================================================

    with open(
        FEATURE_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            train_features,
            file,
            indent=4
        )

    print()

    print(
        f"✅ Feature list saved:"
        f"\n   {FEATURE_PATH}"
    )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 65)
    print(
        "RANDOM FOREST TRAINING & EVALUATION COMPLETE"
    )
    print("=" * 65)

    print()

    print("Dataset:             1,650 videos")
    print(
        f"Training samples:    {len(X_train)}"
    )
    print(
        f"Testing samples:     {len(X_test)}"
    )
    print(
        f"Features:            {X_train.shape[1]}"
    )

    print(
        "Model:               Random Forest"
    )

    print(
        f"Trees:               {model.n_estimators}"
    )

    print()

    print(
        f"Accuracy:            {accuracy:.4f}"
    )

    print(
        f"Precision:           {precision:.4f}"
    )

    print(
        f"Recall:              {recall:.4f}"
    )

    print(
        f"F1-score:            {f1:.4f}"
    )

    print()

    print("Generated files:")

    print(
        f" - {MODEL_PATH}"
    )

    print(
        f" - {FEATURE_PATH}"
    )

    print(
        f" - {FEATURE_IMPORTANCE_PATH}"
    )

    print(
        f" - {CONFUSION_MATRIX_PATH}"
    )

    print()

    print(
        "✅ Ready for Explainable AI analysis."
    )

    print("=" * 65)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()