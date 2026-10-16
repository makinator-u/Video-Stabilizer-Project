"""
View Window: Trajectory Laboratory
Deep-dive exploration of camera trajectory integration, moving-average smoothing,
and residual high-frequency jitter decomposition.
"""

import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


def render_trajectory_window(results: dict) -> None:
    """Renders comprehensive trajectory and residual vibration analysis."""
    st.markdown("<p class='section-title'>Camera Pose Trajectory & Jitter Decomposition</p>", unsafe_allow_html=True)
    st.caption("Inspect the macroscopic intentional camera path vs. isolated high-frequency hand tremors.")

    if not results or "trajectory" not in results:
        st.info("Run stabilization in the Studio first to populate trajectory curves.")
        return

    raw = results["trajectory"]
    smooth = results["smoothed_trajectory"]
    jitter = raw - smooth
    frames = np.arange(len(raw))

    # Metric summaries
    rms_x = np.sqrt(np.mean(jitter[:, 0] ** 2))
    rms_y = np.sqrt(np.mean(jitter[:, 1] ** 2))
    max_jitter_px = np.max(np.sqrt(jitter[:, 0] ** 2 + jitter[:, 1] ** 2))
    max_wobble_deg = np.max(np.abs(np.degrees(jitter[:, 2])))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("RMS X Jitter", f"{rms_x:.2f} px")
    with c2:
        st.metric("RMS Y Jitter", f"{rms_y:.2f} px")
    with c3:
        st.metric("Peak Radial Jitter", f"{max_jitter_px:.2f} px")
    with c4:
        st.metric("Peak Angular Wobble", f"{max_wobble_deg:.2f}°")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    analysis_mode = st.radio(
        "View Mode",
        options=["Raw vs. Smoothed Curves", "Isolated Jitter Perturbations (High-Frequency Residual)"],
        horizontal=True,
    )

    fig, axes = plt.subplots(3, 1, figsize=(11, 7.5), sharex=True)
    fig.patch.set_facecolor("#120e0a")

    if analysis_mode == "Raw vs. Smoothed Curves":
        titles = [
            ("X Translation (Pixels)", raw[:, 0], smooth[:, 0], "#d4943a"),
            ("Y Translation (Pixels)", raw[:, 1], smooth[:, 1], "#c4a24e"),
            ("Rotation Angle (Degrees)", np.degrees(raw[:, 2]), np.degrees(smooth[:, 2]), "#a3b858"),
        ]
        for ax, (ylabel, r_val, s_val, col) in zip(axes, titles):
            ax.set_facecolor("#1a1410")
            ax.plot(frames, r_val, label="Raw (Shaky)", color="#8a7560", linestyle="--", linewidth=1.2, alpha=0.8)
            ax.plot(frames, s_val, label="Smoothed", color=col, linewidth=2.0)
            ax.set_ylabel(ylabel, color="#b8a48e", fontsize=9)
            ax.grid(True, linestyle=":", alpha=0.25, color="#6b5a46")
            ax.tick_params(colors="#8a7560", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#3d2e1e")
            ax.legend(loc="upper right", framealpha=0.6, facecolor="#120e0a", edgecolor="#3d2e1e", fontsize=8)
    else:
        titles = [
            ("Residual X Tremor (Pixels)", jitter[:, 0], "#d4943a"),
            ("Residual Y Tremor (Pixels)", jitter[:, 1], "#c4a24e"),
            ("Residual Angular Tremor (Degrees)", np.degrees(jitter[:, 2]), "#a3b858"),
        ]
        for ax, (ylabel, j_val, col) in zip(axes, titles):
            ax.set_facecolor("#1a1410")
            ax.axhline(0, color="#6b5a46", linestyle="-", linewidth=0.8, alpha=0.5)
            ax.plot(frames, j_val, label="Filtered Jitter", color=col, linewidth=1.5)
            ax.fill_between(frames, 0, j_val, color=col, alpha=0.15)
            ax.set_ylabel(ylabel, color="#b8a48e", fontsize=9)
            ax.grid(True, linestyle=":", alpha=0.25, color="#6b5a46")
            ax.tick_params(colors="#8a7560", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#3d2e1e")
            ax.legend(loc="upper right", framealpha=0.6, facecolor="#120e0a", edgecolor="#3d2e1e", fontsize=8)

    axes[-1].set_xlabel("Frame Index", color="#b8a48e", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
