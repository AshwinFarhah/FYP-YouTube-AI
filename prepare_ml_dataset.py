import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/final_dataset_refined.csv"

OUTPUT_DIR = "data/ml"

X_TRAIN_FILE = os.path.join(OUTPUT_DIR, "X_train.csv")
X_TEST_FILE = os.path.join(OUTPUT_DIR, "X_test.csv")
Y_TRAIN_FILE = os.path.join(OUTPUT_DIR, "y_train.csv")
Y_TEST_FILE = os.path.join(OUTPUT_DIR, "y_test.csv")

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# START
# ============================================================

print("\n=========================================================")
print("NEUROSHIELD AI - ML DATASET PREPARATION")
print("=========================================================")


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

print("\n📂 Loading refined dataset...")

if not os.path.exists(INPUT_FILE):

    print("❌ Dataset not found:")
    print(INPUT_FILE)

    raise FileNotFoundError(INPUT_FILE)


df = pd.read_csv(INPUT_FILE)

print("✅ Dataset loaded successfully.")

print("\nRows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# CHECK TARGET
# ============================================================

TARGET = "development_label_refined"

print("\n=========================================================")
print("TARGET VALIDATION")
print("=========================================================")

if TARGET not in df.columns:

    raise ValueError(
        f"Target column '{TARGET}' not found."
    )

print("Target column:", TARGET)

print("\nTarget distribution:")

print(
    df[TARGET]
    .value_counts()
)


# ============================================================
# CHECK FOR INVALID TARGET VALUES
# ============================================================

valid_labels = {
    "low_risk",
    "medium_risk",
    "high_risk"
}

invalid_labels = set(
    df[TARGET].dropna().unique()
) - valid_labels


if invalid_labels:

    print("\n❌ Invalid target labels found:")

    print(invalid_labels)

    raise ValueError(
        "Invalid target labels detected."
    )


print("\n✅ Target labels validated.")


# ============================================================
# REMOVE ROWS WITH MISSING TARGET
# ============================================================

before = len(df)

df = df.dropna(
    subset=[TARGET]
).copy()

after = len(df)

print(
    "\nRows removed due to missing target:",
    before - after
)


# ============================================================
# DEFINE NON-FEATURE COLUMNS
# ============================================================

print("\n=========================================================")
print("FEATURE SELECTION")
print("=========================================================")


# These columns should NOT be used as ML predictors.

excluded_columns = [

    # Target
    "development_label_refined",

    # Original label
    "development_label",

    # Original stimulation score
    # IMPORTANT: prevents target leakage
    "stim_score",

    # Video identification
    "video_path",
    "content_name",

    # Raw transcript
    "transcript",

    # Dataset/version information
    "dataset_version",

    # Processing metadata
    "analysis_duration_seconds",

    # Transcript quality indicators
    # These describe extraction quality rather than
    # developmental stimulation.
    "original_transcript_quality_label",
    "original_transcript_quality_score",
    "transcript_rejected"

]


print("\nExcluded columns:")

for col in excluded_columns:

    if col in df.columns:

        print("   -", col)


# ============================================================
# CREATE FEATURE DATAFRAME
# ============================================================

feature_columns = [
    col
    for col in df.columns
    if col not in excluded_columns
]


X = df[feature_columns].copy()

y = df[TARGET].copy()


print("\nNumber of ML features:", len(X.columns))

print("\nML features:")

for col in X.columns:

    print("   -", col)


# ============================================================
# KEEP ONLY NUMERIC FEATURES
# ============================================================

print("\n=========================================================")
print("NUMERIC FEATURE VALIDATION")
print("=========================================================")


non_numeric = X.select_dtypes(
    exclude=np.number
).columns.tolist()


if non_numeric:

    print("\n⚠️ Non-numeric columns found:")

    for col in non_numeric:

        print("   -", col)

    print("\nRemoving non-numeric columns.")

    X = X.select_dtypes(
        include=np.number
    )


print(
    "\n✅ Numeric ML features:",
    len(X.columns)
)


# ============================================================
# MISSING VALUE ANALYSIS
# ============================================================

print("\n=========================================================")
print("MISSING VALUE ANALYSIS")
print("=========================================================")


missing = X.isnull().sum()

missing = missing[
    missing > 0
]


if len(missing) == 0:

    print("✅ No missing feature values.")


else:

    print("⚠️ Missing feature values:")

    print(missing)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\n=========================================================")
print("TRAIN / TEST SPLIT")
print("=========================================================")


X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=TEST_SIZE,

    random_state=RANDOM_STATE,

    stratify=y

)


print(
    "\nTraining samples:",
    len(X_train)
)

print(
    "Testing samples:",
    len(X_test)
)


# ============================================================
# CHECK CLASS DISTRIBUTION
# ============================================================

print("\n=========================================================")
print("TRAINING CLASS DISTRIBUTION")
print("=========================================================")

print(
    y_train.value_counts()
)


print("\nTesting class distribution:")

print(
    y_test.value_counts()
)


# ============================================================
# IMPUTE MISSING VALUES
# ============================================================

print("\n=========================================================")
print("MISSING VALUE IMPUTATION")
print("=========================================================")


imputer = SimpleImputer(
    strategy="median"
)


X_train_imputed = pd.DataFrame(

    imputer.fit_transform(X_train),

    columns=X_train.columns,

    index=X_train.index

)


X_test_imputed = pd.DataFrame(

    imputer.transform(X_test),

    columns=X_test.columns,

    index=X_test.index

)


print(
    "✅ Missing numeric values handled using median imputation."
)


# ============================================================
# ENCODE TARGET
# ============================================================

print("\n=========================================================")
print("TARGET ENCODING")
print("=========================================================")


label_encoder = LabelEncoder()


y_train_encoded = label_encoder.fit_transform(
    y_train
)

y_test_encoded = label_encoder.transform(
    y_test
)


print("\nClass mapping:")

for class_name, class_id in zip(
    label_encoder.classes_,
    range(len(label_encoder.classes_))
):

    print(
        f"   {class_name} -> {class_id}"
    )


# ============================================================
# SAVE DATASETS
# ============================================================

print("\n=========================================================")
print("SAVING ML DATA")
print("=========================================================")


X_train_imputed.to_csv(
    X_TRAIN_FILE,
    index=False
)

X_test_imputed.to_csv(
    X_TEST_FILE,
    index=False
)

pd.DataFrame({
    "label": y_train_encoded
}).to_csv(
    Y_TRAIN_FILE,
    index=False
)

pd.DataFrame({
    "label": y_test_encoded
}).to_csv(
    Y_TEST_FILE,
    index=False
)


print("\n✅ ML datasets saved.")

print(
    "X_train:",
    X_TRAIN_FILE
)

print(
    "X_test:",
    X_TEST_FILE
)

print(
    "y_train:",
    Y_TRAIN_FILE
)

print(
    "y_test:",
    Y_TEST_FILE
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n=========================================================")
print("ML DATASET PREPARATION COMPLETE")
print("=========================================================")

print(
    "Total videos:",
    len(df)
)

print(
    "Training videos:",
    len(X_train)
)

print(
    "Testing videos:",
    len(X_test)
)

print(
    "ML features:",
    len(X_train.columns)
)

print(
    "Target:",
    TARGET
)

print(
    "\nTarget classes:"
)

for class_name, count in (
    df[TARGET]
    .value_counts()
    .items()
):

    print(
        f"   {class_name}: {count}"
    )

print(
    "\n🔒 stim_score excluded from ML features "
    "to prevent target leakage."
)

print(
    "\n✅ Ready for Random Forest training."
)

print(
    "========================================================="
)