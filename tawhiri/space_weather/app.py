"""
Space Weather Streamlit Application

Main UI entry point for the space weather monitoring module.
This is where you'll migrate your existing Space_weather_module.py run() function.
"""

import streamlit as st
import logging
from tawhiri.config import get_config
from tawhiri.common import setup_logging

logger = logging.getLogger(__name__)


def run(set_page_config: bool = True):
    """
    Main entry point for Space Weather Streamlit UI.
    
    Args:
        set_page_config: Whether to call st.set_page_config (set False if 
                        integrating into larger dashboard)
    
    TODO: Migrate content from your existing Space_weather_module.py here.
    """
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    if 'logging_configured' not in st.session_state:
        setup_logging(
            log_file=config['logging']['log_file'],
            log_level=config['logging']['log_level'],
            log_to_console=config['logging']['log_to_console'],
        )
        st.session_state.logging_configured = True
        logger.info("Space Weather module started")
    
    # Page config
    if set_page_config:
        st.set_page_config(
            page_title="TAWHIRI Space Weather",
            page_icon="🌞",
            layout="wide",
        )
    
    # Temporary placeholder UI
    st.title("🌞 TAWHIRI Space Weather")
    st.info(
        "**Migration in progress:** This is the modular version of the space weather module. "
        "Copy your existing UI code from `Space_weather_module.py` into this file, "
        "updating imports to use the new modular structure."
    )
    
    st.markdown("""
    ### Next Steps for Migration:
    
    1. **Import from modules** instead of local definitions:
       ```python
       from tawhiri.space_weather.scales import r_scale, s_scale, g_scale
       from tawhiri.space_weather.constants import NOAA_URLS, R_SCALE_THRESHOLDS
       from tawhiri.space_weather.data_fetchers import fetch_json, fetch_text
       ```
    
    2. **Keep your UI logic here** - All Streamlit widgets, tabs, and rendering
    
    3. **Use config instead of hardcoded values**:
       ```python
       config = get_config()
       api_key = config['space_weather']['noaa_api_key']
       ```
    
    4. **Test incrementally** - Migrate one section at a time
    """)
    
    # Example of using modular imports
    st.subheader("Example: Scale Classifications")
    
    from tawhiri.space_weather.scales import r_scale, s_scale, g_scale
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        xray_flux = st.number_input("X-ray Flux (W/m²)", value=1e-5, format="%.2e")
        level, severity = r_scale(xray_flux)
        st.metric("R Scale", f"{level} ({severity})")
    
    with col2:
        proton_flux = st.number_input("Proton Flux (pfu)", value=10.0, format="%.1f")
        level, severity = s_scale(proton_flux)
        st.metric("S Scale", f"{level} ({severity})")
    
    with col3:
        kp_index = st.number_input("Kp Index", value=3.0, min_value=0.0, max_value=9.0)
        level, severity = g_scale(kp_index)
        st.metric("G Scale", f"{level} ({severity})")


def main():
    """Entry point for command-line execution"""
    run(set_page_config=True)


if __name__ == "__main__":
    main()
