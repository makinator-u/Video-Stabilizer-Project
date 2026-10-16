"""
Backend Core: Motion Estimator
Shi-Tomasi corners, Pyramidal Lucas-Kanade optical flow, and RANSAC 2D partial affine.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional, Callable
from ..utils.video_io import get_video_info


class MotionEstimator:
    """Estimates inter-frame 2D ego-motion transforms [dx, dy, da]."""

    def __init__(
        self,
        max_corners: int = 200,
        quality_level: float = 0.01,
        min_distance: int = 30,
        block_size: int = 3,
        ransac_threshold: float = 3.0,
    ):
        self.max_corners = max_corners
        self.quality_level = quality_level
        self.min_distance = min_distance
        self.block_size = block_size
        self.ransac_threshold = ransac_threshold

    def detect_corners(self, gray_frame: np.ndarray) -> Optional[np.ndarray]:
        """Detects salient corners using the Shi-Tomasi method."""
        return cv2.goodFeaturesToTrack(
            gray_frame,
            maxCorners=self.max_corners,
            qualityLevel=self.quality_level,
            minDistance=self.min_distance,
            blockSize=self.block_size,
        )

    def track_corners(
        self,
        prev_gray: np.ndarray,
        curr_gray: np.ndarray,
        prev_pts: np.ndarray,
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Tracks corners across consecutive frames via Pyramidal Lucas-Kanade Optical Flow."""
        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(
            prev_gray,
            curr_gray,
            prev_pts,
            None,
            winSize=(21, 21),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
        )
        valid_idx = np.where(status == 1)[0]
        if len(valid_idx) < 4:
            return None, None
        return prev_pts[valid_idx], curr_pts[valid_idx]

    def estimate_frame_motion(
        self,
        prev_pts: np.ndarray,
        curr_pts: np.ndarray,
    ) -> Tuple[float, float, float, bool]:
        """Estimates 2D partial affine transform (dx, dy, da) using RANSAC."""
        matrix, _ = cv2.estimateAffinePartial2D(
            prev_pts,
            curr_pts,
            method=cv2.RANSAC,
            ransacReprojThreshold=self.ransac_threshold,
        )
        if matrix is not None:
            dx = float(matrix[0, 2])
            dy = float(matrix[1, 2])
            da = float(np.arctan2(matrix[1, 0], matrix[0, 0]))
            return dx, dy, da, True

        return 0.0, 0.0, 0.0, False

    def estimate_video_transforms(
        self,
        video_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Extracts per-frame transforms [dx, dy, da] across the entire video."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        info = get_video_info(video_path)
        frame_count = info["frame_count"]

        ret, prev_frame = cap.read()
        if not ret or prev_frame is None:
            cap.release()
            raise ValueError("Failed to read initial video frame.")

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        transforms = []
        last_valid = np.array([0.0, 0.0, 0.0], dtype=np.float64)

        frame_idx = 0
        while True:
            ret, curr_frame = cap.read()
            if not ret or curr_frame is None:
                break
            frame_idx += 1

            if progress_callback and frame_count > 1:
                progress_callback(
                    frame_idx / (frame_count - 1),
                    f"Tracking optical flow: Frame {frame_idx}/{frame_count - 1}",
                )

            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            prev_pts = self.detect_corners(prev_gray)

            dx, dy, da, success = 0.0, 0.0, 0.0, False
            if prev_pts is not None and len(prev_pts) >= 4:
                good_prev, good_curr = self.track_corners(prev_gray, curr_gray, prev_pts)
                if good_prev is not None and len(good_prev) >= 4:
                    dx, dy, da, success = self.estimate_frame_motion(good_prev, good_curr)

            if success:
                current_transform = np.array([dx, dy, da], dtype=np.float64)
                last_valid = current_transform
            else:
                current_transform = last_valid.copy()

            transforms.append(current_transform)
            prev_gray = curr_gray

        cap.release()
        transforms = np.array(transforms, dtype=np.float64)
        if len(transforms) == 0:
            raise ValueError("No video frames could be tracked.")

        return transforms, info
