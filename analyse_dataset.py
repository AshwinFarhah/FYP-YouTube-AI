import pandas as pd
import numpy as np
import os


# ============================================================
# MULTIMODAL DATASET ANALYSIS
# FYP - YouTube Children's Content
# ============================================================

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/final_dataset.csv"
OUTPUT_FILE = "data/final_dataset_refined.csv"

EXPECTED_DATASET_SIZE = 1650


print("\n=========================================================")
print("MULTIMODAL DATASET ANALYSIS")
print("=========================================================")


# ============================================================
# LOAD DATASET
# ============================================================

print("\n📂 Loading dataset...")

if not os.path.exists(INPUT_FILE):

    print("❌ Dataset file not found:")
    print(INPUT_FILE)
    raise FileNotFoundError(INPUT_FILE)


df = pd.read_csv(INPUT_FILE)

print("✅ Dataset loaded successfully.")

print("\nRows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# BASIC DATASET INFORMATION
# ============================================================

print("\n=========================================================")
print("DATASET INFORMATION")
print("=========================================================")

print("Expected dataset:", EXPECTED_DATASET_SIZE)
print("Actual rows loaded:", len(df))

if len(df) == EXPECTED_DATASET_SIZE:

    print("✅ Dataset contains exactly 1650 videos.")

elif len(df) > EXPECTED_DATASET_SIZE:

    print(
        f"⚠️ Dataset contains {len(df)} rows."
    )

    print(
        "This appears to contain more than the dataset."
    )

else:

    print(
        f"⚠️ Dataset contains only {len(df)} rows."
    )


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

print("\n=========================================================")
print("COLUMN VALIDATION")
print("=========================================================")


required_columns = [

    "video_path",
    "video_duration_seconds",

    # Visual
    "avg_saturation",
    "avg_brightness",
    "motion_mean",
    "motion_std",
    "scene_rate",
    "flicker_rate",

    # Audio
    "audio_available",
    "loudness",
    "sound_density",
    "audio_variation",
    "avg_pitch",
    "pitch_variation",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff",
    "spectral_contrast",
    "zero_crossing_rate",
    "harmonic_ratio",
    "percussive_ratio",
    "tempo",

    # Behavioural / engagement
    "motion_spike_rate",
    "attention_score",
    "loop_detection_score",
    "reward_cue_frequency",
    "attention_reset_rate",

    # NLP
    "transcript_length",
    "sentence_complexity",
    "average_sentence_length",
    "vocabulary_diversity",
    "phrase_repetition",
    "educational_word_ratio",
    "reward_keyword_frequency",
    "transcript_word_count",
    "unique_word_ratio",
    "repeated_word_ratio",
    "hallucination_score",
    "english_ratio",
    "nonsense_ratio",

    # Transcript quality
    "original_transcript_quality_score",
    "original_transcript_quality_label",
    "transcript_rejected",

    # Development
    "emotion_arousal",
    "emotion_valence",
    "emotion_stability",
    "stim_score",

    # Existing label
    "development_label"

]


missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]


if len(missing_columns) > 0:

    print("\n❌ Missing columns:")

    for col in missing_columns:
        print("   -", col)

    raise ValueError(
        "Required dataset columns are missing."
    )


print("✅ All required columns are present.")


# ============================================================
# DUPLICATE ANALYSIS
# ============================================================

print("\n=========================================================")
print("DUPLICATE ANALYSIS")
print("=========================================================")


before = len(df)

duplicate_count = df["video_path"].duplicated().sum()

print(
    "Duplicate video paths found:",
    duplicate_count
)


df = df.drop_duplicates(
    subset=["video_path"],
    keep="first"
)


after = len(df)

print(
    "Duplicates removed:",
    before - after
)

print(
    "Remaining videos:",
    after
)


# ============================================================
# MISSING VALUE ANALYSIS
# ============================================================

print("\n=========================================================")
print("MISSING VALUE ANALYSIS")
print("=========================================================")


missing = df.isnull().sum()

missing = missing[missing > 0]


if len(missing) == 0:

    print("✅ No missing values found.")


else:

    print("⚠️ Missing values found:")

    print(missing)


# ============================================================
# TRANSCRIPT VALIDATION
# ============================================================

print("\n=========================================================")
print("TRANSCRIPT VALIDATION")
print("=========================================================")


total_videos = len(df)


rejected_count = (
    df["transcript_rejected"]
    .astype(bool)
    .sum()
)


accepted_count = total_videos - rejected_count


print(
    "Accepted transcripts:",
    accepted_count
)

print(
    "Rejected transcripts:",
    rejected_count
)


if total_videos > 0:

    rejected_percentage = (
        rejected_count /
        total_videos
        *
        100
    )

    print(
        f"Rejected percentage: "
        f"{rejected_percentage:.2f}%"
    )


# ------------------------------------------------------------
# IMPORTANT:
# We DO NOT delete rejected transcripts.
#
# Rejected transcripts remain part of the dataset because
# the video itself is still valid.
# ------------------------------------------------------------


# ============================================================
# TRANSCRIPT QUALITY SUMMARY
# ============================================================

print("\n=========================================================")
print("TRANSCRIPT QUALITY")
print("=========================================================")


print(
    "\nQuality labels:"
)

print(
    df[
        "original_transcript_quality_label"
    ].value_counts(
        dropna=False
    )
)


print(
    "\nQuality score statistics:"
)

print(
    df[
        "original_transcript_quality_score"
    ].describe()
)


# ============================================================
# TRANSCRIPT LENGTH NORMALIZATION
# ============================================================

print("\n=========================================================")
print("TEXT FEATURE NORMALIZATION")
print("=========================================================")


df["transcript_length_normalized"] = (

    df["transcript_length"] /

    df["video_duration_seconds"]
    .clip(lower=1)

)


df["sentence_complexity"] = (

    df["sentence_complexity"]
    .clip(lower=0)

)


print(
    "✅ Transcript length normalized."
)

print(
    "Feature created:",
    "transcript_length_normalized"
)


# ============================================================
# FEATURE RANGE VALIDATION
# ============================================================

print("\n=========================================================")
print("FEATURE RANGE VALIDATION")
print("=========================================================")


features = [

    # Visual
    "avg_saturation",
    "avg_brightness",
    "motion_mean",
    "motion_std",
    "scene_rate",
    "flicker_rate",

    # Audio
    "loudness",
    "sound_density",
    "audio_variation",
    "avg_pitch",
    "pitch_variation",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff",
    "spectral_contrast",
    "zero_crossing_rate",
    "harmonic_ratio",
    "percussive_ratio",
    "tempo",

    # Behavioural
    "attention_score",
    "loop_detection_score",
    "reward_cue_frequency",
    "attention_reset_rate",

    # Emotion
    "emotion_arousal",
    "emotion_valence",
    "emotion_stability",

    # Overall
    "stim_score"

]


for col in features:

    if col not in df.columns:
        continue


    try:

        minimum = df[col].min()
        maximum = df[col].max()
        mean = df[col].mean()


        print(
            f"{col:30s}"
            f" min={minimum:.4f}"
            f" max={maximum:.4f}"
            f" mean={mean:.4f}"
        )


    except Exception:

        print(
            f"{col:30s}"
            " ⚠️ Could not analyse"
        )


# ============================================================
# AUDIO AVAILABILITY
# ============================================================

print("\n=========================================================")
print("AUDIO AVAILABILITY")
print("=========================================================")


print(
    df["audio_available"]
    .value_counts(
        dropna=False
    )
)


audio_available_count = (
    df["audio_available"]
    .astype(bool)
    .sum()
)


print(
    "\nVideos with audio:",
    audio_available_count
)

print(
    "Videos without audio:",
    total_videos - audio_available_count
)


# ============================================================
# 300-SECOND PROCESSING CHECK
# ============================================================

print("\n=========================================================")
print("300-SECOND PROCESSING VALIDATION")
print("=========================================================")


print(
    "Maximum video duration:",
    f"{df['video_duration_seconds'].max():.2f}s"
)


print(
    "Maximum analysis duration:",
    f"{df['analysis_duration_seconds'].max():.2f}s"
)


over_limit_video = (
    df["video_duration_seconds"] > 300
).sum()


over_limit_analysis = (
    df["analysis_duration_seconds"] > 300
).sum()


print(
    "Videos longer than 300s:",
    over_limit_video
)

print(
    "Analysis durations over 300s:",
    over_limit_analysis
)


if over_limit_analysis == 0:

    print(
        "✅ 300-second analysis limit is respected."
    )

else:

    print(
        "⚠️ Some analysis durations exceed 300 seconds."
    )


# ============================================================
# STIMULATION SCORE
# ============================================================

print("\n=========================================================")
print("STIMULATION SCORE")
print("=========================================================")


print(
    df["stim_score"].describe()
)


# ============================================================
# DATA-DRIVEN LABEL ANALYSIS
# ============================================================

print("\n=========================================================")
print("DATA-DRIVEN LABEL ANALYSIS")
print("=========================================================")


low_threshold = (
    df["stim_score"]
    .quantile(0.33)
)


high_threshold = (
    df["stim_score"]
    .quantile(0.66)
)


print(
    f"Low threshold:    {low_threshold:.4f}"
)

print(
    f"High threshold:   {high_threshold:.4f}"
)


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


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

print("\n=========================================================")
print("LABEL DISTRIBUTION")
print("=========================================================")


print(
    "\nExisting development labels:"
)

print(
    df["development_label"]
    .value_counts(
        dropna=False
    )
)


print(
    "\nRefined development labels:"
)

print(
    df["development_label_refined"]
    .value_counts(
        dropna=False
    )
)


# ============================================================
# NUMERIC SUMMARY
# ============================================================

print("\n=========================================================")
print("NUMERIC FEATURE SUMMARY")
print("=========================================================")


numeric = df.select_dtypes(
    include=np.number
)


summary = numeric.describe().T


print(summary)


# ============================================================
# CORRELATION WITH STIMULATION SCORE
# ============================================================

print("\n=========================================================")
print("FEATURE CORRELATION WITH STIMULATION SCORE")
print("=========================================================")


corr = (
    numeric
    .corr(
        numeric_only=True
    )["stim_score"]
)


corr = (
    corr
    .sort_values(
        ascending=False
    )
)


print(corr)


# ============================================================
# TOP POSITIVE CORRELATIONS
# ============================================================

print("\n=========================================================")
print("TOP POSITIVE CORRELATIONS")
print("=========================================================")


positive_corr = (
    corr[
        corr.index != "stim_score"
    ]
    .sort_values(
        ascending=False
    )
)


print(
    positive_corr.head(10)
)


# ============================================================
# TOP NEGATIVE CORRELATIONS
# ============================================================

print("\n=========================================================")
print("TOP NEGATIVE CORRELATIONS")
print("=========================================================")


negative_corr = (
    corr[
        corr.index != "stim_score"
    ]
    .sort_values(
        ascending=True
    )
)


print(
    negative_corr.head(10)
)


# ============================================================
# SAVE REFINED DATASET
# ============================================================

print("\n=========================================================")
print("SAVING REFINED DATASET")
print("=========================================================")


df.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "✅ Refined dataset saved:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n=========================================================")
print("DATASET ANALYSIS COMPLETE")
print("=========================================================")


print(
    f"Final dataset size: "
    f"{df.shape[0]} rows × {df.shape[1]} columns"
)


print(
    f"Original videos analysed: "
    f"{total_videos}"
)


print(
    f"Duplicate videos removed: "
    f"{before - after}"
)


print(
    f"Rejected transcripts: "
    f"{rejected_count}"
)


print(
    f"Videos with audio: "
    f"{audio_available_count}"
)


print(
    f"300-second violations: "
    f"{over_limit_analysis}"
)


print(
    "\n✅ Final dataset analysis finished."
)

print(
    "========================================================="
)