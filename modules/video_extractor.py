import cv2
import os
from moviepy import VideoFileClip

def extract_frames(video_path, fps_rate=1):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    interval = int(fps / fps_rate)
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


def extract_audio(video_path):
    # create proper folder
    output_dir = "data/extracted"
    os.makedirs(output_dir, exist_ok=True)

    audio_path = os.path.join(output_dir, "audio.wav")

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

    return audio_path