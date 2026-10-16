# Video Stabilization: Full-Stack Architecture
**Image and Video Processing (IVP) Project**

> A production-grade, three-tier software architecture for 2D digital video stabilization:
> - **Frontend:** Interactive Streamlit Studio with modular KPI components and glassmorphic styling.
> - **Backend:** Computer vision algorithms (Shi-Tomasi, Pyramidal LK Optical Flow, RANSAC 2D Partial Affine, Trajectory Smoothing, and Center-Scaling Border Fix).
> - **Database:** Persistent SQLite data store tracking video metadata, stabilization execution logs, and benchmark metrics.

---

## 🌟 Architectural Highlights
- **Layered Separation of Concerns:** Clean division across `frontend/`, `backend/`, `database/`, and `storage/`.
- **Shi-Tomasi Feature Detection:** High-contrast corner tracking (`cv2.goodFeaturesToTrack`).
- **Lucas-Kanade Pyramidal Optical Flow:** Multi-scale motion correspondence (`cv2.calcOpticalFlowPyrLK`).
- **RANSAC 2D Partial Affine Estimation:** Outlier-resilient 4-DOF motion estimation ($dx, dy, d\theta$) isolating camera motion from moving foreground objects.
- **Cumulative Trajectory Smoothing:** Moving-average box filter with edge-replication padding.
- **Center-Scale Border Removal:** Composes a 1.04x center-zoom homothety with the stabilization matrix to remove black borders in a single resampling pass (`cv2.BORDER_REFLECT`).
- **SQLite Job Persistence:** Every execution automatically registers video dimensions, runtime throughput, parameter configurations, and ITF metrics in `database/stabilization.db`.
- **Interactive Web Studio:** Dark-mode dashboard featuring KPI cards, side-by-side synchronized video player, trajectory analysis charts, multi-window benchmark comparisons, and historical run inspection.

---

## 📁 System Architecture & Directory Layout

```
IVP Mini Project/
├── frontend/                             # Presentation Tier (UI, Views & Components)
│   ├── app.py                            # Streamlit Unified Multi-Window Dashboard
│   ├── views/                            # Dedicated functional workspace windows
│   │   ├── __init__.py
│   │   ├── flow_view.py                  # Window 2: Optical Flow & Corner Vector Inspector
│   │   ├── trajectory_view.py            # Window 3: Trajectory & Jitter Decomposition Lab
│   │   ├── benchmark_view.py             # Window 4: Multi-Window Tradeoff Benchmark Suite
│   │   ├── generator_view.py             # Window 5: Custom Synthetic Video Laboratory
│   │   ├── database_view.py              # Window 6: SQLite Execution Audit Vault & CSV Exporter
│   │   └── specs_view.py                 # Window 7: Mathematical Formulations & Specifications
│   ├── components/                       # Modular UI widgets
│   │   ├── __init__.py
│   │   ├── metrics_display.py            # KPI stat cards (ITF, Gain, Preserved Area)
│   │   └── video_viewer.py               # Side-by-side player & download buttons
│   └── styles/
│       └── custom.css                    # Minimalist Swiss dark-mode CSS
│
├── backend/                              # Application & Compute Tier
│   ├── __init__.py                       # Package exports
│   ├── core/                             # Algorithmic engine
│   │   ├── __init__.py
│   │   ├── motion_estimator.py           # Shi-Tomasi corners, LK optical flow, RANSAC affine
│   │   ├── trajectory.py                 # Cumulative trajectory integration & smoothing
│   │   ├── warper.py                     # Center-zoom matrix composition & frame warping
│   │   └── metrics.py                    # Inter-frame Transformation Fidelity (ITF / PSNR)
│   ├── pipeline/                         # Workflow orchestration services
│   │   ├── __init__.py
│   │   └── stabilizer_service.py         # VideoStabilizerService API
│   ├── visualization/                    # Visualization services
│   │   ├── __init__.py
│   │   └── trajectory_plotter.py         # 3-panel Matplotlib trajectory figures
│   └── utils/                            # Video I/O & synthetic data generator
│       ├── __init__.py
│       ├── video_io.py                   # Metadata extraction & H.264 video writer
│       └── synthetic_generator.py        # Handheld tremor & moving-object simulator
│
├── database/                             # Persistence Tier
│   ├── __init__.py
│   ├── db_manager.py                     # SQLite DatabaseManager (queries, insertions, stats)
│   ├── schema.sql                        # Schema for videos, jobs, and experiment benchmarks
│   └── stabilization.db                  # SQLite database file storing historical runs
│
├── storage/                              # Asset & Data Tier
│   ├── samples/                          # Raw input test videos
│   ├── outputs/                          # Stabilized and side-by-side video files
│   └── plots/                            # Trajectory plot images (PNG)
│
├── scripts/                              # Standalone CLI tools & experiment runners
│   ├── run_cli.py                        # Terminal CLI stabilizer with DB logging
│   ├── generate_samples.py               # Synthetic video generator
│   └── run_experiments.py                # Multi-window benchmark experiment runner
│
├── docs/                                 # Technical documentation
│   └── REPORT.md                         # 7-Section Technical Project Report
│
├── results/                              # Benchmark data exports
│   └── experiment_tradeoffs.csv          # Window size tradeoff CSV
│
├── .streamlit/                           # Streamlit server configuration
│   ├── config.toml
│   └── credentials.toml
│
├── app.py                                # Root entry point -> frontend/app.py
├── stabilize.py                          # Root entry point -> scripts/run_cli.py
├── generate_test_video.py                # Root entry point -> scripts/generate_samples.py
├── run_experiments.py                    # Root entry point -> scripts/run_experiments.py
├── video_stabilizer.py                   # Root compatibility wrapper -> backend
├── requirements.txt                      # Project dependencies
└── README.md                             # Architecture documentation & manual
```

---

## 🗄️ Database Schema (`database/schema.sql`)

The persistence tier stores all operational data in SQLite across three relational tables:
1. **`videos`**: Tracks uploaded/processed source video files, dimensions, frame rates, and durations.
2. **`stabilization_jobs`**: Stores every stabilization run with hyperparameters ($W$, zoom), input ITF, stabilized ITF, net gain in dB, preserved area percentage, execution time, and output paths.
3. **`experiment_benchmarks`**: Logs multi-window tradeoff metrics ($W \in \{10, 30, 60\}$ frames) for automated charting.

---

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Clone or navigate to the repository directory
cd "IVP Mini Project"

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Streamlit Web Application (Frontend)
```bash
HOME="/Users/urvadesai/IVP Mini Project" streamlit run frontend/app.py
# (or from root: streamlit run app.py)
```
Open your browser at `http://localhost:8501`:
- Select preloaded sample videos from the **Storage Tier** or upload your own.
- Adjust the temporal smoothing window (5–120 frames) and border zoom sliders.
- View real-time KPI metrics, synchronized side-by-side video playback, and trajectory plots.
- Switch to the **🗄️ Database Run History** tab to view your past jobs stored in SQLite.

---

### 3. Run the CLI Stabilizer (Backend + Database)
```bash
python scripts/run_cli.py --input storage/samples/shaky_sample_pan.mp4
# (or from root: python stabilize.py --input storage/samples/shaky_sample_pan.mp4)
```

**CLI Output Preview:**
```
========================================================================
           BACKEND VIDEO STABILIZATION ENGINE (FULL-STACK)
   Lucas-Kanade Optical Flow | RANSAC Affine | SQLite Persistent Logs
========================================================================
[*] Input video:       storage/samples/shaky_sample_pan.mp4
[*] Output video:      storage/outputs/stabilized_output.mp4
[*] Side-by-side:      storage/outputs/comparison_sbs.mp4
[*] Trajectory plot:   storage/plots/trajectory_plot.png
[*] Window size:       30 frames
[*] Zoom factor:       1.04x
------------------------------------------------------------------------
[==============================] 100.0% | Stabilization Complete!
========================================================================
                      STABILIZATION SUMMARY
========================================================================
  Processed Frames:        120 frames
  Video Dimensions:        640 x 368
  Source Frame Rate:       30.00 FPS
  Processing Time:         1.42 seconds (84.2 FPS)
------------------------------------------------------------------------
  Inter-frame PSNR (Input):       17.41 dB
  Inter-frame PSNR (Stabilized):  21.04 dB
  Stability Gain (ITF Delta):     +3.63 dB
  Cropping Ratio Preserved:       92.46% (Lost: 7.54%)
  Database Status:                Logged as Job #1 in SQLite Database
========================================================================
[+] Stabilized video saved to:       storage/outputs/stabilized_output.mp4
[+] Comparison video saved to:       storage/outputs/comparison_sbs.mp4
[+] Trajectory plot saved to:        storage/plots/trajectory_plot.png
========================================================================
```

---

### 4. Run Benchmark Tradeoff Experiments
```bash
python scripts/run_experiments.py
# (or from root: python run_experiments.py)
```
Evaluates window sizes $W \in \{10, 30, 60\}$ frames, logs results to SQLite, and exports [results/experiment_tradeoffs.csv](file:///Users/urvadesai/IVP%20Mini%20Project/results/experiment_tradeoffs.csv).

| Video | Window $W$ | Window (s) | Input ITF | Stabilized ITF | Gain (dB) | Preserved Area | Speed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Camera Pan** | 10 frames | 0.33s | 17.41 dB | 20.77 dB | +3.35 dB | 92.46% | 130.0 FPS |
| **Camera Pan** | 30 frames | 1.00s | 17.41 dB | 21.04 dB | +3.63 dB | 92.46% | 134.0 FPS |
| **Camera Pan** | 60 frames | 2.00s | 17.41 dB | 21.55 dB | +4.14 dB | 92.46% | 133.5 FPS |
| **Moving Object** | 10 frames | 0.33s | 17.74 dB | 20.81 dB | +3.07 dB | 92.46% | 132.4 FPS |
| **Moving Object** | 30 frames | 1.00s | 17.74 dB | 20.99 dB | +3.26 dB | 92.46% | 135.6 FPS |
| **Moving Object** | 60 frames | 2.00s | 17.74 dB | 21.48 dB | +3.74 dB | 92.46% | 132.6 FPS |

---

## 📖 Technical Documentation & Report
- Technical Project Report & Mathematical Formulation: [docs/REPORT.md](file:///Users/urvadesai/IVP%20Mini%20Project/docs/REPORT.md)
