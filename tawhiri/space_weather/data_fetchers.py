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
        logger.debug(f"Fetching JSON from: {url}")
        response = requests.get(url, timeout=timeout, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Successfully fetched JSON ({len(str(data))} bytes)")
        return data
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
@st.cache_data(ttl=DEFAULT_CACHE_TTL, show_spinner=True)
def fetch_text(url: str, timeout: int = 20) -> str:
    """
    Fetch raw text from a URL.
    
    Args:
        url: URL to fetch from
        timeout: Request timeout in seconds
        
    Returns:
        Raw text content, or empty string if fetch fails
        
    Example:
        >>> text = fetch_text("https://services.swpc.noaa.gov/text/3-day-forecast.txt")
        >>> if "R1-R2" in text:
        ...     print("Forecast contains R-scale data")
    """
    try:
        logger.debug(f"Fetching text from: {url}")
        response = requests.get(url, timeout=timeout, headers=HEADERS)
        response.raise_for_status()
        text = response.text
        logger.debug(f"Successfully fetched text ({len(text)} characters)")
        return text
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch text from {url}: {e}")
        return ""


# ============================================================================
# NOAA Current/Past Data
# ============================================================================

def get_noaa_rsg_now_and_past() -> Tuple[Dict, Dict]:
    """
    Get current and past 24-hour R/S/G scale values from NOAA.
    
    Fetches the latest data for:
        - R scale: X-ray flux (radio blackouts)
        - S scale: Proton flux (radiation storms)
        - G scale: Kp index (geomagnetic storms)
    
    Returns:
        Tuple of (past_24h_data, current_data), each containing:
            - 'r': R scale level (e.g., "R2")
            - 's': S scale level
            - 'g': G scale level
            - 'r_txt', 's_txt', 'g_txt': Human-readable labels
            - 'r_status', 's_status', 'g_status': "Active" or "No"
            - 'lvl', 'lvl_s', 'lvl_g': Severity levels
            
    Example:
        >>> past, current = get_noaa_rsg_now_and_past()
        >>> print(f"Current geomagnetic conditions: {current['g']}")
        >>> if current['r'] != 'R0':
        ...     print("Radio blackout in progress!")
    """
    # Fetch Kp index data
    try:
        kp_data = fetch_json(NOAA_URLS['kp_3day'])
        if kp_data:
            k_now = clamp_float(kp_data[-1].get("kp_index", 0))
            last_24 = kp_data[-24:] if len(kp_data) >= 24 else kp_data
            k_past = max(clamp_float(v.get("kp_index", 0)) for v in last_24) if last_24 else k_now
        else:
            k_now = k_past = 0.0
    except Exception as e:
        logger.error(f"Error processing Kp data: {e}")
        k_now = k_past = 0.0

    # Fetch X-ray flux data
    try:
        xray_data = fetch_json(NOAA_URLS['xray_7day'])
        if xray_data:
            x_now = clamp_float(xray_data[-1].get("flux", 0))
            last_24 = xray_data[-24:] if len(xray_data) >= 24 else xray_data
            x_past = max(clamp_float(v.get("flux", 0)) for v in last_24) if last_24 else x_now
        else:
            x_now = x_past = 0.0
    except Exception as e:
        logger.error(f"Error processing X-ray data: {e}")
        x_now = x_past = 0.0

    # Fetch proton flux data
    try:
        proton_data = fetch_json(NOAA_URLS['proton_7day'])
        if proton_data:
            p_now = clamp_float(proton_data[-1].get("flux", 0))
            last_24 = proton_data[-24:] if len(proton_data) >= 24 else proton_data
            p_past = max(clamp_float(v.get("flux", 0)) for v in last_24) if last_24 else p_now
        else:
            p_now = p_past = 0.0
    except Exception as e:
        logger.error(f"Error processing proton data: {e}")
        p_now = p_past = 0.0

    # Calculate scales
    r_now, r_now_lvl = r_scale(x_now)
    r_past, r_past_lvl = r_scale(x_past)
    s_now, s_now_lvl = s_scale(p_now)
    s_past, s_past_lvl = s_scale(p_past)
    g_now, g_now_lvl = g_scale(k_now)
    g_past, g_past_lvl = g_scale(k_past)

    # Build current status dict
    current = {
        "r": r_now,
        "r_txt": "Radio blackouts",
        "r_status": "No" if r_now == "R0" else "Active",
        "lvl": r_now_lvl,
        "s": s_now,
        "s_txt": "Radiation storms",
        "s_status": "No" if s_now == "S0" else "Active",
        "lvl_s": s_now_lvl,
        "g": g_now,
        "g_txt": "Geomagnetic storms",
        "g_status": "No" if g_now == "G0" else "Active",
        "lvl_g": g_now_lvl
    }

    # Build past 24h status dict
    past = {
        "r": r_past,
        "r_txt": "Radio blackouts",
        "r_status": "No" if r_past == "R0" else "Active",
        "lvl": r_past_lvl,
        "s": s_past,
        "s_txt": "Radiation storms",
        "s_status": "No" if s_past == "S0" else "Active",
        "lvl_s": s_past_lvl,
        "g": g_past,
        "g_txt": "Geomagnetic storms",
        "g_status": "No" if g_past == "G0" else "Active",
        "lvl_g": g_past_lvl
    }

    return past, current


# ============================================================================
# Three-Day Forecast Parsing
# ============================================================================

def parse_three_day_full(txt: str) -> Dict:
    """
    Parse NOAA 3-day forecast text into structured data.
    
    Extracts probability percentages for R-scale and S-scale events,
    plus Kp index predictions for all three days.
    
    Args:
        txt: Raw forecast text from NOAA
        
    Returns:
        Dict with 'days' key containing list of 3 day forecasts, each with:
            - 'r12': R1-R2 probability (%)
            - 'r3': R3+ probability (%)
            - 's1': S1+ probability (%)
            - 'kp': Maximum Kp index expected
            - 'g': G-scale level (e.g., "G2")
    """
    # Normalize dashes and whitespace
    clean = re.sub(r"[–—]", "-", " ".join(txt.split()))

    def _triplet(pattern: str) -> List[Optional[int]]:
        """Extract three values (for 3 days) from a regex pattern."""
        m = re.search(pattern, clean, re.I)
        if not m:
            return [None, None, None]
        a, b, c = m.groups()
        return [int(a), int(b), int(c)]

    # Extract R-scale probabilities
    r12 = _triplet(r"R1-?R2\s+(\d+)%\s+(\d+)%\s+(\d+)%")
    r3p = _triplet(r"R3\s*(?:\+|or greater)\s+(\d+)%\s+(\d+)%\s+(\d+)%")
    
    # Extract S-scale probabilities
    s1p = _triplet(r"S1\s*(?:\+|or greater)\s+(\d+)%\s+(\d+)%\s+(\d+)%")

    # Extract Kp index predictions
    kp_trip = [None, None, None]
    
    # Try to find Kp table (format: HH-HHUT Kp1 Kp2 Kp3)
    table = re.findall(r"\d{2}-\d{2}UT\s+(\d(?:\.\d+)?)\s+(\d(?:\.\d+)?)\s+(\d(?:\.\d+)?)", clean)
    if table:
        # Take max Kp from each column
        colmax = [0.0, 0.0, 0.0]
        for a, b, c in table:
            colmax[0] = max(colmax[0], clamp_float(a))
            colmax[1] = max(colmax[1], clamp_float(b))
            colmax[2] = max(colmax[2], clamp_float(c))
        kp_trip = colmax
    else:
        # Fallback: look for text statement about Kp
        fb = re.search(r"greatest expected 3 hr Kp .*? is\s+(\d+(?:\.\d+)?)", clean, re.I)
        if fb:
            k = clamp_float(fb.group(1))
            kp_trip = [k, k, k]  # Use same value for all 3 days

    # Build day-by-day data
    days = []
    for i in range(3):
        kp = kp_trip[i]
        g_bucket = g_scale(kp)[0] if kp is not None else "G0"
        days.append({
            "r12": int(r12[i] or 0),
            "r3": int(r3p[i] or 0),
            "s1": int(s1p[i] or 0),
            "kp": kp,
            "g": g_bucket
        })

    return {"days": days}


def get_3day_summary() -> Dict:
    """
    Fetch and parse 3-day forecast from NOAA.
    
    Returns:
        Dict with 'days' list containing forecast for 3 days
        
    Note:
        This function includes caching in production (would use @cache decorator)
    """
    try:
        txt = fetch_text(NOAA_URLS['discussion'])
        if txt:
            return parse_three_day_full(txt)
    except Exception as e:
        logger.error(f"Error getting 3-day summary: {e}")

    # Return default empty forecast
    return {
        "days": [
            {"r12": 0, "r3": 0, "s1": 0, "kp": None, "g": "G0"},
            {"r12": 0, "r3": 0, "s1": 0, "kp": None, "g": "G0"},
            {"r12": 0, "r3": 0, "s1": 0, "kp": None, "g": "G0"},
        ]
    }


def parse_three_day_for_next24(txt: str) -> Dict:
    """
    Parse 3-day forecast text focusing on next 24 hours.
    
    Simplified version that extracts only Day 1 probabilities and
    creates summary buckets for quick assessment.
    
    Args:
        txt: Raw forecast text from NOAA
        
    Returns:
        Dict with:
            - 'r_bucket': R scale bucket (R0, R1, R2, etc.)
            - 'r12_prob': R1-R2 probability for day 1
            - 'r3_prob': R3+ probability for day 1
            - 's_bucket': S scale bucket
            - 's1_prob': S1+ probability for day 1
            - 'g_bucket': G scale bucket
            - 'kp_max': Maximum expected Kp as string
    """
    clean = re.sub(r"[–—]", "-", " ".join(txt.split()))
    r12 = r3p = s1p = None
    kpmax_day1 = kpmax_day2 = None

    # Try to extract R-scale probabilities (combined pattern first)
    m_r = re.search(
        r"R1-?R2\s+(\d+)%\s+(\d+)%\s+(\d+)%.*?R3\s*(?:\+|or greater)\s+(\d+)%\s+(\d+)%\s+(\d+)%",
        clean, re.I
    )
    if m_r:
        r12, _r12d2, _r12d3, r3p, _r3d2, _r3d3 = map(int, m_r.groups())
    else:
        # Try separate patterns
        m_r12 = re.search(r"R1-?R2\s+(\d+)%", clean, re.I)
        m_r3 = re.search(r"R3\s*(?:\+|or greater)\s+(\d+)%", clean, re.I)
        r12 = int(m_r12.group(1)) if m_r12 else 0
        r3p = int(m_r3.group(1)) if m_r3 else 0

    # Extract S-scale probabilities
    m_s = re.search(r"S1\s*(?:\+|or greater)\s+(\d+)%\s+(\d+)%\s+(\d+)%", clean, re.I)
    if m_s:
        s1p, _s1d2, _s1d3 = map(int, m_s.groups())
    else:
        m_s1 = re.search(r"S1\s*(?:\+|or greater)\s+(\d+)%", clean, re.I)
        s1p = int(m_s1.group(1)) if m_s1 else 0

    # Extract Kp predictions
    triplets = re.findall(r"\d{2}-\d{2}UT\s+(\d(?:\.\d+)?)\s+(\d(?:\.\d+)?)\s+(\d(?:\.\d+)?)", clean)
    if triplets:
        colmax = [0.0, 0.0, 0.0]
        for a, b, c in triplets:
            colmax[0] = max(colmax[0], clamp_float(a))
            colmax[1] = max(colmax[1], clamp_float(b))
            colmax[2] = max(colmax[2], clamp_float(c))
        kpmax_day1, kpmax_day2 = colmax[0], colmax[1]
    else:
        # Fallback
        fb = re.search(r"greatest expected 3 hr Kp .*? is\s+(\d+(?:\.\d+)?)", clean, re.I)
        if fb:
            k = clamp_float(fb.group(1))
            kpmax_day1 = kpmax_day2 = k

    # Determine R bucket
    r_bucket = "R0"
    if (r12 or 0) >= 10:
        r_bucket = "R1"
    if (r3p or 0) >= 1:
        r_bucket = "R2"

    # Determine S bucket
    s_bucket = "S0"
    if (s1p or 0) >= 10:
        s_bucket = "S1"

    # Determine G bucket
    if kpmax_day1 is not None:
        g_bucket, _ = g_scale(kpmax_day1)
        kp_str = f"{kpmax_day1:.2f}"
    elif kpmax_day2 is not None:
        g_bucket, _ = g_scale(kpmax_day2)
        kp_str = f"{kpmax_day2:.2f}"
    else:
        g_bucket = "G0"
        kp_str = "~"

    return {
        "r_bucket": r_bucket,
        "r12_prob": int(r12 or 0),
        "r3_prob": int(r3p or 0),
        "s_bucket": s_bucket,
        "s1_prob": int(s1p or 0),
        "g_bucket": g_bucket,
        "kp_max": kp_str
    }


def get_next24_summary() -> Dict:
    """
    Get next 24-hour forecast summary from NOAA.
    
    Returns:
        Dict with scale buckets and probabilities for next 24h
    """
    try:
        txt = fetch_text(NOAA_URLS['discussion'])
        if txt:
            return parse_three_day_for_next24(txt)
    except Exception as e:
        logger.error(f"Error getting next 24h summary: {e}")

    # Return default
    return {
        "r_bucket": "R0",
        "r12_prob": 0,
        "r3_prob": 0,
        "s_bucket": "S0",
        "s1_prob": 0,
        "g_bucket": "G0",
        "kp_max": "~"
    }


# ============================================================================
# NOAA Forecast Text
# ============================================================================

def get_noaa_forecast_text() -> Tuple[Dict, Optional[str], str]:
    """
    Get NOAA forecast discussion text.
    
    Tries discussion.txt first, then 3-day-forecast.txt as fallback.
    
    Returns:
        Tuple of (structured_dict, source_url, raw_text) where:
            - structured_dict: Parsed sections (if parser exists)
            - source_url: URL that was successfully fetched
            - raw_text: Full raw text from NOAA
    """
    urls = [
        "https://services.swpc.noaa.gov/text/discussion.txt",
        NOAA_URLS['discussion'],
    ]

    def _try(url: str) -> Optional[Tuple]:
        raw = fetch_text(url)
        if not raw.strip():
            return None
        
        full = raw.strip()
        
        # Placeholder for structured parsing
        # TODO: Implement parse_discussion_structured() if needed
        structured = {
            "solar_activity": {"summary": "", "forecast": ""},
            "energetic_particle": {"summary": "", "forecast": ""},
            "solar_wind": {"summary": "", "forecast": ""},
            "geospace": {"summary": "", "forecast": ""},
            "_reflowed": full
        }
        
        return structured, url, full

    # Try each URL in order
    for url in urls:
        result = _try(url)
        if result:
            return result

    # Hard fallback if all fail
    return (
        {
            "solar_activity": {"summary": "", "forecast": ""},
            "energetic_particle": {"summary": "", "forecast": ""},
            "solar_wind": {"summary": "", "forecast": ""},
            "geospace": {"summary": "", "forecast": ""},
            "_reflowed": "NOAA forecast discussion unavailable."
        },
        None,
        ""
    )


# ============================================================================
# Summary Generation
# ============================================================================

def make_summary(current: Dict, next24: Dict) -> str:
    """
    Generate executive summary text from current conditions and forecast.
    
    Args:
        current: Current conditions dict from get_noaa_rsg_now_and_past()
        next24: Next 24h forecast dict from get_next24_summary()
        
    Returns:
        Human-readable summary string
        
    Example:
        >>> past, current = get_noaa_rsg_now_and_past()
        >>> next24 = get_next24_summary()
        >>> summary = make_summary(current, next24)
        >>> print(summary)
        Now (R/S/G): R0/S0/G1. Next 24 h: G1 (Kp≃4.23); ...
    """
    g = next24["g_bucket"]
    kp = next24["kp_max"]
    r12 = next24["r12_prob"]
    r3 = next24["r3_prob"]
    s1 = next24["s1_prob"]
    
    # Build summary components
    now_status = f"Now (R/S/G): {current['r']}/{current['s']}/{current['g']}."
    forecast_status = f"Next 24 h: {g} (Kp≃{kp}); R1–R2 {r12}% | R3+ {r3}% | S1+ {s1}%."
    
    # Determine implications
    hf_impact = "HF comms at risk; watch D-layer absorption" if current['r'] != 'R0' or r12 >= 10 else "Nominal HF"
    radiation_impact = "SEPs possible; elevate EVA/aviation polar routes" if current['s'] != 'S0' or s1 >= 10 else "Nominal radiation"
    
    # Parse G level for geomagnetic impact
    g_num = int(g[1]) if len(g) > 1 and g[1].isdigit() else 0
    geo_impact = "Geomagnetic impacts possible; GIC risk on high-lat power & GNSS scintillation" if g_num >= 1 else "Nominal geomagnetic."
    
    implications = f"Implications: {hf_impact}, {radiation_impact}, {geo_impact}"
    
    return f"{now_status} {forecast_status} {implications}"


# Export public API
__all__ = [
    'fetch_json',
    'fetch_text',
    'get_noaa_rsg_now_and_past',
    'get_3day_summary',
    'get_next24_summary',
    'get_noaa_forecast_text',
    'parse_three_day_full',
    'parse_three_day_for_next24',
    'make_summary',
]


