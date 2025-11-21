"""
Space Weather Module
====================

Real-time space weather monitoring and forecasting system.

Main components:
    - constants: Scale thresholds and configuration
    - scales: NOAA scale calculation functions (R, S, G)
    - data_fetchers: API interaction with NOAA and BOM
    - utils: Helper functions
    - plotting: Chart generation
    - pdf_export: PDF report generation
    - app: Streamlit UI application

Usage:
    from tawhiri.space_weather import run
    run()
"""

from tawhiri.space_weather.constants import (
    R_SCALE_THRESHOLDS,
    S_SCALE_THRESHOLDS,
    G_SCALE_THRESHOLDS,
    SEVERITY_COLORS,
)

__all__ = [
    'R_SCALE_THRESHOLDS',
    'S_SCALE_THRESHOLDS',
    'G_SCALE_THRESHOLDS',
    'SEVERITY_COLORS',
]