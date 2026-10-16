#!/usr/bin/env python3
"""
Benchmark & Window Size Tradeoff Experiments
Evaluates stabilization performance across window sizes W in [10, 30, 60].
Logs results to SQLite database and exports CSV.
"""

import os
import sys
import time
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.pipeline.stabilizer_service import VideoStabilizerService
from database.db_manager import DatabaseManager


def run_experiment(video_path: str, video_label: str) -> pd.DataFrame:
    print("=" * 80)
    print(f"RUNNING EXPERIMENT FOR: {video_label} ({video_path})")
    print("=" * 80)

    window_sizes = [10, 30, 60]
    results_list = []
    os.makedirs("results", exist_ok=True)
    os.makedirs("storage/outputs", exist_ok=True)

    for w in window_sizes:
        print(f"\n[+] Testing Window Size W = {w} frames...")
        out_vid = f"storage/outputs/{video_label}_w{w}_stab.mp4"
        plot_path = f"storage/plots/{video_label}_w{w}_trajectory.png"

        stabilizer = VideoStabilizerService(
            max_corners=200,
            quality_level=0.01,
            min_distance=30,
            window_size=w,
            zoom_factor=1.04,
        )

        t0 = time.time()
        res = stabilizer.process(
            input_path=video_path,
            output_path=out_vid,
            plot_path=plot_path,
        )
        elapsed = time.time() - t0
        fps_proc = res["frame_count"] / elapsed if elapsed > 0 else 0

        row = {
            "Video": video_label,
            "Window (Frames)": w,
            "Window (Seconds)": round(w / res["fps"], 2),
            "Input ITF (dB)": res["itf_original"],
            "Stabilized ITF (dB)": res["itf_stabilized"],
            "Gain (dB)": res["itf_improvement"],
            "Preserved Area (%)": round(res["cropping_ratio"] * 100, 2),
            "Processing Speed (FPS)": round(fps_proc, 1),
        }
        results_list.append(row)
        print(
            f"    Input ITF: {res['itf_original']:.2f} dB | "
            f"Stabilized ITF: {res['itf_stabilized']:.2f} dB | "
            f"Gain: +{res['itf_improvement']:.2f} dB"
        )

    return pd.DataFrame(results_list)


def main():
    pan_video = "storage/samples/shaky_sample_pan.mp4"
    if not os.path.exists(pan_video):
        pan_video = "samples/shaky_sample_pan.mp4"

    obj_video = "storage/samples/shaky_sample_moving_obj.mp4"
    if not os.path.exists(obj_video):
        obj_video = "samples/shaky_sample_moving_obj.mp4"

    dfs = []
    if os.path.exists(pan_video):
        df_pan = run_experiment(pan_video, "camera_pan")
        dfs.append(df_pan)

    if os.path.exists(obj_video):
        df_obj = run_experiment(obj_video, "moving_object")
        dfs.append(df_obj)

    if dfs:
        full_df = pd.concat(dfs, ignore_index=True)
        csv_path = "results/experiment_tradeoffs.csv"
        full_df.to_csv(csv_path, index=False)

        # Log benchmarks to database
        db = DatabaseManager()
        db.record_experiment_benchmarks(full_df.to_dict(orient="records"))

        print("\n" + "=" * 80)
        print("                   FINAL EXPERIMENT TRADEOFF TABLE")
        print("=" * 80)
        print(full_df.to_string(index=False))
        print("=" * 80)
        print(f"[+] Saved experiment results to: {csv_path}")
        print("[+] Logged experiment records to database: database/stabilization.db")


if __name__ == "__main__":
    main()
