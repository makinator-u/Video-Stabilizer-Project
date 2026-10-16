"""
Backend Core: Trajectory
Cumulative camera pose integration and moving-average smoothing with edge padding.
"""

import numpy as np


def build_trajectory(transforms: np.ndarray) -> np.ndarray:
    """Accumulates frame motions into global trajectory P(t) = sum(Delta P)."""
    trajectory = np.zeros((len(transforms) + 1, 3), dtype=np.float64)
    trajectory[1:] = np.cumsum(transforms, axis=0)
    return trajectory


def smooth_trajectory(trajectory: np.ndarray, window_size: int = 30) -> np.ndarray:
    """Moving-average filter with symmetric edge replication padding."""
    if window_size <= 1:
        return trajectory.copy()

    n_samples, n_dims = trajectory.shape
    if window_size % 2 == 0:
        window_size += 1
    radius = window_size // 2

    kernel = np.ones(window_size, dtype=np.float64) / window_size
    smoothed = np.zeros_like(trajectory)

    for d in range(n_dims):
        padded = np.pad(trajectory[:, d], (radius, radius), mode="edge")
        smoothed_dim = np.convolve(padded, kernel, mode="valid")
        smoothed[:, d] = smoothed_dim[:n_samples]

    return smoothed


def compute_trajectory_difference(
    trajectory: np.ndarray, smoothed_trajectory: np.ndarray
) -> np.ndarray:
    """Computes compensatory offset: P_smooth(t) - P_raw(t)."""
    return smoothed_trajectory - trajectory
