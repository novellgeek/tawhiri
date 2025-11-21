"""
Space Weather Utilities Module
===============================

Helper functions for data processing, validation, and formatting.
"""

from datetime import datetime
from typing import Any, Optional


def clamp_float(x: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float, with fallback to default.
    
    This is useful when processing API data that might have unexpected
    formats, null values, or non-numeric strings.
    
    Args:
        x: Value to convert (can be int, float, string, or None)
        default: Value to return if conversion fails
        
    Returns:
        Float value or default if conversion fails
        
    Examples:
        >>> clamp_float("3.14")
        3.14
        >>> clamp_float(None, 0.0)
        0.0
        >>> clamp_float("invalid", 5.0)
        5.0
    """
    try:
        return float(x)
    except (ValueError, TypeError):
        try:
            # Try stripping whitespace if it's a string
            return float(str(x).strip())
        except (ValueError, TypeError, AttributeError):
            return default


def last_updated() -> str:
    """
    Get current UTC timestamp formatted for display.
    
    Returns:
        Formatted timestamp string in "YYYY-MM-DD HH:MM UTC" format
        
    Example:
        >>> last_updated()
        '2025-11-21 14:30 UTC'
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


def safe_dict_get(data: Optional[dict], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary that might be None.
    
    Args:
        data: Dictionary to get value from (can be None)
        key: Key to retrieve
        default: Default value if key not found or data is None
        
    Returns:
        Value from dict or default
        
    Examples:
        >>> safe_dict_get({'a': 1}, 'a')
        1
        >>> safe_dict_get(None, 'a', 0)
        0
    """
    if data is None:
        return default
    return data.get(key, default)


def safe_list_get(data: Optional[list], index: int, default: Any = None) -> Any:
    """
    Safely get an item from a list that might be None or too short.
    
    Args:
        data: List to get item from (can be None)
        index: Index to retrieve (can be negative for reverse indexing)
        default: Default value if index out of range or data is None
        
    Returns:
        Item from list or default
        
    Examples:
        >>> safe_list_get([1, 2, 3], -1)
        3
        >>> safe_list_get(None, 0, 'default')
        'default'
        >>> safe_list_get([1], 5, 0)
        0
    """
    if data is None or len(data) == 0:
        return default
    try:
        return data[index]
    except IndexError:
        return default


def format_percentage(value: Optional[float], precision: int = 0) -> str:
    """
    Format a value as a percentage string.
    
    Args:
        value: Numeric value (e.g., 0.75 for 75%)
        precision: Number of decimal places
        
    Returns:
        Formatted percentage string
        
    Examples:
        >>> format_percentage(0.75)
        '75%'
        >>> format_percentage(0.333, 1)
        '33.3%'
    """
    if value is None:
        return "~"
    try:
        return f"{float(value):.{precision}f}%"
    except (ValueError, TypeError):
        return "~"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append if truncated
        
    Returns:
        Truncated text
        
    Examples:
        >>> truncate_text("This is a very long string", 10)
        'This is...'
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def any_phrase_in_text(text: str, *phrases: str) -> bool:
    """
    Check if any of the given phrases appear in text (case-insensitive).
    
    Args:
        text: Text to search in
        *phrases: Variable number of phrases to search for
        
    Returns:
        True if any phrase is found, False otherwise
        
    Examples:
        >>> any_phrase_in_text("The quick brown fox", "quick", "slow")
        True
        >>> any_phrase_in_text("hello world", "goodbye")
        False
    """
    if not text:
        return False
    text_lower = text.lower()
    return any(phrase.lower() in text_lower for phrase in phrases)


def class_to_level(class_key: str) -> str:
    """
    Map internal severity class to human-readable level name.
    
    This is used for UI display and report generation.
    
    Args:
        class_key: Internal class key ('ok', 'caution', 'watch', 'severe')
        
    Returns:
        Same key, validated to be one of the known levels
        
    Examples:
        >>> class_to_level("caution")
        'caution'
        >>> class_to_level("unknown")
        'ok'
    """
    level_map = {
        "ok": "ok",
        "caution": "caution",
        "watch": "watch",
        "severe": "severe"
    }
    return level_map.get((class_key or "").lower(), "ok")


def validate_scale_level(scale_level: str, scale_type: str) -> str:
    """
    Validate and normalize a scale level string.
    
    Args:
        scale_level: Scale level (e.g., "R3", "g2", "S5")
        scale_type: Expected scale type ('R', 'S', or 'G')
        
    Returns:
        Normalized scale level (e.g., "R3") or default for that scale
        
    Examples:
        >>> validate_scale_level("r3", "R")
        'R3'
        >>> validate_scale_level("invalid", "G")
        'G0'
    """
    if not scale_level:
        return f"{scale_type}0"
    
    scale_level = scale_level.upper()
    scale_type = scale_type.upper()
    
    # Check if it starts with the expected type
    if not scale_level.startswith(scale_type):
        return f"{scale_type}0"
    
    # Validate the number part
    try:
        num = int(scale_level[1:])
        if 0 <= num <= 5:
            return f"{scale_type}{num}"
    except (ValueError, IndexError):
        pass
    
    return f"{scale_type}0"


# Export all public functions
__all__ = [
    'clamp_float',
    'last_updated',
    'safe_dict_get',
    'safe_list_get',
    'format_percentage',
    'truncate_text',
    'any_phrase_in_text',
    'class_to_level',
    'validate_scale_level',
]
