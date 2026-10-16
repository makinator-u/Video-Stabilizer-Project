"""
Streamlit Community Cloud Default Entry Point
"""

import os
import sys
import runpy

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

frontend_app = os.path.join(project_root, "frontend", "app.py")
runpy.run_path(frontend_app, run_name="__main__")
