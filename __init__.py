"""Olympus SC30 camera package.

This package contains:
- `uEye`: low-level ctypes bindings and helper functions for the Olympus/IDS API
- `SC30Camera`: high-level camera wrapper
"""

from .Olympus_SC30 import SC30Camera
from . import uEye

__all__ = ["SC30Camera", "uEye"]
