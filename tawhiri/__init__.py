"""
TAWHIRI Space Domain Awareness Platform

A modular platform for space weather monitoring and orbital visualization
designed for NZDF operational use.

Modules:
    - space_weather: Real-time space weather monitoring and alerting
    - orbit_viz: 3D and 2D satellite orbit visualization
    - common: Shared utilities and configuration
"""

__version__ = "1.0.0"
__author__ = "NZDF Space Domain Awareness Team"

# Make key functions easily accessible
from tawhiri.config import load_config

__all__ = ["load_config", "__version__"]
