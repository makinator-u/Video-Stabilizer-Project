#!/usr/bin/env python3
"""
Root Entry Point for Synthetic Sample Generator
Delegates to scripts/generate_samples.py
"""

import os
import sys
import runpy

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

script_path = os.path.join(project_root, "scripts", "generate_samples.py")
runpy.run_path(script_path, run_name="__main__")
