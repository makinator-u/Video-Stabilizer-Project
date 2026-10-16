#!/usr/bin/env python3
"""
Root Entry Point for Video Stabilization CLI
Delegates to scripts/run_cli.py
"""

import os
import sys
import runpy

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

cli_script = os.path.join(project_root, "scripts", "run_cli.py")
runpy.run_path(cli_script, run_name="__main__")
