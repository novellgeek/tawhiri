# Operation Module Developer Guide

This guide describes the standard module interface for Operation/* modules after the refactoring to make them standalone, testable, and consistent.

## Overview

The Operation modules have been refactored to follow a clean architecture pattern that separates:
- **Pure functions**: Data processing and computation (no side effects, no Streamlit calls)
- **Streamlit wrappers**: Thin display functions that call pure functions and render in Streamlit UI

This design makes modules:
- **Testable**: Pure functions can be unit tested without Streamlit
- **Reusable**: Core logic can be imported and used in CLI tools, scripts, or other frameworks
- **Maintainable**: Clear separation of concerns

## Standard Module Interface

### 1. Shared Utilities (Operation/common.py)

All modules should import shared functionality from `Operation/common.py`:

```python
from Operation.common import setup_logger, load_tles, read_multi_epoch_tle_file
from Operation.common import EARTH_RADIUS_KM, MU_EARTH

# Setup logger for the module
logger = setup_logger(__name__)
```

**Available utilities:**
- `setup_logger(name, level)`: Configure logging with standard format
- `_lines_from_source(source)`: Parse TLE lines from file path, bytes, or file-like object
- `load_tles(source)`: Load TLEs as dict {norad_id: (name, line1, line2)}
- `read_multi_epoch_tle_file(source)`: Load multi-epoch TLEs grouped by satellite
- Constants: `EARTH_RADIUS_KM`, `MU_EARTH`

### 2. Module Structure

Each module should follow this pattern:

```python
# Imports
from Operation.common import setup_logger, load_tles
logger = setup_logger(__name__)

# Pure functions (no Streamlit calls)
def load_data(source):
    """Load and parse data (file-like objects supported)."""
    return data

def compute_result(data, params):
    """Pure computation function."""
    return result

def create_figure(result):
    """Create Plotly/matplotlib figure (returns figure object)."""
    fig = go.Figure(...)
    return fig

# Streamlit wrappers (thin display layer)
def display_result(result):
    """Display result in Streamlit UI."""
    fig = create_figure(result)
    st.plotly_chart(fig, use_container_width=True)

def run():
    """Main Streamlit entrypoint (preserves public API)."""
    st.title("Module Title")
    # Sidebar inputs
    # Call pure functions
    # Display results
```

### 3. Pure Functions

**Characteristics:**
- No side effects (no file I/O, no network calls in compute functions)
- No Streamlit calls (st.*)
- Accept standard Python types or file-like objects
- Return structured data (dict, DataFrame, Figure object)
- Can be unit tested easily

**Examples:**

```python
def compute_ric(master_sat, target_sat, start_time, end_time, step_seconds=60):
    """
    Pure function: computes RIC coordinates.
    Returns: times, ric_vals, eci_r1, eci_r2, ric_master, ric_target
    """
    # ... computation ...
    return times, ric_vals, eci_r1, eci_r2, ric_master, ric_target

def create_3d_ric_objects_figure(ric_master, ric_target, name_master, name_target):
    """
    Pure function: creates Plotly figure.
    Returns: Plotly Figure object
    """
    fig = go.Figure()
    # ... build figure ...
    return fig
```

### 4. Streamlit Wrappers

Thin functions that:
- Accept user inputs via Streamlit widgets
- Call pure functions
- Display results using st.* functions

**Example:**

```python
def display_3d_ric_objects(ric_master, ric_target, name_master="Master", name_target="Target"):
    """Streamlit wrapper for 3D RIC visualization."""
    fig = create_3d_ric_objects_figure(ric_master, ric_target, name_master, name_target)
    st.plotly_chart(fig, use_container_width=True)
```

### 5. File Upload Support

Pure functions should accept file-like objects for TLE uploads:

```python
# In run() function:
uploaded_file = st.file_uploader("Upload TLE file", type=["txt"])
if uploaded_file:
    tles = load_tles(uploaded_file)  # Accepts file-like object
```

### 6. Logging

Use logger instead of print statements:

```python
logger = setup_logger(__name__)

# Instead of print:
logger.info("Processing data...")
logger.warning("Missing optional parameter")
logger.error(f"Failed to process: {e}")
```

## Examples

### Using Pure Functions in CLI

```python
# cli_tool.py
from Operation.ric_dashboard_monolithic import compute_ric
from sgp4.api import Satrec
from datetime import datetime

# Load TLEs
with open("tles.txt", "r") as f:
    tles = load_tles(f)

# Create satellites
master_sat = Satrec.twoline2rv(tles['12345'][1], tles['12345'][2])
target_sat = Satrec.twoline2rv(tles['67890'][1], tles['67890'][2])

# Compute RIC
times, ric_vals, *_ = compute_ric(
    master_sat, target_sat,
    datetime(2024, 1, 1), datetime(2024, 1, 2)
)

print(f"Computed {len(times)} time steps")
print(f"Min distance: {np.linalg.norm(ric_vals, axis=1).min():.2f} km")
```

### Using Modules in Streamlit

```python
# main-dash.py
import streamlit as st
from Operation import ric_dashboard_monolithic, globe_sidebar_module

st.set_page_config(page_title="Dashboard", layout="wide")

tab1, tab2 = st.tabs(["RIC Analysis", "Globe View"])

with tab1:
    ric_dashboard_monolithic.run()

with tab2:
    globe_sidebar_module.run()
```

## Running Tests

The project includes a pytest scaffold for testing pure functions:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_common.py -v

# Run with coverage
pytest tests/ --cov=Operation --cov-report=html
```

**Test structure:**
- `tests/test_common.py`: Tests for common utilities (TLE parsing, etc.)
- `tests/test_ric.py`: Tests for RIC computation (uses pytest markers to skip if sgp4 missing)

**Writing tests:**

```python
import pytest
from Operation.common import load_tles
import io

def test_load_tles():
    """Test TLE loading from file-like object."""
    tle_str = """ISS (ZARYA)
1 25544U 98067A   21001.00000000  .00002182  00000-0  41420-4 0  9990
2 25544  51.6461 339.8014 0002571  34.5857 120.4689 15.48919393265123"""
    
    file_obj = io.StringIO(tle_str)
    tles = load_tles(file_obj)
    
    assert "25544" in tles
    name, line1, line2 = tles["25544"]
    assert name == "ISS (ZARYA)"
```

## Caching Notes

Streamlit's `@st.cache_data` decorator can be used on pure functions for performance:

```python
@st.cache_data
def load_multi_epoch_tles_cached(filepath: str):
    """Cached wrapper for read_multi_epoch_tle_file."""
    return read_multi_epoch_tle_file(filepath)
```

**Best practices:**
- Cache data loading functions (TLE files, CSV files)
- Don't cache functions with file-like object parameters (not hashable)
- Use TTL for data that changes frequently: `@st.cache_data(ttl=3600)`

## Configuration

### Secrets Management

Use `st.secrets` for sensitive credentials (Space-Track, API keys):

```toml
# .streamlit/secrets.toml
[spacetrack]
username = "your_username"
password = "your_password"
```

```python
# In module:
if "spacetrack" in st.secrets:
    username = st.secrets["spacetrack"]["username"]
    password = st.secrets["spacetrack"]["password"]
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
```

## Migration Checklist

When refactoring an existing module:

- [ ] Import from `Operation.common` instead of defining utilities locally
- [ ] Replace `print()` with `logger.*()` calls
- [ ] Extract pure computation functions (no `st.*` calls)
- [ ] Extract pure plotting functions (return Figure objects)
- [ ] Create thin Streamlit wrapper functions
- [ ] Add file-like object support for file uploads
- [ ] Keep existing `run()` function for backward compatibility
- [ ] Add unit tests for pure functions
- [ ] Update any hardcoded paths to use sidebar inputs or st.secrets

## Module-Specific Notes

### ric_dashboard_monolithic.py
- Pure functions: `compute_ric()`, `eci_to_ric()`, `plot_3d_orbits()`
- Display wrappers: `display_ric_plot_tab()`, `display_3d_ric_deviation_panel()`
- Uses `load_tle_dict()` as backward-compatible wrapper for `load_tles()`

### globe_sidebar_module.py
- Pure functions: `plot_orbits()`, `plot_ground_2d()` (both return figures and inc_rows)
- Uses `load_multi_epoch_tles_cached()` for caching
- Supports texture file selection via sidebar

### neighbourhood_module.py
- Pure worker: `get_orbit_from_tle_worker()` (no Streamlit calls, supports multiprocessing)
- Pure plotting: `create_orbit_evolution_figure()`, `plot_3d_neighbourhood()`
- Display wrappers: `display_history_table()`, `plot_orbit_evolution()`

### conjunctions_module.py
- Pure fetch: `fetch_and_save_cdm_csv()` returns `(success, message)` tuple
- Pure plotting: `create_summary_bar_figure()`, `create_histogram_figure()`, etc.
- Credentials via sidebar inputs or `st.secrets["spacetrack"]`
- `load_cdm_csv()` accepts file-like objects

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [SGP4 Library](https://pypi.org/project/sgp4/)
- [Skyfield Astronomy Library](https://rhodesmill.org/skyfield/)

## Contributing

When adding new modules or modifying existing ones:
1. Follow the standard module interface outlined above
2. Add unit tests for pure functions
3. Update this DEVELOPER.md with any module-specific notes
4. Ensure `run()` function remains compatible with main dashboard

---

**Version:** 1.0  
**Last Updated:** 2025-10-24  
**Maintainer:** novellgeek
