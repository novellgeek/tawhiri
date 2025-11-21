"""
Space Weather Plotting Functions

This module provides reusable chart creation functions for space weather data visualization.
Uses Plotly for interactive charts with consistent styling.

Functions:
    - create_xray_chart: X-ray flux time series
    - create_proton_chart: Proton flux time series
    - create_kp_chart: Kp index time series
    - create_timeseries_chart: Generic configurable time series chart
"""

from typing import Optional, Dict, List, Any
import plotly.graph_objects as go
from plotly.graph_objs import Figure

from .data_fetchers import fetch_json
from .utils import clamp_float
from .constants import SEVERITY_COLORS


# Default chart styling
DEFAULT_CHART_CONFIG = {
    "height": 220,
    "margin": {"l": 10, "r": 10, "t": 30, "b": 10},
    "xaxis_color": "#9fc8ff",
    "yaxis_color": "#9fc8ff",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
}


def create_timeseries_chart(
    data: List[Dict[str, Any]],
    time_field: str = "time_tag",
    value_field: str = "flux",
    title: str = "Time Series",
    y_label: str = "Value",
    trace_name: str = "Data",
    height: int = 220,
    log_y: bool = False,
    color: str = "#1f77b4",
    **layout_kwargs
) -> Optional[Figure]:
    """
    Create a generic time series chart from data.
    
    Args:
        data: List of data dictionaries containing time and value fields
        time_field: Key name for time data (default: "time_tag")
        value_field: Key name for value data (default: "flux")
        title: Chart title
        y_label: Y-axis label
        trace_name: Name for the data trace
        height: Chart height in pixels
        log_y: Use logarithmic y-axis
        color: Line color
        **layout_kwargs: Additional Plotly layout parameters
        
    Returns:
        Plotly Figure object or None if data is invalid
        
    Example:
        >>> data = [{"time_tag": "2025-01-01T00:00:00Z", "flux": 1.5e-6}, ...]
        >>> fig = create_timeseries_chart(data, title="X-ray Flux")
        >>> fig.show()
    """
    if not data:
        return None
        
    # Extract times and values
    times = [row.get(time_field) for row in data if time_field in row]
    values = [row.get(value_field, 0) for row in data]
    
    if not times or not values:
        return None
    
    # Create figure
    fig = go.Figure()
    
    # Add trace
    fig.add_trace(
        go.Scatter(
            x=times,
            y=values,
            mode="lines",
            name=trace_name,
            line=dict(color=color)
        )
    )
    
    # Base layout
    layout_config = {
        "title": title,
        "height": height,
        "margin": DEFAULT_CHART_CONFIG["margin"],
        "xaxis": {
            "title": "Time",
            "color": DEFAULT_CHART_CONFIG["xaxis_color"]
        },
        "yaxis": {
            "title": y_label,
            "color": DEFAULT_CHART_CONFIG["yaxis_color"],
            "type": "log" if log_y else "linear"
        },
        "plot_bgcolor": DEFAULT_CHART_CONFIG["plot_bgcolor"],
        "paper_bgcolor": DEFAULT_CHART_CONFIG["paper_bgcolor"],
    }
    
    # Merge with custom layout kwargs
    layout_config.update(layout_kwargs)
    
    fig.update_layout(**layout_config)
    
    return fig


def create_xray_chart(
    url: str = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json",
    title: str = "X-rays (6-hour)",
    height: int = 220,
    **kwargs
) -> Optional[Figure]:
    """
    Create X-ray flux chart from NOAA GOES data.
    
    The X-ray flux is measured in watts per square meter (W/m²) and indicates
    solar flare activity. Values are plotted on a logarithmic scale.
    
    Args:
        url: NOAA JSON endpoint for X-ray data
        title: Chart title
        height: Chart height in pixels
        **kwargs: Additional parameters passed to create_timeseries_chart
        
    Returns:
        Plotly Figure object or None if data fetch fails
        
    Example:
        >>> fig = create_xray_chart()
        >>> if fig:
        ...     fig.show()
    """
    data = fetch_json(url)
    if not data:
        return None
        
    return create_timeseries_chart(
        data=data,
        time_field="time_tag",
        value_field="flux",
        title=title,
        y_label="Flux (W/m²)",
        trace_name="X-ray Flux",
        height=height,
        log_y=True,  # X-ray flux is typically shown on log scale
        color=SEVERITY_COLORS.get("R3", "#ff9500"),  # Orange
        **kwargs
    )


def create_proton_chart(
    url: str = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
    title: str = "Integral Protons (1-day)",
    height: int = 220,
    **kwargs
) -> Optional[Figure]:
    """
    Create proton flux chart from NOAA GOES data.
    
    The proton flux is measured in particles per square cm per second per steradian (pfu)
    and indicates radiation storm activity. Values are plotted on a logarithmic scale.
    
    Args:
        url: NOAA JSON endpoint for proton data
        title: Chart title
        height: Chart height in pixels
        **kwargs: Additional parameters passed to create_timeseries_chart
        
    Returns:
        Plotly Figure object or None if data fetch fails
        
    Example:
        >>> fig = create_proton_chart()
        >>> if fig:
        ...     fig.show()
    """
    data = fetch_json(url)
    if not data:
        return None
        
    return create_timeseries_chart(
        data=data,
        time_field="time_tag",
        value_field="flux",
        title=title,
        y_label="Flux (pfu)",
        trace_name="Proton Flux",
        height=height,
        log_y=True,  # Proton flux is typically shown on log scale
        color=SEVERITY_COLORS.get("S3", "#ffc800"),  # Yellow
        **kwargs
    )


def create_kp_chart(
    url: str = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
    title: str = "Kp Index (1-minute)",
    height: int = 220,
    **kwargs
) -> Optional[Figure]:
    """
    Create Kp index chart from NOAA data.
    
    The Kp index ranges from 0 to 9 and indicates geomagnetic storm activity.
    Values >= 5 indicate minor to severe geomagnetic storms.
    
    Args:
        url: NOAA JSON endpoint for Kp data
        title: Chart title
        height: Chart height in pixels
        **kwargs: Additional parameters passed to create_timeseries_chart
        
    Returns:
        Plotly Figure object or None if data fetch fails
        
    Example:
        >>> fig = create_kp_chart()
        >>> if fig:
        ...     fig.show()
    """
    kp_data = fetch_json(url)
    if not kp_data:
        return None
    
    # Extract times and clamped Kp values
    times = [row.get("time_tag") for row in kp_data if "time_tag" in row]
    kp_values = [clamp_float(row.get("kp_index", 0)) for row in kp_data]
    
    if not times or not kp_values:
        return None
    
    # Create figure manually to allow for custom Kp-specific features
    fig = go.Figure()
    
    # Add Kp trace
    fig.add_trace(
        go.Scatter(
            x=times,
            y=kp_values,
            mode="lines",
            name="Kp Index",
            line=dict(color=SEVERITY_COLORS.get("G3", "#ffc800"))
        )
    )
    
    # Add horizontal line at Kp=5 (storm threshold)
    fig.add_hline(
        y=5,
        line_dash="dash",
        line_color="red",
        annotation_text="Storm Threshold (Kp≥5)",
        annotation_position="right"
    )
    
    # Layout
    fig.update_layout(
        title=title,
        height=height,
        margin=DEFAULT_CHART_CONFIG["margin"],
        xaxis=dict(title="Time", color=DEFAULT_CHART_CONFIG["xaxis_color"]),
        yaxis=dict(
            title="Kp Index",
            color=DEFAULT_CHART_CONFIG["yaxis_color"],
            range=[0, 9]  # Kp always 0-9
        ),
        plot_bgcolor=DEFAULT_CHART_CONFIG["plot_bgcolor"],
        paper_bgcolor=DEFAULT_CHART_CONFIG["paper_bgcolor"],
        **kwargs
    )
    
    return fig


def create_multi_threshold_chart(
    data: List[Dict[str, Any]],
    time_field: str,
    value_field: str,
    thresholds: Dict[str, float],
    title: str,
    y_label: str,
    height: int = 300,
    log_y: bool = False
) -> Optional[Figure]:
    """
    Create a chart with multiple threshold lines (e.g., R-scale thresholds).
    
    Args:
        data: List of data dictionaries
        time_field: Key for time data
        value_field: Key for value data
        thresholds: Dict mapping threshold names to values (e.g., {"R1": 1e-5, "R2": 1e-4})
        title: Chart title
        y_label: Y-axis label
        height: Chart height
        log_y: Use log scale for y-axis
        
    Returns:
        Plotly Figure with data trace and threshold lines
        
    Example:
        >>> thresholds = {"R1": 1e-5, "R2": 1e-4, "R3": 1e-3}
        >>> fig = create_multi_threshold_chart(
        ...     data, "time_tag", "flux", thresholds,
        ...     "X-ray Flux with R-scale", "Flux (W/m²)"
        ... )
    """
    if not data:
        return None
    
    # Create base chart
    fig = create_timeseries_chart(
        data=data,
        time_field=time_field,
        value_field=value_field,
        title=title,
        y_label=y_label,
        height=height,
        log_y=log_y
    )
    
    if not fig:
        return None
    
    # Add threshold lines
    for name, value in thresholds.items():
        fig.add_hline(
            y=value,
            line_dash="dash",
            line_color=SEVERITY_COLORS.get(name, "gray"),
            annotation_text=name,
            annotation_position="right"
        )
    
    return fig


# Module exports
__all__ = [
    "create_xray_chart",
    "create_proton_chart",
    "create_kp_chart",
    "create_timeseries_chart",
    "create_multi_threshold_chart",
    "DEFAULT_CHART_CONFIG",
]
