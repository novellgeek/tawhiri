"""
Tests for space weather plotting functions.

These tests verify chart creation, configuration, and error handling
without making actual API calls.
"""

import pytest
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go

# We'll test the plotting module
# For now, let's create placeholder tests that will work once the module is in place


class TestTimeseriesChart:
    """Test the generic time series chart creation."""
    
    def test_create_basic_chart(self):
        """Test creating a basic time series chart."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        # Sample data
        data = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1.5},
            {"time_tag": "2025-01-01T01:00:00Z", "flux": 2.0},
            {"time_tag": "2025-01-01T02:00:00Z", "flux": 1.8},
        ]
        
        fig = create_timeseries_chart(
            data=data,
            title="Test Chart",
            y_label="Test Value"
        )
        
        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1  # One trace
        assert fig.data[0].x == [d["time_tag"] for d in data]
        assert fig.data[0].y == [d["flux"] for d in data]
    
    def test_empty_data_returns_none(self):
        """Test that empty data returns None."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        fig = create_timeseries_chart(
            data=[],
            title="Empty Chart"
        )
        
        assert fig is None
    
    def test_missing_fields_returns_none(self):
        """Test that data with missing required fields returns None."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        # Data without the required fields
        data = [
            {"wrong_field": "2025-01-01T00:00:00Z"},
            {"another_field": 1.5},
        ]
        
        fig = create_timeseries_chart(
            data=data,
            time_field="time_tag",
            value_field="flux",
            title="Invalid Data Chart"
        )
        
        assert fig is None
    
    def test_custom_field_names(self):
        """Test using custom field names."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        data = [
            {"timestamp": "2025-01-01T00:00:00Z", "value": 10},
            {"timestamp": "2025-01-01T01:00:00Z", "value": 20},
        ]
        
        fig = create_timeseries_chart(
            data=data,
            time_field="timestamp",
            value_field="value",
            title="Custom Fields"
        )
        
        assert fig is not None
        assert fig.data[0].x == ["2025-01-01T00:00:00Z", "2025-01-01T01:00:00Z"]
        assert fig.data[0].y == [10, 20]
    
    def test_log_scale(self):
        """Test logarithmic y-axis."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        data = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1e-5},
            {"time_tag": "2025-01-01T01:00:00Z", "flux": 1e-4},
        ]
        
        fig = create_timeseries_chart(
            data=data,
            log_y=True,
            title="Log Scale Chart"
        )
        
        assert fig is not None
        assert fig.layout.yaxis.type == "log"
    
    def test_custom_height(self):
        """Test custom chart height."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        data = [{"time_tag": "2025-01-01T00:00:00Z", "flux": 1.0}]
        
        fig = create_timeseries_chart(
            data=data,
            height=400,
            title="Tall Chart"
        )
        
        assert fig is not None
        assert fig.layout.height == 400
    
    def test_custom_color(self):
        """Test custom line color."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        
        data = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1.0},
            {"time_tag": "2025-01-01T01:00:00Z", "flux": 2.0},
        ]
        
        fig = create_timeseries_chart(
            data=data,
            color="#ff0000",
            title="Red Line Chart"
        )
        
        assert fig is not None
        assert fig.data[0].line.color == "#ff0000"


class TestXrayChart:
    """Test X-ray flux chart creation."""
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_xray_chart_success(self, mock_fetch):
        """Test successful X-ray chart creation."""
        from tawhiri.space_weather.plotting import create_xray_chart
        
        # Mock API response
        mock_fetch.return_value = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1e-6},
            {"time_tag": "2025-01-01T01:00:00Z", "flux": 5e-6},
            {"time_tag": "2025-01-01T02:00:00Z", "flux": 1e-5},
        ]
        
        fig = create_xray_chart()
        
        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert "X-rays" in fig.layout.title.text
        assert fig.layout.yaxis.type == "log"  # Should be log scale
        
        # Verify fetch_json was called with correct URL
        mock_fetch.assert_called_once()
        assert "xrays-6-hour" in mock_fetch.call_args[0][0]
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_xray_chart_failure(self, mock_fetch):
        """Test X-ray chart when API fails."""
        from tawhiri.space_weather.plotting import create_xray_chart
        
        # Mock API failure
        mock_fetch.return_value = None
        
        fig = create_xray_chart()
        
        assert fig is None
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_xray_chart_custom_title(self, mock_fetch):
        """Test X-ray chart with custom title."""
        from tawhiri.space_weather.plotting import create_xray_chart
        
        mock_fetch.return_value = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1e-6},
        ]
        
        fig = create_xray_chart(title="Custom X-ray Title")
        
        assert fig is not None
        assert "Custom X-ray Title" in fig.layout.title.text


class TestProtonChart:
    """Test proton flux chart creation."""
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_proton_chart_success(self, mock_fetch):
        """Test successful proton chart creation."""
        from tawhiri.space_weather.plotting import create_proton_chart
        
        # Mock API response
        mock_fetch.return_value = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1.0},
            {"time_tag": "2025-01-01T01:00:00Z", "flux": 10.0},
            {"time_tag": "2025-01-01T02:00:00Z", "flux": 100.0},
        ]
        
        fig = create_proton_chart()
        
        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert "Protons" in fig.layout.title.text
        assert fig.layout.yaxis.type == "log"  # Should be log scale
        
        # Verify correct URL was used
        mock_fetch.assert_called_once()
        assert "integral-protons" in mock_fetch.call_args[0][0]
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_proton_chart_failure(self, mock_fetch):
        """Test proton chart when API fails."""
        from tawhiri.space_weather.plotting import create_proton_chart
        
        mock_fetch.return_value = None
        
        fig = create_proton_chart()
        
        assert fig is None


class TestKpChart:
    """Test Kp index chart creation."""
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_kp_chart_success(self, mock_fetch):
        """Test successful Kp chart creation."""
        from tawhiri.space_weather.plotting import create_kp_chart
        
        # Mock API response
        mock_fetch.return_value = [
            {"time_tag": "2025-01-01T00:00:00Z", "kp_index": 2.0},
            {"time_tag": "2025-01-01T01:00:00Z", "kp_index": 4.0},
            {"time_tag": "2025-01-01T02:00:00Z", "kp_index": 6.0},
        ]
        
        fig = create_kp_chart()
        
        assert fig is not None
        assert isinstance(fig, go.Figure)
        assert "Kp" in fig.layout.title.text
        assert fig.layout.yaxis.type != "log"  # Kp is linear scale
        assert fig.layout.yaxis.range == [0, 9]  # Kp range is 0-9
        
        # Check for storm threshold line
        hlines = [shape for shape in fig.layout.shapes if shape.type == 'line']
        assert len(hlines) >= 1  # Should have threshold line at Kp=5
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_kp_chart_with_clamping(self, mock_fetch):
        """Test Kp chart handles invalid values with clamping."""
        from tawhiri.space_weather.plotting import create_kp_chart
        
        # Mock API response with some invalid values
        mock_fetch.return_value = [
            {"time_tag": "2025-01-01T00:00:00Z", "kp_index": "not_a_number"},
            {"time_tag": "2025-01-01T01:00:00Z", "kp_index": 3.5},
            {"time_tag": "2025-01-01T02:00:00Z", "kp_index": None},
        ]
        
        fig = create_kp_chart()
        
        # Should still create chart, with clamped values
        assert fig is not None
        # Invalid values should be clamped to 0.0
        assert fig.data[0].y[0] == 0.0
        assert fig.data[0].y[1] == 3.5
        assert fig.data[0].y[2] == 0.0
    
    @patch('tawhiri.space_weather.plotting.fetch_json')
    def test_create_kp_chart_failure(self, mock_fetch):
        """Test Kp chart when API fails."""
        from tawhiri.space_weather.plotting import create_kp_chart
        
        mock_fetch.return_value = None
        
        fig = create_kp_chart()
        
        assert fig is None


class TestMultiThresholdChart:
    """Test chart with multiple threshold lines."""
    
    def test_create_multi_threshold_chart(self):
        """Test creating chart with threshold lines."""
        from tawhiri.space_weather.plotting import create_multi_threshold_chart
        
        data = [
            {"time_tag": "2025-01-01T00:00:00Z", "flux": 1e-6},
            {"time_tag": "2025-01-01T01:00:00Z", "flux": 5e-5},
            {"time_tag": "2025-01-01T02:00:00Z", "flux": 1e-3},
        ]
        
        thresholds = {
            "R1": 1e-5,
            "R2": 1e-4,
            "R3": 1e-3,
        }
        
        fig = create_multi_threshold_chart(
            data=data,
            time_field="time_tag",
            value_field="flux",
            thresholds=thresholds,
            title="X-ray with R-scale",
            y_label="Flux",
            log_y=True
        )
        
        assert fig is not None
        
        # Check for threshold lines (should be horizontal lines in layout.shapes)
        hlines = [shape for shape in fig.layout.shapes if shape.type == 'line']
        assert len(hlines) == len(thresholds)
    
    def test_multi_threshold_empty_data(self):
        """Test multi-threshold chart with empty data."""
        from tawhiri.space_weather.plotting import create_multi_threshold_chart
        
        fig = create_multi_threshold_chart(
            data=[],
            time_field="time_tag",
            value_field="flux",
            thresholds={"R1": 1e-5},
            title="Empty Chart",
            y_label="Flux"
        )
        
        assert fig is None


class TestChartConfiguration:
    """Test chart configuration and styling."""
    
    def test_default_chart_config(self):
        """Test that default configuration is properly defined."""
        from tawhiri.space_weather.plotting import DEFAULT_CHART_CONFIG
        
        assert "height" in DEFAULT_CHART_CONFIG
        assert "margin" in DEFAULT_CHART_CONFIG
        assert "xaxis_color" in DEFAULT_CHART_CONFIG
        assert "yaxis_color" in DEFAULT_CHART_CONFIG
    
    def test_chart_uses_severity_colors(self):
        """Test that charts use severity colors from constants."""
        from tawhiri.space_weather.plotting import create_timeseries_chart
        from tawhiri.space_weather.constants import SEVERITY_COLORS
        
        data = [{"time_tag": "2025-01-01T00:00:00Z", "flux": 1.0}]
        
        # Create chart and verify it can access SEVERITY_COLORS
        fig = create_timeseries_chart(
            data=data,
            title="Test",
            color=SEVERITY_COLORS.get("R3", "#ff9500")
        )
        
        assert fig is not None
        # The color should be from SEVERITY_COLORS or the fallback
        assert fig.data[0].line.color in [SEVERITY_COLORS.get("R3"), "#ff9500"]


# Integration test
class TestPlottingIntegration:
    """Test plotting module integration with other modules."""
    
    def test_plotting_imports(self):
        """Test that plotting module imports successfully."""
        try:
            from tawhiri.space_weather import plotting
            assert hasattr(plotting, 'create_xray_chart')
            assert hasattr(plotting, 'create_proton_chart')
            assert hasattr(plotting, 'create_kp_chart')
            assert hasattr(plotting, 'create_timeseries_chart')
        except ImportError as e:
            pytest.fail(f"Failed to import plotting module: {e}")
    
    def test_plotting_uses_data_fetchers(self):
        """Test that plotting module correctly imports from data_fetchers."""
        from tawhiri.space_weather.plotting import create_xray_chart
        from tawhiri.space_weather.data_fetchers import fetch_json
        
        # This should not raise ImportError
        assert callable(fetch_json)
    
    def test_plotting_uses_utils(self):
        """Test that plotting module correctly imports from utils."""
        from tawhiri.space_weather.plotting import create_kp_chart
        from tawhiri.space_weather.utils import clamp_float
        
        # This should not raise ImportError
        assert callable(clamp_float)
    
    def test_plotting_uses_constants(self):
        """Test that plotting module correctly imports from constants."""
        from tawhiri.space_weather.plotting import DEFAULT_CHART_CONFIG
        from tawhiri.space_weather.constants import SEVERITY_COLORS
        
        # This should not raise ImportError
        assert isinstance(SEVERITY_COLORS, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
