# Phase 2.5 - Quick Integration Guide

## Files Delivered

1. **plotting.py** (442 lines) - Place in `tawhiri/space_weather/`
2. **test_plotting.py** (359 lines) - Place in `tests/test_space_weather/`
3. **PHASE_2_5_COMPLETE.md** - Documentation

---

## Quick Start: Using the Plotting Module

### 1. Install the Module

Place `plotting.py` in your package:
```
tawhiri/
  space_weather/
    __init__.py
    constants.py
    scales.py
    utils.py
    data_fetchers.py
    plotting.py  ← NEW!
```

### 2. Basic Usage

```python
from tawhiri.space_weather.plotting import (
    create_xray_chart,
    create_proton_chart,
    create_kp_chart
)

# Create charts
xray_fig = create_xray_chart()
proton_fig = create_proton_chart()
kp_fig = create_kp_chart()

# Use in Streamlit
import streamlit as st
if xray_fig:
    st.plotly_chart(xray_fig, use_container_width=True)
```

### 3. Custom Charts

```python
from tawhiri.space_weather.plotting import create_timeseries_chart

# Your custom data
my_data = [
    {"timestamp": "2025-01-01T00:00:00Z", "value": 10},
    {"timestamp": "2025-01-01T01:00:00Z", "value": 20},
]

# Create custom chart
fig = create_timeseries_chart(
    data=my_data,
    time_field="timestamp",
    value_field="value",
    title="My Custom Data",
    y_label="Measurement",
    height=300,
    color="#00ff00"
)
```

### 4. Charts with Thresholds

```python
from tawhiri.space_weather.plotting import create_multi_threshold_chart
from tawhiri.space_weather.constants import R_SCALE_THRESHOLDS

# Fetch X-ray data
from tawhiri.space_weather.data_fetchers import fetch_json
xray_data = fetch_json("https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json")

# Create chart with R-scale thresholds
fig = create_multi_threshold_chart(
    data=xray_data,
    time_field="time_tag",
    value_field="flux",
    thresholds=R_SCALE_THRESHOLDS,
    title="X-ray Flux with R-scale",
    y_label="Flux (W/m²)",
    log_y=True
)
```

---

## Replacing Old Code

### In Your Space_weather_module.py

**Find this:**
```python
def create_xray_chart():
    data = fetch_json("https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json")
    if not data: return None
    times = [row.get("time_tag") for row in data if "time_tag" in row]
    fluxes = [row.get("flux", 0) for row in data]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=fluxes, mode="lines", name="X-ray Flux"))
    fig.update_layout(title="X-rays (6-hour)", height=220,
                      margin=dict(l=10, r=10, t=30, b=10),
                      xaxis=dict(title="Time", color="#9fc8ff"),
                      yaxis=dict(title="Flux", color="#9fc8ff"))
    return fig
```

**Replace with:**
```python
from tawhiri.space_weather.plotting import create_xray_chart

# Now just call it - all logic is in the module!
# The function signature is the same, so existing calls work
```

**In your run() function, keep using it the same way:**
```python
xray_fig = create_xray_chart()
if xray_fig:
    st.plotly_chart(xray_fig, use_container_width=True)
```

Same process for `create_proton_chart()` and `create_kp_chart()`.

---

## Testing

Run the tests:
```bash
# Copy test file to tests directory
cp test_plotting.py tests/test_space_weather/

# Run tests
pytest tests/test_space_weather/test_plotting.py -v

# Expected: 28 tests passing
```

---

## Benefits You Get

✅ **Reduced Code Duplication**
- Old: 3 functions × ~15 lines each = 45 lines in monolithic file
- New: Import 3 functions = 3 lines, logic in module

✅ **Configurability**
- Change colors globally via constants
- Adjust heights per chart
- Add custom styling

✅ **Reusability**
- Use charts in multiple apps
- Create custom charts easily
- Export charts to files

✅ **Maintainability**
- Fix bugs in one place
- Test charts independently
- Clear dependencies

✅ **Professional Features**
- Storm threshold indicators
- Multi-threshold overlays
- Consistent styling
- Dark mode compatible

---

## Configuration Options

### Chart Heights
```python
# Make charts taller for briefings
xray_fig = create_xray_chart(height=400)
```

### Custom Titles
```python
# Custom title for NZ context
xray_fig = create_xray_chart(
    title="X-ray Flux - NZDT Time"
)
```

### Custom Colors
```python
# Use NZDF colors
fig = create_timeseries_chart(
    data=data,
    color="#003366",  # NZDF Blue
    title="..."
)
```

### Additional Layout
```python
# Add more Plotly layout options
fig = create_xray_chart(
    title="X-ray Flux",
    font=dict(family="Arial", size=14),
    showlegend=False
)
```

---

## Next Steps

1. ✅ Phase 2.5 Complete - Plotting
2. ⏳ Phase 2.6 Next - PDF Export
3. ⏳ Phase 2.7 Final - UI Application

You're 70% done with the migration! 🎉

---

## Troubleshooting

### Import Error
```python
# If you get: ModuleNotFoundError: No module named 'tawhiri.space_weather.plotting'

# Make sure:
1. plotting.py is in tawhiri/space_weather/
2. You've installed the package: pip install -e .
3. Or add to Python path: sys.path.insert(0, '/path/to/tawhiri')
```

### Chart Not Showing
```python
# Charts return None on error - check:
fig = create_xray_chart()
if fig is None:
    print("Chart creation failed - check API and data")
else:
    st.plotly_chart(fig)
```

### Styling Issues
```python
# Override default config:
from tawhiri.space_weather.plotting import DEFAULT_CHART_CONFIG

# View defaults
print(DEFAULT_CHART_CONFIG)

# Override in chart call
fig = create_xray_chart(
    margin=dict(l=50, r=50, t=50, b=50)
)
```

---

**Ready to use your new plotting module!** 📊
