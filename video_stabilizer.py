"""
Root Compatibility Layer
Exposes the core functions and classes of the video stabilization pipeline:
- VideoStabilizer / VideoStabilizerService
- MotionEstimator (Shi-Tomasi + Lucas-Kanade + RANSAC affine)
- FrameWarper (Center zoom, matrix composition, bilinear affine warp)
- Trajectory tools (build, smooth with moving average, difference)
- Metrics (ITF / PSNR, cropping ratio)
- Visualization (plot_trajectories)
"""

from backend.pipeline.stabilizer_service import (
    VideoStabilizerService,
    VideoStabilizerService as VideoStabilizer,
)
from backend.core.motion_estimator import MotionEstimator
from backend.core.warper import FrameWarper
from backend.core.trajectory import (
    build_trajectory,
    smooth_trajectory,
    compute_trajectory_difference,
)
from backend.core.metrics import compute_itf, compute_cropping_ratio
from backend.visualization.trajectory_plotter import plot_trajectories

__all__ = [
    "VideoStabilizer",
    "VideoStabilizerService",
    "MotionEstimator",
    "FrameWarper",
    "build_trajectory",
    "smooth_trajectory",
    "compute_trajectory_difference",
    "compute_itf",
    "compute_cropping_ratio",
    "plot_trajectories",
]
