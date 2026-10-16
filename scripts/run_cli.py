#!/usr/bin/env python3
"""
CLI Video Stabilization Tool
Connects directly to backend stabilization services and logs results to the database.
"""

import argparse
import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.pipeline.stabilizer_service import VideoStabilizerService
from database.db_manager import DatabaseManager


def parse_args():
    parser = argparse.ArgumentParser(
        description="Video Stabilization CLI (Backend Engine)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Path to the shaky input video (e.g. storage/samples/shaky_sample_pan.mp4)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="storage/outputs/stabilized_output.mp4",
        help="Path to save the stabilized video",
    )
    parser.add_argument(
        "-s", "--side-by-side",
        type=str,
        default="storage/outputs/comparison_sbs.mp4",
        help="Path to save the side-by-side comparison video",
    )
    parser.add_argument(
        "-p", "--plot",
        type=str,
        default="storage/plots/trajectory_plot.png",
        help="Path to save the trajectory plot image (PNG)",
    )
    parser.add_argument(
        "-w", "--window",
        type=int,
        default=30,
        help="Smoothing window size in frames (default 30 ≈ 1 sec at 30 fps)",
    )
    parser.add_argument(
        "-z", "--zoom",
        type=float,
        default=1.04,
        help="Zoom scale factor to eliminate black border artifacts (default 1.04 = 4% zoom)",
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Skip logging run to SQLite database",
    )
    return parser.parse_args()


def print_banner():
    banner = r"""
========================================================================
           BACKEND VIDEO STABILIZATION ENGINE (FULL-STACK)
   Lucas-Kanade Optical Flow | RANSAC Affine | SQLite Persistent Logs
========================================================================
"""
    print(banner)


def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input video '{args.input}' not found.")
        sys.exit(1)

    print_banner()
    print(f"[*] Input video:       {args.input}")
    print(f"[*] Output video:      {args.output}")
    print(f"[*] Side-by-side:      {args.side_by_side}")
    print(f"[*] Trajectory plot:   {args.plot}")
    print(f"[*] Window size:       {args.window} frames")
    print(f"[*] Zoom factor:       {args.zoom}x")
    print("-" * 72)

    stabilizer = VideoStabilizerService(
        window_size=args.window,
        zoom_factor=args.zoom,
    )

    start_time = time.time()

    def console_progress(progress: float, message: str):
        bar_len = 30
        filled = int(round(bar_len * progress))
        bar = "=" * filled + "-" * (bar_len - filled)
        percent = progress * 100.0
        sys.stdout.write(f"\r[{bar}] {percent:5.1f}% | {message[:42]:<42}")
        sys.stdout.flush()

    try:
        results = stabilizer.process(
            input_path=args.input,
            output_path=args.output,
            side_by_side_path=args.side_by_side,
            plot_path=args.plot,
            progress_callback=console_progress,
        )
    except Exception as e:
        print(f"\n[!] Error during stabilization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    elapsed = time.time() - start_time
    fps_processing = results["frame_count"] / elapsed if elapsed > 0 else 0

    # Log to SQLite Database
    if not args.no_db:
        db = DatabaseManager()
        vid_id = db.register_video(args.input, results)
        job_id = db.record_job(
            video_id=vid_id,
            window_size=args.window,
            zoom_factor=args.zoom,
            results=results,
            processing_time=elapsed,
            output_path=args.output,
            sbs_path=args.side_by_side,
            plot_path=args.plot,
        )
        db_log_msg = f"Logged as Job #{job_id} in SQLite Database"
    else:
        db_log_msg = "Database logging skipped (--no-db)"

    print("\n" + "=" * 72)
    print("                      STABILIZATION SUMMARY")
    print("=" * 72)
    print(f"  Processed Frames:        {results['frame_count']} frames")
    print(f"  Video Dimensions:        {results['width']} x {results['height']}")
    print(f"  Source Frame Rate:       {results['fps']:.2f} FPS")
    print(f"  Processing Time:         {elapsed:.2f} seconds ({fps_processing:.1f} FPS)")
    print("-" * 72)
    print(f"  Inter-frame PSNR (Input):       {results['itf_original']:.2f} dB")
    print(f"  Inter-frame PSNR (Stabilized):  {results['itf_stabilized']:.2f} dB")
    delta = results['itf_improvement']
    sign = "+" if delta >= 0 else ""
    print(f"  Stability Gain (ITF Delta):     {sign}{delta:.2f} dB")
    print(f"  Cropping Ratio Preserved:       {results['cropping_ratio'] * 100:.2f}% (Lost: {results['crop_loss_pct']:.2f}%)")
    print(f"  Database Status:                {db_log_msg}")
    print("=" * 72)
    print(f"[+] Stabilized video saved to:       {os.path.abspath(args.output)}")
    print(f"[+] Comparison video saved to:       {os.path.abspath(args.side_by_side)}")
    print(f"[+] Trajectory plot saved to:        {os.path.abspath(args.plot)}")
    print("=" * 72)


if __name__ == "__main__":
    main()
