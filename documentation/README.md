# TAWHIRI Space Domain Awareness Platform
## Modular Architecture Template

This template provides a clean, modular structure for the TAWHIRI platform, making it easier to:
- Test individual components
- Make changes without breaking unrelated functionality
- Deploy to secure/offline environments
- Collaborate with multiple developers

---

## Project Structure

```
tawhiri/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.example.json                # Example configuration (copy to config.json)
├── setup.py                           # Package installation
│
├── tawhiri/                           # Main package
│   ├── __init__.py
│   ├── config.py                      # Configuration loader
│   │
│   ├── common/                        # Shared utilities
│   │   ├── __init__.py
│   │   ├── logging_setup.py           # Logging configuration
│   │   └── file_utils.py              # File operation helpers
│   │
│   ├── space_weather/                 # Space Weather module
│   │   ├── __init__.py
│   │   ├── app.py                     # Main Streamlit UI (run function)
│   │   ├── constants.py               # Thresholds, URLs, colors
│   │   ├── scales.py                  # R/S/G scale calculations
│   │   ├── data_fetchers.py           # API calls with caching
│   │   ├── nz_translations.py         # NZ-specific text
│   │   ├── plotting.py                # Chart generation
│   │   ├── pdf_export.py              # PDF report generation
│   │   └── utils.py                   # Helper functions
│   │
│   └── orbit_viz/                     # Orbit Visualization module
│       ├── __init__.py
│       ├── app.py                     # Main Streamlit UI (run function)
│       ├── constants.py               # Physical constants
│       ├── tle_parser.py              # TLE file parsing
│       ├── orbital_math.py            # Coordinate transforms, coverage
│       ├── sun_terminator.py          # Solar position calculations
│       ├── plotting_3d.py             # 3D orbit plots
│       ├── plotting_2d.py             # 2D ground track plots
│       └── presets.py                 # Preset save/load
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_space_weather/
│   │   ├── __init__.py
│   │   ├── test_scales.py
│   │   ├── test_data_fetchers.py
│   │   └── test_utils.py
│   └── test_orbit_viz/
│       ├── __init__.py
│       ├── test_orbital_math.py
│       └── test_tle_parser.py
│
├── data/                              # Data directory (not in version control)
│   ├── earth/                         # Earth texture images
│   ├── skyfield_cache/                # Skyfield ephemeris data
│   ├── 3d/                            # Orbit viz preferences
│   │   └── sat_metadata.csv
│   └── tle-single.txt
│
└── logs/                              # Log files (not in version control)
    └── tawhiri.log
```

---

## Quick Start

### 1. Installation

```bash
# Clone or copy this template
cd tawhiri_modular_template

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example config
cp config.example.json config.json

# Edit config.json with your paths
nano config.json
```

### 3. Run Space Weather Module

```bash
# Option A: As standalone app
python -m tawhiri.space_weather.app

# Option B: Import in your own script
python
>>> from tawhiri.space_weather import run
>>> run()
```

### 4. Run Orbit Visualization Module

```bash
# Option A: As standalone app
python -m tawhiri.orbit_viz.app

# Option B: Import in your own script
python
>>> from tawhiri.orbit_viz import run
>>> run()
```

### 5. Run Tests

```bash
# Run all tests
pytest tests/

# Run specific module tests
pytest tests/test_space_weather/

# Run with coverage
pytest --cov=tawhiri tests/
```

---

## Migration from Monolithic Files

### Step-by-Step Migration Guide

**Week 1: Setup & Constants**
1. Copy this template to your project
2. Move constants from monolithic files to `constants.py` modules
3. Update imports in original files to use new constants
4. Test that everything still works

**Week 2: Extract Pure Functions**
1. Move scale calculation functions to `scales.py`
2. Move data fetching to `data_fetchers.py`
3. Write tests for extracted functions
4. Verify original functionality unchanged

**Week 3: Extract Plotting**
1. Move chart generation to `plotting.py` modules
2. Test chart rendering independently
3. Update main app to import from new modules

**Week 4: Finalize**
1. Move remaining UI code to `app.py`
2. Delete old monolithic files
3. Update deployment documentation

---

## Configuration

The `config.json` file controls all file paths and settings:

```json
{
  "data_dir": "/opt/tawhiri/data",
  "earth_textures_dir": "/opt/tawhiri/data/earth",
  "tle_file": "/opt/tawhiri/data/tle-single.txt",
  "sat_metadata": "/opt/tawhiri/data/3d/sat_metadata.csv",
  "preferences_dir": "/opt/tawhiri/data/3d",
  "skyfield_cache": "/opt/tawhiri/data/skyfield_cache",
  "log_file": "/opt/tawhiri/logs/tawhiri.log",
  "log_level": "INFO"
}
```

---

## Testing Philosophy

Each module should be independently testable:

```python
# Test scales without running Streamlit
from tawhiri.space_weather.scales import r_scale
assert r_scale(1e-5) == ("R1", "minor")

# Test data fetching with mocked requests
from tawhiri.space_weather.data_fetchers import fetch_json
# ... mock and test

# Test plotting with known data
from tawhiri.space_weather.plotting import create_xray_chart
# ... test chart generation
```

---

## Deployment

### For Development (Windows/Mac/Linux)

```bash
pip install -e .
python -m tawhiri.space_weather.app
```

### For NZDF Secure Environment (Air-Gapped Linux)

1. **On internet-connected machine:**
   ```bash
   # Download dependencies
   pip download -r requirements.txt -d ./packages
   
   # Download Skyfield data
   python scripts/download_skyfield_data.py
   
   # Package everything
   tar -czf tawhiri_deploy.tar.gz tawhiri/ data/ config.json packages/
   ```

2. **On secure machine:**
   ```bash
   # Extract
   tar -xzf tawhiri_deploy.tar.gz
   
   # Install offline
   pip install --no-index --find-links=./packages -e .
   
   # Run
   python -m tawhiri.space_weather.app
   ```

---

## Benefits of This Structure

✅ **Isolation** - Changes to plotting don't affect data fetching  
✅ **Testability** - Each module can be tested independently  
✅ **Maintainability** - Easy to find and fix issues  
✅ **Collaboration** - Multiple developers can work on different modules  
✅ **Deployment** - Configuration-driven, works on any OS  
✅ **Security** - No hardcoded paths, offline-capable  

---

## Contributing

When adding new functionality:

1. Determine which module it belongs to
2. Add function to appropriate module file
3. Write tests in corresponding test file
4. Update module's `__init__.py` if exposing new functions
5. Document in module docstring

---

## Support

For TAWHIRI-specific questions:
- Internal NZDF documentation
- Project maintainer contact

For technical issues:
- Check logs in `logs/tawhiri.log`
- Run tests: `pytest tests/ -v`
- Review configuration: `config.json`

---

**Version:** 1.0  
**Last Updated:** 2025-11-16  
**Maintainer:** NZDF Space Domain Awareness Team
