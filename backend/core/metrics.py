"""
Backend Core: Metrics
Inter-frame Transformation Fidelity (ITF / PSNR) and cropping ratio calculations.
"""

import cv2
import numpy as np
from typing import Optional, Dict


def compute_itf(video_path: str, max_frames: Optional[int] = None) -> float:
    """Computes average inter-frame PSNR."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0

    psnr_values = []
    ret, prev_frame = cap.read()
    if not ret or prev_frame is None:
        cap.release()
        return 0.0

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    count = 0

    while True:
        ret, curr_frame = cap.read()
        if not ret or curr_frame is None:
            break
        count += 1
        if max_frames and count > max_frames:
            break

        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        mse = np.mean((prev_gray.astype(np.float64) - curr_gray.astype(np.float64)) ** 2)

        if mse == 0:
            psnr = 100.0
        else:
            psnr = 10.0 * np.log10((255.0 ** 2) / mse)

        psnr_values.append(psnr)
        prev_gray = curr_gray

    cap.release()
    return float(np.mean(psnr_values)) if psnr_values else 0.0


def compute_cropping_ratio(zoom_factor: float) -> Dict[str, float]:
    """Computes preserved area and lost area percentage."""
    ratio = 1.0 / (zoom_factor ** 2)
    return {
        "preserved_ratio": round(ratio, 4),
        "preserved_pct": round(ratio * 100.0, 2),
        "lost_pct": round((1.0 - ratio) * 100.0, 2),
    }
