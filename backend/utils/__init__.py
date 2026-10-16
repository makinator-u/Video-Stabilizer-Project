"""Backend utilities."""

from .video_io import (
    get_video_info,
    create_video_writer,
    write_video_frame,
    close_video_writer,
)
from .synthetic_generator import generate_synthetic_shaky_video

__all__ = [
    "get_video_info",
    "create_video_writer",
    "write_video_frame",
    "close_video_writer",
    "generate_synthetic_shaky_video",
]
