"""
Configuration Management

Loads configuration from config.json with fallbacks to sensible defaults.
Supports environment-specific overrides for development, production, and secure deployments.
"""

import json
import os
import pathlib
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file with defaults.
    
    Args:
        config_path: Path to config.json file. If None, searches in:
                     1. Environment variable TAWHIRI_CONFIG
                     2. ./config.json (current directory)
                     3. ~/.tawhiri/config.json (user home)
                     4. /etc/tawhiri/config.json (system-wide)
    
    Returns:
        Dictionary containing configuration
        
    Example:
        >>> config = load_config()
        >>> print(config['data_dir'])
        /opt/tawhiri/data
    """
    
    # Default configuration
    home = pathlib.Path.home()
    default_config = {
        "data_dir": str(home / "tawhiri_data"),
        "space_weather": {
            "noaa_api_key": "",
            "bom_api_key": "",
            "cache_ttl_seconds": 600,
            "update_interval_minutes": 10,
        },
        "orbit_viz": {
            "earth_textures_dir": str(home / "tawhiri_data" / "earth"),
            "tle_file": str(home / "tawhiri_data" / "tle-single.txt"),
            "sat_metadata": str(home / "tawhiri_data" / "3d" / "sat_metadata.csv"),
            "preferences_dir": str(home / "tawhiri_data" / "3d"),
            "skyfield_cache": str(home / "tawhiri_data" / "skyfield_cache"),
        },
        "logging": {
            "log_file": str(home / "tawhiri_data" / "logs" / "tawhiri.log"),
            "log_level": "INFO",
            "log_to_console": True,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "deployment": {
            "environment": "development",
            "offline_mode": False,
            "high_contrast_mode": False,
        },
    }
    
    # Search for config file
    if config_path is None:
        search_paths = [
            os.getenv("TAWHIRI_CONFIG"),
            "./config.json",
            str(home / ".tawhiri" / "config.json"),
            "/etc/tawhiri/config.json",
        ]
        
        for path in search_paths:
            if path and os.path.isfile(path):
                config_path = path
                break
    
    # Load user configuration if found
    if config_path and os.path.isfile(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Deep merge with defaults
            _deep_merge(default_config, user_config)
            logger.info(f"Loaded configuration from: {config_path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
    else:
        logger.warning("No config file found, using defaults")
    
    # Environment variable overrides
    if os.getenv("TAWHIRI_DATA_DIR"):
        default_config["data_dir"] = os.getenv("TAWHIRI_DATA_DIR")
    
    if os.getenv("TAWHIRI_OFFLINE"):
        default_config["deployment"]["offline_mode"] = True
    
    return default_config


def _deep_merge(base: Dict, updates: Dict) -> None:
    """
    Deep merge updates into base dictionary (in-place).
    
    Args:
        base: Base dictionary to update
        updates: Dictionary with updates to apply
    """
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_data_path(config: Dict[str, Any], *parts: str) -> pathlib.Path:
    """
    Construct a path within the data directory.
    
    Args:
        config: Configuration dictionary
        *parts: Path components to join
        
    Returns:
        Path object
        
    Example:
        >>> config = load_config()
        >>> tle_path = get_data_path(config, "tle-single.txt")
    """
    base = pathlib.Path(config["data_dir"])
    return base.joinpath(*parts)


def ensure_directories(config: Dict[str, Any]) -> None:
    """
    Create all necessary directories defined in configuration.
    
    Args:
        config: Configuration dictionary
    """
    dirs_to_create = [
        config["data_dir"],
        config["orbit_viz"]["earth_textures_dir"],
        config["orbit_viz"]["preferences_dir"],
        config["orbit_viz"]["skyfield_cache"],
        os.path.dirname(config["logging"]["log_file"]),
    ]
    
    for dir_path in dirs_to_create:
        try:
            os.makedirs(dir_path, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")


# Global config instance (lazy loaded)
_global_config: Optional[Dict[str, Any]] = None


def get_config() -> Dict[str, Any]:
    """
    Get global configuration instance (lazy loaded).
    
    Returns:
        Configuration dictionary
    """
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config
