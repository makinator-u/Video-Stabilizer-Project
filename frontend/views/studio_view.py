"""
View Window: Stabilization Studio
Core video stabilization workspace with parameter tuning, progress feedback,
KPI metric tiles, and side-by-side video playback.
"""

import os
import time
import tempfile
import streamlit as st

from backend.pipeline.stabilizer_service import VideoStabilizerService
from backend.utils.video_io import get_video_info
from database.db_manager import DatabaseManager
from frontend.components.metrics_display import render_kpi_cards
from frontend.components.video_viewer import render_video_section


def render_studio_window(selected_video_path: str, db: DatabaseManager) -> None:
    """Renders the primary stabilization studio workspace."""
    st.markdown("<p class='section-title'>Stabilization Studio Workspace</p>", unsafe_allow_html=True)
    st.caption("Apply 2D partial affine motion estimation, trajectory smoothing, and border fix homothety to stabilize footage.")

    if not selected_video_path or not os.path.exists(selected_video_path):
        st.warning("Please choose a video from the sidebar to begin.")
        return

    try:
        info = get_video_info(selected_video_path)
    except Exception as e:
        st.error(f"Error inspecting video metadata: {e}")
        return

    # Metadata Strip
    st.markdown(
        f"""
        <div style="display:flex; gap:20px; font-size:0.82rem; color:#b8a48e; padding:8px 0; border-bottom:1px solid rgba(210,160,90,0.10); margin-bottom:16px;">
            <div><span style="color:#8a7560;">Clip:</span> {os.path.basename(selected_video_path)}</div>
            <div><span style="color:#8a7560;">Resolution:</span> {info['width']} &times; {info['height']}</div>
            <div><span style="color:#8a7560;">FPS:</span> {info['fps']:.1f}</div>
            <div><span style="color:#8a7560;">Frames:</span> {info['frame_count']}</div>
            <div><span style="color:#8a7560;">Duration:</span> {info['duration']:.2f}s</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Inline parameter tuning
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        window_size = st.slider(
            "Smoothing Window (Frames)",
            min_value=5,
            max_value=120,
            value=30,
            step=5,
            help="Temporal moving-average window length. 30 frames ≈ 1.0s at 30 FPS.",
        )
    with p_col2:
        zoom_factor = st.slider(
            "Border Zoom Homothety",
            min_value=1.00,
            max_value=1.15,
            value=1.04,
            step=0.01,
            help="Center-scaling zoom factor to hide warp margin voids.",
        )

    with st.expander("Advanced Optical Flow & RANSAC Hyperparameters", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            max_corners = st.slider("Max Corners", 50, 500, 200, 25)
        with c2:
            quality_level = st.select_slider("Corner Quality", options=[0.001, 0.005, 0.01, 0.02, 0.05], value=0.01)
        with c3:
            min_distance = st.slider("Min Distance (px)", 10, 60, 30, 5)
        with c4:
            ransac_thresh = st.slider("RANSAC Threshold (px)", 1.0, 10.0, 3.0, 0.5)

    start_button = st.button("Run Stabilization", type="primary", use_container_width=True)

    output_dir = os.path.join(tempfile.gettempdir(), "stabilization_studio_outputs")
    os.makedirs(output_dir, exist_ok=True)
    stabilized_output_path = os.path.join(output_dir, "stabilized_result.mp4")
    sbs_output_path = os.path.join(output_dir, "side_by_side_result.mp4")
    plot_output_path = os.path.join(output_dir, "trajectory_plot.png")

    if start_button:
        progress_bar = st.progress(0.0)
        status_box = st.empty()

        def update_progress(p: float, msg: str):
            progress_bar.progress(min(max(p, 0.0), 1.0))
            status_box.markdown(f"<span style='font-size:0.82rem; color:#b8a48e;'>{msg}</span>", unsafe_allow_html=True)

        stabilizer = VideoStabilizerService(
            max_corners=max_corners,
            quality_level=quality_level,
            min_distance=min_distance,
            window_size=window_size,
            zoom_factor=zoom_factor,
            ransac_threshold=ransac_thresh,
        )

        t_start = time.time()
        try:
            results = stabilizer.process(
                input_path=selected_video_path,
                output_path=stabilized_output_path,
                side_by_side_path=sbs_output_path,
                plot_path=plot_output_path,
                progress_callback=update_progress,
            )
            elapsed = time.time() - t_start
            results["elapsed_time"] = elapsed

            # Log to SQLite Database
            vid_id = db.register_video(selected_video_path, info)
            job_id = db.record_job(
                video_id=vid_id,
                window_size=window_size,
                zoom_factor=zoom_factor,
                results=results,
                processing_time=elapsed,
                output_path=stabilized_output_path,
                sbs_path=sbs_output_path,
                plot_path=plot_output_path,
            )
            results["job_id"] = job_id

            st.session_state["results"] = results
            st.session_state["processed"] = True
            progress_bar.empty()
            status_box.empty()
        except Exception as e:
            st.error(f"Stabilization failed: {e}")

    if st.session_state.get("processed") and "results" in st.session_state:
        results = st.session_state["results"]
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        render_kpi_cards(results)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        render_video_section(
            original_path=selected_video_path,
            stabilized_path=stabilized_output_path,
            sbs_path=sbs_output_path,
            plot_path=plot_output_path,
        )
