import os
import csv
import shutil
import cv2
import numpy as np

from modules.video_extractor import extract_audio

from modules.audio_features import (
    extract_audio_features
)

from modules.behavioural_features import (
    extract_behavioural_features
)

from modules.emotional_features import (
    extract_emotional_features
)

from modules.text_features import (
    extract_text_features
)

from modules.whisper_features import (
    extract_transcript
)

from utils.text_cleaner import (
    clean_transcript
)

from utils.transcript_quality import (
    evaluate_transcript_quality
)


# =====================================================
# CONFIG
# =====================================================

VIDEO_ROOT = r"D:\videos\KidsVideos20"

OUTPUT_FILE = "../data/final_dataset.csv"

os.makedirs("../data", exist_ok=True)


# =====================================================
# SETTINGS
# =====================================================

FRAME_SAMPLE_RATE = 1

RESIZE = (160,120)

SCENE_THRESHOLD = 0.5

FLICKER_THRESHOLD = 30

MOTION_SPIKE_THRESHOLD = 2.5

MAX_SECONDS = 300

DATASET_VERSION = ("FYP_FinalVer_300SEC_MULTIMODAL")


print("🚀 Building Multimodal Dataset")

print(f"⏱️ Max processing per video: " f"{MAX_SECONDS} seconds")

# =====================================================
#
#  Converts problematic numerical values into
#  CSV-safe values.
#
# =====================================================

def safe_value(value):


    if value is None:
        return ""

    try:

        if isinstance(
            value,
            (float, np.floating)
        ):

            if np.isnan(value):
                return ""

            if np.isinf(value):
                return ""

        return value

    except Exception:

        return value
# =====================================================
# RESUME SYSTEM
# =====================================================

processed = set()

existing_rows = 0
duplicate_rows = 0
invalid_rows = 0

if os.path.exists(OUTPUT_FILE):

    print(
        "🔄 Checking existing dataset..."
    )

    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8",
            newline=""
        ) as f:

            reader = csv.DictReader(f)

            existing_header = (
                reader.fieldnames
            )

            # -------------------------------------------------
            # Validate existing CSV
            # -------------------------------------------------

            if not existing_header:

                print(
                    "⚠️ Existing CSV has no header."
                )

                backup_file = (
                    OUTPUT_FILE
                    +
                    ".old"
                )

                if os.path.exists(
                    backup_file
                ):

                    os.remove(
                        backup_file
                    )

                shutil.move(
                    OUTPUT_FILE,
                    backup_file
                )

                existing_header = None

            elif "dataset_version" not in existing_header:

                print(
                    "⚠️ Existing CSV uses an old format."
                )

                backup_file = (
                    OUTPUT_FILE
                    +
                    ".old"
                )

                if os.path.exists(
                    backup_file
                ):

                    os.remove(
                        backup_file
                    )

                shutil.move(
                    OUTPUT_FILE,
                    backup_file
                )

                existing_header = None

            elif "video_path" not in existing_header:

                print(
                    "⚠️ Existing CSV has no video_path column."
                )

                backup_file = (
                    OUTPUT_FILE
                    +
                    ".old"
                )

                if os.path.exists(
                    backup_file
                ):

                    os.remove(
                        backup_file
                    )

                shutil.move(
                    OUTPUT_FILE,
                    backup_file
                )

                existing_header = None

            else:

                # -------------------------------------------------
                # Read existing processed videos
                # -------------------------------------------------

                for row in reader:

                    dataset_version = (
                        row.get(
                            "dataset_version",
                            ""
                        )
                        or ""
                    ).strip()

                    video_path = (
                        row.get(
                            "video_path",
                            ""
                        )
                        or ""
                    ).strip()

                    # ---------------------------------------------
                    # Only accept rows from current dataset version
                    # ---------------------------------------------

                    if (
                        dataset_version
                        !=
                        DATASET_VERSION
                    ):

                        continue

                    # ---------------------------------------------
                    # Invalid row
                    # ---------------------------------------------

                    if not video_path:

                        invalid_rows += 1

                        continue

                    # ---------------------------------------------
                    # Duplicate row
                    # ---------------------------------------------

                    if video_path in processed:

                        duplicate_rows += 1

                        continue

                    # ---------------------------------------------
                    # Valid processed row
                    # ---------------------------------------------

                    processed.add(
                        video_path
                    )

                    existing_rows += 1

        print(
            f"   📂 Existing valid rows: "
            f"{existing_rows}"
        )

        print(
            f"   🔁 Existing duplicate rows: "
            f"{duplicate_rows}"
        )

        print(
            f"   ⚠️ Invalid rows: "
            f"{invalid_rows}"
        )

        print(
            f"   ✅ Videos available for resume: "
            f"{len(processed)}"
        )

    except Exception as e:

        print(
            "❌ Failed to read existing dataset."
        )

        print(
            "Reason:",
            e
        )

        raise


# =====================================================
# LOAD VIDEOS
# =====================================================

video_list = []

for root, _, files in os.walk(
    VIDEO_ROOT
):

    for f in files:

        if f.lower().endswith(
            ".mp4"
        ):

            full_path = os.path.join(
                root,
                f
            )

            label = os.path.basename(
                root
            )

            video_list.append(
                (
                    full_path,
                    label
                )
            )


print(
    f"📊 Total videos found: "
    f"{len(video_list)}"
)

# =====================================================
# CURRENT RUN DUPLICATE PROTECTION
# =====================================================

current_run_paths = set()

print(
    f"🔒 Resume protection active."
)

# =====================================================
# CSV SETUP
# =====================================================

file_exists = os.path.exists(
    OUTPUT_FILE
)

with open(
    OUTPUT_FILE,
    "a",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(
        file
    )

    if not file_exists:

        writer.writerow([

            # VERSION
            "dataset_version",

            # VISUAL
            "avg_saturation",
            "avg_brightness",
            "motion_mean",
            "motion_std",
            "scene_rate",
            "flicker_rate",

            # AUDIO
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

            # ATTENTION / BEHAVIOUR
            "motion_spike_rate",
            "attention_score",
            "loop_detection_score",
            "reward_cue_frequency",
            "attention_reset_rate",

            # TEXT
            "transcript_length",
            "sentence_complexity",
            "average_sentence_length",
            "vocabulary_diversity",
            "phrase_repetition",
            "educational_word_ratio",
            "reward_keyword_frequency",

            # TRANSCRIPT QUALITY
            "transcript_word_count",
            "unique_word_ratio",
            "repeated_word_ratio",
            "hallucination_score",
            "english_ratio",
            "nonsense_ratio",

            # ORIGINAL QUALITY
            "original_transcript_quality_score",
            "original_transcript_quality_label",

            # FILTERING
            "transcript_rejected",

            "transcript",

            # EMOTION
            "emotion_arousal",
            "emotion_valence",
            "emotion_stability",

            # LABEL
            "stim_score",
            "content_name",
            "development_label",

            # VIDEO INFORMATION
            "video_duration_seconds",
            "analysis_duration_seconds",

            # PATH
            "video_path"

        ])


    # =================================================
    # PROCESS LOOP
    # =================================================

    for idx, (
        video_path,
        label
    ) in enumerate(
        video_list,
        1
    ):

        video_id = os.path.normcase(
            os.path.normpath(
                os.path.abspath(
                    video_path
                )
            )
        )

        # ---------------------------------------------
        # Resume
        # ---------------------------------------------

        if video_id in processed:
            print(
                f"⏭️ Skipping already processed: "
                f"{os.path.basename(video_path)}"
            )

            continue

        if video_id in current_run_paths:
            print(
                f"⚠️ Duplicate video detected in current run: "
                f"{os.path.basename(video_path)}"
            )

            print(
                "   Skipping duplicate."
            )

            continue

        current_run_paths.add(
            video_id
        )


        print(
            f"[{idx}] 🎬 "
            f"{os.path.basename(video_path)}"
        )


        # =================================================
        # SAFE DEFAULT VALUES
        # =================================================

        avg_sat = 0.0
        avg_brightness = 0.0
        motion_mean = 0.0
        motion_std = 0.0
        scene_rate = 0.0
        flicker_rate = 0.0

        audio_available = False

        loudness = 0.0
        density = 0.0
        audio_variation = 0.0
        avg_pitch = 0.0
        pitch_var = 0.0
        spectral_centroid = 0.0
        spectral_bandwidth = 0.0
        spectral_rolloff = 0.0
        spectral_contrast = 0.0
        zero_crossing_rate = 0.0
        harmonic_ratio = 0.0
        percussive_ratio = 0.0
        tempo = 0.0

        motion_spike_rate = 0.0
        attention_score = 0.0
        loop_detection_score = 0.0
        reward_cue_frequency = 0.0
        attention_reset_rate = 0.0

        transcript_length = 0
        text_complexity = np.nan
        average_sentence_length = np.nan
        vocabulary_diversity = np.nan
        phrase_repetition = np.nan
        educational_word_ratio = np.nan
        reward_keyword_frequency = np.nan

        transcript_word_count = 0
        unique_word_ratio_value = 0.0
        repeated_word_ratio_value = 0.0
        hallucination_score_value = 1.0
        english_ratio_value = 0.0
        nonsense_ratio_value = 1.0

        original_transcript_quality_score = 0.0
        original_transcript_quality_label = (
            "rejected"
        )

        transcript_rejected = True

        transcript = ""

        emotion_arousal = 0.0
        emotion_valence = 0.0
        emotion_stability = 0.0

        stim_score = 0.0

        development_label = (
            "low_risk"
        )

        video_duration_seconds = 0.0

        analysis_duration_seconds = 0.0


        # =================================================
        # MAIN PROCESSING
        # =================================================

        try:

            # =============================================
            # VISUAL
            # =============================================

            cap = cv2.VideoCapture(
                video_path
            )

            fps = cap.get(
                cv2.CAP_PROP_FPS
            )

            if fps == 0:

                raise ValueError(
                    "Invalid FPS"
                )

            total_frames = cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )

            video_duration_seconds = (
                total_frames / fps
            )

            interval = max(
                int(
                    fps *
                    FRAME_SAMPLE_RATE
                ),
                1
            )

            prev_frame = None
            prev_gray = None
            prev_luminance = None

            sat_vals = []
            brightness_vals = []
            motion_vals = []

            scene_changes = 0
            flicker_count = 0
            motion_spikes = 0

            frame_count = 0


            # =============================================
            # FRAME LOOP
            # =============================================

            while True:

                ret, frame = cap.read()

                if not ret:
                    break

                if (
                    frame_count
                    >=
                    fps *
                    MAX_SECONDS
                ):

                    print(
                        "⏹️ Reached max duration limit"
                    )

                    break

                if (
                    frame_count
                    %
                    interval
                    !=
                    0
                ):

                    frame_count += 1

                    continue


                current_sec = int(
                    frame_count /
                    fps
                )


                if (
                    current_sec % 30 == 0
                    and
                    frame_count % interval == 0
                ):

                    print(
                        f"   ⏱️ Processing: "
                        f"{current_sec}s"
                    )


                frame = cv2.resize(
                    frame,
                    RESIZE
                )

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                hsv = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2HSV
                )

                sat_vals.append(
                    hsv[
                        :,
                        :,
                        1
                    ].mean()
                    /
                    255
                )

                brightness_vals.append(
                    frame.mean()
                    /
                    255
                )


                luminance = gray.mean()


                if (
                    prev_luminance
                    is not None
                ):

                    if (
                        abs(
                            luminance
                            -
                            prev_luminance
                        )
                        >
                        FLICKER_THRESHOLD
                    ):

                        flicker_count += 1


                prev_luminance = (
                    luminance
                )


                if (
                    prev_gray
                    is not None
                ):

                    flow = (
                        cv2.calcOpticalFlowFarneback(
                            prev_gray,
                            gray,
                            None,
                            0.5,
                            3,
                            15,
                            3,
                            5,
                            1.2,
                            0
                        )
                    )

                    magnitude = np.sqrt(
                        flow[..., 0] ** 2
                        +
                        flow[..., 1] ** 2
                    )

                    motion = np.mean(
                        magnitude
                    )

                    motion_vals.append(
                        motion
                    )

                    if (
                        motion
                        >
                        MOTION_SPIKE_THRESHOLD
                    ):

                        motion_spikes += 1


                if (
                    prev_frame
                    is not None
                ):

                    prev_hist = cv2.calcHist(
                        [
                            prev_frame
                        ],
                        [0],
                        None,
                        [256],
                        [0, 256]
                    )

                    curr_hist = cv2.calcHist(
                        [
                            frame
                        ],
                        [0],
                        None,
                        [256],
                        [0, 256]
                    )

                    diff = cv2.compareHist(
                        prev_hist,
                        curr_hist,
                        cv2.HISTCMP_BHATTACHARYYA
                    )

                    if (
                        diff
                        >
                        SCENE_THRESHOLD
                    ):

                        scene_changes += 1


                prev_frame = frame

                prev_gray = gray

                frame_count += 1


            cap.release()


            print(
                "   ✅ Video processed"
            )


            # =============================================
            # VISUAL STATISTICS
            # =============================================

            analysis_duration_seconds = min(
                frame_count / fps,
                MAX_SECONDS
            )

            duration = max(
                analysis_duration_seconds,
                1
            )


            avg_sat = (
                np.mean(sat_vals)
                if sat_vals
                else 0
            )

            avg_brightness = (
                np.mean(
                    brightness_vals
                )
                if brightness_vals
                else 0
            )

            motion_mean = (
                np.mean(
                    motion_vals
                )
                if motion_vals
                else 0
            )

            motion_std = (
                np.std(
                    motion_vals
                )
                if motion_vals
                else 0
            )


            scene_rate = (
                scene_changes /
                duration
            )

            flicker_rate = (
                flicker_count /
                duration
            )

            motion_spike_rate = (
                motion_spikes /
                duration
            )


            # =============================================
            # AUDIO
            # =============================================

            try:

                audio_path = extract_audio(
                    video_path
                )

                audio_available = (
                    audio_path is not None
                )

                audio_features = (
                    extract_audio_features(
                        audio_path
                    )
                )

            except Exception as e:

                print(
                    "⚠️ Audio failed:",
                    e
                )

                audio_path = None

                audio_available = False

                audio_features = (
                    extract_audio_features(
                        None
                    )
                )


            loudness = audio_features[
                "loudness"
            ]

            density = audio_features[
                "sound_density"
            ]

            audio_variation = audio_features[
                "audio_variation"
            ]

            avg_pitch = audio_features[
                "avg_pitch"
            ]

            pitch_var = audio_features[
                "pitch_variation"
            ]

            tempo = audio_features[
                "tempo"
            ]

            spectral_centroid = audio_features[
                "spectral_centroid"
            ]

            spectral_bandwidth = audio_features[
                "spectral_bandwidth"
            ]

            spectral_rolloff = audio_features[
                "spectral_rolloff"
            ]

            spectral_contrast = audio_features[
                "spectral_contrast"
            ]

            zero_crossing_rate = audio_features[
                "zero_crossing_rate"
            ]

            harmonic_ratio = audio_features[
                "harmonic_ratio"
            ]

            percussive_ratio = audio_features[
                "percussive_ratio"
            ]


            # =============================================
            # EMOTIONAL FEATURES
            # =============================================

            try:

                emotion_features = (
                    extract_emotional_features(
                        loudness,
                        pitch_var,
                        tempo,
                        spectral_contrast
                    )
                )

                emotion_arousal = (
                    emotion_features[
                        "emotion_arousal"
                    ]
                )

                emotion_valence = (
                    emotion_features[
                        "emotion_valence"
                    ]
                )

                emotion_stability = (
                    emotion_features[
                        "emotion_stability"
                    ]
                )

            except Exception as e:

                print(
                    "⚠️ Emotion extraction failed:",
                    e
                )


            # =============================================
            # AUDIO REPETITION
            # =============================================

            repetition_score = (
                audio_features[
                    "audio_repetition"
                ]
            )


            # =============================================
            # ATTENTION SCORE
            # =============================================

            attention_score = (

                0.4 *
                min(
                    motion_spike_rate,
                    1
                )

                +

                0.3 *
                min(
                    scene_rate,
                    1
                )

                +

                0.3 *
                min(
                    density,
                    1
                )

            )


            # =============================================
            # WHISPER
            # =============================================

            try:

                print(
                    "Audio path:",
                    audio_path
                )

                raw_transcript = (
                    extract_transcript(
                        audio_path
                    )
                )

            except Exception as e:

                print(
                    "⚠️ Whisper failed:",
                    e
                )

                raw_transcript = ""


            # =============================================
            # CLEAN TRANSCRIPT
            # =============================================

            transcript = clean_transcript(
                raw_transcript
            )

            print(
                "Raw transcript length:",
                len(raw_transcript)
            )

            print(
                "Clean transcript length:",
                len(transcript)
            )


            # =============================================
            # TRANSCRIPT QUALITY
            # =============================================

            transcript_quality = (
                evaluate_transcript_quality(
                    transcript
                )
            )


            transcript_word_count = (
                transcript_quality[
                    "transcript_word_count"
                ]
            )

            unique_word_ratio_value = (
                transcript_quality[
                    "unique_word_ratio"
                ]
            )

            repeated_word_ratio_value = (
                transcript_quality[
                    "repeated_word_ratio"
                ]
            )

            hallucination_score_value = (
                transcript_quality[
                    "hallucination_score"
                ]
            )

            english_ratio_value = (
                transcript_quality[
                    "english_ratio"
                ]
            )

            nonsense_ratio_value = (
                transcript_quality[
                    "nonsense_ratio"
                ]
            )


            original_transcript_quality_score = (
                transcript_quality[
                    "transcript_quality_score"
                ]
            )

            original_transcript_quality_label = (
                transcript_quality[
                    "transcript_quality_label"
                ]
            )


            print(
                "Original transcript quality:",
                original_transcript_quality_label
            )

            print(
                "Original quality score:",
                original_transcript_quality_score
            )


            # =============================================
            # TRANSCRIPT FILTERING
            # =============================================

            transcript_rejected = False


            if (

                original_transcript_quality_score
                <
                0.70

                or

                english_ratio_value
                <
                0.75

                or

                transcript_word_count
                <
                20

            ):

                print(
                    "⚠️ Transcript rejected."
                )

                transcript_rejected = True

                transcript = ""


            # =============================================
            # NLP FEATURES
            # =============================================

            if transcript_rejected:

                print(
                    "ℹ️ NLP features skipped "
                    "because transcript was rejected."
                )

                transcript_length = 0

                text_complexity = np.nan

                average_sentence_length = np.nan

                vocabulary_diversity = np.nan

                phrase_repetition = np.nan

                educational_word_ratio = np.nan

                reward_keyword_frequency = np.nan


                text_features = {

                    "sentence_complexity": 0,

                    "average_sentence_length": 0,

                    "vocabulary_diversity": 0,

                    "phrase_repetition": 0,

                    "educational_word_ratio": 0,

                    "reward_keyword_frequency": 0,

                    "transcript_length": 0

                }

            else:

                try:

                    text_features = (
                        extract_text_features(
                            transcript
                        )
                    )

                    transcript_length = (
                        text_features[
                            "transcript_length"
                        ]
                    )

                    text_complexity = (
                        text_features[
                            "sentence_complexity"
                        ]
                    )

                    average_sentence_length = (
                        text_features[
                            "average_sentence_length"
                        ]
                    )

                    vocabulary_diversity = (
                        text_features[
                            "vocabulary_diversity"
                        ]
                    )

                    phrase_repetition = (
                        text_features[
                            "phrase_repetition"
                        ]
                    )

                    educational_word_ratio = (
                        text_features[
                            "educational_word_ratio"
                        ]
                    )

                    reward_keyword_frequency = (
                        text_features[
                            "reward_keyword_frequency"
                        ]
                    )

                except Exception as e:

                    print(
                        "⚠️ NLP failed:",
                        e
                    )

                    transcript_rejected = True

                    text_features = {

                        "sentence_complexity": 0,

                        "average_sentence_length": 0,

                        "vocabulary_diversity": 0,

                        "phrase_repetition": 0,

                        "educational_word_ratio": 0,

                        "reward_keyword_frequency": 0,

                        "transcript_length": 0

                    }

                    transcript_length = 0

                    text_complexity = np.nan

                    average_sentence_length = np.nan

                    vocabulary_diversity = np.nan

                    phrase_repetition = np.nan

                    educational_word_ratio = np.nan

                    reward_keyword_frequency = np.nan


            # =============================================
            # BEHAVIOURAL FEATURES
            # =============================================

            visual_features = {

                "scene_rate":
                    scene_rate,

                "motion_std":
                    motion_std,

                "motion_spike_rate":
                    motion_spike_rate,

                "flicker_rate":
                    flicker_rate

            }


            behavioural_audio_features = {

                "audio_variation":
                    audio_variation,

                "audio_repetition":
                    repetition_score

            }


            try:

                behaviour = (
                    extract_behavioural_features(
                        visual_features,
                        behavioural_audio_features,
                        text_features
                    )
                )

                loop_detection_score = (
                    behaviour[
                        "loop_detection_score"
                    ]
                )

                reward_cue_frequency = (
                    behaviour[
                        "reward_cue_frequency"
                    ]
                )

                attention_reset_rate = (
                    behaviour[
                        "attention_reset_rate"
                    ]
                )

            except Exception as e:

                print(
                    "⚠️ Behavioural extraction failed:",
                    e
                )


            # =============================================
            # DEVELOPMENTAL IMPACT SCORE
            # =============================================

            content_name = label


            stim_score = (

                0.35 *
                attention_score

                +

                0.15 *
                avg_sat

                +

                0.10 *
                avg_brightness

                +

                0.15 *
                reward_cue_frequency

                +

                0.10 *
                loop_detection_score

                +

                0.05 *
                attention_reset_rate

                +

                0.10 *
                repetition_score

            )


            stim_score = np.clip(
                stim_score,
                0,
                1
            )


            # =============================================
            # DEVELOPMENTAL RISK LABEL
            # =============================================

            if stim_score < 0.33:

                development_label = (
                    "low_risk"
                )

            elif stim_score < 0.66:

                development_label = (
                    "medium_risk"
                )

            else:

                development_label = (
                    "high_risk"
                )


        except Exception as e:

            print(
                f"❌ Processing error: "
                f"{video_path}"
            )

            print(
                "Reason:",
                e
            )

            print(
                "⚠️ Saving fallback row "
                "to preserve 1-row-per-video."
            )

        # =================================================
        # SAVE ROW
        # =================================================

        try:

            writer.writerow([

                # VERSION
                DATASET_VERSION,

                # VISUAL
                safe_value(avg_sat),
                safe_value(avg_brightness),
                safe_value(motion_mean),
                safe_value(motion_std),
                safe_value(scene_rate),
                safe_value(flicker_rate),

                # AUDIO
                audio_available,
                safe_value(loudness),
                safe_value(density),
                safe_value(audio_variation),
                safe_value(avg_pitch),
                safe_value(pitch_var),
                safe_value(spectral_centroid),
                safe_value(spectral_bandwidth),
                safe_value(spectral_rolloff),
                safe_value(spectral_contrast),
                safe_value(zero_crossing_rate),
                safe_value(harmonic_ratio),
                safe_value(percussive_ratio),
                safe_value(tempo),

                # BEHAVIOUR
                safe_value(motion_spike_rate),
                safe_value(attention_score),
                safe_value(loop_detection_score),
                safe_value(reward_cue_frequency),
                safe_value(attention_reset_rate),

                # TEXT
                safe_value(transcript_length),
                safe_value(text_complexity),
                safe_value(average_sentence_length),
                safe_value(vocabulary_diversity),
                safe_value(phrase_repetition),
                safe_value(educational_word_ratio),
                safe_value(reward_keyword_frequency),

                # TRANSCRIPT QUALITY
                safe_value(transcript_word_count),
                safe_value(unique_word_ratio_value),
                safe_value(repeated_word_ratio_value),
                safe_value(hallucination_score_value),
                safe_value(english_ratio_value),
                safe_value(nonsense_ratio_value),

                # ORIGINAL QUALITY
                safe_value(
                    original_transcript_quality_score
                ),

                original_transcript_quality_label,

                # FILTERING
                transcript_rejected,

                transcript,

                # EMOTION
                safe_value(emotion_arousal),
                safe_value(emotion_valence),
                safe_value(emotion_stability),

                # LABEL
                safe_value(stim_score),
                content_name,
                development_label,

                # VIDEO INFORMATION
                safe_value(
                    video_duration_seconds
                ),

                safe_value(
                    analysis_duration_seconds
                ),

                # PATH
                video_id

            ])

            # -------------------------------------------------
            # Force data to disk
            # -------------------------------------------------

            file.flush()

            # -------------------------------------------------
            # Only mark processed AFTER successful write
            # -------------------------------------------------

            processed.add(
                video_id
            )

            print(
                "   💾 Row saved successfully."
            )

        except Exception as e:

            print(
                "❌ CSV row could not be saved."
            )

            print(
                "Reason:",
                e
            )

            print(
                "⚠️ Video will NOT be marked as processed."
            )


print(
    "\n✅ DATASET COMPLETE — FYP READY"
)