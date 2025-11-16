# Globe Sidebar Module - Comprehensive Code Review

**Reviewed:** November 16, 2025  
**File:** globe_sidebar_module.py (1,445 lines)  
**Module:** TAWHIRI 3D Orbital Visualization  
**Overall Assessment:** Solid production code with critical path issues for offline/secure deployment

---

## 🔴 CRITICAL ISSUES (Fix Before Offline Deployment)

### 1. **Hardcoded Windows Paths - Multiple Locations**
**Lines 45-56:** All file paths are hardcoded for a specific Windows user.

```python
# Line 45-46: Texture presets
"Blue Marble (day, 8K JPG)": r"C:\Users\Standalone1\Desktop\Space_tactical_Dashboard\earth\land_ocean_ice_8192.jpg",

# Line 50: TLE file
DEFAULT_TLE_FILE_PATH = r"C:\Users\Standalone1\Desktop\Space_tactical_Dashboard\data\tle-single.txt"

# Line 52: Metadata
SAT_METADATA_PATH = r"C:\Users\Standalone1\Desktop\Space_tactical_Dashboard\data\3d\sat_metadata.csv"

# Line 55: Preferences
PREFERENCES_DIR = r"C:\Users\Standalone1\Desktop\Space_Tactical_Dashboard\data\3d"
```

**CRITICAL ISSUE:** 
- Won't work for any other user
- Won't work on Linux servers (NZDF likely uses Linux for secure systems)
- Case inconsistency: `Space_tactical_Dashboard` vs `Space_Tactical_Dashboard`
- Exposes username/directory structure

**FIX - Use Configuration File:**

```python
import pathlib
import json

# At module top, after imports
CONFIG_FILE = pathlib.Path(__file__).parent / "config.json"

def load_config():
    """Load path configuration from config.json or use defaults"""
    default_config = {
        "data_dir": str(pathlib.Path.home() / "tawhiri_data"),
        "earth_textures_dir": str(pathlib.Path.home() / "tawhiri_data" / "earth"),
        "tle_file": str(pathlib.Path.home() / "tawhiri_data" / "tle-single.txt"),
        "sat_metadata": str(pathlib.Path.home() / "tawhiri_data" / "3d" / "sat_metadata.csv"),
        "preferences_dir": str(pathlib.Path.home() / "tawhiri_data" / "3d"),
    }
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            user_config = json.load(f)
            default_config.update(user_config)
    
    return default_config

CONFIG = load_config()

# Then use throughout:
DEFAULT_TLE_FILE_PATH = CONFIG["tle_file"]
SAT_METADATA_PATH = CONFIG["sat_metadata"]
PREFERENCES_DIR = CONFIG["preferences_dir"]

TEXTURE_PRESETS = {
    "Blue Marble (day, 8K JPG)": str(pathlib.Path(CONFIG["earth_textures_dir"]) / "land_ocean_ice_8192.jpg"),
    "Natural Earth II (8K raster)": str(pathlib.Path(CONFIG["earth_textures_dir"]) / "NE2_8192.jpg"),
}
```

**Deployment config.json for NZDF:**
```json
{
  "data_dir": "/opt/tawhiri/data",
  "earth_textures_dir": "/opt/tawhiri/data/earth",
  "tle_file": "/opt/tawhiri/data/tle-single.txt",
  "sat_metadata": "/opt/tawhiri/data/3d/sat_metadata.csv",
  "preferences_dir": "/opt/tawhiri/data/3d"
}
```

---

### 2. **External Data Dependencies - Skyfield**
**Line 34:** Skyfield loads astronomical data from the internet by default.

```python
from skyfield.api import EarthSatellite, load
```

**PROBLEM:** The `load()` function downloads ephemeris files from the internet:
- `de421.bsp` (planetary positions)
- `finals2000A.all` (Earth orientation parameters)

This will **FAIL in air-gapped secure environments** (which NZDF definitely uses).

**FIX - Pre-cache Skyfield Data:**

```python
import os
from skyfield.api import Loader

# Use local data directory instead of downloading
SKYFIELD_DATA_DIR = os.path.join(CONFIG["data_dir"], "skyfield_cache")
os.makedirs(SKYFIELD_DATA_DIR, exist_ok=True)

# Create loader pointing to local cache
ts_loader = Loader(SKYFIELD_DATA_DIR)

# In your code, replace 'load' with 'ts_loader'
ts = ts_loader.timescale()
eph = ts_loader('de421.bsp')  # Must be pre-downloaded and placed in cache dir
```

**Deployment Instructions:**
```bash
# On internet-connected machine, download required files:
python3 -c "
from skyfield.api import Loader
loader = Loader('./skyfield_cache')
loader.timescale()
loader('de421.bsp')
"

# Copy ./skyfield_cache/ to air-gapped system at /opt/tawhiri/data/skyfield_cache/
```

---

### 3. **Missing Error Handling for File Operations**
Throughout the code, file operations assume files exist:

```python
# Line 179 - No check if file exists
with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    lines = [L.strip() for L in f if L.strip()]

# Line 1357 - Check exists but doesn't handle gracefully
if not earth_image_path or not os.path.isfile(earth_image_path):
    st.warning("Selected day texture not found; using default surface.")
```

**FIX - Defensive File Access:**

```python
def read_multi_epoch_tle_file(filepath: str):
    """Read TLE file with proper error handling"""
    if not os.path.isfile(filepath):
        st.error(f"TLE file not found: {filepath}")
        st.info("Please check your configuration and ensure data files are present.")
        return {}
    
    try:
        tles = {}
        epoch_pattern = re.compile(r"^1\s+\S+\s+(\d{5}\.\d+)")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = [L.strip() for L in f if L.strip()]
        
        # ... rest of parsing logic
        
    except PermissionError:
        st.error(f"Permission denied reading: {filepath}")
        return {}
    except Exception as e:
        st.error(f"Error reading TLE file: {e}")
        return {}
```

---

### 4. **Inconsistent Path Casing**
**Lines 50, 52, 55:** Mix of `Space_tactical_Dashboard` and `Space_Tactical_Dashboard`

```python
r"C:\Users\Standalone1\Desktop\Space_tactical_Dashboard\data\tle-single.txt"  # Line 50
r"C:\Users\Standalone1\Desktop\Space_Tactical_Dashboard\data\3d"              # Line 55
```

This **will cause file-not-found errors** if the actual directory doesn't match exactly.

**Windows is case-insensitive but Linux is NOT** - this will break on Linux systems.

---

## 🟠 HIGH PRIORITY (Before Production Hardening)

### 5. **No Logging System**
Production code in a tactical environment needs proper logging for debugging and audit trails.

**ADD:**
```python
import logging

logger = logging.getLogger(__name__)

# In deployment, configure to file
logging.basicConfig(
    filename='/var/log/tawhiri/globe_module.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Then use throughout:
logger.info(f"Loaded {len(chosen_sats)} satellites for visualization")
logger.warning(f"TLE file not found: {filepath}")
logger.error(f"Failed to parse TLE epoch: {e}", exc_info=True)
```

---

### 6. **Broad Exception Catching**
Multiple bare `except Exception` blocks hide specific errors.

```python
# Line 1434-1437
try:
    save_last_session(collect_current_settings())
except Exception:
    pass  # Silent failure - bad for debugging
```

**Better:**
```python
try:
    save_last_session(collect_current_settings())
except IOError as e:
    logger.warning(f"Could not save session: {e}")
except Exception as e:
    logger.error(f"Unexpected error saving session: {e}", exc_info=True)
```

---

### 7. **Magic Numbers Throughout**
Constants are scattered and sometimes duplicated:

```python
# Line 58-60
EARTH_RADIUS_KM = 6371.0
GEO_ALTITUDE_KM = 35786.0
GEOSTATIONARY_RADIUS_KM = EARTH_RADIUS_KM + GEO_ALTITUDE_KM

# But then line 110 hardcodes again:
R = EARTH_RADIUS_KM  # Okay, uses constant

# Line 122: Magic number
bearings = np.linspace(0, 2*np.pi, npts, endpoint=True)  # npts default 240 - why?
```

**Centralize Constants:**
```python
# ========== Physical Constants ==========
EARTH_RADIUS_KM = 6371.0           # WGS84 mean radius
GEO_ALTITUDE_KM = 35786.0          # Geostationary altitude
GEOSTATIONARY_RADIUS_KM = EARTH_RADIUS_KM + GEO_ALTITUDE_KM

# ========== Visualization Defaults ==========
DEFAULT_GEODESIC_POINTS = 240      # Circle resolution
DEFAULT_ORBIT_POINTS = 1000        # Orbit trace resolution
DEFAULT_MESH_RES_U = 256           # Globe mesh U-resolution
DEFAULT_MESH_RES_V = 128           # Globe mesh V-resolution

# ========== Dateline Wrapping ==========
DATELINE_GAP_THRESHOLD = 120.0     # Degrees, for split detection
```

---

### 8. **Duplicate Function Definitions (Potential)**
The comment block at top mentions multiple fixes, suggesting this file has been patched extensively. Check for:
- Duplicate helper functions
- Dead code paths
- Commented-out alternatives

**Run a deduplication check:**
```bash
# Look for duplicate function definitions
grep -n "^def " globe_sidebar_module.py | sort -k2
```

---

### 9. **No Type Hints on Most Functions**
Only a few functions have type hints. This makes maintenance harder.

**Before:**
```python
def _wrap180(lon):
    lon = (np.asarray(lon) + 180.0) % 360.0 - 180.0
    # ...
```

**After:**
```python
def _wrap180(lon: np.ndarray | float) -> np.ndarray | float:
    """
    Wrap longitude to [-180, 180] range.
    
    Args:
        lon: Longitude in degrees (scalar or array)
        
    Returns:
        Wrapped longitude in range [-180, 180]
    """
    lon = (np.asarray(lon) + 180.0) % 360.0 - 180.0
    # ...
```

---

### 10. **Metadata File Loading Not Cached**
If `SAT_METADATA_PATH` is loaded in the render loop, it's being read from disk repeatedly.

**Check if this function exists and is cached:**
```python
@st.cache_data
def load_sat_metadata(filepath: str) -> dict:
    """Load satellite metadata from CSV with caching"""
    if not os.path.isfile(filepath):
        logger.warning(f"Metadata file not found: {filepath}")
        return {}
    
    try:
        import csv
        metadata = {}
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metadata[row['name']] = {
                    'color': row.get('color', DEFAULT_COL_OTHER),
                    'category': row.get('category', 'OTHER'),
                    'norad_id': row.get('norad_id', ''),
                }
        return metadata
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return {}
```

---

## 🟡 MEDIUM PRIORITY (Good to Address)

### 11. **Code Organization**
At 1,445 lines, consider splitting:

```
tawhiri/
└── orbit_viz/
    ├── __init__.py
    ├── app.py                    # Main run() function
    ├── tle_parser.py             # TLE reading/parsing
    ├── orbital_math.py           # Coordinate transforms, coverage calcs
    ├── sun_terminator.py         # Solar position, day/night
    ├── plotting_3d.py            # 3D orbit visualization
    ├── plotting_2d.py            # 2D ground track visualization
    ├── presets.py                # Save/load preset management
    ├── constants.py              # All constants in one place
    └── config.py                 # Configuration loading
```

---

### 12. **Inconsistent Naming Conventions**
Mix of styles:

```python
EARTH_RADIUS_KM        # SCREAMING_SNAKE_CASE (constants) ✓
DEFAULT_TLE_FILE_PATH  # SCREAMING_SNAKE_CASE ✓
mesh_res_u             # snake_case (variables) ✓
USE_CATEGORY_COLOURS   # SCREAMING_SNAKE_CASE but feature flag
```

Feature flags should be distinguished:
```python
# ========== Feature Flags ==========
FEATURE_CATEGORY_COLORS = True
FEATURE_HIGHLIGHT_IDS = True
FEATURE_COMPACT_LEGEND = False
```

---

### 13. **Comment Quality**
Some comments are good, others are cryptic:

```python
# Line 20: "Add 2d animation, single satellite only"
# Line 21: "fixed satellite colours based on CSV metadata file"
# Line 23: "Added TLE update functionality"
```

These look like **changelog entries** rather than code documentation. Move to a CHANGELOG.md file.

**Better inline comments:**
```python
# Ensure TLE epochs are sorted chronologically for slider consistency
epochs.sort(key=lambda x: x['epoch_val'])

# Split ground tracks at dateline to prevent wrap-around artifacts
segments = _split_on_dateline(lons, lats)
```

---

### 14. **Potential Performance Issues**
**Line 122:** Creating 240-point geodesic circles for every footprint

If drawing many footprints, this could be optimized:
```python
# Cache common geodesic circle templates
@st.cache_data
def get_geodesic_template(npts: int = 240):
    """Return pre-computed unit circle for geodesic transformations"""
    return np.linspace(0, 2*np.pi, npts, endpoint=True)
```

---

### 15. **No Input Validation**
Functions accept inputs without validation:

```python
def coverage_radius_deg(alt_km: float, min_elev_deg: float = 0.0) -> float:
    R = EARTH_RADIUS_KM
    h = max(0.0, float(alt_km))  # Clamps negative to 0, good
    e = np.radians(min_elev_deg)  # But what if min_elev_deg > 90?
```

**Add validation:**
```python
def coverage_radius_deg(alt_km: float, min_elev_deg: float = 0.0) -> float:
    """
    Calculate ground coverage radius for satellite at given altitude.
    
    Args:
        alt_km: Altitude above Earth surface in km (must be >= 0)
        min_elev_deg: Minimum elevation angle in degrees (0-90)
        
    Returns:
        Coverage radius in degrees
        
    Raises:
        ValueError: If inputs are out of valid range
    """
    if alt_km < 0:
        raise ValueError(f"Altitude must be >= 0, got {alt_km}")
    if not 0 <= min_elev_deg <= 90:
        raise ValueError(f"Elevation must be 0-90°, got {min_elev_deg}")
    
    # ... rest of calculation
```

---

### 16. **Session State Key Naming**
Keys like `"globe_show_apogee"` are consistent, but could benefit from namespacing:

```python
# Current:
st.session_state["globe_show_apogee"]
st.session_state["gt_anim_enable"]

# Better - use a namespace class:
class SessionKeys:
    SHOW_APOGEE = "orbit_viz.show_apogee"
    ANIM_ENABLE = "orbit_viz.gt_anim_enable"
    FRAME_TYPE = "orbit_viz.frame"
    # etc.

# Usage:
st.session_state[SessionKeys.SHOW_APOGEE]
```

This prevents key collisions if you integrate with other modules.

---

## 🟢 LOW PRIORITY (Nice to Have)

### 17. **Add Unit Tests**
Critical for orbital mechanics calculations:

```python
# tests/test_orbital_math.py
import pytest
import numpy as np
from orbit_viz.orbital_math import _wrap180, coverage_radius_deg

def test_wrap180_single():
    assert _wrap180(190) == -170
    assert _wrap180(-190) == 170
    assert _wrap180(0) == 0

def test_wrap180_array():
    result = _wrap180(np.array([0, 90, 180, 270, 360]))
    expected = np.array([0, 90, -180, -90, 0])
    np.testing.assert_array_almost_equal(result, expected)

def test_coverage_radius_geo():
    # GEO satellite at 35,786 km should cover ~81° radius
    radius = coverage_radius_deg(35786.0, min_elev_deg=0.0)
    assert 80.0 < radius < 82.0

def test_coverage_radius_leo():
    # LEO at 550km should cover ~23° radius
    radius = coverage_radius_deg(550.0, min_elev_deg=0.0)
    assert 22.0 < radius < 24.0
```

---

### 18. **Documentation**
Add module-level docstring:

```python
"""
TAWHIRI Orbit Visualization Module
==================================

Provides 3D and 2D visualization of satellite orbits using TLE data.

Features:
- 3D orbit traces in ECI/ECEF reference frames
- 2D ground track projections with day/night terminator
- Perigee/apogee/node markers
- GEO station-keeping box visualization
- Animated ground tracks
- Footprint coverage rings
- Multiple Earth texture options

Usage:
    from tawhiri.orbit_viz import run
    run()

Configuration:
    Edit config.json to specify data file paths for your environment.

Dependencies:
    - Skyfield (orbital propagation)
    - Plotly (visualization)
    - NumPy (numerical operations)
    - Streamlit (UI framework)
"""
```

---

### 19. **Accessibility Improvements**
For tactical displays that may be used in various lighting conditions:

```python
# Add color blindness safe palettes
COLORBLIND_SAFE_PALETTE = {
    'CN_RU': '#D55E00',    # Vermillion (instead of red)
    'COMM': '#009E73',     # Bluish green (instead of green)
    'OTHER': '#0072B2',    # Blue
    'HIGHLIGHT': '#F0E442' # Yellow
}

# Add high-contrast mode
if st.session_state.get("high_contrast_mode", False):
    ORBIT_COLORS = COLORBLIND_SAFE_PALETTE
else:
    ORBIT_COLORS = DEFAULT_COLORS
```

---

### 20. **Performance Profiling Hooks**
For debugging slow renders:

```python
import time

def timed_operation(operation_name: str):
    """Decorator to log operation timing"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.info(f"{operation_name} took {elapsed:.3f}s")
            return result
        return wrapper
    return decorator

@timed_operation("TLE parsing")
def read_multi_epoch_tle_file(filepath: str):
    # ... existing code
```

---

## 🎯 Offline/Secure Deployment Checklist

For NZDF air-gapped deployment, you MUST address:

- [ ] Remove all hardcoded Windows paths
- [ ] Create config.json for flexible path configuration
- [ ] Pre-download Skyfield ephemeris data
- [ ] Configure Skyfield to use local cache directory
- [ ] Test on Linux (NZDF likely uses RHEL/CentOS)
- [ ] Add comprehensive error handling for missing files
- [ ] Implement logging to file (not just Streamlit warnings)
- [ ] Create deployment documentation
- [ ] Package Earth texture files (8K images are ~50MB each)
- [ ] Package TLE data files
- [ ] Create installation script for offline deployment

---

## 📋 Recommended Deployment Structure

```
/opt/tawhiri/
├── bin/
│   └── start_orbit_viz.sh
├── config/
│   └── config.json
├── data/
│   ├── earth/
│   │   ├── land_ocean_ice_8192.jpg
│   │   └── NE2_8192.jpg
│   ├── skyfield_cache/
│   │   ├── de421.bsp
│   │   └── finals2000A.all
│   ├── 3d/
│   │   ├── sat_metadata.csv
│   │   └── __last__.json
│   └── tle-single.txt
├── logs/
│   └── orbit_viz.log
└── src/
    └── orbit_viz/
        ├── globe_sidebar_module.py
        └── config.py
```

**config.json:**
```json
{
  "data_dir": "/opt/tawhiri/data",
  "earth_textures_dir": "/opt/tawhiri/data/earth",
  "tle_file": "/opt/tawhiri/data/tle-single.txt",
  "sat_metadata": "/opt/tawhiri/data/3d/sat_metadata.csv",
  "preferences_dir": "/opt/tawhiri/data/3d",
  "skyfield_cache": "/opt/tawhiri/data/skyfield_cache",
  "log_file": "/opt/tawhiri/logs/orbit_viz.log"
}
```

---

## 🔧 Quick Wins (Do These First)

### Week 1: Critical Path
1. Create config.json system to replace hardcoded paths
2. Fix Skyfield to use local cache
3. Add file existence checks with proper error messages
4. Test on a Linux VM

### Week 2: Hardening
5. Add logging framework
6. Improve exception handling specificity
7. Add input validation to key functions
8. Create deployment documentation

### Week 3: Quality
9. Add type hints to public functions
10. Extract magic numbers to constants
11. Write unit tests for orbital calculations
12. Test full offline deployment scenario

---

## ✅ What You're Doing Right

Strong points in this module:

1. ✨ **Comprehensive features** - 3D/2D, animations, coverage, presets
2. ✨ **Session state management** - Clean handling with `ss_default()`
3. ✨ **Preset save/load** - Good UX for operational users
4. ✨ **Edge case fixes documented** - The fix banners show attention to stability
5. ✨ **Skyfield integration** - Proper use of professional astrodynamics library
6. ✨ **Visual polish** - Terminator, textures, decluttering show attention to detail
7. ✨ **Metadata-driven colors** - CSV configuration is operator-friendly

---

## ⚠️ DEPLOYMENT BLOCKER

**The hardcoded paths and internet-dependent Skyfield loading are SHOWSTOPPERS for secure/offline deployment.**

You cannot deploy this to an air-gapped NZDF network without fixing these issues first. They're not just "nice to have" - they're deployment blockers.

Priority order:
1. Config file system (1-2 days work)
2. Skyfield offline cache (1 day work + testing)
3. File error handling (1 day work)
4. Linux testing (1 day)

Total estimated effort: 1 week to make this deployment-ready for secure environments.

---

## 📝 Summary

This is well-structured production code with excellent features, but it's currently **locked to a specific Windows development environment**. For NZDF tactical deployment, especially in secure/classified areas, you need to:

1. **Abstract away all file paths** using configuration
2. **Eliminate internet dependencies** by pre-caching Skyfield data
3. **Add defensive programming** for file operations
4. **Test on Linux** since that's what Defence uses

The visualization capabilities are impressive and exactly what operators need. The technical debt is primarily in deployment configuration, not in the core logic.

**Final Grade: B (Good technical implementation, needs deployment hardening)**

---

*Review prepared: 2025-11-16*  
*Reviewer: Claude (Sonnet 4.5)*  
*Context: TAWHIRI Space Domain Awareness Platform (NZDF)*
