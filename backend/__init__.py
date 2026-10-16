"""
Backend Architecture Package
Combines core algorithms, pipeline services, visualization, and video utilities.
"""

from .pipeline.stabilizer_service import VideoStabilizerService
from .core.motion_estimator import MotionEstimator
from .core.warper import FrameWarper
from .core.trajectory import (
    build_trajectory,
    smooth_trajectory,
    compute_trajectory_difference,
)
from .core.metrics import compute_itf, compute_cropping_ratio
from .visualization.trajectory_plotter import plot_trajectories

__all__ = [
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
