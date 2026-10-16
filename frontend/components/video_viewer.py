"""
Frontend Component: Video Viewer
Displays stabilized video streams and comparison player in a clean, minimalist layout.
"""

import os
import streamlit as st


def render_video_section(
    original_path: str,
    stabilized_path: str,
    sbs_path: str,
    plot_path: str,
) -> None:
    """Renders organized video playback and clean download actions."""
    view_mode = st.radio(
        "Display Format",
        options=["Side-by-Side Composite", "Dual Streams (Original vs. Stabilized)"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if view_mode == "Side-by-Side Composite":
        if os.path.exists(sbs_path):
            st.video(sbs_path)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Original (Shaky)")
            st.video(original_path)
        with col2:
            st.caption("Stabilized (Smoothed)")
            if os.path.exists(stabilized_path):
                st.video(stabilized_path)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Clean download bar
    dcol1, dcol2, dcol3 = st.columns(3)
    with dcol1:
        if os.path.exists(stabilized_path):
            with open(stabilized_path, "rb") as f:
                st.download_button(
                    "Download Stabilized Video",
                    data=f.read(),
                    file_name="stabilized_output.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )

    with dcol2:
        if os.path.exists(sbs_path):
            with open(sbs_path, "rb") as f:
                st.download_button(
                    "Download Side-by-Side Video",
                    data=f.read(),
                    file_name="comparison_sbs.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )

    with dcol3:
        if os.path.exists(plot_path):
            with open(plot_path, "rb") as f:
                st.download_button(
                    "Download Trajectory Plot",
                    data=f.read(),
                    file_name="trajectory_plot.png",
                    mime="image/png",
                    use_container_width=True,
                )
