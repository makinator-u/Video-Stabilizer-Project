"""
Backend Visualization: Trajectory Plotter
Publication-grade trajectory figures comparing raw vs. smoothed motion.
"""

import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Optional


def plot_trajectories(
    trajectory: np.ndarray,
    smoothed_trajectory: np.ndarray,
    save_path: Optional[str] = None,
) -> matplotlib.figure.Figure:
    """Renders dark-themed 3-panel comparison figure."""
    frames = np.arange(len(trajectory))

    fig, axes = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
    fig.patch.set_facecolor("#0e1117")

    titles = [
        ("X Translation Trajectory (Pixels)", "X (px)", trajectory[:, 0], smoothed_trajectory[:, 0]),
        ("Y Translation Trajectory (Pixels)", "Y (px)", trajectory[:, 1], smoothed_trajectory[:, 1]),
        ("Rotation Angle Trajectory (Degrees)", "Angle (deg)", np.degrees(trajectory[:, 2]), np.degrees(smoothed_trajectory[:, 2])),
    ]

    colors = ["#ff5252", "#448aff", "#69f0ae"]

    for ax, (title, ylabel, raw, smooth), col in zip(axes, titles, colors):
        ax.set_facecolor("#161b22")
        ax.plot(frames, raw, label="Raw (Shaky)", color="#9e9e9e", linestyle="--", linewidth=1.2, alpha=0.85)
        ax.plot(frames, smooth, label="Smoothed", color=col, linewidth=2.2)

        ax.set_title(title, color="#f0f6fc", fontsize=12, fontweight="bold", pad=8)
        ax.set_ylabel(ylabel, color="#c9d1d9", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.3, color="#8b949e")
        ax.tick_params(colors="#8b949e", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#30363d")

        legend = ax.legend(loc="upper right", framealpha=0.8, facecolor="#0d1117", edgecolor="#30363d")
        for text in legend.get_texts():
            text.set_color("#c9d1d9")

    axes[-1].set_xlabel("Frame Index", color="#c9d1d9", fontsize=10)
    fig.suptitle(
        "Video Camera Trajectory: Raw vs. Smoothed Motion",
        color="#f0f6fc",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        plt.savefig(save_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())

    return fig
