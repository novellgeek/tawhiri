"""
Space Weather Constants

All thresholds, URLs, and configuration constants for the space weather module.
"""

# ========== NOAA Scale Thresholds ==========

# R-Scale (Radio Blackout) - X-ray flux thresholds (W/m²)
R_SCALE_THRESHOLDS = {
    'R5': 2e-3,    # X20+ flares - Extreme
    'R4': 1e-3,    # X10-X19 flares - Severe
    'R3': 1e-4,    # X1-X9 flares - Strong
    'R2': 5e-5,    # M5-M9 flares - Moderate
    'R1': 1e-5,    # M1-M4 flares - Minor
}

# S-Scale (Solar Radiation Storm) - Proton flux thresholds (pfu, >10 MeV)
S_SCALE_THRESHOLDS = {
    'S5': 1e5,     # >=100,000 pfu - Extreme
    'S4': 1e4,     # 10,000-99,999 pfu - Severe
    'S3': 1e3,     # 1,000-9,999 pfu - Strong
    'S2': 1e2,     # 100-999 pfu - Moderate
    'S1': 10,      # 10-99 pfu - Minor
}

# G-Scale (Geomagnetic Storm) - Kp index thresholds
G_SCALE_THRESHOLDS = {
    'G5': 9,       # Kp >= 9 - Extreme
    'G4': 8,       # Kp >= 8 - Severe
    'G3': 7,       # Kp >= 7 - Strong
    'G2': 6,       # Kp >= 6 - Moderate
    'G1': 5,       # Kp >= 5 - Minor
}

# Severity labels mapping
SEVERITY_LABELS = {
    'R5': 'extreme', 'S5': 'extreme', 'G5': 'extreme',
    'R4': 'severe',  'S4': 'severe',  'G4': 'severe',
    'R3': 'strong',  'S3': 'strong',  'G3': 'strong',
    'R2': 'moderate','S2': 'moderate','G2': 'moderate',
    'R1': 'minor',   'S1': 'minor',   'G1': 'minor',
    'R0': 'quiet',   'S0': 'quiet',   'G0': 'quiet',
}

# ========== NOAA API Endpoints ==========

NOAA_URLS = {
    'xray_7day': 'https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json',
    'proton_7day': 'https://services.swpc.noaa.gov/json/goes/primary/integral-protons-plot-7-day.json',
    'kp_3day': 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json',
    'discussion': 'https://services.swpc.noaa.gov/text/3-day-forecast.txt',
    'alerts': 'https://services.swpc.noaa.gov/products/alerts.json',
}

# ========== BOM API Endpoints ==========

BOM_URLS = {
    'aurora': 'https://sws-data.sws.bom.gov.au/api/v1/get-aurora-outlook',
}

# ========== Color Schemes ==========

# Severity color mapping (for UI alerts)
SEVERITY_COLORS = {
    'quiet': '#E8F5E9',      # Light green
    'minor': '#FFF9C4',      # Light yellow
    'moderate': '#FFE0B2',   # Light orange
    'strong': '#FFCCBC',     # Light red-orange
    'severe': '#FFCDD2',     # Light red
    'extreme': '#F8BBD0',    # Light pink-red
}

# High contrast color scheme (for accessibility)
SEVERITY_COLORS_HIGH_CONTRAST = {
    'quiet': '#FFFFFF',      # White
    'minor': '#FFFF00',      # Bright yellow
    'moderate': '#FFA500',   # Orange
    'strong': '#FF6600',     # Dark orange
    'severe': '#FF0000',     # Red
    'extreme': '#8B0000',    # Dark red
}

# Chart colors
CHART_COLORS = {
    'xray': '#E74C3C',       # Red
    'proton': '#3498DB',     # Blue
    'kp': '#2ECC71',         # Green
    'grid': '#CCCCCC',       # Light gray
    'background': '#FFFFFF', # White
}

# ========== Physical Constants ==========

# Earth radius (km)
EARTH_RADIUS_KM = 6371.0

# ========== Cache Settings ==========

# Cache time-to-live in seconds (default: 10 minutes)
DEFAULT_CACHE_TTL = 600

# ========== User Agent ==========

USER_AGENT = "TAWHIRI-SpaceWeather/1.0 (NZDF)"

# ========== NZ-Specific Settings ==========

# NZ location for localized impacts
NZ_LOCATION = {
    'name': 'Palmerston North, NZ',
    'latitude': -40.3568,
    'longitude': 175.6108,
}
