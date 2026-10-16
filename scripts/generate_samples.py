#!/usr/bin/env python3
"""
Sample Generator Script
Produces synthetic shaky videos with ground truth tremors and moving objects.
Saves outputs to storage/samples/ and samples/.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.utils.synthetic_generator import generate_synthetic_shaky_video


def main():
    os.makedirs("storage/samples", exist_ok=True)
    os.makedirs("samples", exist_ok=True)
    print("[*] Generating synthetic sample videos in storage tier...")

    pan_path = generate_synthetic_shaky_video(
        output_path="storage/samples/shaky_sample_pan.mp4",
        num_frames=120,
        fps=30,
        width=640,
        height=360,
        shake_intensity=14.0,
        rotation_shake_deg=3.0,
        include_moving_object=False,
    )
    # Also save to legacy samples/ for convenience
    os.system("cp storage/samples/shaky_sample_pan.mp4 samples/shaky_sample_pan.mp4")
    print(f"[+] Created: {pan_path}")

    obj_path = generate_synthetic_shaky_video(
        output_path="storage/samples/shaky_sample_moving_obj.mp4",
        num_frames=120,
        fps=30,
        width=640,
        height=360,
        shake_intensity=12.0,
        rotation_shake_deg=2.5,
        include_moving_object=True,
    )
    os.system("cp storage/samples/shaky_sample_moving_obj.mp4 samples/shaky_sample_moving_obj.mp4")
    print(f"[+] Created: {obj_path}")


if __name__ == "__main__":
    main()
