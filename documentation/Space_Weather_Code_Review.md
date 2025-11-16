# Space Weather Module - Comprehensive Code Review

**Reviewed:** November 16, 2025  
**File:** Space_weather_module.py (2,401 lines)  
**Overall Assessment:** Good quality production code with room for refinement

---

## 🔴 CRITICAL ISSUES (Fix Immediately)

### 1. **Duplicate Function Definition**
**Lines 107-153:** The `g_scale()` function is defined twice identically.

```python
# Remove one of these - they're identical
def g_scale(kp_index: float) -> tuple[str, str]:  # Line 107
def g_scale(kp_index: float) -> tuple[str, str]:  # Line 131 (DUPLICATE)
```

**Impact:** Python will use only the second definition, but this creates confusion and maintenance issues.  
**Fix:** Delete lines 131-153.

---

### 2. **Hardcoded API Key in Source Code**
**Line 43:** BOM API key is committed to source code.

```python
BOM_API_KEY = st.secrets.get("BOM_API_KEY", "51585962-2fdd-4cf5-9d9e-74cdd09e3bab")
```

**Security Risk:** If this repository is public or shared, your API key is exposed.  
**Fix:** Remove the fallback key entirely:

```python
BOM_API_KEY = st.secrets.get("BOM_API_KEY", "")
if not BOM_API_KEY:
    st.error("BOM_API_KEY not configured in secrets")
```

---

### 3. **Hardcoded Windows Path**
**Line 41:** Default path assumes Windows and specific user directory.

```python
DATA_DIR = st.secrets.get("DATA_DIR", r"C:\Users\Standalone1\Desktop\Space_Tactical_Dashboard\data")
```

**Problem:** Code won't work on Linux/Mac or for other users.  
**Fix:** Use platform-agnostic defaults:

```python
import pathlib
DEFAULT_DATA_DIR = pathlib.Path.home() / "space_weather_data"
DATA_DIR = st.secrets.get("DATA_DIR", str(DEFAULT_DATA_DIR))
```

---

## 🟠 HIGH PRIORITY (Should Fix Soon)

### 4. **Typos in Comments**
**Lines 14-17:** Multiple spelling errors in comments.

```python
# "promament" → "prominent"
# "txt" → "text"  
# "fint" → "font"
# "beans" → "banners"
```

These appear in your version control history and reduce professionalism.

---

### 5. **Missing Defensive Checks on Data Access**
Throughout the code, you access nested dictionaries without null checks:

```python
# Line 2249 - could crash if day1 is None or missing 'kp'
f"Next 24 h (UTC): {g_lbl} (Kp~{day1['kp'] if day1['kp'] is not None else '~'})"
```

**Better approach:**
```python
kp_value = day1.get('kp') if day1 else None
kp_display = kp_value if kp_value is not None else '~'
f"Next 24 h (UTC): {g_lbl} (Kp~{kp_display})"
```

---

### 6. **Broad Exception Catching**
**Lines 52, 63, 69, 73:** Using bare `except Exception` hides specific errors.

```python
except Exception as e:
    st.warning(f"Failed to load {url}: {e}")
```

**Better approach:**
```python
except requests.RequestException as e:
    st.warning(f"Network error loading {url}: {e}")
except ValueError as e:
    st.warning(f"Invalid JSON from {url}: {e}")
```

This helps with debugging and allows different handling for different failure modes.

---

### 7. **Magic Numbers**
Thresholds are hardcoded throughout. Examples:

```python
# Line 78-89: R-scale thresholds
if xray_flux_wm2 >= 2e-3:  # Why 2e-3? Document this!
```

**Fix:** Create a constants section:

```python
# ========== NOAA Scale Thresholds ==========
# R-Scale (Radio Blackout) X-ray flux thresholds (W/m²)
R_SCALE_THRESHOLDS = {
    'R5': 2e-3,   # X20+ flares
    'R4': 1e-3,   # X10-X19 flares
    'R3': 1e-4,   # X1-X9 flares
    'R2': 5e-5,   # M5-M9 flares
    'R1': 1e-5,   # M1-M4 flares
}

# S-Scale (Radiation Storm) proton flux thresholds (pfu, >10 MeV)
S_SCALE_THRESHOLDS = {
    'S5': 1e5,
    'S4': 1e4,
    'S3': 1e3,
    'S2': 1e2,
    'S1': 10,
}

# G-Scale (Geomagnetic Storm) Kp index thresholds
G_SCALE_THRESHOLDS = {
    'G5': 9,
    'G4': 8,
    'G3': 7,
    'G2': 6,
    'G1': 5,
}
```

Then use them:
```python
def r_scale(xray_flux_wm2):
    for level, threshold in sorted(R_SCALE_THRESHOLDS.items(), reverse=True):
        if xray_flux_wm2 >= threshold:
            return (level, SEVERITY_LABELS[level])
    return ("R0", "quiet")
```

---

### 8. **Inconsistent Return Type Handling**
Some functions return `None` on failure, others return empty strings `""`, others return default values.

```python
fetch_json()  # returns None on failure
fetch_text()  # returns "" on failure
clamp_float() # returns 0.0 on failure
```

**Recommendation:** Be consistent. Consider using `Optional[T]` type hints and handle `None` explicitly in calling code.

---

## 🟡 MEDIUM PRIORITY (Good to Address)

### 9. **Code Organization & Length**
At 2,401 lines, this file does too much. Consider splitting into:

```
space_weather/
├── __init__.py
├── app.py                    # Main run() function and UI
├── data_fetchers.py          # fetch_json, fetch_text, API calls
├── scales.py                 # r_scale, s_scale, g_scale functions
├── nz_translations.py        # NZ-specific text rewrites
├── plotting.py               # All Plotly chart generation
├── pdf_export.py             # PDF generation logic
├── constants.py              # Thresholds, colors, URLs
└── utils.py                  # clamp_float, last_updated, etc.
```

**Benefits:**
- Easier testing (test `scales.py` independently)
- Easier to find things
- Multiple developers can work on different modules
- Cleaner imports

---

### 10. **Lack of Type Hints**
Only a few functions have type hints. Add them throughout:

```python
# Before
def clamp_float(x, default=0.0):
    ...

# After
def clamp_float(x: any, default: float = 0.0) -> float:
    ...
```

This catches bugs at development time if you use a type checker like `mypy`.

---

### 11. **No Logging**
Currently using `st.warning()` for errors. Consider adding proper logging:

```python
import logging

logger = logging.getLogger(__name__)

@st.cache_data(ttl=600, show_spinner=True)
def fetch_json(url, timeout=20):
    try:
        r = requests.get(url, timeout=timeout, headers=UA)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}", exc_info=True)
        st.warning(f"Failed to load {url}")
        return None
```

**Benefits:**
- Logs persist beyond Streamlit session
- Can configure different log levels for development vs production
- Can send logs to monitoring services

---

### 12. **Unused Import**
**Line 32:** `time` is imported but never used directly in your code.

```python
import time  # Line 32 - not used
```

**Fix:** Remove it unless you're planning to use it.

---

### 13. **Function Complexity**
The `run()` function is massive (likely 1000+ lines). Consider breaking it into smaller functions:

```python
def run(set_page_config=True):
    if set_page_config:
        configure_page()
    
    setup_sidebar()
    data = fetch_all_data()
    
    render_overview_tab(data)
    render_detailed_charts_tab(data)
    render_expert_data_tab(data)
    render_nowcast_tab(data)
    render_management_tab(data)
    render_help_tab()
```

---

### 14. **Inconsistent String Formatting**
Mix of f-strings, `.format()`, and `%` formatting:

```python
f"Failed to load {url}: {e}"         # f-string (good)
"Generated %Y-%m-%d %H:%M UTC"       # strftime format (appropriate here)
```

**Recommendation:** Use f-strings consistently for string interpolation unless there's a specific reason not to (like strftime).

---

### 15. **Color Constants Scattered**
Color codes are defined in multiple places. Centralize them:

```python
# ========== Color Schemes ==========
COLORS = {
    'slate': (45, 55, 72),
    'teal': (0, 128, 128),
    'gray': (128, 128, 128),
    'severity': {
        'ok': (240, 255, 240),
        'caution': (255, 250, 205),
        'watch': (255, 228, 196),
        'severe': (255, 99, 71),
        'extreme': (139, 0, 0),
    }
}
```

---

## 🟢 LOW PRIORITY (Nice to Have)

### 16. **Add Unit Tests**
Create a test suite:

```python
# tests/test_scales.py
import pytest
from space_weather.scales import r_scale, s_scale, g_scale

def test_r_scale_quiet():
    assert r_scale(1e-6) == ("R0", "quiet")

def test_r_scale_minor():
    assert r_scale(1e-5) == ("R1", "minor")

def test_r_scale_extreme():
    assert r_scale(3e-3) == ("R5", "extreme")

# Run with: pytest tests/
```

---

### 17. **Documentation**
Add docstrings to major functions:

```python
def fetch_json(url: str, timeout: int = 20) -> Optional[dict]:
    """
    Fetch and parse JSON from a URL with caching.
    
    Args:
        url: The URL to fetch from
        timeout: Request timeout in seconds (default: 20)
        
    Returns:
        Parsed JSON as dict, or None if request fails
        
    Note:
        Results are cached for 10 minutes via st.cache_data
    """
```

---

### 18. **Configuration Management**
Consider using a proper config file instead of just `st.secrets`:

```yaml
# config.yaml
api:
  noaa_key: ${NOAA_API_KEY}
  bom_key: ${BOM_API_KEY}
  
cache:
  ttl_seconds: 600
  
thresholds:
  r_scale:
    R5: 2e-3
    R4: 1e-3
    # etc.
```

Load with PyYAML or similar.

---

### 19. **Performance Optimization**
If the app feels slow:

1. **Profile the code** to find bottlenecks
2. Consider **async requests** if fetching multiple APIs simultaneously
3. Use `st.cache_resource` for expensive computations that don't change often
4. Implement **lazy loading** for charts in tabs that aren't initially visible

---

### 20. **Accessibility Enhancements**
You mention accessibility but could improve:

```python
# Add ARIA labels more explicitly
st.markdown('<div role="status" aria-live="polite">', unsafe_allow_html=True)
st.metric("Current X-ray Flux", value)
st.markdown('</div>', unsafe_allow_html=True)

# Ensure color isn't the only indicator
# Add icons/text patterns alongside colors
```

---

### 21. **Auto-Refresh**
**Line 17:** Comment mentions auto-update fix is "not hopeful". Consider:

```python
# Add to sidebar
refresh_interval = st.sidebar.selectbox(
    "Auto-refresh interval",
    options=[0, 60, 300, 600],
    format_func=lambda x: "Manual" if x == 0 else f"{x//60} minutes"
)

if refresh_interval > 0:
    st_autorefresh(interval=refresh_interval * 1000, key="data_refresh")
```

Requires `streamlit-autorefresh` package.

---

### 22. **Error Recovery**
Add retry logic for transient network failures:

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Use in fetch functions
```

---

## 📊 Code Quality Metrics

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| Lines of code | 2,401 | <500 per file | Medium |
| Cyclomatic complexity | High (run() function) | <10 per function | High |
| Test coverage | 0% | >80% | Low |
| Type hint coverage | ~5% | >90% | Medium |
| Duplicate code | Some | Minimal | Low |
| Security issues | 1 (API key) | 0 | Critical |

---

## 🎯 Recommended Action Plan

### Week 1 (Critical)
1. ✅ Remove duplicate `g_scale()` function
2. ✅ Remove hardcoded API key
3. ✅ Fix hardcoded Windows path
4. ✅ Add defensive null checks to critical paths

### Week 2 (High Priority)
5. ✅ Fix all typos in comments
6. ✅ Improve exception handling specificity
7. ✅ Extract magic numbers to constants
8. ✅ Add type hints to public functions

### Week 3 (Refactoring)
9. ✅ Split into multiple modules
10. ✅ Add logging framework
11. ✅ Reduce `run()` function complexity

### Week 4 (Quality)
12. ✅ Write unit tests for scales/calculations
13. ✅ Add docstrings to major functions
14. ✅ Set up code linting (black, flake8, mypy)

---

## 💡 Specific Code Snippets to Replace

### Replace this:
```python
def clamp_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        try:
            return float(str(x).strip())
        except Exception:
            return default
```

### With this:
```python
def clamp_float(x: any, default: float = 0.0) -> float:
    """
    Safely convert a value to float, returning default if conversion fails.
    
    Handles numeric types, strings, and whitespace.
    """
    try:
        return float(x)
    except (TypeError, ValueError):
        try:
            return float(str(x).strip())
        except (TypeError, ValueError, AttributeError):
            return default
```

---

### Replace this:
```python
if _any(low, "x-class", "major flare", "significant flare"):
    base = "Major solar flares noted — higher chance of radio/GNSS issues across New Zealand."
elif _any(low, "m-class", "moderate"):
    base = "Moderate solar flares observed — brief HF/GNSS hiccups possible over NZ."
```

### With this:
```python
SOLAR_ACTIVITY_PATTERNS = {
    'major': (["x-class", "major flare", "significant flare"],
              "Major solar flares noted — higher chance of radio/GNSS issues across New Zealand."),
    'moderate': (["m-class", "moderate"],
                 "Moderate solar flares observed — brief HF/GNSS hiccups possible over NZ."),
    # etc.
}

def classify_solar_activity(text: str) -> str:
    """Return NZ-appropriate description of solar activity."""
    low = (text or "").lower()
    for level, (patterns, description) in SOLAR_ACTIVITY_PATTERNS.items():
        if any(p in low for p in patterns):
            return description
    return "Solar activity is mixed but not unusual for the cycle; NZ impacts limited."
```

---

## 🔧 Tools to Help

Consider adding these to your development workflow:

1. **black** - Auto-format code consistently
2. **flake8** - Catch common errors and style issues
3. **mypy** - Type checking
4. **pytest** - Testing framework
5. **pytest-cov** - Test coverage reports
6. **bandit** - Security linting
7. **pre-commit** - Run checks before each commit

Setup example:
```bash
pip install black flake8 mypy pytest pytest-cov bandit pre-commit
black space_weather_module.py
flake8 space_weather_module.py --max-line-length=120
mypy space_weather_module.py
```

---

## ✅ What You're Doing Right

Don't lose sight of these strengths:

1. ✨ **Excellent user focus** - NZ-specific translations show you understand your audience
2. ✨ **Good separation** - Wrapping UI in `run()` is the right architectural choice
3. ✨ **Comprehensive features** - PDF export, multiple data sources, accessibility options
4. ✨ **Professional polish** - Color coding, clear metrics, help documentation
5. ✨ **Proper caching** - Using `@st.cache_data` appropriately
6. ✨ **Graceful degradation** - Falls back when data unavailable rather than crashing
7. ✨ **Real-world ready** - This is clearly being used in production

---

## 📝 Summary

Your code is fundamentally sound and clearly production-quality. The issues identified are primarily about:
- **Maintainability** (code organization, documentation)
- **Robustness** (error handling, defensive programming)  
- **Security** (API key exposure)
- **Code quality** (consistency, type safety)

None of these are "broken" - they're just opportunities to make good code great. Focus on the Critical and High Priority items first, especially removing that API key from source control.

**Final Grade: B+ (Good, moving toward excellent with recommended improvements)**

---

*Review prepared: 2025-11-16*  
*Reviewer: Claude (Sonnet 4.5)*
