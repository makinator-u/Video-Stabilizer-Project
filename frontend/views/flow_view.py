"""
View Window: Optical Flow & Feature Visualizer
Inspects Shi-Tomasi corners, Lucas-Kanade motion vectors, and RANSAC inliers/outliers
on a frame-by-frame basis.
"""

import cv2
import numpy as np
import streamlit as st


def render_flow_window(video_path: str) -> None:
    """Renders frame-by-frame feature tracking and optical flow diagnostics."""
    st.markdown("<p class='section-title'>Optical Flow & Corner Tracking Inspector</p>", unsafe_allow_html=True)
    st.caption("Visually inspect Shi-Tomasi corners and Lucas-Kanade motion vectors. RANSAC inliers (camera background motion) are highlighted in emerald, and outliers (moving objects/noise) in crimson.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error(f"Cannot open video: {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        frame_idx = st.slider(
            "Select Frame Pair (t -> t+1)",
            min_value=0,
            max_value=max(0, frame_count - 2),
            value=min(15, max(0, frame_count - 2)),
        )
    with col_ctrl2:
        draw_scale = st.slider("Vector Scale", min_value=1.0, max_value=8.0, value=3.0, step=0.5)

    # Read frame t and frame t+1
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret1, frame1 = cap.read()
    ret2, frame2 = cap.read()
    cap.release()

    if not ret1 or not ret2 or frame1 is None or frame2 is None:
        st.warning("Could not read frame pair.")
        return

    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Feature Detection
    corners = cv2.goodFeaturesToTrack(
        gray1,
        maxCorners=250,
        qualityLevel=0.01,
        minDistance=25,
        blockSize=3,
    )

    vis_frame = frame1.copy()
    num_detected = 0
    num_tracked = 0
    num_inliers = 0
    dx, dy, da = 0.0, 0.0, 0.0

    if corners is not None and len(corners) >= 4:
        num_detected = len(corners)
        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(
            gray1,
            gray2,
            corners,
            None,
            winSize=(21, 21),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
        )

        valid_idx = np.where(status == 1)[0]
        num_tracked = len(valid_idx)

        if num_tracked >= 4:
            good_prev = corners[valid_idx]
            good_curr = curr_pts[valid_idx]

            matrix, inliers = cv2.estimateAffinePartial2D(
                good_prev,
                good_curr,
                method=cv2.RANSAC,
                ransacReprojThreshold=3.0,
            )

            inlier_mask = inliers.ravel() if inliers is not None else np.zeros(num_tracked, dtype=int)
            num_inliers = int(np.sum(inlier_mask))

            if matrix is not None:
                dx = float(matrix[0, 2])
                dy = float(matrix[1, 2])
                da = float(np.arctan2(matrix[1, 0], matrix[0, 0]))

            # Draw vectors on vis_frame
            for i, (p0, p1) in enumerate(zip(good_prev, good_curr)):
                x0, y0 = int(p0[0][0]), int(p0[0][1])
                vx = (p1[0][0] - p0[0][0]) * draw_scale
                vy = (p1[0][1] - p0[0][1]) * draw_scale
                x1, y1 = int(x0 + vx), int(y0 + vy)

                is_inlier = inlier_mask[i] == 1
                color = (50, 220, 100) if is_inlier else (50, 50, 240)  # Green vs Red

                cv2.circle(vis_frame, (x0, y0), 3, (255, 200, 50), -1)
                cv2.arrowedLine(vis_frame, (x0, y0), (x1, y1), color, 1, tipLength=0.25)

    # Telemetry Tiles
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Corners Detected", num_detected)
    with m2:
        st.metric("Points Tracked", f"{num_tracked} / {num_detected}")
    with m3:
        inlier_pct = (num_inliers / num_tracked * 100.0) if num_tracked > 0 else 0
        st.metric("RANSAC Inliers", f"{num_inliers} ({inlier_pct:.1f}%)")
    with m4:
        st.metric("Motion (dx, dy, dθ)", f"{dx:.1f}px, {dy:.1f}px, {np.degrees(da):.2f}°")

    st.image(cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
    st.caption(f"Frame {frame_idx} -> {frame_idx + 1} | Yellow: Detected Corners | Green: Background Inliers | Red: Foreground Outliers / Noise")
