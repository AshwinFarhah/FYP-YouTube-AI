import pandas as pd
import numpy as np
import os

# ==========================================
# CONFIG
# ==========================================

INPUT_FILE = "data/dataset_test2.csv"
OUTPUT_FILE = "data/dataset_refined_test2.csv"

print("\n=========================================")
print("MULTIMODAL DATASET ANALYSIS")
print("=========================================")

# ==========================================
# LOAD DATASET
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print("Loaded successfully.")

print("\nRows:", len(df))
print("Columns:", len(df.columns))

# ==========================================
# REMOVE DUPLICATES
# ==========================================

print("\n=========================================")
print("DUPLICATE ANALYSIS")
print("=========================================")

before = len(df)

df = df.drop_duplicates(subset=["video_path"])

after = len(df)

print("Duplicates removed:", before - after)
print("Remaining videos:", after)

# ==========================================
# MISSING VALUES
# ==========================================

print("\n=========================================")
print("MISSING VALUE ANALYSIS")
print("=========================================")

missing = df.isnull().sum()

missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing values found.")
else:
    print(missing)

# ==========================================
# REMOVE EMPTY TRANSCRIPTS
# ==========================================

print("\n=========================================")
print("TRANSCRIPT VALIDATION")
print("=========================================")

before = len(df)

df = df[
    df["transcript_quality_score"] >= 0.40
]

after = len(df)

print("Poor transcripts removed:", before - after)
print("Remaining:", after)

# ==========================================
# NORMALIZE TRANSCRIPT LENGTH
# ==========================================

print("\n=========================================")
print("TEXT FEATURE NORMALIZATION")
print("=========================================")

df["transcript_length_normalized"] = (
    df["transcript_length"] /
    df["video_duration_seconds"].clip(lower=1)
)

df["sentence_complexity"] = (
    df["sentence_complexity"]
    .clip(lower=0)
)

print("Transcript length normalized.")

# ==========================================
# CHECK FEATURE RANGES
# ==========================================

print("\n=========================================")
print("FEATURE RANGE VALIDATION")
print("=========================================")

features = [

    "avg_saturation",
    "avg_brightness",
    "motion_mean",
    "scene_rate",
    "flicker_rate",

    "loudness",
    "sound_density",
    "avg_pitch",
    "tempo",

    "attention_score",

    "emotion_arousal",
    "emotion_valence",
    "emotion_stability",

    "stim_score"

]

for col in features:

    if col in df.columns:

        print(f"{col:30s}"
              f" min={df[col].min():.3f}"
              f" max={df[col].max():.3f}"
              f" mean={df[col].mean():.3f}")

# ==========================================
# TRANSCRIPT QUALITY SUMMARY
# ==========================================

print("\n=========================================")
print("TRANSCRIPT QUALITY")
print("=========================================")

print(df["transcript_quality_label"].value_counts())

print()

print(df["transcript_quality_score"].describe())

# ==========================================
# STIMULATION SCORE
# ==========================================

print("\n=========================================")
print("STIMULATION SCORE")
print("=========================================")

print(df["stim_score"].describe())

# ==========================================
# CREATE DATA-DRIVEN LABELS
# ==========================================

low_threshold = df["stim_score"].quantile(0.33)
high_threshold = df["stim_score"].quantile(0.66)

print("\nSuggested thresholds")

print(f"Low    < {low_threshold:.3f}")
print(f"Medium < {high_threshold:.3f}")
print(f"High   >= {high_threshold:.3f}")

def create_label(score):

    if score < low_threshold:
        return "low_risk"

    elif score < high_threshold:
        return "medium_risk"

    else:
        return "high_risk"

df["development_label_refined"] = (
    df["stim_score"]
    .apply(create_label)
)

# ==========================================
# LABEL DISTRIBUTION
# ==========================================

print("\n=========================================")
print("LABEL DISTRIBUTION")
print("=========================================")

print(df["development_label_refined"].value_counts())

# ==========================================
# NUMERIC SUMMARY
# ==========================================

print("\n=========================================")
print("NUMERIC FEATURE SUMMARY")
print("=========================================")

numeric = df.select_dtypes(include=np.number)

print(numeric.describe().T)

# ==========================================
# CORRELATION WITH STIM SCORE
# ==========================================

print("\n=========================================")
print("TOP FEATURES CORRELATED WITH STIM SCORE")
print("=========================================")

corr = numeric.corr(numeric_only=True)["stim_score"]

corr = corr.sort_values(ascending=False)

print(corr)

# ==========================================
# SAVE
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n=========================================")
print("DATASET ANALYSIS COMPLETE")
print("=========================================")

print("Saved refined dataset to:")
print(OUTPUT_FILE)

print("\nFinal dataset size:", df.shape)