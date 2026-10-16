-- Video Stabilization Database Schema
-- Manages video metadata, stabilization processing jobs, and benchmark experiments

CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    fps REAL NOT NULL,
    frame_count INTEGER NOT NULL,
    duration REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stabilization_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    window_size INTEGER NOT NULL,
    zoom_factor REAL NOT NULL,
    input_itf REAL NOT NULL,
    stabilized_itf REAL NOT NULL,
    itf_gain REAL NOT NULL,
    preserved_area_pct REAL NOT NULL,
    processing_time_sec REAL NOT NULL,
    processing_fps REAL NOT NULL,
    output_video_path TEXT,
    sbs_video_path TEXT,
    plot_image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiment_benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    video_label TEXT NOT NULL,
    window_size INTEGER NOT NULL,
    window_sec REAL NOT NULL,
    input_itf REAL NOT NULL,
    stabilized_itf REAL NOT NULL,
    itf_gain REAL NOT NULL,
    preserved_area_pct REAL NOT NULL,
    processing_fps REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES stabilization_jobs(id) ON DELETE SET NULL
);
