"""
Backend Utility: Synthetic Data Generator
Generates reproducible shaky test video benchmarks.
"""

import os
import cv2
import numpy as np
from .video_io import create_video_writer, write_video_frame, close_video_writer


def generate_synthetic_shaky_video(
    output_path: str = "storage/samples/shaky_sample.mp4",
    num_frames: int = 150,
    fps: int = 30,
    width: int = 640,
    height: int = 360,
    shake_intensity: float = 12.0,
    rotation_shake_deg: float = 2.5,
    include_moving_object: bool = False,
) -> str:
    """Generates synthetic video with controlled camera tremor and intentional pan."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    canvas_w = width * 3
    canvas_h = height * 3
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)

    for y in range(canvas_h):
        r = int(30 + 50 * (y / canvas_h))
        g = int(40 + 60 * (1.0 - y / canvas_h))
        b = int(70 + 80 * (y / canvas_h))
        canvas[y, :] = [b, g, r]

    grid_spacing = 40
    for x in range(0, canvas_w, grid_spacing):
        cv2.line(canvas, (x, 0), (x, canvas_h), (80, 100, 120), 1)
    for y in range(0, canvas_h, grid_spacing):
        cv2.line(canvas, (0, y), (canvas_w, y), (80, 100, 120), 1)

    np.random.seed(42)
    colors = [
        (220, 180, 60),
        (50, 180, 240),
        (240, 80, 80),
        (100, 220, 120),
        (200, 100, 220),
        (255, 255, 255),
    ]

    for _ in range(350):
        cx = np.random.randint(50, canvas_w - 50)
        cy = np.random.randint(50, canvas_h - 50)
        size = np.random.randint(15, 65)
        shape_type = np.random.choice(["rect", "circle", "poly", "cross", "text"])
        col = colors[np.random.randint(0, len(colors))]

        if shape_type == "rect":
            cv2.rectangle(canvas, (cx, cy), (cx + size, cy + size), col, -1)
            cv2.rectangle(canvas, (cx, cy), (cx + size, cy + size), (20, 20, 20), 2)
        elif shape_type == "circle":
            cv2.circle(canvas, (cx, cy), size // 2, col, -1)
            cv2.circle(canvas, (cx, cy), size // 2, (30, 30, 30), 2)
        elif shape_type == "poly":
            pts = np.array([
                [cx, cy - size // 2],
                [cx + size // 2, cy + size // 2],
                [cx - size // 2, cy + size // 2],
            ], np.int32)
            cv2.fillPoly(canvas, [pts], col)
            cv2.polylines(canvas, [pts], True, (20, 20, 20), 2)
        elif shape_type == "cross":
            cv2.line(canvas, (cx - size, cy), (cx + size, cy), col, 4)
            cv2.line(canvas, (cx, cy - size), (cx, cy + size), col, 4)
        elif shape_type == "text":
            cv2.putText(canvas, "IVP-LAB", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2, cv2.LINE_AA)

    t = np.linspace(0, 1, num_frames)
    base_center_x = canvas_w / 2.0 + 200.0 * np.sin(2 * np.pi * 0.4 * t)
    base_center_y = canvas_h / 2.0 + 100.0 * np.cos(2 * np.pi * 0.4 * t)
    base_angle = 0.0

    np.random.seed(1337)
    shake_x = (
        shake_intensity * np.sin(2 * np.pi * 3.8 * t)
        + (shake_intensity * 0.5) * np.sin(2 * np.pi * 7.5 * t)
        + np.random.normal(0, shake_intensity * 0.35, num_frames)
    )
    shake_y = (
        shake_intensity * np.cos(2 * np.pi * 4.2 * t)
        + (shake_intensity * 0.5) * np.sin(2 * np.pi * 8.1 * t)
        + np.random.normal(0, shake_intensity * 0.35, num_frames)
    )
    shake_theta = (
        rotation_shake_deg * np.sin(2 * np.pi * 2.7 * t)
        + np.random.normal(0, rotation_shake_deg * 0.3, num_frames)
    )

    cam_x = base_center_x + shake_x
    cam_y = base_center_y + shake_y
    cam_theta = base_angle + shake_theta

    writer = create_video_writer(output_path, fps, width, height)

    for i in range(num_frames):
        cx = cam_x[i]
        cy = cam_y[i]
        angle = cam_theta[i]

        rot_mat = cv2.getRotationMatrix2D((cx, cy), -angle, 1.0)
        rot_mat[0, 2] += (width / 2.0) - cx
        rot_mat[1, 2] += (height / 2.0) - cy

        frame = cv2.warpAffine(canvas, rot_mat, (width, height), borderMode=cv2.BORDER_REFLECT)

        if include_moving_object:
            obj_x = int(50 + (width - 100) * (i / num_frames))
            obj_y = int(height * 0.65)
            cv2.rectangle(frame, (obj_x - 30, obj_y - 25), (obj_x + 30, obj_y + 25), (30, 30, 240), -1)
            cv2.putText(frame, "CAR", (obj_x - 22, obj_y + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.putText(
            frame,
            f"T={i/fps:.2f}s (Frame {i+1})",
            (20, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

        write_video_frame(writer, frame)

    close_video_writer(writer)
    return os.path.abspath(output_path)
