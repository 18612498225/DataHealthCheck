"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

# Ensure project root is in path for data_quality_tool imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
