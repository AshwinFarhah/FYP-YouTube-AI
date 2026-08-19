"""
VIDEO EXTRACTION MODULE

Handles:
- Frame extraction
- Audio extraction

Audio extraction is limited to the first 300 seconds
to keep visual, audio and transcript analysis consistent.
"""

import cv2
import os
import hashlib

from moviepy import VideoFileClip


# =====================================================
# CONFIGURATION
# =====================================================

MAX_AUDIO_SECONDS = 300


# =====================================================
# FRAME EXTRACTION
# =====================================================

def extract_frames(video_path, fps_rate=1):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps == 0:
        cap.release()
        return []

    interval = max(
        int(fps / fps_rate),
        1
    )

    frames = []

    count = 0

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        if count % interval == 0:

            frames.append(frame)

        count += 1

    cap.release()

    return frames


# =====================================================
# AUDIO EXTRACTION
# =====================================================

def extract_audio(video_path):

    output_dir = "data/extracted/audio"

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # -------------------------------------------------
    # Create unique filename
    # -------------------------------------------------

    filename = hashlib.md5(
        video_path.encode()
    ).hexdigest()

    audio_path = os.path.join(
        output_dir,
        filename + ".wav"
    )

    # -------------------------------------------------
    # Avoid extracting again
    # -------------------------------------------------

    if os.path.exists(audio_path):

        return audio_path

    video = None

    try:

        video = VideoFileClip(
            video_path
        )

        # -------------------------------------------------
        # Check whether video contains audio
        # -------------------------------------------------

        if video.audio is None:

            print(
                "⚠️ No audio found:",
                video_path
            )

            return None

        # -------------------------------------------------
        # Limit audio to first 300 seconds
        # -------------------------------------------------

        video_duration = video.duration

        audio_duration = min(
            video_duration,
            MAX_AUDIO_SECONDS
        )

        print(
            f"🔊 Extracting audio: "
            f"0-{audio_duration:.1f}s"
        )

        # MoviePy v2
        audio_clip = video.audio.subclipped(
            0,
            audio_duration
        )

        audio_clip.write_audiofile(
            audio_path,
            logger=None
        )

        audio_clip.close()

        return audio_path

    except Exception as e:

        print(
            "❌ Audio extraction failed:",
            video_path
        )

        print(
            "Reason:",
            e
        )

        return None

    finally:

        if video is not None:

            try:

                video.close()

            except Exception:

                pass