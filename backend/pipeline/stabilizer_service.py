"""
Backend Pipeline Service: Video Stabilizer Service
High-level service orchestrating motion tracking, trajectory smoothing,
center-scale border warping, database logging, and metric evaluation.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, Optional, Callable

from ..core.motion_estimator import MotionEstimator
from ..core.trajectory import build_trajectory, smooth_trajectory, compute_trajectory_difference
from ..core.warper import FrameWarper
from ..core.metrics import compute_itf, compute_cropping_ratio
from ..visualization.trajectory_plotter import plot_trajectories
from ..utils.video_io import (
    get_video_info,
    create_video_writer,
    write_video_frame,
    close_video_writer,
)


class VideoStabilizerService:
    """Stabilization Service combining algorithm components with I/O and metrics."""

    def __init__(
        self,
        max_corners: int = 200,
        quality_level: float = 0.01,
        min_distance: int = 30,
        block_size: int = 3,
        window_size: int = 30,
        zoom_factor: float = 1.04,
        ransac_threshold: float = 3.0,
    ):
        self.window_size = window_size
        self.zoom_factor = zoom_factor

        self.motion_estimator = MotionEstimator(
            max_corners=max_corners,
            quality_level=quality_level,
            min_distance=min_distance,
            block_size=block_size,
            ransac_threshold=ransac_threshold,
        )
        self.warper = FrameWarper(zoom_factor=zoom_factor)

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """Video metadata inspection."""
        return get_video_info(video_path)

    @staticmethod
    def compute_itf(video_path: str, max_frames: Optional[int] = None) -> float:
        """Computes ITF (average PSNR)."""
        return compute_itf(video_path, max_frames)

    def process(
        self,
        input_path: str,
        output_path: str,
        side_by_side_path: Optional[str] = None,
        plot_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """Executes full stabilization pipeline."""
        # 1. Motion estimation
        transforms, info = self.motion_estimator.estimate_video_transforms(
            input_path,
            progress_callback=lambda p, msg: progress_callback(p * 0.45, msg)
            if progress_callback
            else None,
        )

        n_frames = info["frame_count"]
        fps = info["fps"]
        w = info["width"]
        h = info["height"]

        # 2. Trajectory accumulation
        trajectory = build_trajectory(transforms)

        # 3. Trajectory smoothing
        smoothed_trajectory = smooth_trajectory(trajectory, self.window_size)

        # 4. Compensatory offsets
        diff = compute_trajectory_difference(trajectory, smoothed_trajectory)

        # 5. Frame warping
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to reopen video: {input_path}")

        stab_writer = create_video_writer(output_path, fps, w, h)
        sbs_writer = (
            create_video_writer(side_by_side_path, fps, w * 2, h)
            if side_by_side_path
            else None
        )

        scale_mat = self.warper.get_center_zoom_matrix(w, h)

        ret, frame0 = cap.read()
        if not ret or frame0 is None:
            cap.release()
            close_video_writer(stab_writer)
            if sbs_writer:
                close_video_writer(sbs_writer)
            raise ValueError("Error reading anchor frame from video.")

        frame0_stab = self.warper.warp(frame0, scale_mat, w, h)
        write_video_frame(stab_writer, frame0_stab)

        if sbs_writer:
            sbs0 = self.warper.render_side_by_side(frame0, frame0_stab, 0, n_frames, fps)
            write_video_frame(sbs_writer, sbs0)

        for t in range(len(transforms)):
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            if progress_callback:
                progress_callback(
                    0.45 + 0.45 * ((t + 1) / len(transforms)),
                    f"Warping & Stabilizing: Frame {t + 2}/{n_frames}",
                )

            dx = diff[t + 1, 0]
            dy = diff[t + 1, 1]
            da = diff[t + 1, 2]

            m_combined = self.warper.compose_transform(scale_mat, dx, dy, da)
            frame_stab = self.warper.warp(frame, m_combined, w, h)

            write_video_frame(stab_writer, frame_stab)

            if sbs_writer:
                sbs = self.warper.render_side_by_side(frame, frame_stab, t + 1, n_frames, fps)
                write_video_frame(sbs_writer, sbs)

        cap.release()
        close_video_writer(stab_writer)
        if sbs_writer:
            close_video_writer(sbs_writer)

        if progress_callback:
            progress_callback(0.92, "Calculating Inter-frame Transformation Fidelity (ITF)...")

        # 6. Evaluation metrics
        itf_original = compute_itf(input_path)
        itf_stabilized = compute_itf(output_path)
        itf_improvement = itf_stabilized - itf_original
        crop_stats = compute_cropping_ratio(self.zoom_factor)

        # 7. Visualization plot
        fig = plot_trajectories(trajectory, smoothed_trajectory, plot_path)

        if progress_callback:
            progress_callback(1.0, "Stabilization Complete!")

        return {
            "fps": fps,
            "width": w,
            "height": h,
            "frame_count": n_frames,
            "window_size": self.window_size,
            "zoom_factor": self.zoom_factor,
            "itf_original": round(itf_original, 2),
            "itf_stabilized": round(itf_stabilized, 2),
            "itf_improvement": round(itf_improvement, 2),
            "cropping_ratio": crop_stats["preserved_ratio"],
            "crop_loss_pct": crop_stats["lost_pct"],
            "trajectory": trajectory,
            "smoothed_trajectory": smoothed_trajectory,
            "plot_figure": fig,
        }
