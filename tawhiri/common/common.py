"""
Tawhiri Common Utilities

Shared utilities and constants for all Tawhiri modules.
Provides logging, TLE parsing, configuration, and common calculations.

This module should be imported by all other modules to ensure consistency
across the platform.

Functions:
    Logging:
        - setup_logger: Create standardized logger
        - get_logger: Get existing logger
    
    TLE Parsing:
        - load_tles: Load TLEs from various sources
        - read_multi_epoch_tle_file: Load multi-epoch TLE files
        - parse_tle_line1: Extract data from TLE line 1
        - parse_tle_line2: Extract data from TLE line 2
        - validate_tle: Validate TLE format
    
    File I/O:
        - _lines_from_source: Parse lines from file/bytes/stream
        - load_json: Load JSON with error handling
        - save_json: Save JSON with error handling
    
    Time Utilities:
        - utc_now: Get current UTC time
        - format_timestamp: Format datetime consistently
        - parse_timestamp: Parse timestamp strings
    
    Math/Physics:
        - deg_to_rad: Degrees to radians
        - rad_to_deg: Radians to degrees
        - normalize_angle: Normalize angle to [0, 360)
        - haversine_distance: Distance between lat/lon points

Constants:
    EARTH_RADIUS_KM: Earth's mean radius (km)
    MU_EARTH: Earth's gravitational parameter (km³/s²)
    EARTH_J2: Earth's J2 oblateness coefficient
    EARTH_ROTATION_RATE: Earth's rotation rate (rad/s)
"""

import logging
import io
import json
import re
from datetime import datetime, timezone
from typing import Union, Dict, Tuple, List, Optional, Any
from pathlib import Path
import math


# ============================================================================
# Physical Constants
# ============================================================================

# Earth parameters
EARTH_RADIUS_KM = 6371.0  # Mean radius
EARTH_EQUATORIAL_RADIUS_KM = 6378.137  # Equatorial radius (WGS84)
EARTH_POLAR_RADIUS_KM = 6356.752  # Polar radius (WGS84)
MU_EARTH = 398600.4418  # Gravitational parameter km³/s²
EARTH_J2 = 0.00108263  # J2 oblateness coefficient
EARTH_ROTATION_RATE = 7.2921159e-5  # rad/s (sidereal)

# Orbit altitudes (km)
LEO_MAX_ALTITUDE = 2000  # Low Earth Orbit
MEO_MIN_ALTITUDE = 2000
MEO_MAX_ALTITUDE = 35786  # Medium Earth Orbit
GEO_ALTITUDE = 35786  # Geostationary orbit

# Speed of light
SPEED_OF_LIGHT_KM_S = 299792.458  # km/s


# ============================================================================
# Logging
# ============================================================================

# Global logger cache to avoid duplicate handlers
_loggers: Dict[str, logging.Logger] = {}


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Create and configure a logger with standard format.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: logging.INFO)
        log_file: Optional file path for file logging
        format_string: Optional custom format string
    
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger(__name__, logging.DEBUG)
        >>> logger.info("Module initialized")
    """
    # Return cached logger if exists
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(
        format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Cache logger
    _loggers[name] = logger
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get existing logger or create new one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)


# ============================================================================
# File I/O Utilities
# ============================================================================

def _lines_from_source(source: Union[str, bytes, io.IOBase, Path]) -> List[str]:
    """
    Parse lines from various sources.
    
    Handles file paths, bytes content, file-like objects, and Path objects.
    
    Args:
        source: File path (str/Path), bytes content, or file-like object
    
    Returns:
        List of stripped non-empty lines
    
    Raises:
        ValueError: If source type is unsupported
        FileNotFoundError: If file path doesn't exist
        
    Example:
        >>> lines = _lines_from_source("data.txt")
        >>> lines = _lines_from_source(Path("data.txt"))
        >>> lines = _lines_from_source(b"line1\\nline2\\n")
    """
    if isinstance(source, (str, Path)):
        # File path
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if line.strip()]
    
    elif isinstance(source, bytes):
        # Bytes content
        content = source.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    elif hasattr(source, 'read'):
        # File-like object
        content = source.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    else:
        raise ValueError(f"Unsupported source type: {type(source)}")
    
    return lines


def load_json(
    file_path: Union[str, Path],
    default: Optional[Any] = None
) -> Any:
    """
    Load JSON file with error handling.
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid
        
    Returns:
        Parsed JSON data or default value
        
    Example:
        >>> config = load_json("config.json", default={})
    """
    logger = get_logger(__name__)
    path = Path(file_path)
    
    if not path.exists():
        logger.warning(f"JSON file not found: {path}")
        return default
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON from {path}: {e}")
        return default


def save_json(
    data: Any,
    file_path: Union[str, Path],
    indent: int = 2
) -> bool:
    """
    Save data to JSON file with error handling.
    
    Args:
        data: Data to serialize
        file_path: Path to save JSON file
        indent: JSON indentation (default: 2)
        
    Returns:
        True if successful, False otherwise
        
    Example:
        >>> save_json({"key": "value"}, "output.json")
    """
    logger = get_logger(__name__)
    path = Path(file_path)
    
    try:
        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {e}")
        return False


# ============================================================================
# TLE Parsing
# ============================================================================

def validate_tle(line1: str, line2: str) -> bool:
    """
    Validate TLE format.
    
    Checks:
    - Line lengths (69 characters)
    - Line numbers (1 and 2)
    - Checksum validity
    
    Args:
        line1: TLE line 1
        line2: TLE line 2
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> valid = validate_tle(line1, line2)
    """
    # Check line lengths
    if len(line1) < 69 or len(line2) < 69:
        return False
    
    # Check line numbers
    if not (line1[0] == '1' and line2[0] == '2'):
        return False
    
    # Check NORAD IDs match
    try:
        norad1 = line1[2:7].strip()
        norad2 = line2[2:7].strip()
        if norad1 != norad2:
            return False
    except:
        return False
    
    # TODO: Add checksum validation if needed
    
    return True


def parse_tle_line1(line1: str) -> Dict[str, Any]:
    """
    Parse TLE line 1 and extract orbital elements.
    
    Args:
        line1: TLE line 1 (69 characters)
        
    Returns:
        Dict with parsed elements: norad_id, classification, epoch, etc.
        
    Example:
        >>> data = parse_tle_line1(line1)
        >>> print(data['norad_id'])
    """
    if len(line1) < 69:
        raise ValueError(f"TLE line 1 too short: {len(line1)} < 69")
    
    return {
        'line_number': int(line1[0]),
        'norad_id': line1[2:7].strip(),
        'classification': line1[7],
        'intl_designator': line1[9:17].strip(),
        'epoch_year': int(line1[18:20]),
        'epoch_day': float(line1[20:32]),
        'mean_motion_derivative': float(line1[33:43]),
        'mean_motion_2nd_derivative': line1[44:52].strip(),
        'bstar': line1[53:61].strip(),
        'ephemeris_type': int(line1[62]),
        'element_number': int(line1[64:68]),
        'checksum': int(line1[68])
    }


def parse_tle_line2(line2: str) -> Dict[str, Any]:
    """
    Parse TLE line 2 and extract orbital parameters.
    
    Args:
        line2: TLE line 2 (69 characters)
        
    Returns:
        Dict with parsed parameters: inclination, raan, eccentricity, etc.
        
    Example:
        >>> data = parse_tle_line2(line2)
        >>> print(data['inclination'])
    """
    if len(line2) < 69:
        raise ValueError(f"TLE line 2 too short: {len(line2)} < 69")
    
    return {
        'line_number': int(line2[0]),
        'norad_id': line2[2:7].strip(),
        'inclination': float(line2[8:16]),  # degrees
        'raan': float(line2[17:25]),  # Right Ascension of Ascending Node (degrees)
        'eccentricity': float('0.' + line2[26:33]),
        'arg_of_perigee': float(line2[34:42]),  # degrees
        'mean_anomaly': float(line2[43:51]),  # degrees
        'mean_motion': float(line2[52:63]),  # revolutions per day
        'revolution_number': int(line2[63:68]),
        'checksum': int(line2[68])
    }


def load_tles(
    source: Union[str, bytes, io.IOBase, Path]
) -> Dict[str, Tuple[str, str, str]]:
    """
    Load TLEs from various sources and return as dict.
    
    Supports both 2-line (no name) and 3-line (with name) TLE formats.
    
    Args:
        source: File path (str/Path), bytes content, or file-like object
    
    Returns:
        Dict mapping NORAD ID to (name, line1, line2)
        For 2-line TLEs without names, name will be "Unknown"
        
    Example:
        >>> tles = load_tles("satellites.txt")
        >>> name, line1, line2 = tles["25544"]  # ISS
        >>> print(f"Loaded {len(tles)} satellites")
    """
    logger = get_logger(__name__)
    lines = _lines_from_source(source)
    tle_dict = {}
    
    i = 0
    while i < len(lines) - 1:  # Need at least 2 lines for a TLE
        # Check if this is a 3-line TLE (name line doesn't start with "1 ")
        if i < len(lines) - 2 and not lines[i].startswith("1 "):
            # 3-line format: name, line1, line2
            name = lines[i]
            if name.startswith("0 "):
                name = name[2:].strip()
            line1 = lines[i + 1]
            line2 = lines[i + 2]
            i += 3
        else:
            # 2-line format: line1, line2
            name = "Unknown"
            line1 = lines[i]
            line2 = lines[i + 1]
            i += 2
        
        # Validate and extract NORAD ID
        if not validate_tle(line1, line2):
            logger.warning(f"Invalid TLE format, skipping: {name}")
            continue
        
        try:
            norad_id = line1[2:7].strip()
            if norad_id:
                tle_dict[norad_id] = (name, line1, line2)
        except (IndexError, ValueError) as e:
            logger.warning(f"Error parsing TLE for {name}: {e}")
            continue
    
    logger.info(f"Loaded {len(tle_dict)} TLEs")
    return tle_dict


def read_multi_epoch_tle_file(
    source: Union[str, bytes, io.IOBase, Path]
) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Load multi-epoch TLE file where satellites may have multiple TLE sets.
    
    Expected format: 3-line TLEs (name, line1, line2) repeated for each epoch.
    Useful for historical TLE analysis and orbit evolution studies.
    
    Args:
        source: File path (str/Path), bytes content, or file-like object
    
    Returns:
        Dict mapping satellite name to list of (label, line1, line2) tuples
        Label includes epoch information extracted from line1
        
    Example:
        >>> multi_tles = read_multi_epoch_tle_file("historical_tles.txt")
        >>> iss_epochs = multi_tles["ISS (ZARYA)"]
        >>> print(f"ISS has {len(iss_epochs)} historical epochs")
    """
    logger = get_logger(__name__)
    lines = _lines_from_source(source)
    tles = {}
    
    # Pattern to capture epoch: YYDDD.DDDDDDDD
    epoch_pattern = re.compile(r"^1\s+\S+\s+\S+\s+(\d{5}\.\d+)")
    
    i = 0
    while i < len(lines) - 2:
        name = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]
        i += 3
        
        # Extract epoch from line1
        match = epoch_pattern.match(line1)
        epoch_val = match.group(1) if match else "unknown"
        
        # Convert epoch to readable format
        try:
            year = int(epoch_val[:2])
            year = 2000 + year if year < 57 else 1900 + year
            day = float(epoch_val[2:])
            label = f"{name} @ {year}:{day:.2f}"
        except:
            label = f"{name} @ {epoch_val}"
        
        # Group by satellite name
        tles.setdefault(name, []).append((label, line1, line2))
    
    logger.info(f"Loaded multi-epoch TLEs for {len(tles)} satellites")
    return tles


# ============================================================================
# Time Utilities
# ============================================================================

def utc_now() -> datetime:
    """
    Get current UTC time as timezone-aware datetime.
    
    Returns:
        Current UTC datetime
        
    Example:
        >>> now = utc_now()
        >>> print(now.isoformat())
    """
    return datetime.now(timezone.utc)


def format_timestamp(
    dt: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S UTC"
) -> str:
    """
    Format datetime consistently.
    
    Args:
        dt: Datetime to format
        format_string: strftime format string
        
    Returns:
        Formatted timestamp string
        
    Example:
        >>> ts = format_timestamp(utc_now())
        >>> print(ts)
    """
    return dt.strftime(format_string)


def parse_timestamp(
    timestamp_str: str,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Parse timestamp string to datetime.
    
    Args:
        timestamp_str: Timestamp string
        format_string: strptime format string
        
    Returns:
        Parsed datetime or None if parsing fails
        
    Example:
        >>> dt = parse_timestamp("2025-11-22 10:30:00")
    """
    logger = get_logger(__name__)
    try:
        return datetime.strptime(timestamp_str, format_string)
    except ValueError as e:
        logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
        return None


# ============================================================================
# Math Utilities
# ============================================================================

def deg_to_rad(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def rad_to_deg(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi


def normalize_angle(angle: float, lower: float = 0.0, upper: float = 360.0) -> float:
    """
    Normalize angle to range [lower, upper).
    
    Args:
        angle: Angle in degrees
        lower: Lower bound (default: 0)
        upper: Upper bound (default: 360)
        
    Returns:
        Normalized angle
        
    Example:
        >>> normalize_angle(370)  # Returns 10.0
        >>> normalize_angle(-10)  # Returns 350.0
    """
    range_size = upper - lower
    return (angle - lower) % range_size + lower


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    radius: float = EARTH_RADIUS_KM
) -> float:
    """
    Calculate great circle distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)
        radius: Sphere radius (default: Earth radius in km)
        
    Returns:
        Distance in same units as radius
        
    Example:
        >>> # Distance from Wellington to Auckland
        >>> dist = haversine_distance(-41.28, 174.78, -36.85, 174.76)
        >>> print(f"{dist:.1f} km")
    """
    # Convert to radians
    lat1_rad = deg_to_rad(lat1)
    lon1_rad = deg_to_rad(lon1)
    lat2_rad = deg_to_rad(lat2)
    lon2_rad = deg_to_rad(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return radius * c


# Module exports
__all__ = [
    # Constants
    'EARTH_RADIUS_KM',
    'EARTH_EQUATORIAL_RADIUS_KM',
    'EARTH_POLAR_RADIUS_KM',
    'MU_EARTH',
    'EARTH_J2',
    'EARTH_ROTATION_RATE',
    'LEO_MAX_ALTITUDE',
    'MEO_MIN_ALTITUDE',
    'MEO_MAX_ALTITUDE',
    'GEO_ALTITUDE',
    'SPEED_OF_LIGHT_KM_S',
    
    # Logging
    'setup_logger',
    'get_logger',
    
    # File I/O
    'load_json',
    'save_json',
    '_lines_from_source',
    
    # TLE Parsing
    'validate_tle',
    'parse_tle_line1',
    'parse_tle_line2',
    'load_tles',
    'read_multi_epoch_tle_file',
    
    # Time
    'utc_now',
    'format_timestamp',
    'parse_timestamp',
    
    # Math
    'deg_to_rad',
    'rad_to_deg',
    'normalize_angle',
    'haversine_distance',
]
