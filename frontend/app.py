"""
Frontend Application: Video Stabilization Studio
Streamlined to strictly the 4 actual core functions of the project:
1. Video Stabilization (Core stabilization, parameter tuning, side-by-side player)
2. Optical Flow & Feature Tracking (Frame-by-frame corner vectors & RANSAC consensus)
3. Camera Trajectory Analysis (Raw vs smoothed paths & residual jitter decomposition)
4. Window Size Benchmarks (Multi-window tradeoff experiments W = 10, 30, 60)
"""

import os
import sys
import tempfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import streamlit as st
from database.db_manager import DatabaseManager

# Import Core Function Views
from frontend.views import (
    render_home_portal,
    render_studio_window,
    render_flow_window,
    render_trajectory_window,
    render_benchmark_window,
)

# Page Configuration
st.set_page_config(
    page_title="Video Stabilization System",
    page_icon="⏺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load Minimalist Stylesheet
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Database
db = DatabaseManager()

# Session State for Window Navigation
if "active_window" not in st.session_state:
    st.session_state["active_window"] = "Home"

# Top Navigation Bar
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    if st.session_state["active_window"] != "Home":
        if st.button("← Return to Home", key="btn_back_home"):
            st.session_state["active_window"] = "Home"
            st.rerun()
with top_col2:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 4px;">
            <span class="status-pill"><span class="status-dot"></span> Pipeline Ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------
# 1. HOME PORTAL: Shows ONLY the actual functions of the project
# -------------------------------------------------------------
if st.session_state["active_window"] == "Home":
    render_home_portal()

# -------------------------------------------------------------
# 2. FUNCTION WINDOWS
# -------------------------------------------------------------
else:
    # Sidebar provides video selection and function switcher
    with st.sidebar:
        st.markdown("### Functions")
        function_options = [
            "Home",
            "Video Stabilization",
            "Optical Flow Tracking",
            "Trajectory Analysis",
            "Window Size Benchmarks",
        ]
        chosen_window = st.selectbox(
            "Active Function",
            function_options,
            index=function_options.index(st.session_state["active_window"])
            if st.session_state["active_window"] in function_options
            else 1,
            label_visibility="collapsed",
        )
        if chosen_window != st.session_state["active_window"]:
            st.session_state["active_window"] = chosen_window
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("### Source Video")

        video_source = st.radio(
            "Source Type",
            options=["Storage Samples", "Upload Video"],
            label_visibility="collapsed",
        )

        sample_candidates = [
            ("Handheld Camera Pan", "storage/samples/shaky_sample_pan.mp4"),
            ("Handheld Pan (Fallback)", "samples/shaky_sample_pan.mp4"),
            ("Dynamic Moving Car", "storage/samples/shaky_sample_moving_obj.mp4"),
            ("Dynamic Car (Fallback)", "samples/shaky_sample_moving_obj.mp4"),
        ]

        available_samples = {}
        for label, rel_path in sample_candidates:
            abs_p = os.path.join(PROJECT_ROOT, rel_path)
            if os.path.exists(abs_p):
                available_samples[label] = abs_p

        selected_video_path = None

        if video_source == "Storage Samples":
            if available_samples:
                sample_choice = st.selectbox(
                    "Choose Preloaded Clip",
                    list(available_samples.keys()),
                    label_visibility="collapsed",
                )
                selected_video_path = available_samples[sample_choice]
            else:
                st.caption("No sample clips found in storage/samples.")
        else:
            uploaded_file = st.file_uploader(
                "Upload Video",
                type=["mp4", "mov", "avi"],
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tfile.write(uploaded_file.read())
                tfile.flush()
                selected_video_path = tfile.name

    current = st.session_state["active_window"]

    # 1. Video Stabilization Function
    if current == "Video Stabilization":
        render_studio_window(selected_video_path, db)

    # 2. Optical Flow & Feature Tracking Function
    elif current == "Optical Flow Tracking":
        if selected_video_path:
            render_flow_window(selected_video_path)
        else:
            st.info("Select a video in the sidebar to inspect optical flow vectors.")

    # 3. Camera Trajectory Analysis Function
    elif current == "Trajectory Analysis":
        results = st.session_state.get("results")
        if results:
            render_trajectory_window(results)
        else:
            st.info("Please run the Video Stabilization function first to compute camera trajectories.")

    # 4. Window Size Benchmarks Function
    elif current == "Window Size Benchmarks":
        if selected_video_path:
            render_benchmark_window(selected_video_path, db)
        else:
            st.info("Select a video in the sidebar to run benchmarks.")
