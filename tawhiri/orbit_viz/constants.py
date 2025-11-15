"""
Orbit Visualization Constants

Physical constants, defaults, and configuration for orbit visualization.
"""

import pathlib

# ========== Physical Constants ==========

EARTH_RADIUS_KM = 6371.0           # WGS84 mean radius
GEO_ALTITUDE_KM = 35786.0          # Geostationary altitude above Earth surface
GEOSTATIONARY_RADIUS_KM = EARTH_RADIUS_KM + GEO_ALTITUDE_KM

# ========== Visualization Defaults ==========

DEFAULT_GEODESIC_POINTS = 240      # Points in geodesic circles (footprints)
DEFAULT_ORBIT_POINTS = 1000        # Points in orbit traces
DEFAULT_MESH_RES_U = 256           # Globe mesh U-resolution (medium)
DEFAULT_MESH_RES_V = 128           # Globe mesh V-resolution (medium)

# Mesh resolution presets
MESH_RESOLUTIONS = {
    "Low": (180, 90),
    "Medium": (256, 128),
    "High": (512, 256),
}

# ========== Dateline Handling ==========

DATELINE_GAP_THRESHOLD = 120.0     # Degrees, for detecting dateline crossings

# ========== Default Colors ==========

# Satellite category colors (can be overridden by metadata)
DEFAULT_COLORS = {
    'CN_RU': '#FF4D4D',      # Red - Chinese/Russian assets
    'COMM': '#2ECC71',       # Green - Commercial/Communications
    'OTHER': '#1E90FF',      # Blue - Other satellites
    'HIGHLIGHT': '#FFD700',  # Gold - Highlighted satellites
}

# Colorblind-safe alternative palette
COLORBLIND_SAFE_COLORS = {
    'CN_RU': '#D55E00',      # Vermillion
    'COMM': '#009E73',       # Bluish green
    'OTHER': '#0072B2',      # Blue
    'HIGHLIGHT': '#F0E442',  # Yellow
}

# ========== Feature Flags ==========

FEATURE_CATEGORY_COLORS = True     # Use category-based colors from metadata
FEATURE_HIGHLIGHT_IDS = True       # Support highlighting specific satellites
FEATURE_COMPACT_LEGEND = False     # Use compact legend layout

# ========== Default Settings ==========

# TODO: These will be loaded from config.json in production
# Kept here as fallbacks for development

DEFAULT_TLE_FILE = "tle-single.txt"
DEFAULT_SAT_METADATA_FILE = "sat_metadata.csv"

# ========== Globe Texture Presets ==========

# These are example paths - actual paths come from config
TEXTURE_PRESET_NAMES = [
    "Blue Marble (8K)",
    "Natural Earth II (8K)",
    "Black Marble (Night)",
]
