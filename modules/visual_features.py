import cv2
import numpy as np

def compute_saturation(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return np.mean(hsv[:, :, 1]) / 255


def compute_motion(prev_frame, curr_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, curr_gray, None,
        0.5, 3, 15, 3, 5, 1.2, 0
    )

    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
    return np.mean(magnitude)


def compute_scene_change(prev_frame, curr_frame):
    diff = cv2.absdiff(prev_frame, curr_frame)
    return np.mean(diff)