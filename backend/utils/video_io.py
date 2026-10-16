"""
Backend Utility: Video I/O
Provides video metadata reading and web-compatible video encoding services.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, Tuple

try:
    import imageio
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Inspects video metadata."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0 or np.isnan(fps):
        fps = 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0.0
    cap.release()

    return {
        "frame_count": frame_count,
        "fps": fps,
        "width": width,
        "height": height,
        "duration": duration,
    }


def create_video_writer(
    output_path: str,
    fps: float,
    width: int,
    height: int,
) -> Tuple[str, Any]:
    """Creates an H.264 web-compatible writer or cv2.VideoWriter."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if HAS_IMAGEIO and output_path.lower().endswith(".mp4"):
        try:
            writer = imageio.get_writer(
                output_path,
                fps=fps,
                codec="libx264",
                quality=8,
                pixelformat="yuv420p",
                ffmpeg_log_level="quiet",
                macro_block_size=None,
            )
            return ("imageio", writer)
        except Exception:
            pass

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    return ("cv2", writer)


def write_video_frame(writer_tuple: Tuple[str, Any], frame_bgr: np.ndarray) -> None:
    """Writes a single BGR frame."""
    mode, writer = writer_tuple
    if mode == "imageio":
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        writer.append_data(frame_rgb)
    else:
        writer.write(frame_bgr)


def close_video_writer(writer_tuple: Tuple[str, Any]) -> None:
    """Closes the video writer."""
    mode, writer = writer_tuple
    if mode == "imageio":
        writer.close()
    else:
        writer.release()
