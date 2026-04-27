import os
import csv
import cv2
import numpy as np
import librosa

from modules.video_extractor import extract_audio
from modules.audio_features import load_audio, compute_loudness, compute_sound_density

# =========================
# CONFIG
# =========================
VIDEO_ROOT = r"D:\testvids"
OUTPUT_FILE = "data/dataset.csv"

os.makedirs("data", exist_ok=True)

# =========================
# SETTINGS
# =========================
FRAME_SAMPLE_RATE = 1          # seconds
RESIZE = (160, 120)

SCENE_THRESHOLD = 0.5          # histogram diff
FLICKER_THRESHOLD = 30         # luminance change
MOTION_SPIKE_THRESHOLD = 2.5

# =========================
# LIMIT VIDEO DURATION
# =========================
MAX_SECONDS = 600   # 600 = 10 min (use 300 for 5 min)

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

            # ATTENTION / ENGAGEMENT
            "motion_spike_rate",
            "attention_score",

            # TEXT (placeholder for now)
            "text_complexity",
            "phrase_repetition",

            # LABEL
            "content_label",
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

                # ⛔ STOP after MAX_SECONDS
                if frame_count >= fps * MAX_SECONDS:
                    print("⏹️ Reached max duration limit")
                    break

                if frame_count % interval != 0:
                    frame_count += 1
                    continue

                current_sec = int(frame_count / fps)

                # 🔍 Progress every 30 sec (no spam)
                if current_sec % 30 == 0 and frame_count % interval == 0:
                    print(f"   ⏱️ Processing: {current_sec}s")

                frame = cv2.resize(frame, RESIZE)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # --- COLOR FEATURES ---
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                sat_vals.append(hsv[:, :, 1].mean() / 255)
                brightness_vals.append(frame.mean() / 255)

                luminance = gray.mean()

                # --- FLICKER ---
                if prev_luminance is not None:
                    if abs(luminance - prev_luminance) > FLICKER_THRESHOLD:
                        flicker_count += 1
                prev_luminance = luminance

                # --- MOTION (OPTICAL FLOW) ---
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

                # --- SCENE CHANGE ---
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

            # =========================
            # VISUAL METRICS
            # =========================
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
            y, sr = load_audio(audio_path)

            loudness = compute_loudness(y)
            density = compute_sound_density(y, sr)
            audio_variation = float(np.std(y)) if len(y) > 0 else 0

            # --- PITCH ---
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            pitch_vals = pitches[pitches > 0]

            avg_pitch = np.mean(pitch_vals) if len(pitch_vals) > 0 else 0
            pitch_var = np.std(pitch_vals) if len(pitch_vals) > 0 else 0

            # =========================
            # ATTENTION SCORE
            # =========================
            attention_score = (
                0.4 * motion_spike_rate +
                0.3 * scene_rate +
                0.3 * density
            )

            # =========================
            # TEXT PLACEHOLDER
            # =========================
            text_complexity = 0
            phrase_repetition = 0

            # =========================
            # SAVE
            # =========================
            writer.writerow([
                avg_sat,
                avg_brightness,
                motion_mean,
                motion_std,
                scene_rate,
                flicker_rate,
                loudness,
                density,
                audio_variation,
                avg_pitch,
                pitch_var,
                motion_spike_rate,
                attention_score,
                text_complexity,
                phrase_repetition,
                label,
                video_id
            ])

            file.flush()

            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass

            processed.add(video_id)

        except Exception as e:
            print(f"❌ Failed: {video_path}")
            print("Reason:", e)
            continue

print("\n✅ DATASET COMPLETE — FYP READY")