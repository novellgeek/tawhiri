"""
Data Fetchers

API data retrieval with caching and error handling for NOAA and BOM sources.

TODO: Migrate your fetch_json() and fetch_text() functions here.
"""

import requests
import streamlit as st
import logging
from typing import Optional, Dict, Any
from .constants import USER_AGENT, DEFAULT_CACHE_TTL

logger = logging.getLogger(__name__)


@st.cache_data(ttl=DEFAULT_CACHE_TTL, show_spinner=True)
def fetch_json(url: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    """
    Fetch and parse JSON from URL with caching and error handling.
    
    Args:
        url: URL to fetch from
        timeout: Request timeout in seconds
        
    Returns:
        Parsed JSON as dictionary, or None if request fails
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, timeout=timeout, headers=headers)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(f"Network error fetching {url}: {e}")
        st.warning(f"Failed to load data from {url}")
        return None
    except ValueError as e:
        logger.error(f"Invalid JSON from {url}: {e}")
        st.warning(f"Invalid data format from {url}")
        return None


@st.cache_data(ttl=DEFAULT_CACHE_TTL, show_spinner=True)
def fetch_text(url: str, timeout: int = 20) -> str:
    """
    Fetch text content from URL with caching and error handling.
    
    Args:
        url: URL to fetch from
        timeout: Request timeout in seconds
        
    Returns:
        Text content, or empty string if request fails
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, timeout=timeout, headers=headers)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        logger.error(f"Network error fetching {url}: {e}")
        st.warning(f"Failed to load data from {url}")
        return ""


# TODO: Add your specific data fetchers here:
# - fetch_noaa_xray_data()
# - fetch_noaa_proton_data()
# - fetch_noaa_kp_data()
# - fetch_bom_aurora()
# etc.
