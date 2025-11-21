# Phase 2.6 - PDF Export Quick Start

## Files Delivered

1. **pdf_export.py** (620 lines) - Place in `tawhiri/space_weather/`
2. **test_pdf_export.py** (440 lines) - Place in `tests/test_space_weather/`
3. **pdf_requirements.txt** - Additional dependencies needed
4. **PHASE_2_6_COMPLETE.md** - Full documentation

---

## Installation

### Step 1: Install Dependencies

```bash
# Core PDF functionality
pip install reportlab>=4.0.0

# For image handling (recommended)
pip install Pillow>=10.0.0

# For chart embedding (optional, requires kaleido)
pip install kaleido>=0.2.1
```

### Step 2: Place Files

```
tawhiri/
  space_weather/
    __init__.py
    constants.py
    scales.py
    utils.py
    data_fetchers.py
    plotting.py
    pdf_export.py  ← NEW!

tests/
  test_space_weather/
    test_pdf_export.py  ← NEW!
```

---

## Quick Usage Examples

### Example 1: Basic PDF (No Charts)

```python
from tawhiri.space_weather.pdf_export import create_space_weather_pdf

# Create simple text-based PDF
success = create_space_weather_pdf(
    output_path="space_weather_brief.pdf",
    current_conditions={"r": "R1", "s": "S0", "g": "G2"},
    past_conditions={"r": "R0", "s": "S0", "g": "G1"},
    forecast_24h={
        "kp": 4,
        "r12": 25,  # R1-R2 probability
        "r3": 5,    # R3+ probability
        "s1": 10    # S1+ probability
    },
    summary_text="Current space weather conditions are moderate. "
                 "Increased geomagnetic activity expected over next 24 hours.",
    organization="NZDF Space Weather Service"
)

if success:
    print("✅ PDF created successfully!")
else:
    print("❌ PDF creation failed")
```

### Example 2: Full PDF with Charts and Discussion

```python
from tawhiri.space_weather.pdf_export import create_space_weather_pdf
from tawhiri.space_weather.plotting import (
    create_xray_chart,
    create_proton_chart,
    create_kp_chart
)
import tempfile

# Create charts
xray_fig = create_xray_chart()
proton_fig = create_proton_chart()
kp_fig = create_kp_chart()

# Save charts to temporary files
chart_paths = {}
with tempfile.TemporaryDirectory() as tmpdir:
    # Save each chart
    if xray_fig:
        xray_path = f"{tmpdir}/xray.png"
        xray_fig.write_image(xray_path, width=1200, height=500)
        chart_paths["X-ray Flux"] = xray_path
    
    if proton_fig:
        proton_path = f"{tmpdir}/proton.png"
        proton_fig.write_image(proton_path, width=1200, height=500)
        chart_paths["Proton Flux"] = proton_path
    
    if kp_fig:
        kp_path = f"{tmpdir}/kp.png"
        kp_fig.write_image(kp_path, width=1200, height=500)
        chart_paths["Kp Index"] = kp_path
    
    # Create comprehensive PDF
    success = create_space_weather_pdf(
        output_path="space_weather_full_report.pdf",
        current_conditions={"r": "R2", "s": "S1", "g": "G3"},
        past_conditions={"r": "R1", "s": "S0", "g": "G2"},
        forecast_24h={"kp": 5, "r12": 35, "r3": 10, "s1": 20},
        summary_text="Enhanced space weather activity in progress...",
        discussion_text="Solar Activity Forecast:\n\n"
                       "Solar activity is expected to be moderate...\n\n"
                       "Geomagnetic Activity Forecast:\n\n"
                       "The geomagnetic field is expected to reach storm levels...",
        aurora_text="Aurora visible in southern regions tonight.",
        chart_paths=chart_paths,
        logo_path="nzdf_logo.png",  # Optional
        include_charts=True,
        include_discussion=True
    )
```

### Example 3: Streamlit Integration

```python
import streamlit as st
from tawhiri.space_weather.pdf_export import create_space_weather_pdf
import tempfile

# In your PDF Export tab:
st.markdown("## Export Space Weather Report")

if st.button("Generate PDF Report"):
    with st.spinner("Creating PDF..."):
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            success = create_space_weather_pdf(
                output_path=tmp.name,
                current_conditions=current,  # Your data
                past_conditions=past,
                forecast_24h=forecast,
                summary_text=summary,
                discussion_text=noaa_discussion,
                aurora_text=bom_aurora
            )
            
            if success:
                # Read the PDF
                with open(tmp.name, "rb") as f:
                    pdf_bytes = f.read()
                
                # Offer download
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"space_weather_{datetime.now():%Y%m%d_%H%M}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ PDF generated successfully!")
            else:
                st.error("❌ Failed to generate PDF. Check that reportlab is installed.")
```

---

## Using the OOP Interface

For more control, use the `SpaceWeatherPDF` class directly:

```python
from tawhiri.space_weather.pdf_export import SpaceWeatherPDF

# Create PDF object
pdf = SpaceWeatherPDF(
    output_path="custom_report.pdf",
    title="Space Weather Intelligence Brief",
    logo_path="logo.png",
    organization="NZDF Space Domain"
)

# Add content in any order
pdf.add_title("CONFIDENTIAL")
pdf.add_section_heading("Executive Summary")
pdf.add_paragraph("Current space weather conditions require attention...")

pdf.add_bullet_list([
    "Solar activity: Moderate with risk of M-class flares",
    "Geomagnetic field: Active to minor storm levels",
    "Radiation environment: Elevated but manageable"
])

# Add custom table
table_data = [
    ["Metric", "Current", "Forecast"],
    ["R-scale", "R1", "R2-R3 likely"],
    ["S-scale", "S0", "S1 possible"],
    ["G-scale", "G2", "G3-G4 expected"]
]
pdf.add_table(table_data, header_row=True)

# Add image
pdf.add_image("chart.png", width=15, caption="X-ray flux trends")

# Build PDF
pdf.build()
```

---

## Replacing Old PDF Code

### Old Code (Space_weather_module.py):

```python
def export_management_pdf(noaa_discussion_raw, past, current, ...):
    # 200+ lines of fpdf code
    chart_paths = []
    try:
        import plotly.io as pio
        pio.kaleido.scope.mathjax = None
        # ... kaleido code that often breaks
    except Exception:
        chart_paths = []
    
    class PDF(FPDF):
        # ... custom header/footer
    
    pdf = PDF()
    # ... lots of manual positioning
    pdf.output(...)
```

### New Code (Using Module):

```python
from tawhiri.space_weather.pdf_export import create_space_weather_pdf

# Just call the function!
success = create_space_weather_pdf(
    output_path="report.pdf",
    current_conditions=current,
    past_conditions=past,
    forecast_24h=forecast,
    summary_text=summary,
    discussion_text=noaa_discussion,
    chart_paths=chart_paths  # Optional
)
```

---

## Features Comparison

### Old (fpdf-based):
- ❌ Unreliable table rendering
- ❌ Manual positioning required
- ❌ Hard to maintain
- ❌ Poor Unicode support
- ❌ Kaleido dependency always required
- ❌ Limited styling options

### New (reportlab-based):
- ✅ Professional table rendering
- ✅ Automatic layout
- ✅ Easy to maintain and extend
- ✅ Excellent Unicode support
- ✅ Charts are optional
- ✅ Rich styling capabilities
- ✅ NZDF-ready formatting

---

## Configuration Options

### Custom Organization Branding

```python
success = create_space_weather_pdf(
    output_path="report.pdf",
    ...,
    logo_path="/path/to/nzdf_crest.png",
    organization="New Zealand Defence Force - Space Operations"
)
```

### Control Content Inclusion

```python
success = create_space_weather_pdf(
    output_path="report.pdf",
    ...,
    include_charts=False,      # Skip charts (faster, smaller)
    include_discussion=False   # Executive summary only
)
```

### Custom Timeframe

```python
# Future: add date parameter
success = create_space_weather_pdf(
    output_path="report.pdf",
    ...,
    report_date=datetime(2025, 11, 22),  # Custom date
)
```

---

## Error Handling

The module is designed to fail gracefully:

```python
# Check if reportlab is available
from tawhiri.space_weather.pdf_export import check_reportlab_available

if not check_reportlab_available():
    print("PDF export not available. Install: pip install reportlab")
else:
    # Proceed with PDF creation
    success = create_space_weather_pdf(...)
    
    if not success:
        print("PDF creation failed - check logs for details")
```

---

## Testing

```bash
# Run PDF export tests
pytest tests/test_space_weather/test_pdf_export.py -v

# With reportlab installed: ~25 tests pass
# Without reportlab: ~15 tests pass, 10 skip
```

---

## Troubleshooting

### Issue: "No module named 'reportlab'"
```bash
pip install reportlab
```

### Issue: "Charts not appearing in PDF"
```bash
# Option 1: Install kaleido for chart export
pip install kaleido

# Option 2: Create PDF without charts
create_space_weather_pdf(..., include_charts=False)
```

### Issue: "Logo not showing"
- Check logo file exists: `os.path.exists(logo_path)`
- Supported formats: PNG, JPG, JPEG
- Logo will be skipped if invalid (PDF still created)

### Issue: "Special characters not rendering"
- reportlab has good Unicode support
- If issues persist, use ASCII alternatives:
  - ° → deg
  - ≥ → >=
  - λ → lambda

---

## Next Steps

1. ✅ Install dependencies: `pip install reportlab`
2. ✅ Place `pdf_export.py` in your package
3. ✅ Test: `pytest tests/test_space_weather/test_pdf_export.py`
4. ✅ Integrate into your Streamlit app
5. ⏳ Ready for Phase 2.7 - Final UI migration!

---

## Benefits Summary

✅ **More Reliable** - reportlab is industry standard  
✅ **Better Tables** - Automatic layout and styling  
✅ **Optional Charts** - PDFs work without kaleido  
✅ **Professional Output** - NZDF-ready formatting  
✅ **Easy to Maintain** - Clean, testable code  
✅ **Extensible** - Add new sections easily  

---

**You're ready to generate professional PDF reports!** 📄
