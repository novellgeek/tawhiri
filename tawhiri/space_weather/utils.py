"""
Utility Functions

Helper functions for space weather module.
"""

from datetime import datetime, timezone
from typing import Any


def clamp_float(x: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float, returning default if conversion fails.
    
    Handles numeric types, strings, and whitespace.
    
    Args:
        x: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(x)
    except (TypeError, ValueError):
        try:
            return float(str(x).strip())
        except (TypeError, ValueError, AttributeError):
            return default


def last_updated() -> str:
    """
    Get current UTC timestamp as formatted string.
    
    Returns:
        Timestamp string in format "YYYY-MM-DD HH:MM UTC"
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


# TODO: Add other utility functions from your monolithic file:
# - Any helper functions that don't fit in other modules
# - Date/time utilities
# - String formatting helpers
# etc.
