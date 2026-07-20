#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

root_scripts = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(root_scripts))
runpy.run_path(str(root_scripts / "prepare_inputs.py"), run_name="__main__")
