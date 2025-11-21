"""
Space Weather Dashboard - Streamlit Application

Professional space weather monitoring dashboard for NZDF operations.
Integrates real-time NOAA and BOM data with NZ-specific operational translations.

Usage:
    streamlit run app.py
    
Or import into larger dashboard:
    from tawhiri.space_weather.app import run
    run()
"""

import streamlit as st
from streamlit.components.v1 import html
from datetime import datetime
import tempfile
import base64
import os

# Import our modular components
from .constants import SEVERITY_COLORS, NOAA_URLS
from .scales import r_scale, s_scale, g_scale, g_scale_from_kp
from .data_fetchers import (
    get_noaa_rsg_now_and_past,
    get_3day_summary,
    get_next24_summary,
    make_summary,
    fetch_json,
    fetch_text
)
from .plotting import create_xray_chart, create_proton_chart, create_kp_chart
from .pdf_export import create_space_weather_pdf, save_chart_for_pdf
from .nz_translations import rewrite_to_nz, _r_class, _s_class, _g_class
from .utils import last_updated

import logging
logger = logging.getLogger(__name__)


def run(set_page_config: bool = False):
    """
    Render the Space Weather dashboard UI.
    
    Args:
        set_page_config: If True, call st.set_page_config() for standalone use.
                        Set False when importing into existing app.
    """
    
    # Page configuration (only if running standalone)
    if set_page_config:
        try:
            st.set_page_config(
                page_title="Space Weather Dashboard",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except Exception:
            # Ignore if already set by parent app
            pass
    
    # ========== Sidebar Settings ==========
    with st.sidebar:
        st.markdown("## Dashboard Settings")
        
        # Auto-refresh
        refresh_min = st.slider("Auto-refresh (minutes)", 0, 30, 10)
        if refresh_min > 0:
            interval_ms = int(refresh_min * 60 * 1000)
            html(
                f"<script>setTimeout(function(){{ window.location.reload(); }}, {interval_ms});</script>",
                height=0
            )
        
        # Display settings
        high_contrast = st.toggle("High-contrast mode", True)
        font_scale = st.slider("Font scale", 1.0, 1.6, 1.2, 0.05)
        
        st.markdown("---")
        st.caption(f"Last updated: {last_updated()}")
    
    _high_contrast = bool(high_contrast)
    _font_scale = float(font_scale)
    
    # ========== Global Styles ==========
    apply_styles(_font_scale, _high_contrast)
    
    # ========== Fetch Data ==========
    with st.spinner("Loading space weather data..."):
        # Current and past conditions
        past, current = get_noaa_rsg_now_and_past()
        
        # 3-day forecast
        forecast_3day = get_3day_summary()
        day1 = forecast_3day['days'][0] if forecast_3day['days'] else {}
        day2 = forecast_3day['days'][1] if len(forecast_3day['days']) > 1 else {}
        day3 = forecast_3day['days'][2] if len(forecast_3day['days']) > 2 else {}
        
        # Next 24h summary
        next24 = get_next24_summary()
        
        # Executive summary
        summary_text = make_summary(current, next24)
        
        # BOM Aurora data (optional)
        bom_aurora_text = fetch_text("https://www.sws.bom.gov.au/HF_Systems/6/3")
        
        # NOAA Discussion
        noaa_discussion_raw = fetch_text(NOAA_URLS['discussion'])
    
    # ========== Tab Structure ==========
    tabs = st.tabs([
        "Overview",
        "24h Operations Impact",
        "Charts",
        "Forecasts",
        "Aurora",
        "Expert Data",
        "PDF Export",
        "Help & Info"
    ])
    
    # ========== Overview Tab ==========
    with tabs[0]:
        render_overview_tab(current, past, next24, summary_text)
    
    # ========== 24h Operations Impact Tab ==========
    with tabs[1]:
        render_operations_impact_tab(current, next24, day1)
    
    # ========== Charts Tab ==========
    with tabs[2]:
        render_charts_tab()
    
    # ========== Forecasts Tab ==========
    with tabs[3]:
        render_forecasts_tab(day1, day2, day3)
    
    # ========== Aurora Tab ==========
    with tabs[4]:
        render_aurora_tab(bom_aurora_text, current)
    
    # ========== Expert Data Tab ==========
    with tabs[5]:
        render_expert_data_tab(noaa_discussion_raw, past, current, next24)
    
    # ========== PDF Export Tab ==========
    with tabs[6]:
        render_pdf_export_tab(
            current, past, day1, summary_text,
            noaa_discussion_raw, bom_aurora_text
        )
    
    # ========== Help & Info Tab ==========
    with tabs[7]:
        render_help_tab()
    
    # Footer
    st.caption(f"Server time: {last_updated()} • Refresh page to update feeds.")


def apply_styles(font_scale: float, high_contrast: bool):
    """Apply global CSS styles to the dashboard."""
    neon = "#00ffff" if high_contrast else "#8be9fd"
    fg = "#ffffff" if high_contrast else "#dbe7ff"
    bg = "#0a0a0a" if high_contrast else "#0d1419"
    card = "#0f0f0f" if high_contrast else "#111a21"
    border = "#ffffff90" if high_contrast else "rgba(139,233,253,.25)"
    
    st.markdown(f"""
    <style>
    :root {{
      --scale: {font_scale};
      --neon: {neon};
      --fg: {fg};
      --bg: {bg};
      --card: {card};
      --border: {border};
    }}
    html, body, .main, .block-container {{ font-size: calc(16px * var(--scale)); }}
    .badge-col {{ display:flex; gap:.5rem; flex-wrap:wrap; margin:.5rem 0 1rem 0; }}
    .neon-badge {{ padding:.35rem .6rem; border-radius:.5rem; border:1px solid var(--border); color:var(--fg); }}
    .box {{ background:var(--card); border:1px solid var(--border); border-radius:.6rem; padding:.75rem; }}
    .box h5 {{ margin:.2rem 0 .6rem 0; color:#cfe3ff; font-size:1rem; }}
    .rs-inline {{ display:flex; gap:.35rem; flex-wrap:wrap; }}
    .rs-pill {{ padding:.18rem .45rem; border-radius:.45rem; color:#0a0a0a; font-weight:700; }}
    .ok {{ background:#2ecc71; color:#0b0b0b; }}
    .caution {{ background:#f1c40f; color:#0b0b0b; }}
    .watch {{ background:#e67e22; color:#0b0b0b; }}
    .severe {{ background:#e74c3c; color:#0b0b0b; }}
    </style>
    """, unsafe_allow_html=True)


def render_overview_tab(current: dict, past: dict, next24: dict, summary: str):
    """Render the Overview tab with current conditions."""
    st.markdown("## Space Weather Overview")
    
    # Current Status
    st.markdown("### Current Conditions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### R - Radio Blackouts")
        r_value = current.get('r', 'R0')
        r_class = _r_class(r_value)
        st.markdown(f'<div class="rs-pill {r_class}">{r_value}</div>', unsafe_allow_html=True)
        st.caption("Solar X-ray flares affecting HF radio")
    
    with col2:
        st.markdown("#### S - Radiation Storms")
        s_value = current.get('s', 'S0')
        s_class = _s_class(s_value)
        st.markdown(f'<div class="rs-pill {s_class}">{s_value}</div>', unsafe_allow_html=True)
        st.caption("Solar energetic particles")
    
    with col3:
        st.markdown("#### G - Geomagnetic Storms")
        g_value = current.get('g', 'G0')
        g_class = _g_class(g_value)
        st.markdown(f'<div class="rs-pill {g_class}">{g_value}</div>', unsafe_allow_html=True)
        st.caption("Disturbances in Earth's magnetic field")
    
    # Executive Summary
    st.markdown("### Executive Summary")
    st.info(summary)
    
    # Past 24h
    st.markdown("### Past 24 Hours")
    st.markdown(f"""
    - **R-scale:** {past.get('r', 'R0')}
    - **S-scale:** {past.get('s', 'S0')}
    - **G-scale:** {past.get('g', 'G0')}
    """)
    
    # Next 24h forecast
    st.markdown("### Next 24 Hours Forecast")
    kp = next24.get('kp', '~')
    r12 = next24.get('r12', 0)
    r3 = next24.get('r3', 0)
    s1 = next24.get('s1', 0)
    
    st.markdown(f"""
    - **Kp Index:** ~{kp}
    - **R1-R2 Probability:** {r12}%
    - **R3+ Probability:** {r3}%
    - **S1+ Probability:** {s1}%
    """)


def render_operations_impact_tab(current: dict, next24: dict, day1: dict):
    """Render the 24h Operations Impact tab with NZ-specific impacts."""
    st.markdown("## 24-Hour Operational Impact Assessment")
    
    st.info("NZ-specific operational impacts for NZDF planning and decision-making.")
    
    # HF Communications Impact
    st.markdown("### 📡 HF Communications")
    r_now = current.get('r', 'R0')
    r_nz = rewrite_to_nz("solar_activity", "", r_now=r_now)
    st.markdown(r_nz)
    
    # GNSS/GPS Impact
    st.markdown("### 📍 GNSS/GPS Systems")
    g_now = current.get('g', 'G0')
    g_nz = rewrite_to_nz("geospace", "", g_now=g_now)
    st.markdown(g_nz)
    
    # Radiation Environment
    st.markdown("### ☢️ Radiation Environment")
    s_now = current.get('s', 'S0')
    s_nz = rewrite_to_nz("solar_wind", "", s_now=s_now)
    st.markdown(s_nz)
    
    # Aurora Likelihood
    st.markdown("### 🌌 Aurora Activity")
    kp = next24.get('kp', 0)
    if kp >= 5:
        st.success("Aurora visible in southern NZ likely tonight!")
    elif kp >= 4:
        st.info("Possible aurora in far southern regions (Southland, Stewart Island)")
    else:
        st.caption("Low aurora probability for NZ tonight")


def render_charts_tab():
    """Render the Charts tab with live space weather data."""
    st.markdown("## Real-Time Space Weather Charts")
    
    # X-ray Flux
    st.markdown("### X-ray Flux (6-hour)")
    xray_fig = create_xray_chart()
    if xray_fig:
        st.plotly_chart(xray_fig, use_container_width=True)
    else:
        st.warning("X-ray chart data unavailable")
    
    # Proton Flux
    st.markdown("### Proton Flux (24-hour)")
    proton_fig = create_proton_chart()
    if proton_fig:
        st.plotly_chart(proton_fig, use_container_width=True)
    else:
        st.warning("Proton chart data unavailable")
    
    # Kp Index
    st.markdown("### Kp Index (Geomagnetic Activity)")
    kp_fig = create_kp_chart()
    if kp_fig:
        st.plotly_chart(kp_fig, use_container_width=True)
    else:
        st.warning("Kp chart data unavailable")


def render_forecasts_tab(day1: dict, day2: dict, day3: dict):
    """Render the Forecasts tab with 3-day outlook."""
    st.markdown("## 3-Day Space Weather Forecast")
    
    days = [
        ("Day 1 (Today/Tomorrow)", day1),
        ("Day 2", day2),
        ("Day 3", day3)
    ]
    
    for day_name, day_data in days:
        with st.expander(f"### {day_name}", expanded=(day_name == "Day 1 (Today/Tomorrow)")):
            if not day_data:
                st.caption("Forecast data unavailable")
                continue
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Solar Activity**")
                st.markdown(f"- R1-R2: {day_data.get('r12', 0)}%")
                st.markdown(f"- R3+: {day_data.get('r3', 0)}%")
                
                st.markdown("**Radiation**")
                st.markdown(f"- S1+: {day_data.get('s1', 0)}%")
            
            with col2:
                st.markdown("**Geomagnetic Activity**")
                kp = day_data.get('kp')
                if kp:
                    st.markdown(f"- Kp: ~{kp}")
                    g_label, g_severity = g_scale_from_kp(kp)
                    st.markdown(f"- G-scale: {g_label} ({g_severity})")


def render_aurora_tab(bom_text: str, current: dict):
    """Render the Aurora tab with BOM data and visibility predictions."""
    st.markdown("## Aurora Forecast (BOM)")
    
    if bom_text:
        st.markdown("### Australian Bureau of Meteorology Outlook")
        st.text(bom_text[:500])  # First 500 chars
        
        with st.expander("Full BOM Aurora Forecast"):
            st.text(bom_text)
    else:
        st.warning("BOM aurora data unavailable")
    
    # NZ-specific aurora guidance
    st.markdown("### Aurora Visibility for New Zealand")
    
    g_now = current.get('g', 'G0')
    g_level = int(g_now[1]) if len(g_now) > 1 and g_now[1].isdigit() else 0
    
    if g_level >= 4:
        st.success("🌌 Strong aurora likely visible in South Island and possibly lower North Island!")
    elif g_level >= 3:
        st.info("🌌 Aurora probable in Southland, Otago, and possibly Canterbury")
    elif g_level >= 2:
        st.info("🌌 Aurora possible in far southern regions (Stewart Island, Southland)")
    else:
        st.caption("Low aurora probability tonight. G3+ storms needed for NZ visibility.")


def render_expert_data_tab(discussion: str, past: dict, current: dict, next24: dict):
    """Render the Expert Data tab with raw NOAA information."""
    st.markdown("## Expert Data & Raw Feeds")
    
    st.warning("⚠️ This tab contains technical NOAA data for expert analysis")
    
    # NOAA Discussion
    with st.expander("NOAA Space Weather Discussion (Full Text)", expanded=True):
        if discussion:
            st.text(discussion)
        else:
            st.caption("Discussion text unavailable")
    
    # Raw scale data
    with st.expander("Raw R/S/G Scale Data"):
        st.json({
            "current": current,
            "past_24h": past,
            "next_24h": next24
        })


def render_pdf_export_tab(
    current: dict,
    past: dict,
    day1: dict,
    summary: str,
    discussion: str,
    aurora: str
):
    """Render the PDF Export tab."""
    st.markdown("## Export Management PDF Report")
    
    st.info("Generate a professional PDF report for briefings and operational planning.")
    
    # Options
    include_charts = st.checkbox("Include charts (requires kaleido)", value=False)
    include_discussion = st.checkbox("Include NOAA discussion", value=True)
    
    if st.button("Generate PDF Report"):
        with st.spinner("Creating PDF..."):
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    # Prepare chart paths if requested
                    chart_paths = {}
                    if include_charts:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            # Generate and save charts
                            xray_fig = create_xray_chart()
                            if xray_fig:
                                path = f"{tmpdir}/xray.png"
                                if save_chart_for_pdf(xray_fig, path):
                                    chart_paths["X-ray Flux"] = path
                            
                            proton_fig = create_proton_chart()
                            if proton_fig:
                                path = f"{tmpdir}/proton.png"
                                if save_chart_for_pdf(proton_fig, path):
                                    chart_paths["Proton Flux"] = path
                            
                            kp_fig = create_kp_chart()
                            if kp_fig:
                                path = f"{tmpdir}/kp.png"
                                if save_chart_for_pdf(kp_fig, path):
                                    chart_paths["Kp Index"] = path
                    
                    # Create PDF
                    success = create_space_weather_pdf(
                        output_path=tmp.name,
                        current_conditions=current,
                        past_conditions=past,
                        forecast_24h=day1,
                        summary_text=summary,
                        discussion_text=discussion if include_discussion else None,
                        aurora_text=aurora,
                        chart_paths=chart_paths if chart_paths else None,
                        organization="NZDF Space Weather Service",
                        include_charts=include_charts,
                        include_discussion=include_discussion
                    )
                    
                    if success:
                        # Read PDF and offer download
                        with open(tmp.name, "rb") as f:
                            pdf_bytes = f.read()
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        filename = f"space_weather_report_{timestamp}.pdf"
                        
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf"
                        )
                        st.success("✅ PDF generated successfully!")
                    else:
                        st.error("❌ PDF generation failed. Check that reportlab is installed.")
                
                # Clean up temp file
                try:
                    os.unlink(tmp.name)
                except:
                    pass
                    
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
                logger.error(f"PDF generation error: {e}")


def render_help_tab():
    """Render the Help & Info tab."""
    st.markdown("## Help & Information")
    
    st.info(
        "This dashboard displays real-time space weather data from NOAA and BOM, "
        "including solar activity, geomagnetic storms, and aurora outlooks. "
        "Use the tabs above to view detailed charts, expert data, and export management-grade PDFs."
    )
    
    st.markdown("### Key Metrics Explained")
    st.markdown("""
    - **R scale**: Radio blackout risk due to solar flares (affects HF communications)
    - **S scale**: Solar radiation storms (affects satellites, aviation, astronauts)
    - **G scale**: Geomagnetic storm risk from Kp index (affects GNSS, power grids, aurora)
    - **Aurora**: Visibility and disruption risk from BOM forecasts
    """)
    
    st.markdown("### Data Sources")
    st.markdown("""
    - **NOAA Space Weather Prediction Center (SWPC)**: <https://www.swpc.noaa.gov/>
    - **Australian Bureau of Meteorology (BOM) Space Weather Service**: <https://www.sws.bom.gov.au/>
    """)
    
    st.markdown("### Credits & Attribution")
    st.markdown("""
    This application acknowledges and thanks:
    - **National Oceanic and Atmospheric Administration (NOAA)** — [SWPC](https://www.swpc.noaa.gov/)
    - **Australian Bureau of Meteorology (BOM)** — [SWS](https://www.sws.bom.gov.au/)
    
    Data are used under each provider's respective terms of use and availability.
    """)
    
    st.markdown("### Feedback & Support")
    st.markdown("For feature requests or bug reports, contact your system administrator.")


# Entry point for standalone execution
if __name__ == "__main__":
    run(set_page_config=True)
