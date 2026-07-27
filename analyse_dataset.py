import pandas as pd
import numpy as np


# =====================================================
# CONFIG
# =====================================================

INPUT_FILE = "data/dataset_test.csv"
OUTPUT_FILE = "data/dataset_refined.csv"


# =====================================================
# LOAD DATASET
# =====================================================

print("📂 Loading dataset...")

df = pd.read_csv(INPUT_FILE)


print("\n=================================")
print("DATASET OVERVIEW")
print("=================================")

print("\nShape:")
print(df.shape)


print("\nColumns:")
print(df.columns.tolist())


# =====================================================
# MISSING VALUE CHECK
# =====================================================

print("\n=================================")
print("MISSING VALUE ANALYSIS")
print("=================================")

missing = df.isnull().sum()

print(
    missing[missing > 0]
)


if missing.sum() == 0:
    print("✅ No missing values detected")


# =====================================================
# DUPLICATE CHECK
# =====================================================

print("\n=================================")
print("DUPLICATE CHECK")
print("=================================")

duplicates = df["video_path"].duplicated().sum()

print(
    "Duplicate videos:",
    duplicates
)


# =====================================================
# STIMULATION SCORE ANALYSIS
# =====================================================

print("\n=================================")
print("STIM SCORE DISTRIBUTION")
print("=================================")


print(
    df["stim_score"].describe()
)


# =====================================================
# AUTOMATIC THRESHOLD ANALYSIS
# =====================================================

low_threshold = (
    df["stim_score"]
    .quantile(0.33)
)


high_threshold = (
    df["stim_score"]
    .quantile(0.66)
)


print("\nSuggested thresholds:")
print(
    f"Low risk < {low_threshold:.3f}"
)

print(
    f"Medium risk < {high_threshold:.3f}"
)

print(
    f"High risk >= {high_threshold:.3f}"
)



# =====================================================
# RELABEL DEVELOPMENT IMPACT
# =====================================================


def relabel(score):

    if score < low_threshold:

        return "low_risk"

    elif score < high_threshold:

        return "medium_risk"

    else:

        return "high_risk"



df["development_label_refined"] = (
    df["stim_score"]
    .apply(relabel)
)



print("\n=================================")
print("LABEL DISTRIBUTION")
print("=================================")


print(
    df["development_label_refined"]
    .value_counts()
)



# =====================================================
# TRANSCRIPT ANALYSIS
# =====================================================

print("\n=================================")
print("TEXT FEATURE CHECK")
print("=================================")


print(
    "Videos with transcript:"
)

print(
    (df["transcript_length"] > 0)
    .sum()
)


print(
    "Videos without transcript:"
)

print(
    (df["transcript_length"] == 0)
    .sum()
)



# =====================================================
# FEATURE RANGE CHECK
# =====================================================

print("\n=================================")
print("NUMERIC FEATURE SUMMARY")
print("=================================")


numeric_features = df.select_dtypes(
    include=np.number
)


print(
    numeric_features.describe().T
)



# =====================================================
# SAVE CLEAN DATASET
# =====================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n=================================")
print("✅ ANALYSIS COMPLETE")
print("Saved:")
print(OUTPUT_FILE)
print("=================================")