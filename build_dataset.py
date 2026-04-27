import os
import csv
import cv2
import numpy as np

from modules.video_extractor import extract_audio
from modules.audio_features import load_audio, compute_loudness, compute_sound_density

# =========================
# CONFIG
# =========================
video_root = r"D:\videos"
output_file = "data/dataset.csv"
os.makedirs("data", exist_ok=True)

print("🚀 SAFE + FAST DATASET BUILDER (3K videos ready)")

# =========================
# SETTINGS
# =========================
FRAME_SAMPLE_RATE = 1
RESIZE = (160, 120)
SCENE_THRESHOLD = 20
MOTION_THRESHOLD = 5
AUDIO_SPIKE_THRESHOLD = -15

# =========================
# SAFE RESUME SYSTEM (FIXED)
# =========================
processed = set()

if os.path.exists(output_file):
    print("📂 Loading existing dataset for resume...")
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            if len(row) > 0:
                # last column = video_path (we will store it)
                processed.add(row[-1])

# =========================
# COLLECT ALL VIDEOS RECURSIVELY
# =========================
video_list = []

for root, _, files in os.walk(video_root):
    for f in files:
        if f.lower().endswith(".mp4"):
            full_path = os.path.join(root, f)
            label = os.path.basename(root)

            video_list.append((full_path, label))

total_videos = len(video_list)
print(f"📊 Total videos found: {total_videos}")

# =========================
# OPEN CSV (ONE FILE ONLY)
# =========================
file_exists = os.path.exists(output_file)

with open(output_file, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            "avg_sat",
            "avg_motion",
            "avg_brightness",
            "scene_rate",
            "loudness",
            "density",
            "audio_variation",
            "attention_rate",
            "content_label",
            "video_path"   # IMPORTANT FIX
        ])

    # =========================
    # PROCESS VIDEOS
    # =========================
    for idx, (video_path, label) in enumerate(video_list, 1):

        # UNIQUE ID (CRITICAL FIX)
        video_id = video_path.replace("\\", "/")

        # skip if already processed
        if video_id in processed:
            continue

        print(f"[{idx}/{total_videos}] 🎬 {os.path.basename(video_path)}")

        try:
            # =====================
            # VIDEO FEATURES
            # =====================
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)

            if fps == 0:
                cap.release()
                continue

            interval = int(fps * FRAME_SAMPLE_RATE)

            prev_frame = None
            frame_count = 0

            sat_vals = []
            motion_vals = []
            brightness_vals = []
            scene_changes = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % interval != 0:
                    frame_count += 1
                    continue

                frame = cv2.resize(frame, RESIZE)

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                sat = hsv[:, :, 1].mean() / 255
                brightness = frame.mean() / 255

                sat_vals.append(sat)
                brightness_vals.append(brightness)

                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, frame)
                    motion = diff.mean()
                    motion_vals.append(motion)

                    if motion > SCENE_THRESHOLD:
                        scene_changes += 1

                prev_frame = frame
                frame_count += 1

            cap.release()

            duration = max(len(sat_vals) * FRAME_SAMPLE_RATE, 1)

            avg_sat = np.mean(sat_vals) if sat_vals else 0
            avg_motion = np.mean(motion_vals) if motion_vals else 0
            avg_brightness = np.mean(brightness_vals) if brightness_vals else 0
            scene_rate = scene_changes / duration

            # =====================
            # AUDIO FEATURES
            # =====================
            audio_path = extract_audio(video_path)
            y, sr = load_audio(audio_path)

            loudness = compute_loudness(y)
            density = compute_sound_density(y, sr)
            audio_variation = float(np.std(y)) if len(y) > 0 else 0

            # =====================
            # ATTENTION FEATURES
            # =====================
            spikes = sum(
                1 for m in motion_vals
                if m > MOTION_THRESHOLD and loudness > AUDIO_SPIKE_THRESHOLD
            )

            attention_rate = spikes / duration

            # =====================
            # WRITE TO CSV (SINGLE FILE)
            # =====================
            writer.writerow([
                avg_sat,
                avg_motion,
                avg_brightness,
                scene_rate,
                loudness,
                density,
                audio_variation,
                attention_rate,
                label,
                video_id
            ])

            file.flush()

            # cleanup audio temp
            if os.path.exists(audio_path):
                os.remove(audio_path)

            # mark processed
            processed.add(video_id)

        except Exception as e:
            print(f"❌ Failed: {video_path}")
            print("Reason:", e)
            continue

print("\n✅ DONE — Single dataset.csv built safely!")