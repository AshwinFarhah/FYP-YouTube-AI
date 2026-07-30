import os
import csv
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
from utils.text_cleaner import clean_transcript

from utils.transcript_quality import evaluate_transcript_quality


# =========================
# CONFIG
# =========================
VIDEO_ROOT = r"D:\videos\test"
OUTPUT_FILE = "data/dataset_test2.csv"

os.makedirs("data", exist_ok=True)

# =========================
# SETTINGS
# =========================
FRAME_SAMPLE_RATE = 1
RESIZE = (160, 120)

SCENE_THRESHOLD = 0.5
FLICKER_THRESHOLD = 30
MOTION_SPIKE_THRESHOLD = 2.5

# =========================
# LIMIT VIDEO DURATION
# =========================
MAX_SECONDS = 300

print("🚀 Building Multimodal Dataset")
print(f"⏱️ Max processing per video: {MAX_SECONDS} seconds")

# =========================
# RESUME SYSTEM
# =========================
processed = set()

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) > 0:
                processed.add(row[-1])

# =========================
# LOAD VIDEOS
# =========================
video_list = []

for root, _, files in os.walk(VIDEO_ROOT):
    for f in files:
        if f.lower().endswith(".mp4"):
            full_path = os.path.join(root, f)
            label = os.path.basename(root)
            video_list.append((full_path, label))

print(f"📊 Total videos found: {len(video_list)}")

# =========================
# CSV SETUP
# =========================
file_exists = os.path.exists(OUTPUT_FILE)

with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            # VISUAL
            "avg_saturation",
            "avg_brightness",
            "motion_mean",
            "motion_std",
            "scene_rate",
            "flicker_rate",

            # AUDIO
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

            # Transcript Quality
            "transcript_word_count",
            "unique_word_ratio",
            "repeated_word_ratio",
            "hallucination_score",
            "english_ratio",
            "nonsense_ratio",
            "transcript_quality_score",
            "transcript_quality_label",
            "transcript",

            # EMOTION
            "emotion_arousal",
            "emotion_valence",
            "emotion_stability",

            # ORIGINAL LABEL
            "stim_score",
            "content_name",
            "development_label",

            # VIDEO INFORMATION
            "video_duration_seconds",

            # PATH
            "video_path"
        ])

    # =========================
    # PROCESS LOOP
    # =========================
    for idx, (video_path, label) in enumerate(video_list, 1):

        video_id = video_path.replace("\\", "/")

        if video_id in processed:
            continue

        print(f"[{idx}] 🎬 {os.path.basename(video_path)}")

        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)

            if fps == 0:
                cap.release()
                continue

            interval = max(int(fps * FRAME_SAMPLE_RATE), 1)

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

            # =========================
            # FRAME LOOP
            # =========================
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count >= fps * MAX_SECONDS:
                    print("⏹️ Reached max duration limit")
                    break

                if frame_count % interval != 0:
                    frame_count += 1
                    continue

                current_sec = int(frame_count / fps)

                if current_sec % 30 == 0 and frame_count % interval == 0:
                    print(f"   ⏱️ Processing: {current_sec}s")

                frame = cv2.resize(frame, RESIZE)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                sat_vals.append(hsv[:, :, 1].mean() / 255)
                brightness_vals.append(frame.mean() / 255)

                luminance = gray.mean()

                if prev_luminance is not None:
                    if abs(luminance - prev_luminance) > FLICKER_THRESHOLD:
                        flicker_count += 1
                prev_luminance = luminance

                if prev_gray is not None:
                    flow = cv2.calcOpticalFlowFarneback(
                        prev_gray, gray, None,
                        0.5, 3, 15, 3, 5, 1.2, 0
                    )

                    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                    motion = np.mean(magnitude)
                    motion_vals.append(motion)

                    if motion > MOTION_SPIKE_THRESHOLD:
                        motion_spikes += 1

                if prev_frame is not None:
                    prev_hist = cv2.calcHist([prev_frame], [0], None, [256], [0, 256])
                    curr_hist = cv2.calcHist([frame], [0], None, [256], [0, 256])

                    diff = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_BHATTACHARYYA)

                    if diff > SCENE_THRESHOLD:
                        scene_changes += 1

                prev_frame = frame
                prev_gray = gray
                frame_count += 1

            cap.release()
            print("   ✅ Video processed")

            duration = max(len(sat_vals) * FRAME_SAMPLE_RATE, 1)
            video_duration_seconds = min(
                frame_count / fps,
                MAX_SECONDS
            )

            avg_sat = np.mean(sat_vals) if sat_vals else 0
            avg_brightness = np.mean(brightness_vals) if brightness_vals else 0
            motion_mean = np.mean(motion_vals) if motion_vals else 0
            motion_std = np.std(motion_vals) if motion_vals else 0

            scene_rate = scene_changes / duration
            flicker_rate = flicker_count / duration
            motion_spike_rate = motion_spikes / duration

            # =========================
            # AUDIO
            # =========================

            audio_path = extract_audio(video_path)

            audio_features = extract_audio_features(
                audio_path
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

            # =========================
            # EMOTIONAL FEATURES
            # =========================

            emotion_features = extract_emotional_features(
                loudness,
                pitch_var,
                tempo,
                spectral_contrast
            )

            emotion_arousal = emotion_features[
                "emotion_arousal"
            ]

            emotion_valence = emotion_features[
                "emotion_valence"
            ]

            emotion_stability = emotion_features[
                "emotion_stability"
            ]

            # =========================
            # REPETITION (Audio repetition was extracted using chroma similarity analysis rather than a manually defined threshold.)
            # =========================
            repetition_score = audio_features[
                "audio_repetition"
            ]

            # =========================
            # ATTENTION SCORE
            # =========================
            attention_score = (
                    0.4 * min(motion_spike_rate, 1) +
                    0.3 * min(scene_rate, 1) +
                    0.3 * min(density, 1)
            )

            # =========================
            # REWARD CUE PROXY
            # =========================
            # high motion + high sound = stimulation spike
            if motion_spike_rate > 0.3 and density > 2.0:
                reward_score = 1
            else:
                reward_score = 0

            # =========================
            # TEXT FEATURES (WHISPER)
            # =========================

            if audio_path is not None:

                print("Audio path:", audio_path)
                print("Exists:", os.path.exists(audio_path))

                raw_transcript = extract_transcript(
                    audio_path
                )

            else:

                print("⚠️ Skipping Whisper - no audio")

                raw_transcript = ""

            # =========================
            # CLEAN TRANSCRIPT
            # =========================

            transcript = clean_transcript(
                raw_transcript
            )

            print("Raw transcript length:",
                  len(raw_transcript))

            print("Clean transcript length:",
                  len(transcript))

            # =========================
            # TRANSCRIPT QUALITY CHECK
            # =========================

            transcript_quality = evaluate_transcript_quality(
                transcript
            )

            print(
                "Transcript quality:",
                transcript_quality["transcript_quality_label"]
            )

            # =========================
            # NLP FEATURES
            # =========================

            text_features = extract_text_features(
                transcript
            )

            text_complexity = text_features[
                "sentence_complexity"
            ]

            average_sentence_length = text_features[
                "average_sentence_length"
            ]

            vocabulary_diversity = text_features[
                "vocabulary_diversity"
            ]

            phrase_repetition = text_features[
                "phrase_repetition"
            ]

            educational_word_ratio = text_features[
                "educational_word_ratio"
            ]

            reward_keyword_frequency = text_features[
                "reward_keyword_frequency"
            ]

            transcript_length = text_features[
                "transcript_length"
            ]


            # =========================
            # BEHAVIOURAL FEATURES
            # =========================

            visual_features = {

                "scene_rate": scene_rate,
                "motion_std": motion_std,
                "motion_spike_rate": motion_spike_rate,
                "flicker_rate": flicker_rate

            }

            audio_features = {

                "audio_variation": audio_variation,
                "audio_repetition": repetition_score

            }

            behaviour = extract_behavioural_features(
                visual_features,
                audio_features,
                text_features
            )

            loop_detection_score = behaviour[
                "loop_detection_score"
            ]

            reward_cue_frequency = behaviour[
                "reward_cue_frequency"
            ]

            attention_reset_rate = behaviour[
                "attention_reset_rate"
            ]

            # =========================
            # DEVELOPMENTAL IMPACT SCORE
            # =========================

            content_name = label

            # Weighted multimodal stimulation score
            # Combines visual, audio, behavioural indicators
            stim_score = (

                    0.35 * attention_score +

                    0.15 * avg_sat +

                    0.10 * avg_brightness +

                    0.15 * reward_cue_frequency +

                    0.10 * loop_detection_score +

                    0.05 * attention_reset_rate +

                    0.10 * repetition_score

            )

            # Normalize score into range 0 - 1
            # Ensures compatibility with ML models
            stim_score = np.clip(
                stim_score,
                0,
                1
            )

            # =========================
            # DEVELOPMENTAL RISK LABEL
            # =========================

            if stim_score < 0.33:

                development_label = "low_risk"

            elif stim_score < 0.66:

                development_label = "medium_risk"

            else:

                development_label = "high_risk"

            # =========================
            # SAVE
            # =========================
            writer.writerow([

                # VISUAL
                avg_sat,
                avg_brightness,
                motion_mean,
                motion_std,
                scene_rate,
                flicker_rate,

                # AUDIO
                loudness,
                density,
                audio_variation,
                avg_pitch,
                pitch_var,
                spectral_centroid,
                spectral_bandwidth,
                spectral_rolloff,
                spectral_contrast,
                zero_crossing_rate,
                harmonic_ratio,
                percussive_ratio,
                tempo,

                # BEHAVIOUR
                motion_spike_rate,
                attention_score,
                loop_detection_score,
                reward_cue_frequency,
                attention_reset_rate,

                # TEXT
                transcript_length,
                text_complexity,
                average_sentence_length,
                vocabulary_diversity,
                phrase_repetition,
                educational_word_ratio,
                reward_keyword_frequency,

                # Transcript quality
                transcript_quality["transcript_word_count"],
                transcript_quality["unique_word_ratio"],
                transcript_quality["repeated_word_ratio"],
                transcript_quality["hallucination_score"],
                transcript_quality["english_ratio"],
                transcript_quality["nonsense_ratio"],
                transcript_quality["transcript_quality_score"],
                transcript_quality["transcript_quality_label"],

                transcript,

                # EMOTION
                emotion_arousal,
                emotion_valence,
                emotion_stability,

                # LABEL
                stim_score,
                content_name,
                development_label,

                video_duration_seconds,

                # PATH
                video_id

            ])

            file.flush()

            # Keep audio files temporarily for debugging

            pass

            processed.add(video_id)

        except Exception as e:
            print(f"❌ Failed: {video_path}")
            print("Reason:", e)
            continue

print("\n✅ DATASET COMPLETE — FYP READY")