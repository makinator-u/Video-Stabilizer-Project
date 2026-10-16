"""
View Window: Home Portal
Clean, minimalist launchpad presenting strictly the actual core functions of the project.
Warm Ember color scheme.
"""

import streamlit as st


def render_home_portal() -> None:
    """Renders launch options strictly for the actual functions of the project."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2.5rem 0 2rem 0;">
            <p style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #d4943a; margin-bottom: 8px;">
                Image &amp; Video Processing &bull; Core Pipeline
            </p>
            <h1 style="font-size: 2.4rem; font-weight: 700; letter-spacing: -0.03em; color: #f0e6d8; margin: 0;">
                Video Stabilization System
            </h1>
            <p style="font-size: 0.95rem; color: #b8a48e; max-width: 540px; margin: 10px auto 0 auto; line-height: 1.5;">
                Select a project function below to execute:
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="stat-card" style="height: 180px;">
                <div class="stat-label">Function 01</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #f0e6d8; margin: 4px 0 8px 0;">Video Stabilization</div>
                <div style="font-size: 0.85rem; color: #b8a48e; line-height: 1.5;">
                    Stabilize shaky footage using 2D partial affine motion compensation, center-scaling border zoom, and side-by-side comparison playback.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Stabilizer →", key="btn_stabilizer", use_container_width=True):
            st.session_state["active_window"] = "Video Stabilization"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="stat-card" style="height: 180px;">
                <div class="stat-label">Function 02</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #f0e6d8; margin: 4px 0 8px 0;">Optical Flow &amp; Feature Tracking</div>
                <div style="font-size: 0.85rem; color: #b8a48e; line-height: 1.5;">
                    Inspect Shi-Tomasi corners and Lucas-Kanade motion vectors frame-by-frame with RANSAC background inlier vs. outlier classification.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Optical Flow →", key="btn_flow", use_container_width=True):
            st.session_state["active_window"] = "Optical Flow Tracking"
            st.rerun()

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            """
            <div class="stat-card" style="height: 180px;">
                <div class="stat-label">Function 03</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #f0e6d8; margin: 4px 0 8px 0;">Camera Trajectory Analysis</div>
                <div style="font-size: 0.85rem; color: #b8a48e; line-height: 1.5;">
                    Plot and analyze raw vs. smoothed camera motion curves (X, Y, and rotation) and decompose residual high-frequency hand tremors.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Trajectory Analysis →", key="btn_trajectory", use_container_width=True):
            st.session_state["active_window"] = "Trajectory Analysis"
            st.rerun()

    with col4:
        st.markdown(
            """
            <div class="stat-card" style="height: 180px;">
                <div class="stat-label">Function 04</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #f0e6d8; margin: 4px 0 8px 0;">Window Size Benchmarks</div>
                <div style="font-size: 0.85rem; color: #b8a48e; line-height: 1.5;">
                    Evaluate filtering tradeoffs across window lengths (W = 10, 30, 60 frames) measuring Inter-frame Transformation Fidelity (ITF gain).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Benchmarks →", key="btn_benchmark", use_container_width=True):
            st.session_state["active_window"] = "Window Size Benchmarks"
            st.rerun()
