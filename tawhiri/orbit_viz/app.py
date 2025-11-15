"""
Orbit Visualization Streamlit Application

Main UI entry point for the 3D/2D orbit visualization module.
This is where you'll migrate your existing globe_sidebar_module.py run() function.
"""

import streamlit as st
import logging
from tawhiri.config import get_config
from tawhiri.common import setup_logging

logger = logging.getLogger(__name__)


def run(set_page_config: bool = True):
    """
    Main entry point for Orbit Visualization Streamlit UI.
    
    Args:
        set_page_config: Whether to call st.set_page_config (set False if 
                        integrating into larger dashboard)
    
    TODO: Migrate content from your existing globe_sidebar_module.py here.
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
        logger.info("Orbit Visualization module started")
    
    # Page config
    if set_page_config:
        st.set_page_config(
            page_title="TAWHIRI Orbit Visualization",
            page_icon="🛰️",
            layout="wide",
        )
    
    # Temporary placeholder UI
    st.title("🛰️ TAWHIRI Orbit Visualization")
    st.info(
        "**Migration in progress:** This is the modular version of the orbit visualization module. "
        "Copy your existing UI code from `globe_sidebar_module.py` into this file, "
        "updating imports to use the new modular structure."
    )
    
    st.markdown("""
    ### Next Steps for Migration:
    
    1. **Import from modules** instead of local definitions:
       ```python
       from tawhiri.orbit_viz.tle_parser import read_multi_epoch_tle_file
       from tawhiri.orbit_viz.constants import EARTH_RADIUS_KM, GEO_ALTITUDE_KM
       from tawhiri.orbit_viz.orbital_math import coverage_radius_deg
       from tawhiri.orbit_viz.plotting_3d import plot_orbits
       from tawhiri.orbit_viz.plotting_2d import plot_ground_2d
       ```
    
    2. **Use config for file paths**:
       ```python
       config = get_config()
       tle_file = config['orbit_viz']['tle_file']
       textures_dir = config['orbit_viz']['earth_textures_dir']
       ```
    
    3. **Update Skyfield to use local cache**:
       ```python
       from skyfield.api import Loader
       loader = Loader(config['orbit_viz']['skyfield_cache'])
       ts = loader.timescale()
       ```
    
    4. **Test incrementally** - Start with basic orbit plotting, then add features
    """)


def main():
    """Entry point for command-line execution"""
    run(set_page_config=True)


if __name__ == "__main__":
    main()
