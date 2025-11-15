"""
NOAA Space Weather Scale Classifications

Functions to classify space weather events according to NOAA R/S/G scales.
"""

from typing import Tuple
from .constants import (
    R_SCALE_THRESHOLDS,
    S_SCALE_THRESHOLDS,
    G_SCALE_THRESHOLDS,
    SEVERITY_LABELS,
)


def r_scale(xray_flux_wm2: float) -> Tuple[str, str]:
    """
    Classify X-ray flux according to NOAA R-scale (Radio Blackout).
    
    Args:
        xray_flux_wm2: X-ray flux in watts per square meter
        
    Returns:
        Tuple of (scale_level, severity_label)
        Example: ("R3", "strong")
        
    Scale:
        R5 (Extreme): >= 2e-3 W/m² (X20+ flares)
        R4 (Severe):  >= 1e-3 W/m² (X10-X19 flares)
        R3 (Strong):  >= 1e-4 W/m² (X1-X9 flares)
        R2 (Moderate):>= 5e-5 W/m² (M5-M9 flares)
        R1 (Minor):   >= 1e-5 W/m² (M1-M4 flares)
        R0 (Quiet):   <  1e-5 W/m²
    """
    for level in ['R5', 'R4', 'R3', 'R2', 'R1']:
        if xray_flux_wm2 >= R_SCALE_THRESHOLDS[level]:
            return (level, SEVERITY_LABELS[level])
    return ("R0", SEVERITY_LABELS['R0'])


def s_scale(proton_pfu_10mev: float) -> Tuple[str, str]:
    """
    Classify proton flux according to NOAA S-scale (Solar Radiation Storm).
    
    Args:
        proton_pfu_10mev: Proton flux in particle flux units (>10 MeV)
        
    Returns:
        Tuple of (scale_level, severity_label)
        Example: ("S2", "moderate")
        
    Scale:
        S5 (Extreme):  >= 100,000 pfu
        S4 (Severe):   >= 10,000 pfu
        S3 (Strong):   >= 1,000 pfu
        S2 (Moderate): >= 100 pfu
        S1 (Minor):    >= 10 pfu
        S0 (Quiet):    < 10 pfu
    """
    for level in ['S5', 'S4', 'S3', 'S2', 'S1']:
        if proton_pfu_10mev >= S_SCALE_THRESHOLDS[level]:
            return (level, SEVERITY_LABELS[level])
    return ("S0", SEVERITY_LABELS['S0'])


def g_scale(kp_index: float) -> Tuple[str, str]:
    """
    Classify geomagnetic activity by Kp index according to NOAA G-scale.
    
    Args:
        kp_index: Planetary Kp index (0-9 scale)
        
    Returns:
        Tuple of (scale_level, severity_label)
        Example: ("G1", "minor")
        
    Scale:
        G5 (Extreme):  Kp >= 9
        G4 (Severe):   Kp >= 8
        G3 (Strong):   Kp >= 7
        G2 (Moderate): Kp >= 6
        G1 (Minor):    Kp >= 5
        G0 (Quiet):    Kp < 5
    """
    for level in ['G5', 'G4', 'G3', 'G2', 'G1']:
        if kp_index >= G_SCALE_THRESHOLDS[level]:
            return (level, SEVERITY_LABELS[level])
    return ("G0", SEVERITY_LABELS['G0'])


def ap_to_kp(ap: float) -> float:
    """
    Convert Ap index to approximate Kp index.
    
    Note: This is a coarse conversion commonly used in operations.
    For precise work, use actual Kp values.
    
    Args:
        ap: Ap index value
        
    Returns:
        Approximate Kp index
    """
    ap = float(ap)
    if ap >= 400: return 9.0
    if ap >= 240: return 8.0
    if ap >= 140: return 7.0
    if ap >= 80:  return 6.0
    if ap >= 48:  return 5.0
    if ap >= 27:  return 4.0
    if ap >= 15:  return 3.0
    if ap >= 7:   return 2.0
    if ap >= 3:   return 1.0
    return 0.0


def g_scale_from_ap(ap: float) -> Tuple[str, str]:
    """
    Classify geomagnetic activity from Ap index.
    
    Args:
        ap: Ap index value
        
    Returns:
        Tuple of (scale_level, severity_label)
    """
    kp = ap_to_kp(ap)
    return g_scale(kp)


def get_impact_description(scale_type: str, level: str, region: str = "NZ") -> str:
    """
    Get operational impact description for a given scale level.
    
    Args:
        scale_type: Type of scale ('R', 'S', or 'G')
        level: Severity level ('quiet', 'minor', 'moderate', 'strong', 'severe', 'extreme')
        region: Region for localized descriptions (default: 'NZ')
        
    Returns:
        Human-readable impact description
    """
    
    if region == "NZ":
        return _nz_impact_description(scale_type, level)
    else:
        return _generic_impact_description(scale_type, level)


def _nz_impact_description(scale_type: str, level: str) -> str:
    """NZ-specific impact descriptions"""
    
    if scale_type == "R":
        descriptions = {
            'quiet': "HF communications across NZ should be fine.",
            'minor': "Brief HF dropouts possible on sunlit paths; most NZ circuits OK.",
            'moderate': "Short HF disruptions likely, mainly on sunlit side; GNSS may see minor effects.",
            'strong': "Heightened risk of HF and GNSS disruption across NZ, especially midday paths.",
            'severe': "Significant HF and GNSS disruption likely across NZ and the Pacific.",
            'extreme': "Widespread HF blackout possible; major GNSS degradation likely.",
        }
    elif scale_type == "S":
        descriptions = {
            'quiet': "Radiation environment normal over NZ.",
            'minor': "Slightly elevated radiation; minimal operational impact.",
            'moderate': "Elevated radiation — minor impacts; commercial flights OK, polar routes more affected.",
            'strong': "High radiation levels; monitor aviation and space assets in our region.",
            'severe': "Very high radiation risk for polar operations; protect space assets.",
            'extreme': "Extreme radiation storm — restrict high-latitude ops; critical space asset protection required.",
        }
    else:  # G scale
        descriptions = {
            'quiet': "Geomagnetic field quiet; GNSS is stable across NZ.",
            'minor': "Field slightly unsettled — small GNSS accuracy dips possible; slim aurora chance in Southland.",
            'moderate': "Active conditions — GNSS accuracy can degrade at times; aurora possible in deep south.",
            'strong': "Storm conditions — GNSS accuracy degradation likely; good aurora odds in southern regions.",
            'severe': "Severe storm — GNSS, HF, and power systems may be impacted; widespread aurora possible.",
            'extreme': "Extreme storm — major GNSS/HF disruption; power grid impacts possible; aurora likely visible across much of NZ.",
        }
    
    return descriptions.get(level, "Impact description not available.")


def _generic_impact_description(scale_type: str, level: str) -> str:
    """Generic impact descriptions (not region-specific)"""
    
    if scale_type == "R":
        descriptions = {
            'quiet': "No radio blackout conditions.",
            'minor': "Weak HF radio degradation on sunlit side.",
            'moderate': "Limited HF radio blackout; some loss of radio contact.",
            'strong': "Wide-area HF radio blackout; loss of radio contact for about an hour.",
            'severe': "HF radio blackout on most of sunlit side; loss of radio contact for one to two hours.",
            'extreme': "Complete HF radio blackout on entire sunlit side; no radio contact for several hours.",
        }
    elif scale_type == "S":
        descriptions = {
            'quiet': "No solar radiation storm.",
            'minor': "Minor impacts on polar operations.",
            'moderate': "Small effects on HF at polar regions; passengers and crew at high latitudes may receive low-level radiation exposure.",
            'strong': "Degraded HF at polar regions; increased radiation hazard for passengers and crew.",
            'severe': "HF blackout at polar regions; radiation hazard avoidance recommended.",
            'extreme': "No HF at polar regions; high radiation hazard; satellite operations affected.",
        }
    else:  # G scale
        descriptions = {
            'quiet': "No geomagnetic storm.",
            'minor': "Weak power grid fluctuations; minor impacts on satellite operations.",
            'moderate': "High-latitude power systems may experience voltage alarms; spacecraft charging may occur.",
            'strong': "Power systems: voltage corrections required; spacecraft: surface charging and tracking problems.",
            'severe': "Power systems: widespread voltage control problems; spacecraft: surface charging and tracking problems, corrections required.",
            'extreme': "Power systems: widespread blackouts possible; spacecraft: extensive surface charging, tracking, orientation problems.",
        }
    
    return descriptions.get(level, "Impact description not available.")
