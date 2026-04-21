import os
import csv
from modules.video_extractor import extract_frames, extract_audio
from modules.visual_features import compute_saturation, compute_motion
from modules.audio_features import load_audio, compute_loudness, compute_sound_density

video_root = "data/videos"
output_file = "data/dataset.csv"

os.makedirs("data", exist_ok=True)

print("🚀 Building dataset from 30 videos...")

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # header
    writer.writerow(["avg_sat", "avg_motion", "loudness", "density", "label"])

    # loop through categories
    for label in os.listdir(video_root):
        folder_path = os.path.join(video_root, label)

        if not os.path.isdir(folder_path):
            continue

        print(f"\n📁 Processing category: {label}")

        for video in os.listdir(folder_path):
            video_path = os.path.join(folder_path, video)

            # =========================
            # SAFETY CHECKS (IMPORTANT)
            # =========================
            if not os.path.isfile(video_path):
                print(f"⚠️ Skipping invalid file: {video}")
                continue

            if not video.lower().endswith(".mp4"):
                print(f"⚠️ Skipping non-mp4: {video}")
                continue

            print(f"🎬 Processing {video}")

            try:
                # =====================
                # extract features
                # =====================
                frames = extract_frames(video_path)
                audio_path = extract_audio(video_path)

                # =====================
                # visual features
                # =====================
                sat_vals = []
                motion_vals = []

                if len(frames) >= 2:
                    for i in range(1, len(frames)):
                        sat_vals.append(compute_saturation(frames[i]))
                        motion_vals.append(compute_motion(frames[i-1], frames[i]))

                avg_sat = sum(sat_vals) / len(sat_vals) if sat_vals else 0
                avg_motion = sum(motion_vals) / len(motion_vals) if motion_vals else 0

                # =====================
                # audio features
                # =====================
                y, sr = load_audio(audio_path)
                loudness = compute_loudness(y)
                density = compute_sound_density(y, sr)

                # =====================
                # save row
                # =====================
                writer.writerow([
                    avg_sat,
                    avg_motion,
                    loudness,
                    density,
                    label
                ])

            except Exception as e:
                print(f"❌ Error processing {video}")
                print("Reason:", e)
                continue

print("\n✅ Dataset created successfully!")