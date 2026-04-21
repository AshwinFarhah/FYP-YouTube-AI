from modules.video_extractor import extract_frames, extract_audio
from modules.visual_features import compute_saturation, compute_motion
from modules.audio_features import load_audio, compute_loudness, compute_sound_density
from modules.scoring import compute_visual_score, compute_audio_score
import csv
import os

video_path = "data/sample_video.mp4"

print("🚀 Starting pipeline...")

# =========================
# STEP 1: Extract Data
# =========================
print("\n📥 Extracting frames...")
frames = extract_frames(video_path)
print("✅ Frames extracted:", len(frames))

print("\n🎧 Extracting audio...")
audio_path = extract_audio(video_path)
print("✅ Audio saved at:", audio_path)

# =========================
# STEP 2: Visual Analysis
# =========================
print("\n🎨 Running visual analysis...")

saturation_values = []
motion_values = []

if len(frames) < 2:
    print("⚠️ Not enough frames for motion analysis!")
    avg_sat = 0
    avg_motion = 0
else:
    for i in range(1, len(frames)):
        sat = compute_saturation(frames[i])
        mot = compute_motion(frames[i - 1], frames[i])

        saturation_values.append(sat)
        motion_values.append(mot)

    avg_sat = sum(saturation_values) / len(saturation_values)
    avg_motion = sum(motion_values) / len(motion_values)

print(f"📊 Avg Saturation: {avg_sat:.4f}")
print(f"📊 Avg Motion: {avg_motion:.4f}")

# =========================
# STEP 3: Audio Analysis
# =========================
print("\n🔊 Running audio analysis...")

try:
    y, sr = load_audio(audio_path)

    loudness = compute_loudness(y)
    density = compute_sound_density(y, sr)

    print(f"📊 Loudness: {loudness:.4f}")
    print(f"📊 Sound Density: {density:.4f}")

except Exception as e:
    print("❌ Audio processing failed:", e)
    loudness = 0
    density = 0

# =========================
# STEP 4: Scoring
# =========================
print("\n🧠 Computing scores...")

visual_score = compute_visual_score(avg_sat, avg_motion)
audio_score = compute_audio_score(loudness, density)

print("\n🎯 FINAL RESULTS")
print("Visual Score:", visual_score)
print("Audio Score:", audio_score)

# =========================
# STEP 5: Create Label (temporary for dataset)
# =========================
label = "High" if avg_motion > 5 else "Low"

# =========================
# STEP 6: Save Dataset Row
# =========================
print("\n💾 Saving to dataset...")

os.makedirs("data", exist_ok=True)

with open("data/dataset.csv", "a", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        avg_sat,
        avg_motion,
        loudness,
        density,
        label
    ])

print("✅ Saved to dataset.csv")

print("\n✅ Pipeline completed successfully!")