"""
Space Weather Module

Real-time space weather monitoring using NOAA and BOM data sources.
Provides NZ-specific interpretations and operational impacts.

Main Functions:
    run() - Launch the Streamlit UI for space weather monitoring
    
Example:
    >>> from tawhiri.space_weather import run
    >>> run()
"""

from .app import run

__all__ = ["run"]
