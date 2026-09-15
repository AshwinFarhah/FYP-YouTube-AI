# ============================================================
# NeuroShield AI
# Human-Readable Explainable AI Generator
# Research + Parent-Facing Explanations
# ============================================================

import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SHAP_RESULTS_PATH = "results/representative_shap_explanations.csv"

OUTPUT_PATH = "results/human_readable_explanations.csv"


# ============================================================
# FEATURE DESCRIPTIONS
# ============================================================

FEATURE_DESCRIPTIONS = {

    # Visual
    "avg_saturation":
        "color saturation characteristics",

    "avg_brightness":
        "overall brightness characteristics",

    "motion_mean":
        "overall visual motion activity",

    "motion_std":
        "variation in visual motion",

    "scene_rate":
        "frequency of scene changes",

    "flicker_rate":
        "frequency of rapid visual changes",

    "motion_spike_rate":
        "frequency of sudden motion spikes",

    # Audio
    "loudness":
        "audio loudness",

    "sound_density":
        "density of detected sound activity",

    "audio_variation":
        "variation in audio intensity",

    "avg_pitch":
        "average audio pitch",

    "pitch_variation":
        "variation in audio pitch",

    "spectral_centroid":
        "audio spectral characteristics",

    "spectral_bandwidth":
        "audio frequency bandwidth",

    "spectral_rolloff":
        "high-frequency audio content",

    "spectral_contrast":
        "contrast between different audio frequency regions",

    "zero_crossing_rate":
        "variation in the audio waveform",

    "harmonic_ratio":
        "harmonic characteristics of the audio",

    "percussive_ratio":
        "percussive characteristics of the audio",

    "tempo":
        "audio tempo",

    # Attention
    "attention_score":
        "attention-related visual activity",

    "attention_reset_rate":
        "frequency of attention-reset patterns",

    "reward_cue_frequency":
        "frequency of detected reward-related cues",

    "loop_detection_score":
        "repetitive or looping content patterns",

    # Text
    "transcript_length":
        "overall transcript length",

    "sentence_complexity":
        "sentence complexity",

    "average_sentence_length":
        "average sentence length",

    "vocabulary_diversity":
        "vocabulary diversity",

    "phrase_repetition":
        "repetition of phrases",

    "educational_word_ratio":
        "presence of educational vocabulary",

    "reward_keyword_frequency":
        "frequency of reward-related keywords",

    "transcript_word_count":
        "amount of transcript content",

    "unique_word_ratio":
        "proportion of unique words",

    "repeated_word_ratio":
        "proportion of repeated words",

    "hallucination_score":
        "detected transcript reliability patterns",

    "english_ratio":
        "proportion of English-language content",

    "nonsense_ratio":
        "detected nonsensical language patterns",

    # Emotion
    "emotion_arousal":
        "emotional arousal characteristics",

    "emotion_valence":
        "emotional tone",

    "emotion_stability":
        "stability of the detected emotional tone",

    # Other
    "video_duration_seconds":
        "video duration",

    "transcript_length_normalized":
        "normalized transcript length"
}


# ============================================================
# RISK CONTEXT
# ============================================================

def generate_risk_context(predicted_label):

    if predicted_label == "High Risk":

        return (
            "The detected feature pattern was more "
            "consistent with the High Risk category "
            "defined by the developmental scoring framework."
        )

    elif predicted_label == "Medium Risk":

        return (
            "The detected feature pattern was more "
            "consistent with the Medium Risk category "
            "defined by the developmental scoring framework."
        )

    elif predicted_label == "Low Risk":

        return (
            "The detected feature pattern was more "
            "consistent with the Low Risk category "
            "defined by the developmental scoring framework."
        )

    return (
        "The model generated a risk classification "
        "based on the extracted video features."
    )


# ============================================================
# FEATURE DESCRIPTION
# ============================================================

def get_feature_description(feature):

    return FEATURE_DESCRIPTIONS.get(
        feature,
        feature.replace("_", " ")
    )


# ============================================================
# PARENT-FACING FEATURE NAME
# ============================================================

def get_parent_friendly_name(feature):

    names = {

        "attention_score":
            "Attention-related activity",

        "attention_reset_rate":
            "Attention-reset patterns",

        "reward_cue_frequency":
            "Reward-related cues",

        "motion_spike_rate":
            "Sudden motion spikes",

        "motion_mean":
            "Overall visual motion",

        "motion_std":
            "Variation in motion",

        "avg_saturation":
            "Color saturation",

        "avg_brightness":
            "Brightness",

        "audio_variation":
            "Audio variation",

        "loudness":
            "Audio loudness",

        "flicker_rate":
            "Rapid visual changes",

        "scene_rate":
            "Scene changes",

        "loop_detection_score":
            "Repetitive content patterns",

        "emotion_arousal":
            "Emotional arousal",

        "emotion_valence":
            "Emotional tone",

        "emotion_stability":
            "Emotional stability",

        "transcript_length":
            "Transcript length",

        "transcript_word_count":
            "Transcript content",

        "vocabulary_diversity":
            "Vocabulary diversity",

        "phrase_repetition":
            "Phrase repetition",

        "educational_word_ratio":
            "Educational vocabulary",

        "reward_keyword_frequency":
            "Reward-related keywords",

        "average_sentence_length":
            "Average sentence length",

        "sentence_complexity":
            "Sentence complexity",

        "tempo":
            "Audio tempo"
    }

    return names.get(
        feature,
        feature.replace("_", " ").title()
    )


# ============================================================
# CREATE SHORT PARENT EXPLANATION
# ============================================================

def generate_parent_explanation(
    predicted_label,
    positive_features
):

    if len(positive_features) == 0:

        return (
            f"The model classified this video as "
            f"{predicted_label} based on the combined "
            f"video features."
        )


    top_features = positive_features.head(3)

    feature_names = []

    for _, row in top_features.iterrows():

        feature_names.append(
            get_parent_friendly_name(
                row["feature"]
            )
        )


    if len(feature_names) == 1:

        factor_text = feature_names[0]

    elif len(feature_names) == 2:

        factor_text = (
            f"{feature_names[0]} and "
            f"{feature_names[1]}"
        )

    else:

        factor_text = (
            f"{feature_names[0]}, "
            f"{feature_names[1]}, and "
            f"{feature_names[2]}"
        )


    return (
        f"The model's {predicted_label} prediction "
        f"was mainly influenced by {factor_text} "
        f"detected in the video."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("NeuroShield AI - Human-Readable XAI Generator")
    print("=" * 60)


    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not os.path.exists(SHAP_RESULTS_PATH):

        print(
            "\nERROR: SHAP results file was not found:"
        )

        print(SHAP_RESULTS_PATH)

        return


    # --------------------------------------------------------
    # Load SHAP results
    # --------------------------------------------------------

    print("\nLoading SHAP explanations...")

    df = pd.read_csv(
        SHAP_RESULTS_PATH
    )

    print(
        f"Loaded {len(df)} SHAP explanation rows."
    )


    # --------------------------------------------------------
    # Process representative samples
    # --------------------------------------------------------

    explanations = []


    for sample_type in df["sample_type"].unique():

        sample_df = df[
            df["sample_type"] == sample_type
        ].copy()


        first_row = sample_df.iloc[0]


        test_index = int(
            first_row["test_index"]
        )

        actual_label = first_row[
            "actual_label"
        ]

        predicted_label = first_row[
            "predicted_label"
        ]

        confidence = float(
            first_row["prediction_confidence"]
        )


        # ----------------------------------------------------
        # Positive SHAP factors
        # ----------------------------------------------------

        positive_features = sample_df[
            sample_df["shap_value"] > 0
        ].copy()

        positive_features = positive_features.sort_values(
            "shap_value",
            ascending=False
        )


        # ----------------------------------------------------
        # Negative SHAP factors
        # ----------------------------------------------------

        negative_features = sample_df[
            sample_df["shap_value"] < 0
        ].copy()

        negative_features = negative_features.sort_values(
            "shap_value",
            ascending=True
        )


        # ----------------------------------------------------
        # Top 5 research factors
        # ----------------------------------------------------

        research_positive = positive_features.head(5)

        supporting_factors = []

        for _, row in research_positive.iterrows():

            supporting_factors.append(
                get_feature_description(
                    row["feature"]
                )
            )


        # ----------------------------------------------------
        # Top 3 parent-facing factors
        # ----------------------------------------------------

        parent_positive = positive_features.head(3)

        parent_factors = []

        for _, row in parent_positive.iterrows():

            parent_factors.append(
                get_parent_friendly_name(
                    row["feature"]
                )
            )


        # ----------------------------------------------------
        # Top 3 opposing factors
        # ----------------------------------------------------

        opposing_features = negative_features.head(3)

        opposing_factors = []

        for _, row in opposing_features.iterrows():

            opposing_factors.append(
                get_feature_description(
                    row["feature"]
                )
            )


        # ----------------------------------------------------
        # Prediction status
        # ----------------------------------------------------

        if actual_label == predicted_label:

            prediction_status = (
                "Correct prediction"
            )

        else:

            prediction_status = (
                "Incorrect prediction"
            )


        # ----------------------------------------------------
        # Research explanation
        # ----------------------------------------------------

        research_factor_text = ", ".join(
            supporting_factors
        )


        research_explanation = (
            f"The model classified the video as "
            f"{predicted_label}. The prediction was "
            f"mainly influenced by "
            f"{research_factor_text}. "
            f"{generate_risk_context(predicted_label)}"
        )


        # ----------------------------------------------------
        # Parent-facing explanation
        # ----------------------------------------------------

        parent_explanation = (
            generate_parent_explanation(
                predicted_label,
                positive_features
            )
        )


        # ----------------------------------------------------
        # Incorrect prediction explanation
        # ----------------------------------------------------

        if prediction_status == "Incorrect prediction":

            incorrect_explanation = (
                f"The model predicted {predicted_label}, "
                f"while the benchmark label was "
                f"{actual_label}. The prediction was "
                f"mainly influenced by the strongest "
                f"SHAP-contributing features for the "
                f"predicted class."
            )

        else:

            incorrect_explanation = ""


        # ----------------------------------------------------
        # Store
        # ----------------------------------------------------

        explanations.append({

            "sample_type":
                sample_type,

            "test_index":
                test_index,

            "actual_label":
                actual_label,

            "predicted_label":
                predicted_label,

            "prediction_status":
                prediction_status,

            "prediction_confidence":
                round(
                    confidence,
                    2
                ),

            "parent_factors":
                "; ".join(
                    parent_factors
                ),

            "supporting_factors":
                "; ".join(
                    supporting_factors
                ),

            "opposing_factors":
                "; ".join(
                    opposing_factors
                ),

            "parent_explanation":
                parent_explanation,

            "research_explanation":
                research_explanation,

            "incorrect_prediction_explanation":
                incorrect_explanation
        })


    # ========================================================
    # CREATE OUTPUT
    # ========================================================

    output_df = pd.DataFrame(
        explanations
    )


    # ========================================================
    # SAVE
    # ========================================================

    output_df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    print(
        "\nHuman-readable explanations generated."
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_PATH
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    print("\n")
    print("=" * 60)
    print("PARENT-FACING EXPLANATIONS")
    print("=" * 60)


    for _, row in output_df.iterrows():

        print("\n----------------------------------------")

        print(
            f"Type: {row['sample_type']}"
        )

        print(
            f"Actual: {row['actual_label']}"
        )

        print(
            f"Predicted: {row['predicted_label']}"
        )

        print(
            f"Confidence: "
            f"{row['prediction_confidence']:.2f}%"
        )

        print(
            f"Status: "
            f"{row['prediction_status']}"
        )

        print("\nMain contributing factors:")

        print(
            row["parent_factors"]
        )

        print("\nParent-facing explanation:")

        print(
            row["parent_explanation"]
        )


        if row["incorrect_prediction_explanation"]:

            print(
                "\nEvaluation note:"
            )

            print(
                row[
                    "incorrect_prediction_explanation"
                ]
            )


    # ========================================================
    # FINISHED
    # ========================================================

    print("\n")
    print("=" * 60)
    print("EXPLANATION GENERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":

    main()