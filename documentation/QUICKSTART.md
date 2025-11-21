# Tawhiri Migration - Quick Start Guide

## What Has Been Completed ✅

We've successfully completed **Phase 2.1-2.3** of the space weather migration:

### 1. **Constants Module** (`tawhiri/space_weather/constants.py`)
   - All NOAA scale thresholds (R, S, G) properly documented
   - Color schemes for UI and PDF generation
   - API endpoints centralized
   - NZ-specific messaging phrases
   - **Fixed:** Removed all magic numbers
   - **Fixed:** Removed hardcoded API keys

### 2. **Scales Module** (`tawhiri/space_weather/scales.py`)
   - R-scale (Radio Blackout) calculations
   - S-scale (Solar Radiation Storm) calculations  
   - G-scale (Geomagnetic Storm) calculations
   - Ap to Kp conversion
   - **Fixed:** Removed duplicate g_scale() function
   - Full type hints and documentation
   - 100% test coverage (28 tests passing)

### 3. **Utils Module** (`tawhiri/space_weather/utils.py`)
   - Safe data conversion functions
   - Timestamp formatting
   - Text processing utilities
   - Validation functions

### 4. **Testing Infrastructure**
   - Complete test suite for scales module
   - All 28 tests passing
   - Ready for more tests to be added

### 5. **Package Structure**
   - Proper Python package with __init__.py files
   - setup.py for installation
   - requirements.txt with dependencies
   - config.example.json template

---

## How to Get Started

### On Your Windows System:

1. **Download the migration files** from the outputs folder
   
2. **Extract to your project directory:**
   ```
   C:\Users\Standalone1\Desktop\Space_Tactical_Dashboard\
   ```

3. **Copy the tawhiri folder** to your project:
   ```
   Space_Tactical_Dashboard\
   ├── tawhiri\              ← New modular code
   ├── Space_weather_module.py  ← Old monolithic file (keep as backup)
   └── ...
   ```

4. **Create config.json:**
   ```bash
   cd tawhiri_migration
   copy config.example.json config.json
   ```
   
   Edit config.json with your actual paths:
   ```json
   {
     "data_dir": "C:\\Users\\Standalone1\\Desktop\\Space_Tactical_Dashboard\\data",
     "space_weather": {
       "bom_api_key": "YOUR_ACTUAL_KEY_HERE"
     }
   }
   ```

5. **Install in development mode:**
   ```bash
   pip install -e .
   ```

6. **Run tests to verify:**
   ```bash
   pytest tests/test_space_weather/test_scales.py -v
   ```

---

## Next Steps (Phase 2.4-2.7)

### 🔄 Phase 2.4: Data Fetchers (30 minutes)
Create `tawhiri/space_weather/data_fetchers.py`:
- Extract `fetch_json()` and `fetch_text()` from monolithic file
- Remove Streamlit cache dependency (use regular caching)
- Add retry logic for network failures
- Improve error handling

**Key functions to migrate:**
- `fetch_json(url, timeout=20)`
- `fetch_text(url, timeout=20)`
- `get_noaa_rsg_now_and_past()`
- `get_next24_summary()`
- `get_noaa_forecast_text()`

### 📊 Phase 2.5: Plotting Functions (2 hours)
Create `tawhiri/space_weather/plotting.py`:
- Extract all Plotly chart creation functions
- Make charts configurable (colors, sizes, etc.)
- Add export capabilities

**Key functions to migrate:**
- `create_xray_chart()`
- `create_proton_chart()`
- `create_kp_chart()`
- All other visualization functions

### 📄 Phase 2.6: PDF Export (1 hour)
Create `tawhiri/space_weather/pdf_export.py`:
- Extract PDF generation code
- Improve layout and formatting
- Use constants for colors

**Key functions to migrate:**
- `export_management_pdf()`
- PDF class definition
- Chart embedding functions

### 🖥️ Phase 2.7: UI Application (2 hours)
Create `tawhiri/space_weather/app.py`:
- Extract the `run()` function
- Update all imports to use new modules
- Test side-by-side with old version

---

## Testing Your Work

After each phase:

```bash
# Run existing tests
pytest tests/test_space_weather/ -v

# Add new tests for new modules
# Example: tests/test_space_weather/test_data_fetchers.py
```

---

## Important Notes

### ✅ What's Working Now:
- Scale calculations (R, S, G)
- Severity classifications
- All constants properly defined
- 28 tests passing

### 🚧 What Still Needs Migration:
- Data fetching from NOAA/BOM APIs
- Plotting and visualization  
- PDF generation
- Streamlit UI

### 🐛 Bugs Already Fixed:
1. Duplicate g_scale() function
2. Hardcoded API keys
3. Magic numbers throughout code
4. Windows-specific paths

---

## File Locations Guide

### ✅ Completed Files (Ready to Use):
```
tawhiri/
├── __init__.py
└── space_weather/
    ├── __init__.py
    ├── constants.py     ← All thresholds and config
    ├── scales.py        ← R/S/G scale calculations
    └── utils.py         ← Helper functions
```

### 🔄 Next to Create:
```
tawhiri/space_weather/
├── data_fetchers.py   ← Phase 2.4
├── plotting.py        ← Phase 2.5
├── pdf_export.py      ← Phase 2.6
└── app.py            ← Phase 2.7
```

### 📋 Keep as Reference:
```
Space_weather_module.py   ← Original monolithic file (don't delete yet!)
```

---

## How to Use New Modules in Your Old Code

While migrating, you can start using the new modules in your monolithic file:

```python
# At the top of Space_weather_module.py, add:
try:
    from tawhiri.space_weather.scales import r_scale, s_scale, g_scale
    from tawhiri.space_weather.constants import *
    from tawhiri.space_weather.utils import clamp_float, last_updated
    USING_MODULAR = True
    print("✅ Using new modular code")
except ImportError:
    USING_MODULAR = False
    print("⚠️ Using old monolithic code")
    # Keep old function definitions as backup
```

This way you can test the new modules while keeping the old code as a safety net.

---

## Getting Help

If you encounter issues:

1. Check the test output: `pytest tests/ -v`
2. Review the main README.md for detailed progress
3. Check the original MIGRATION_GUIDE.md
4. Look at the Space_Weather_Code_Review.md for context

---

## Progress Tracking

Update the README.md file as you complete each phase:

- [x] Phase 2.1: Constants (Complete)
- [x] Phase 2.2: Scale Functions (Complete)  
- [x] Phase 2.3: Utilities (Complete)
- [ ] Phase 2.4: Data Fetchers (Next)
- [ ] Phase 2.5: Plotting (Pending)
- [ ] Phase 2.6: PDF Export (Pending)
- [ ] Phase 2.7: UI Application (Pending)

**Current Progress: ~25% Complete**

---

## Questions to Consider

As you continue:

1. Do you want to keep BOM API integration or just use NOAA?
2. Should we add more comprehensive logging?
3. Do you need offline mode for air-gapped systems?
4. What's your target Python version? (Currently 3.9+)

---

Good luck with the rest of the migration! The foundation is solid and tested. 🚀
