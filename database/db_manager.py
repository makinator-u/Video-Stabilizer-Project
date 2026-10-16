"""
Database Manager Module
Provides persistent SQLite storage for videos, stabilization execution jobs,
performance metrics (ITF, FPS, cropping ratio), and benchmark experiments.
"""

import os
import sqlite3
from typing import Dict, Any, List, Optional
import pandas as pd

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(DB_DIR, "stabilization.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")


class DatabaseManager:
    """Manages SQLite storage operations for video stabilization runs."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes tables using schema.sql if not present."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self._get_connection() as conn:
                conn.executescript(schema_sql)

    def register_video(self, file_path: str, info: Dict[str, Any]) -> int:
        """
        Inserts or retrieves a video record by absolute file path.
        Returns:
            video_id (int)
        """
        abs_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM videos WHERE file_path = ?", (abs_path,))
            row = cursor.fetchone()
            if row:
                return row["id"]

            cursor.execute(
                """
                INSERT INTO videos (filename, file_path, width, height, fps, frame_count, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename,
                    abs_path,
                    info.get("width", 0),
                    info.get("height", 0),
                    info.get("fps", 0.0),
                    info.get("frame_count", 0),
                    info.get("duration", 0.0),
                ),
            )
            return cursor.lastrowid

    def record_job(
        self,
        video_id: int,
        window_size: int,
        zoom_factor: float,
        results: Dict[str, Any],
        processing_time: float,
        output_path: Optional[str] = None,
        sbs_path: Optional[str] = None,
        plot_path: Optional[str] = None,
    ) -> int:
        """
        Logs a completed video stabilization run and its metrics.
        Returns:
            job_id (int)
        """
        frame_count = results.get("frame_count", 1)
        proc_fps = frame_count / processing_time if processing_time > 0 else 0.0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO stabilization_jobs (
                    video_id, window_size, zoom_factor, input_itf, stabilized_itf,
                    itf_gain, preserved_area_pct, processing_time_sec, processing_fps,
                    output_video_path, sbs_video_path, plot_image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video_id,
                    window_size,
                    zoom_factor,
                    results.get("itf_original", 0.0),
                    results.get("itf_stabilized", 0.0),
                    results.get("itf_improvement", 0.0),
                    results.get("cropping_ratio", 1.0) * 100.0,
                    round(processing_time, 2),
                    round(proc_fps, 1),
                    output_path,
                    sbs_path,
                    plot_path,
                ),
            )
            return cursor.lastrowid

    def record_experiment_benchmarks(self, records: List[Dict[str, Any]]) -> None:
        """Logs multi-window tradeoff benchmark results."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for r in records:
                cursor.execute(
                    """
                    INSERT INTO experiment_benchmarks (
                        video_label, window_size, window_sec, input_itf,
                        stabilized_itf, itf_gain, preserved_area_pct, processing_fps
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        r.get("Video", ""),
                        r.get("Window (Frames)", 0),
                        r.get("Window (Seconds)", 0.0),
                        r.get("Input ITF (dB)", 0.0),
                        r.get("Stabilized ITF (dB)", 0.0),
                        r.get("Gain (dB)", 0.0),
                        r.get("Preserved Area (%)", 0.0),
                        r.get("Processing Speed (FPS)", 0.0),
                    ),
                )

    def get_recent_jobs(self, limit: int = 15) -> pd.DataFrame:
        """Retrieves recent stabilization jobs joined with video metadata."""
        query = """
        SELECT 
            j.id AS job_id,
            v.filename AS video_name,
            v.width || 'x' || v.height AS resolution,
            j.window_size AS window_frames,
            j.zoom_factor,
            j.input_itf || ' dB' AS input_itf,
            j.stabilized_itf || ' dB' AS stab_itf,
            CASE WHEN j.itf_gain >= 0 THEN '+' || j.itf_gain || ' dB' ELSE j.itf_gain || ' dB' END AS stability_gain,
            j.preserved_area_pct || '%' AS preserved_area,
            j.processing_time_sec || ' s' AS duration,
            j.processing_fps || ' FPS' AS speed,
            j.created_at
        FROM stabilization_jobs j
        JOIN videos v ON j.video_id = v.id
        ORDER BY j.id DESC
        LIMIT ?
        """
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit,))

    def get_summary_stats(self) -> Dict[str, Any]:
        """Calculates aggregate metrics across all runs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stabilization_jobs")
            total_jobs = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(itf_gain), AVG(processing_fps), AVG(preserved_area_pct) FROM stabilization_jobs")
            row = cursor.fetchone()
            avg_gain = row[0] if row and row[0] is not None else 0.0
            avg_fps = row[1] if row and row[1] is not None else 0.0
            avg_area = row[2] if row and row[2] is not None else 0.0

            cursor.execute("SELECT COUNT(*) FROM videos")
            total_videos = cursor.fetchone()[0]

        return {
            "total_jobs": total_jobs,
            "total_videos": total_videos,
            "avg_gain_db": round(avg_gain, 2),
            "avg_fps": round(avg_fps, 1),
            "avg_preserved_area": round(avg_area, 2),
        }
