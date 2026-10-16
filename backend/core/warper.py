"""
Backend Core: Warper
1.04x center zoom homothety, combined matrix composition, and side-by-side rendering.
"""

import cv2
import numpy as np


class FrameWarper:
    """Handles warp transformations, border fix zoom, and composite frames."""

    def __init__(self, zoom_factor: float = 1.04):
        self.zoom_factor = zoom_factor

    def get_center_zoom_matrix(self, width: int, height: int) -> np.ndarray:
        """2x3 center-scaling homothety."""
        center_x, center_y = width / 2.0, height / 2.0
        return cv2.getRotationMatrix2D((center_x, center_y), 0, self.zoom_factor)

    def compose_transform(
        self,
        scale_mat: np.ndarray,
        dx: float,
        dy: float,
        da: float,
    ) -> np.ndarray:
        """T_composite = T_zoom * T_stabilize"""
        cos_a = np.cos(da)
        sin_a = np.sin(da)
        m_stab = np.array(
            [
                [cos_a, -sin_a, dx],
                [sin_a, cos_a, dy],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

        m_scale_3x3 = np.vstack([scale_mat, [0.0, 0.0, 1.0]])
        m_combined_3x3 = np.dot(m_scale_3x3, m_stab)
        return m_combined_3x3[:2, :]

    def warp(
        self,
        frame: np.ndarray,
        transform_mat: np.ndarray,
        width: int,
        height: int,
        border_mode: int = cv2.BORDER_REFLECT,
    ) -> np.ndarray:
        """Warps frame using affine transformation with reflection border."""
        return cv2.warpAffine(
            frame,
            transform_mat,
            (width, height),
            borderMode=border_mode,
            flags=cv2.INTER_LINEAR,
        )

    @staticmethod
    def render_side_by_side(
        original: np.ndarray,
        stabilized: np.ndarray,
        frame_idx: int,
        total_frames: int,
        fps: float,
    ) -> np.ndarray:
        """Generates labeled comparison frame."""
        h, w = original.shape[:2]
        sbs = np.hstack([original, stabilized])

        banner_h = max(42, int(h * 0.07))
        banner = sbs[:banner_h, :].copy()
        cv2.rectangle(sbs, (0, 0), (w * 2, banner_h), (15, 15, 20), -1)
        cv2.addWeighted(sbs[:banner_h, :], 0.85, banner, 0.15, 0, sbs[:banner_h, :])

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.55, h / 1100.0)
        thickness = max(1, int(round(font_scale * 2)))

        # Badges
        cv2.rectangle(sbs, (12, int(banner_h * 0.2)), (20, int(banner_h * 0.8)), (50, 50, 230), -1)
        cv2.putText(sbs, "ORIGINAL (SHAKY)", (28, int(banner_h * 0.68)), font, font_scale, (240, 240, 240), thickness, cv2.LINE_AA)

        cv2.rectangle(sbs, (w + 12, int(banner_h * 0.2)), (w + 20, int(banner_h * 0.8)), (80, 220, 100), -1)
        cv2.putText(sbs, "STABILIZED (SMOOTHED)", (w + 28, int(banner_h * 0.68)), font, font_scale, (240, 240, 240), thickness, cv2.LINE_AA)

        cv2.line(sbs, (w, 0), (w, h), (60, 60, 70), 2)

        time_sec = frame_idx / fps if fps > 0 else 0.0
        status_text = f"Frame: {frame_idx + 1}/{total_frames}  |  {time_sec:.1f}s"
        text_size, _ = cv2.getTextSize(status_text, font, font_scale * 0.8, 1)
        bx, by = w * 2 - text_size[0] - 20, h - 15
        cv2.rectangle(sbs, (bx - 8, by - text_size[1] - 6), (bx + text_size[0] + 8, by + 6), (20, 20, 25), -1)
        cv2.putText(sbs, status_text, (bx, by), font, font_scale * 0.8, (200, 200, 200), 1, cv2.LINE_AA)

        return sbs
