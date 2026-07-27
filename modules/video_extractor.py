"""
===========================================================
VIDEO EXTRACTION MODULE

Handles:
- Frame extraction
- Audio extraction

===========================================================
"""


import cv2
import os
import hashlib

from moviepy import VideoFileClip



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


    # create unique filename

    filename = hashlib.md5(
        video_path.encode()
    ).hexdigest()


    audio_path = os.path.join(
        output_dir,
        filename + ".wav"
    )


    # avoid extracting again

    if os.path.exists(audio_path):

        return audio_path


    video = None

    try:

        video = VideoFileClip(
            video_path
        )


        # check if video contains audio

        if video.audio is None:

            video.close()

            print(
                "⚠️ No audio found:",
                video_path
            )

            return None



        video.audio.write_audiofile(
            audio_path,
            logger=None
        )


        video.close()


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


        # ensure video closes after failure

        if video is not None:

            try:

                video.close()

            except:

                pass


        return None