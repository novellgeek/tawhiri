# Migration Guide: Monolithic to Modular

## Overview

This guide walks you through migrating your existing monolithic files to the new modular structure.

**Estimated time:** 2-3 days for full migration  
**Difficulty:** Medium  
**Risk:** Low (incremental approach with fallbacks)

---

## Strategy: Incremental Migration with Dual Operation

You'll run BOTH versions side-by-side during migration:
1. Old monolithic files keep working
2. New modular version gets built piece by piece
3. Once confident, switch over and delete old files

---

## Phase 1: Setup (30 minutes)

### 1.1: Copy Template
```bash
# Copy this template to your project directory
cp -r tawhiri_modular_template /path/to/your/project/tawhiri

cd /path/to/your/project/tawhiri
```

### 1.2: Create config.json
```bash
# Copy example config
cp config.example.json config.json

# Edit with your actual paths
nano config.json
```

Example config.json for your environment:
```json
{
  "data_dir": "C:\\Users\\Standalone1\\Desktop\\Space_Tactical_Dashboard\\data",
  "space_weather": {
    "noaa_api_key": "",
    "bom_api_key": "YOUR_KEY_HERE",
    "cache_ttl_seconds": 600
  },
  "orbit_viz": {
    "earth_textures_dir": "C:\\Users\\Standalone1\\Desktop\\Space_tactical_Dashboard\\earth",
    "tle_file": "C:\\Users\\Standalone1\\Desktop\\Space_tactical_Dashboard\\data\\tle-single.txt",
    "sat_metadata": "C:\\Users\\Standalone1\\Desktop\\Space_tactical_Dashboard\\data\\3d\\sat_metadata.csv",
    "preferences_dir": "C:\\Users\\Standalone1\\Desktop\\Space_Tactical_Dashboard\\data\\3d",
    "skyfield_cache": "C:\\Users\\Standalone1\\Desktop\\Space_Tactical_Dashboard\\data\\skyfield_cache"
  },
  "logging": {
    "log_file": "C:\\Users\\Standalone1\\Desktop\\Space_Tactical_Dashboard\\logs\\tawhiri.log",
    "log_level": "INFO"
  }
}
```

### 1.3: Install Package
```bash
# Install in development mode (editable)
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

---

## Phase 2: Migrate Space Weather Module (Day 1)

### 2.1: Extract Constants (15 minutes)

**FROM:** `Space_weather_module.py`  
**TO:** `tawhiri/space_weather/constants.py`

Open your Space_weather_module.py and find all constants:
```python
# Look for these patterns:
R_SCALE_THRESHOLDS = {...}
NOAA_URLS = {...}
SEVERITY_COLORS = {...}
```

Copy them to `constants.py` (already has placeholders).

### 2.2: Extract Scale Functions (30 minutes)

**FROM:** `Space_weather_module.py`  
**TO:** `tawhiri/space_weather/scales.py`

Find these functions in your file:
```python
def r_scale(xray_flux_wm2): ...
def s_scale(proton_pfu_10mev): ...
def g_scale(kp_index): ...
def g_scale_from_kp(kp): ...  # Remove the duplicate!
```

**Already done!** The `scales.py` file has improved versions. Just verify they match your logic.

### 2.3: Extract Data Fetchers (30 minutes)

**FROM:** `Space_weather_module.py`  
**TO:** `tawhiri/space_weather/data_fetchers.py`

Find these functions:
```python
@st.cache_data(ttl=600, show_spinner=True)
def fetch_json(url, timeout=20): ...

@st.cache_data(ttl=600, show_spinner=True)
def fetch_text(url, timeout=20): ...
```

Copy to `data_fetchers.py` (already has basic versions).

### 2.4: Extract Utils (15 minutes)

**FROM:** `Space_weather_module.py`  
**TO:** `tawhiri/space_weather/utils.py`

Find utility functions:
```python
def clamp_float(x, default=0.0): ...
def last_updated(): ...
```

**Already done!** These are in `utils.py`.

### 2.5: Update Your Monolithic File to Import from Modules (30 minutes)

In `Space_weather_module.py`, add at the top:
```python
try:
    # Try new modular imports
    from tawhiri.space_weather.scales import r_scale, s_scale, g_scale
    from tawhiri.space_weather.constants import *
    from tawhiri.space_weather.data_fetchers import fetch_json, fetch_text
    from tawhiri.space_weather.utils import clamp_float, last_updated
    USING_MODULAR = True
except ImportError:
    # Fall back to local definitions
    USING_MODULAR = False
    # Keep your old function definitions as backup
    def r_scale(xray_flux_wm2):
        # ... old code
        pass
```

### 2.6: Test Side-by-Side

Run your app:
```bash
streamlit run Space_weather_module.py
```

It should work identically. Check logs to see if modular imports succeeded.

### 2.7: Extract Plotting (2 hours)

This is the biggest piece. Find all Plotly chart functions:
```python
def create_xray_chart(...): ...
def create_proton_chart(...): ...
def create_kp_chart(...): ...
```

Move them to `tawhiri/space_weather/plotting.py`.

Update imports in your monolithic file:
```python
from tawhiri.space_weather.plotting import create_xray_chart, create_proton_chart
```

Test again.

### 2.8: Extract PDF Export (1 hour)

Move PDF generation:
```python
def export_management_pdf(...): ...
```

To `tawhiri/space_weather/pdf_export.py`.

### 2.9: Migrate UI to app.py (2 hours)

Once everything else is extracted, copy your `run()` function to `tawhiri/space_weather/app.py`.

Update all imports to use modular versions.

Test the new module:
```bash
python -m tawhiri.space_weather.app
```

---

## Phase 3: Migrate Orbit Viz Module (Day 2)

### 3.1: Extract Constants (15 minutes)

**FROM:** `globe_sidebar_module.py`  
**TO:** `tawhiri/orbit_viz/constants.py`

Move constants:
```python
EARTH_RADIUS_KM = 6371.0
GEO_ALTITUDE_KM = 35786.0
DEFAULT_COLORS = {...}
```

Already in `constants.py` - verify they match.

### 3.2: Extract TLE Parser (1 hour)

**FROM:** `globe_sidebar_module.py`  
**TO:** `tawhiri/orbit_viz/tle_parser.py`

Move:
```python
def read_multi_epoch_tle_file(filepath): ...
```

### 3.3: Extract Orbital Math (1 hour)

**FROM:** `globe_sidebar_module.py`  
**TO:** `tawhiri/orbit_viz/orbital_math.py`

Move:
```python
def _wrap180(lon): ...
def _split_on_dateline(lons, lats, gap=120.0): ...
def coverage_radius_deg(alt_km, min_elev_deg=0.0): ...
def circle_geodesic(lat0_deg, lon0_deg, radius_deg, npts=240): ...
```

### 3.4: Extract Sun/Terminator (30 minutes)

**FROM:** `globe_sidebar_module.py`  
**TO:** `tawhiri/orbit_viz/sun_terminator.py`

Move:
```python
def _julian_day(dt): ...
def subsolar_latlon(dt): ...
def sun_direction_ecef(dt): ...
def make_terminator_layers(...): ...
```

### 3.5: Extract Plotting Functions (2 hours)

**FROM:** `globe_sidebar_module.py`  
**TO:** `tawhiri/orbit_viz/plotting_3d.py` and `plotting_2d.py`

Move 3D plotting:
```python
def plot_orbits(...): ...
```

Move 2D plotting:
```python
def plot_ground_2d(...): ...
def animate_groundtrack_2d(...): ...
```

### 3.6: Extract Presets (30 minutes)

**FROM:** `globe_sidebar_module.py`  
**TO:** `tawhiri/orbit_viz/presets.py`

Move preset management functions.

### 3.7: Update for Offline Operation (1 hour)

**CRITICAL:** Fix Skyfield for air-gapped deployment.

In `tawhiri/orbit_viz/app.py` or wherever you use Skyfield:

```python
from skyfield.api import Loader
from tawhiri.config import get_config

config = get_config()
skyfield_cache = config['orbit_viz']['skyfield_cache']

# Use local cache instead of downloading
loader = Loader(skyfield_cache)
ts = loader.timescale()

# Pre-download on internet-connected machine:
# python -c "from skyfield.api import Loader; l = Loader('./skyfield_cache'); l.timescale(); l('de421.bsp')"
```

### 3.8: Migrate UI to app.py (2 hours)

Copy `run()` function to `tawhiri/orbit_viz/app.py`.

Update imports.

Test:
```bash
python -m tawhiri.orbit_viz.app
```

---

## Phase 4: Write Tests (Day 3)

### 4.1: Test Scales (30 minutes)

Already done! See `tests/test_space_weather/test_scales.py`.

Run it:
```bash
pytest tests/test_space_weather/test_scales.py -v
```

### 4.2: Test Orbital Math (1 hour)

Create `tests/test_orbit_viz/test_orbital_math.py`:
```python
import pytest
import numpy as np
from tawhiri.orbit_viz.orbital_math import coverage_radius_deg, _wrap180

def test_wrap180():
    assert _wrap180(190) == -170
    assert _wrap180(-190) == 170

def test_coverage_geo():
    # GEO satellite should see ~81° radius
    radius = coverage_radius_deg(35786.0, 0.0)
    assert 80 < radius < 82

# Add more tests...
```

### 4.3: Test Data Fetchers (30 minutes)

Create mock tests for API calls (optional but recommended).

---

## Phase 5: Cleanup & Deployment (Day 3 afternoon)

### 5.1: Delete Old Files

Once confident everything works:
```bash
# Backup first!
mkdir backup
cp Space_weather_module.py backup/
cp globe_sidebar_module.py backup/

# Then delete (or keep as reference)
# rm Space_weather_module.py
# rm globe_sidebar_module.py
```

### 5.2: Update Main Dashboard

If you have a main dashboard that imports modules:
```python
# Old:
from Space_weather_module import run as run_spaceweather

# New:
from tawhiri.space_weather import run as run_spaceweather
```

### 5.3: Create Deployment Package

For NZDF secure deployment:
```bash
# Package everything
tar -czf tawhiri_deploy.tar.gz \
    tawhiri/ \
    config.json \
    requirements.txt \
    setup.py \
    data/

# Transfer to secure system and install
```

---

## Troubleshooting

### Import Errors
```python
# If you get "No module named 'tawhiri'"
# Make sure you ran: pip install -e .
# Or add to Python path:
import sys
sys.path.insert(0, '/path/to/tawhiri')
```

### Config Not Found
```python
# Set environment variable
export TAWHIRI_CONFIG=/path/to/config.json

# Or pass explicitly
from tawhiri.config import load_config
config = load_config("/path/to/config.json")
```

### Streamlit Caching Issues
```python
# Clear Streamlit cache
streamlit cache clear

# Or in code:
st.cache_data.clear()
```

---

## Verification Checklist

Before considering migration complete:

- [ ] All constants extracted to constants.py
- [ ] All scale functions tested and working
- [ ] Data fetching works with new modules
- [ ] Plotting functions render correctly
- [ ] PDF export generates valid files
- [ ] Orbit visualization 3D works
- [ ] Orbit visualization 2D works
- [ ] Skyfield works offline (critical for NZDF)
- [ ] Tests pass: `pytest tests/`
- [ ] No hardcoded paths remain
- [ ] Config.json works on different machines
- [ ] Logging writes to correct location
- [ ] Old monolithic files backed up
- [ ] Documentation updated

---

## Next Steps After Migration

1. **Add more tests** - Aim for 80%+ coverage
2. **Set up CI/CD** - Automated testing on commits
3. **Performance profiling** - Find and fix bottlenecks
4. **User documentation** - Operational guides for NZDF users
5. **Deployment automation** - Scripts for secure environment deployment

---

## Getting Help

If stuck during migration:

1. Check the logs: `tail -f logs/tawhiri.log`
2. Run tests to isolate issues: `pytest tests/ -v`
3. Compare with backup versions
4. Verify config.json paths are correct

---

**Good luck with the migration! Take it slow, test frequently, and don't delete the old files until you're 100% confident.**
