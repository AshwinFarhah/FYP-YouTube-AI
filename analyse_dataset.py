import pandas as pd
import numpy as np
import os


# =========================
# LOAD DATASET
# =========================

INPUT_FILE = "data/dataset_test.csv"
OUTPUT_FILE = "data/dataset_refined_test.csv"


print("\n📂 Loading dataset...")

df = pd.read_csv(INPUT_FILE)


print("\n=================================")
print("DATASET OVERVIEW")
print("=================================")

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# =========================
# REMOVE DUPLICATES
# =========================

print("\n=================================")
print("DUPLICATE CHECK")
print("=================================")


before = len(df)

df = df.drop_duplicates(
    subset=["video_path"]
)

after = len(df)


print(
    "Removed duplicates:",
    before-after
)


# =========================
# MISSING VALUES
# =========================


print("\n=================================")
print("MISSING VALUE ANALYSIS")
print("=================================")


missing = df.isnull().sum()

print(
    missing[missing>0]
)


if missing.sum()==0:
    print("✅ No missing values")


# =========================
# NORMALIZE TEXT FEATURES
# =========================


print("\n=================================")
print("TEXT NORMALIZATION")
print("=================================")


df["transcript_length_normalized"] = (
    df["transcript_length"]
    /
    df["video_duration_seconds"]
)


# Fix sentence complexity

df["sentence_complexity"] = (
    df["sentence_complexity"]
    .clip(lower=0)
)


# =========================
# STIM SCORE ANALYSIS
# =========================


print("\n=================================")
print("STIM SCORE DISTRIBUTION")
print("=================================")


print(
    df["stim_score"].describe()
)


# =========================
# CREATE DATA DRIVEN LABELS
# =========================


low_threshold = df["stim_score"].quantile(0.33)

high_threshold = df["stim_score"].quantile(0.66)


print("\nSuggested thresholds:")

print(
    f"Low stimulation < {low_threshold:.3f}"
)

print(
    f"Medium stimulation < {high_threshold:.3f}"
)

print(
    f"High stimulation >= {high_threshold:.3f}"
)



def create_label(score):

    if score < low_threshold:

        return "low_stimulation"

    elif score < high_threshold:

        return "medium_stimulation"

    else:

        return "high_stimulation"



df["development_label_refined"] = (
    df["stim_score"]
    .apply(create_label)
)



# =========================
# LABEL DISTRIBUTION
# =========================


print("\n=================================")
print("LABEL DISTRIBUTION")
print("=================================")


print(
    df["development_label_refined"]
    .value_counts()
)



# =========================
# FEATURE SUMMARY
# =========================


print("\n=================================")
print("NUMERIC FEATURE SUMMARY")
print("=================================")


numeric = df.select_dtypes(
    include=np.number
)


print(
    numeric.describe().T
)



# =========================
# SAVE
# =========================


df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n=================================")

print("✅ ANALYSIS COMPLETE")

print(
    "Saved:",
    OUTPUT_FILE
)

print("=================================")