"""
NZ-Specific Translations

Converts technical space weather descriptions into plain English,
NZ-relevant operational impacts for New Zealand Defence Force operations.

This module provides New Zealand-specific interpretations of space weather
conditions, translating technical NOAA descriptions into actionable intelligence
for NZDF operators.

Functions:
    - rewrite_to_nz: Main translation function for different space weather sections
    - Helper functions for severity classification and risk assessment
"""

from typing import Optional


# Regional hint for NZ context
_NZ_REGIONAL_HINT = " "


def _any(txt: str, *phrases) -> bool:
    """
    Check if any of the given phrases appear in the text (case-insensitive).
    
    Args:
        txt: Text to search in
        *phrases: Variable number of phrases to search for
        
    Returns:
        True if any phrase is found, False otherwise
        
    Example:
        >>> _any("Solar activity is high", "high", "elevated")
        True
        >>> _any("Quiet conditions", "storm", "active")
        False
    """
    low = (txt or "").lower()
    return any(p in low for p in phrases)


def _r_class(r: str) -> str:
    """
    Map R-scale value to severity class.
    
    Args:
        r: R-scale string (e.g., "R0", "R1", "R3")
        
    Returns:
        Severity class: "ok", "caution", "watch", or "severe"
        
    Example:
        >>> _r_class("R1")
        'caution'
        >>> _r_class("R5")
        'severe'
    """
    r = (r or "").upper()
    if r.startswith("R0"):
        return "ok"
    if r.startswith("R1") or r.startswith("R2"):
        return "caution"
    if r.startswith("R3"):
        return "watch"
    if r.startswith(("R4", "R5")):
        return "severe"
    return "ok"  # Default to ok for unknown


def _s_class(s: str) -> str:
    """
    Map S-scale value to severity class.
    
    Args:
        s: S-scale string (e.g., "S0", "S1", "S3")
        
    Returns:
        Severity class: "ok", "caution", "watch", or "severe"
        
    Example:
        >>> _s_class("S2")
        'caution'
        >>> _s_class("S4")
        'severe'
    """
    s = (s or "").upper()
    if s.startswith("S0"):
        return "ok"
    if s.startswith("S1") or s.startswith("S2"):
        return "caution"
    if s.startswith("S3"):
        return "watch"
    if s.startswith(("S4", "S5")):
        return "severe"
    return "ok"  # Default to ok for unknown


def _g_class(g: str) -> str:
    """
    Map G-scale value to severity class.
    
    Args:
        g: G-scale string (e.g., "G0", "G2", "G4")
        
    Returns:
        Severity class: "ok", "caution", "watch", or "severe"
        
    Example:
        >>> _g_class("G1")
        'ok'
        >>> _g_class("G3")
        'watch'
    """
    g = (g or "").upper()
    if g.startswith("G0") or g.startswith("G1"):
        return "ok"
    if g.startswith("G2"):
        return "caution"
    if g.startswith("G3"):
        return "watch"
    if g.startswith(("G4", "G5")):
        return "severe"
    return "ok"  # Default to ok for unknown


def _class_to_level(cls_key: str) -> str:
    """
    Normalize severity class key.
    
    Args:
        cls_key: Severity class string
        
    Returns:
        Normalized severity level
        
    Example:
        >>> _class_to_level("CAUTION")
        'caution'
    """
    mapping = {
        "ok": "ok",
        "caution": "caution",
        "watch": "watch",
        "severe": "severe"
    }
    return mapping.get((cls_key or "").lower(), "ok")


def _nz_risk_phrase(kind: str, level: str) -> str:
    """
    Get NZ-specific operational risk description for a given scale and severity.
    
    Args:
        kind: Scale type ("R", "S", or "G")
        level: Severity level ("ok", "caution", "watch", "severe")
        
    Returns:
        NZ-specific operational impact description
        
    Example:
        >>> _nz_risk_phrase("R", "watch")
        'Heightened risk of HF and GNSS disruption across NZ, esp. midday paths.'
        >>> _nz_risk_phrase("G", "severe")
        'Severe storm — GNSS, HF, and power systems may be impacted; widespread aurora possible.'
    """
    if kind == "R":
        # Radio blackout risks for NZ
        return {
            "ok": "HF comms across NZ should be fine.",
            "caution": "Short HF dropouts are possible, mainly sunlit side; most NZ circuits OK.",
            "watch": "Heightened risk of HF and GNSS disruption across NZ, esp. midday paths.",
            "severe": "Significant HF and GNSS disruption likely across NZ and the Pacific."
        }[level]
    
    if kind == "S":
        # Solar radiation storm risks for NZ
        return {
            "ok": "Radiation environment normal over NZ.",
            "caution": "Elevated radiation — minor impacts; commercial flights OK, polar routes more affected.",
            "watch": "High radiation risk for polar operations; monitor aviation/space assets in our region.",
            "severe": "Severe radiation storm — restrict high-latitude ops; protect space assets."
        }[level]
    
    # Geomagnetic storm risks for NZ (G-scale)
    return {
        "ok": "Geomagnetic field quiet; GNSS is stable across NZ.",
        "caution": "Field unsettled — small GNSS accuracy dips possible; slim aurora chance in Southland.",
        "watch": "Storm conditions — GNSS accuracy can degrade at times; good aurora odds in the deep south.",
        "severe": "Severe storm — GNSS, HF, and power systems may be impacted; widespread aurora possible."
    }[level]


def rewrite_to_nz(
    section: str,
    text: str,
    *,
    r_now: str = "R0",
    s_now: str = "S0",
    g_now: str = "G0",
    day1: Optional[dict] = None
) -> str:
    """
    Rewrite technical NOAA space weather text into NZ-specific operational language.
    
    Takes technical space weather descriptions and converts them into plain English
    with NZ-relevant operational impacts suitable for NZDF briefings.
    
    Args:
        section: Section type ("solar_activity", "solar_wind", "geospace", or other)
        text: Original NOAA technical text
        r_now: Current R-scale value (default: "R0")
        s_now: Current S-scale value (default: "S0")
        g_now: Current G-scale value (default: "G0")
        day1: Optional forecast data for next 24h
        
    Returns:
        NZ-translated description with operational impact assessment
        
    Example:
        >>> rewrite_to_nz(
        ...     "solar_activity",
        ...     "Solar activity reached high levels with an X2 flare.",
        ...     r_now="R3"
        ... )
        'Major solar flares noted — higher chance of radio/GNSS issues across New Zealand. \\n• Heightened risk of HF and GNSS disruption across NZ, esp. midday paths.'
    """
    tx = (text or "").strip()
    
    if not tx:
        base = "No significant activity reported."
    else:
        low = tx.lower()
        
        if section == "solar_activity":
            # Solar flare activity translation
            if _any(low, "x-class", "major flare", "significant flare"):
                base = "Major solar flares noted — higher chance of radio/GNSS issues across New Zealand."
            elif _any(low, "m-class", "moderate"):
                base = "Moderate solar flares observed — brief HF/GNSS hiccups possible over NZ."
            elif _any(low, "c-class", "low", "quiet"):
                base = "The Sun is fairly quiet — only small flares, negligible impact for NZ."
            else:
                base = "Solar activity is mixed but not unusual for the cycle; NZ impacts limited."
        
        elif section == "solar_wind":
            # Solar wind conditions translation
            if _any(low, "cme", "shock", "sheath"):
                base = "A CME is influencing the solar wind — conditions can stir up NZ geomagnetic activity."
            elif _any(low, "high speed", "coronal hole", "600 km/s", "elevated"):
                base = "Solar wind is running fast — may unsettle Earth's field; aurora possible in the far south."
            else:
                base = "Solar wind conditions are near normal — minimal impact expected over NZ."
        
        elif section == "geospace":
            # Geomagnetic field conditions translation
            if _any(low, "g2", "g3", "storm"):
                base = "Geomagnetic storming occurred — GNSS accuracy could dip; aurora chances improve in Southland."
            elif _any(low, "active", "unsettled"):
                base = "Field was unsettled — small GNSS wobbles possible; low aurora chance."
            else:
                base = "Geomagnetic field is quiet for NZ — comms and GNSS are stable."
        
        else:
            # Energetic particles and other sections
            if _any(low, "elevated", "enhanced", "storm"):
                base = "Energetic particles elevated — low operational impact for NZ; monitor polar routes."
            else:
                base = "Radiation environment looks normal for NZ operations."
    
    # Add appropriate risk phrase based on section type
    if section == "solar_activity":
        r_cls = _r_class(r_now)
        main_risk = _nz_risk_phrase("R", _class_to_level(r_cls))
        return f"{base}{_NZ_REGIONAL_HINT}\n• {main_risk}"
    
    elif section == "solar_wind":
        s_cls = _s_class(s_now)
        main_risk = _nz_risk_phrase("S", _class_to_level(s_cls))
        return f"{base}{_NZ_REGIONAL_HINT}\n• {main_risk}"
    
    elif section == "geospace":
        g_cls = _g_class(g_now)
        main_risk = _nz_risk_phrase("G", _class_to_level(g_cls))
        return f"{base}{_NZ_REGIONAL_HINT}\n• {main_risk}"
    
    else:
        # Fallback for other sections - just return base text with regional hint
        return f"{base}{_NZ_REGIONAL_HINT}"


# Module exports
__all__ = [
    "rewrite_to_nz",
    "_nz_risk_phrase",
    "_r_class",
    "_s_class",
    "_g_class",
    "_class_to_level",
    "_any",
]
