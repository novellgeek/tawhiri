"""
File Utilities

Safe file operations with proper error handling.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


def safe_read_file(filepath: str, encoding: str = "utf-8") -> Optional[str]:
    """
    Safely read a text file with error handling.
    
    Args:
        filepath: Path to file
        encoding: Text encoding (default: utf-8)
        
    Returns:
        File contents as string, or None if read fails
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except PermissionError:
        logger.error(f"Permission denied reading: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None


def safe_write_file(filepath: str, content: str, encoding: str = "utf-8") -> bool:
    """
    Safely write to a text file with error handling.
    
    Args:
        filepath: Path to file
        content: Content to write
        encoding: Text encoding (default: utf-8)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        ensure_directory(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except PermissionError:
        logger.error(f"Permission denied writing: {filepath}")
        return False
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return False


def safe_read_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Safely read and parse a JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON as dictionary, or None if read/parse fails
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"JSON file not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading JSON file {filepath}: {e}")
        return None


def safe_write_json(filepath: str, data: Dict[str, Any], indent: int = 2) -> bool:
    """
    Safely write data to a JSON file.
    
    Args:
        filepath: Path to JSON file
        data: Data to serialize as JSON
        indent: Indentation level for pretty printing
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_directory(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file {filepath}: {e}")
        return False


def ensure_directory(dirpath: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dirpath: Path to directory
        
    Returns:
        True if directory exists or was created, False on error
    """
    if not dirpath:
        return True
    
    try:
        os.makedirs(dirpath, exist_ok=True)
        return True
    except PermissionError:
        logger.error(f"Permission denied creating directory: {dirpath}")
        return False
    except Exception as e:
        logger.error(f"Error creating directory {dirpath}: {e}")
        return False


def file_exists(filepath: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file exists and is accessible
    """
    try:
        return os.path.isfile(filepath)
    except Exception:
        return False


def get_file_size(filepath: str) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes, or None if file doesn't exist
    """
    try:
        return os.path.getsize(filepath)
    except Exception:
        return None
