import cv2
import numpy as np

from modules.config import *

# =====================================================
# VISUAL FEATURE EXTRACTION (OpenCV)
# =====================================================

def extract_visual_features(video_path):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        cap.release()
        return None

    interval = max(int(fps * FRAME_SAMPLE_RATE), 1)

    prev_gray = None
    prev_frame = None
    prev_luminance = None

    saturation = []
    brightness = []

    motion = []
    edge_density = []
    colour_variance = []

    scene_changes = 0
    flickers = 0
    motion_spikes = 0

    frame_count = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_count >= fps * MAX_VIDEO_SECONDS:
            break

        if frame_count % interval != 0:
            frame_count += 1
            continue

        frame = cv2.resize(
            frame,
            (RESIZE_WIDTH, RESIZE_HEIGHT)
        )

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        saturation.append(
            hsv[:, :, 1].mean() / 255
        )

        brightness.append(
            gray.mean() / 255
        )

        colour_variance.append(
            np.var(frame.astype(np.float32))
        )

        edges = cv2.Canny(gray, 100, 200)

        edge_density.append(
            np.mean(edges > 0)
        )

        luminance = gray.mean()

        if prev_luminance is not None:

            if abs(luminance - prev_luminance) > FLICKER_THRESHOLD:
                flickers += 1

        prev_luminance = luminance

        if prev_gray is not None:

            flow = cv2.calcOpticalFlowFarneback(
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

            mag = np.sqrt(
                flow[..., 0] ** 2 +
                flow[..., 1] ** 2
            )

            value = np.mean(mag)

            motion.append(value)

            if value > MOTION_SPIKE_THRESHOLD:
                motion_spikes += 1

        if prev_frame is not None:

            h1 = cv2.calcHist(
                [prev_frame],
                [0],
                None,
                [256],
                [0, 256]
            )

            h2 = cv2.calcHist(
                [frame],
                [0],
                None,
                [256],
                [0, 256]
            )

            diff = cv2.compareHist(
                h1,
                h2,
                cv2.HISTCMP_BHATTACHARYYA
            )

            if diff > SCENE_THRESHOLD:
                scene_changes += 1

        prev_gray = gray
        prev_frame = frame

        frame_count += 1

    cap.release()

    duration = max(len(brightness), 1)

    motion_entropy = 0

    if len(motion) > 5:

        hist, _ = np.histogram(
            motion,
            bins=20,
            density=True
        )

        hist += 1e-8

        motion_entropy = -np.sum(
            hist * np.log2(hist)
        )

    return {

        "avg_saturation":
            float(np.mean(saturation)),

        "avg_brightness":
            float(np.mean(brightness)),

        "motion_mean":
            float(np.mean(motion)) if motion else 0,

        "motion_std":
            float(np.std(motion)) if motion else 0,

        "motion_entropy":
            float(motion_entropy),

        "scene_rate":
            scene_changes / duration,

        "flicker_rate":
            flickers / duration,

        "motion_spike_rate":
            motion_spikes / duration,

        "edge_density":
            float(np.mean(edge_density)),

        "colour_variance":
            float(np.mean(colour_variance))
    }