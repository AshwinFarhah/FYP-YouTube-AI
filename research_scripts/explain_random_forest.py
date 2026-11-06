# ============================================================
# NeuroShield AI
# Random Forest - SHAP Explainable AI
# Representative Prediction Explanations
# ============================================================

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

from sklearn.metrics import accuracy_score


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "../models/random_forest_neuroshield.joblib"
FEATURES_PATH = "../models/random_forest_features.json"

X_TEST_PATH = "../data/ml/X_test.csv"
Y_TEST_PATH = "../data/ml/y_test.csv"

RESULTS_DIR = "../results"

os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("NeuroShield AI - SHAP Explainable AI")
print("=" * 60)

print("\nLoading trained Random Forest model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# ============================================================
# LOAD FEATURE NAMES
# ============================================================

with open(FEATURES_PATH, "r") as f:
    feature_names = json.load(f)

print(f"Number of features: {len(feature_names)}")


# ============================================================
# LOAD TEST DATA
# ============================================================

X_test = pd.read_csv(X_TEST_PATH)
y_test = pd.read_csv(Y_TEST_PATH).squeeze()

print(f"Test samples: {len(X_test)}")


# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating model predictions...")

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"Test Accuracy: {accuracy:.4f}")


# ============================================================
# CLASS LABEL MAPPING
# ============================================================

CLASS_NAMES = {
    0: "High Risk",
    1: "Low Risk",
    2: "Medium Risk"
}


# ============================================================
# CREATE PREDICTION TABLE
# ============================================================

prediction_table = pd.DataFrame({
    "test_index": X_test.index,
    "actual_class": y_test.values,
    "predicted_class": y_pred,
    "actual_label": [CLASS_NAMES[int(x)] for x in y_test],
    "predicted_label": [CLASS_NAMES[int(x)] for x in y_pred],
    "prediction_correct": y_test.values == y_pred
})

# Add prediction probabilities

for class_id, class_name in CLASS_NAMES.items():
    prediction_table[
        f"probability_{class_name.lower().replace(' ', '_')}"
    ] = y_proba[:, class_id]


# ============================================================
# FIND REPRESENTATIVE SAMPLES
# ============================================================

print("\nSearching for representative predictions...")

representative_samples = {}


# ------------------------------------------------------------
# 1. Correct High Risk
# ------------------------------------------------------------

correct_high = prediction_table[
    (prediction_table["actual_class"] == 0) &
    (prediction_table["predicted_class"] == 0)
]

if len(correct_high) > 0:

    # Choose the most confident correct prediction
    row = correct_high.sort_values(
        "probability_high_risk",
        ascending=False
    ).iloc[0]

    representative_samples["correct_high_risk"] = int(row["test_index"])


# ------------------------------------------------------------
# 2. Correct Low Risk
# ------------------------------------------------------------

correct_low = prediction_table[
    (prediction_table["actual_class"] == 1) &
    (prediction_table["predicted_class"] == 1)
]

if len(correct_low) > 0:

    row = correct_low.sort_values(
        "probability_low_risk",
        ascending=False
    ).iloc[0]

    representative_samples["correct_low_risk"] = int(row["test_index"])


# ------------------------------------------------------------
# 3. Correct Medium Risk
# ------------------------------------------------------------

correct_medium = prediction_table[
    (prediction_table["actual_class"] == 2) &
    (prediction_table["predicted_class"] == 2)
]

if len(correct_medium) > 0:

    row = correct_medium.sort_values(
        "probability_medium_risk",
        ascending=False
    ).iloc[0]

    representative_samples["correct_medium_risk"] = int(row["test_index"])


# ------------------------------------------------------------
# 4. Incorrect Prediction
# ------------------------------------------------------------

incorrect = prediction_table[
    prediction_table["prediction_correct"] == False
]

if len(incorrect) > 0:

    # Choose the incorrect prediction with
    # the highest model confidence

    incorrect = incorrect.copy()

    incorrect["prediction_confidence"] = incorrect.apply(
        lambda row: y_proba[
            prediction_table.index.get_loc(row.name),
            int(row["predicted_class"])
        ],
        axis=1
    )

    row = incorrect.sort_values(
        "prediction_confidence",
        ascending=False
    ).iloc[0]

    representative_samples["incorrect_prediction"] = int(
        row["test_index"]
    )


# ============================================================
# DISPLAY REPRESENTATIVE SAMPLES
# ============================================================

print("\nRepresentative samples selected:")

for sample_type, index in representative_samples.items():

    row = prediction_table[
        prediction_table["test_index"] == index
    ].iloc[0]

    print("\n----------------------------------------")
    print(f"Type: {sample_type}")
    print(f"Test Index: {index}")
    print(f"Actual: {row['actual_label']}")
    print(f"Predicted: {row['predicted_label']}")

    predicted_class = int(row["predicted_class"])

    print(
        f"Confidence: "
        f"{y_proba[index, predicted_class] * 100:.2f}%"
    )


# ============================================================
# SAVE PREDICTION TABLE
# ============================================================

prediction_table.to_csv(
    os.path.join(
        RESULTS_DIR,
        "random_forest_predictions.csv"
    ),
    index=False
)

print(
    "\nSaved prediction table:"
    " results/random_forest_predictions.csv"
)


# ============================================================
# SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP TreeExplainer...")

explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(X_test)

print("SHAP values generated.")


# ============================================================
# HANDLE SHAP OUTPUT FORMAT
# ============================================================

if isinstance(shap_values, list):

    shap_array = np.array(shap_values)

else:

    shap_array = np.array(shap_values)


print(
    "Original SHAP shape:",
    shap_array.shape
)


# ============================================================
# NORMALIZE SHAP ARRAY
# ============================================================

if shap_array.ndim == 3:

    # SHAP 0.52 commonly returns:
    #
    # samples x features x classes
    #
    # Convert to:
    #
    # classes x samples x features

    if (
        shap_array.shape[0] == len(X_test)
        and shap_array.shape[1] == len(feature_names)
    ):

        shap_array = np.transpose(
            shap_array,
            (2, 0, 1)
        )

    elif (
        shap_array.shape[0] == len(feature_names)
        and shap_array.shape[1] == len(X_test)
    ):

        pass

    elif (
        shap_array.shape[0] <= 10
        and shap_array.shape[1] == len(X_test)
    ):

        pass

    else:

        raise ValueError(
            f"Unexpected SHAP shape: {shap_array.shape}"
        )

else:

    raise ValueError(
        f"Unexpected SHAP dimensions: {shap_array.ndim}"
    )


print(
    "Processed SHAP shape:",
    shap_array.shape
)


# ============================================================
# GLOBAL SHAP FEATURE IMPORTANCE
# ============================================================

global_shap_importance = np.mean(
    np.abs(shap_array),
    axis=(0, 1)
)

global_importance_df = pd.DataFrame({
    "feature": feature_names,
    "mean_abs_shap": global_shap_importance
})

global_importance_df = global_importance_df.sort_values(
    "mean_abs_shap",
    ascending=False
)


# ============================================================
# SAVE GLOBAL SHAP IMPORTANCE
# ============================================================

global_importance_df.to_csv(
    os.path.join(
        RESULTS_DIR,
        "shap_feature_importance.csv"
    ),
    index=False
)


print("\nTop SHAP features:")

print(
    global_importance_df.head(15).to_string(
        index=False
    )
)


# ============================================================
# GLOBAL SHAP BAR CHART
# ============================================================

plt.figure(figsize=(10, 7))

top_features = global_importance_df.head(15).sort_values(
    "mean_abs_shap"
)

plt.barh(
    top_features["feature"],
    top_features["mean_abs_shap"]
)

plt.xlabel("Mean Absolute SHAP Value")
plt.ylabel("Feature")
plt.title(
    "NeuroShield AI - Global SHAP Feature Importance"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULTS_DIR,
        "shap_feature_importance.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# SHAP SUMMARY PLOT
# ============================================================

# Average absolute SHAP values across classes
# for global visualization.

mean_abs_shap_per_sample = np.mean(
    np.abs(shap_array),
    axis=0
)

shap.summary_plot(
    mean_abs_shap_per_sample,
    X_test,
    feature_names=feature_names,
    show=False
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULTS_DIR,
        "shap_summary.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# LOCAL EXPLANATIONS
# ============================================================

all_local_explanations = []


for sample_type, sample_index in representative_samples.items():

    print("\n")
    print("=" * 60)
    print(f"LOCAL SHAP EXPLANATION: {sample_type}")
    print("=" * 60)

    actual_class = int(
        y_test.iloc[sample_index]
    )

    predicted_class = int(
        y_pred[sample_index]
    )

    actual_label = CLASS_NAMES[actual_class]
    predicted_label = CLASS_NAMES[predicted_class]

    confidence = (
        y_proba[
            sample_index,
            predicted_class
        ] * 100
    )

    print(f"\nTest Index: {sample_index}")
    print(f"Actual: {actual_label}")
    print(f"Predicted: {predicted_label}")
    print(f"Confidence: {confidence:.2f}%")


    # --------------------------------------------------------
    # SHAP values for predicted class
    # --------------------------------------------------------

    local_shap = shap_array[
        predicted_class,
        sample_index,
        :
    ]

    sample_features = X_test.iloc[
        sample_index
    ]


    # --------------------------------------------------------
    # Create explanation table
    # --------------------------------------------------------

    local_df = pd.DataFrame({
        "feature": feature_names,
        "feature_value": sample_features.values,
        "shap_value": local_shap
    })


    local_df["absolute_shap"] = np.abs(
        local_df["shap_value"]
    )


    local_df["direction"] = np.where(
        local_df["shap_value"] > 0,
        "increased predicted probability",
        "decreased predicted probability"
    )


    local_df = local_df.sort_values(
        "absolute_shap",
        ascending=False
    )


    # Keep top 10 factors
    top_local = local_df.head(10)


    # --------------------------------------------------------
    # Print top factors
    # --------------------------------------------------------

    print("\nTop contributing factors:")

    for _, row in top_local.iterrows():

        print(
            f"- {row['feature']}: "
            f"value={row['feature_value']:.4f}, "
            f"SHAP={row['shap_value']:.6f}, "
            f"{row['direction']} for "
            f"{predicted_label}"
        )


    # --------------------------------------------------------
    # Add metadata
    # --------------------------------------------------------

    top_local = top_local.copy()

    top_local.insert(
        0,
        "sample_type",
        sample_type
    )

    top_local.insert(
        1,
        "test_index",
        sample_index
    )

    top_local.insert(
        2,
        "actual_label",
        actual_label
    )

    top_local.insert(
        3,
        "predicted_label",
        predicted_label
    )

    top_local.insert(
        4,
        "prediction_confidence",
        confidence
    )


    all_local_explanations.append(
        top_local
    )


# ============================================================
# SAVE ALL LOCAL EXPLANATIONS
# ============================================================

if all_local_explanations:

    combined_local = pd.concat(
        all_local_explanations,
        ignore_index=True
    )

    combined_local.to_csv(
        os.path.join(
            RESULTS_DIR,
            "representative_shap_explanations.csv"
        ),
        index=False
    )

    print(
        "\nSaved representative explanations:"
    )

    print(
        "results/representative_shap_explanations.csv"
    )


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("SHAP EXPLAINABLE AI ANALYSIS COMPLETE")
print("=" * 60)

print("\nGenerated files:")

print("1. results/random_forest_predictions.csv")
print("2. results/shap_feature_importance.csv")
print("3. results/shap_feature_importance.png")
print("4. results/shap_summary.png")
print("5. results/representative_shap_explanations.csv")

print("\nDone.")