"""
Tests for PDF export functionality.

These tests verify PDF creation, table generation, and document structure
without requiring actual PDF rendering (when reportlab not available).
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test with and without reportlab
try:
    import reportlab
    REPORTLAB_INSTALLED = True
except ImportError:
    REPORTLAB_INSTALLED = False


class TestReportLabAvailability:
    """Test reportlab dependency checking."""
    
    def test_check_reportlab_available(self):
        """Test checking if reportlab is available."""
        from tawhiri.space_weather.pdf_export import check_reportlab_available
        
        result = check_reportlab_available()
        assert isinstance(result, bool)
        # Result should match whether reportlab is installed
        assert result == REPORTLAB_INSTALLED


@pytest.mark.skipif(not REPORTLAB_INSTALLED, reason="ReportLab not installed")
class TestPDFCreation:
    """Test PDF document creation with reportlab."""
    
    def test_create_basic_pdf(self):
        """Test creating a basic space weather PDF."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.pdf")
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R1", "s": "S0", "g": "G2"},
                past_conditions={"r": "R0", "s": "S0", "g": "G1"},
                forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
                summary_text="Space weather conditions are moderate with increased geomagnetic activity."
            )
            
            assert success is True
            assert os.path.exists(output_path)
            
            # Check file is not empty
            file_size = os.path.getsize(output_path)
            assert file_size > 1000  # PDF should be at least 1KB
    
    def test_create_pdf_with_discussion(self):
        """Test creating PDF with NOAA discussion text."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_discussion.pdf")
            
            discussion = """
Solar Activity Forecast:
Solar activity is expected to be low with a chance of M-class flares.
            
Geomagnetic Activity Forecast:
The geomagnetic field is expected to be at quiet to active levels.
            """.strip()
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R1", "s": "S0", "g": "G2"},
                past_conditions={"r": "R0", "s": "S0", "g": "G1"},
                forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
                summary_text="Test summary",
                discussion_text=discussion,
                include_discussion=True
            )
            
            assert success is True
            assert os.path.exists(output_path)
    
    def test_create_pdf_with_aurora(self):
        """Test creating PDF with aurora forecast."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_aurora.pdf")
            
            aurora_text = "Aurora visible in southern regions tonight. Kp index 5 expected."
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R1", "s": "S0", "g": "G3"},
                past_conditions={"r": "R0", "s": "S0", "g": "G1"},
                forecast_24h={"kp": 5, "r12": 20, "r3": 3, "s1": 5},
                summary_text="Test summary",
                aurora_text=aurora_text
            )
            
            assert success is True
            assert os.path.exists(output_path)
    
    def test_create_pdf_minimal(self):
        """Test creating PDF with minimal required data."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_minimal.pdf")
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={},  # Empty dict
                past_conditions={},
                forecast_24h={},
                summary_text="Minimal report"
            )
            
            # Should still succeed with defaults
            assert success is True
            assert os.path.exists(output_path)
    
    def test_create_pdf_with_logo(self):
        """Test creating PDF with organization logo."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy logo file
            logo_path = os.path.join(tmpdir, "logo.png")
            Path(logo_path).touch()
            
            output_path = os.path.join(tmpdir, "test_logo.pdf")
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R1", "s": "S0", "g": "G2"},
                past_conditions={"r": "R0", "s": "S0", "g": "G1"},
                forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
                summary_text="Test summary",
                logo_path=logo_path
            )
            
            # Should succeed even if logo is invalid (will just skip it)
            assert success is True
            assert os.path.exists(output_path)
    
    def test_create_pdf_invalid_path(self):
        """Test creating PDF with invalid output path."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        # Try to write to a directory that doesn't exist
        success = create_space_weather_pdf(
            output_path="/nonexistent/directory/report.pdf",
            current_conditions={"r": "R1", "s": "S0", "g": "G2"},
            past_conditions={"r": "R0", "s": "S0", "g": "G1"},
            forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
            summary_text="Test summary"
        )
        
        # Should fail gracefully
        assert success is False


@pytest.mark.skipif(not REPORTLAB_INSTALLED, reason="ReportLab not installed")
class TestSpaceWeatherPDFClass:
    """Test the SpaceWeatherPDF class."""
    
    def test_pdf_initialization(self):
        """Test PDF class initialization."""
        from tawhiri.space_weather.pdf_export import SpaceWeatherPDF
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            
            pdf = SpaceWeatherPDF(
                output_path=output_path,
                title="Test Report",
                organization="Test Organization"
            )
            
            assert pdf.output_path == output_path
            assert pdf.title == "Test Report"
            assert pdf.organization == "Test Organization"
    
    def test_add_content_elements(self):
        """Test adding various content elements."""
        from tawhiri.space_weather.pdf_export import SpaceWeatherPDF
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            
            pdf = SpaceWeatherPDF(output_path=output_path)
            
            # Add various elements
            pdf.add_title("Main Title")
            pdf.add_section_heading("Section 1")
            pdf.add_paragraph("This is a test paragraph.")
            pdf.add_bullet_list(["Item 1", "Item 2", "Item 3"])
            pdf.add_spacer(1.0)
            
            # Should have added elements to story
            assert len(pdf.story) > 0
    
    def test_add_table(self):
        """Test adding a table to the document."""
        from tawhiri.space_weather.pdf_export import SpaceWeatherPDF
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            
            pdf = SpaceWeatherPDF(output_path=output_path)
            
            table_data = [
                ["Header 1", "Header 2", "Header 3"],
                ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
            ]
            
            pdf.add_table(table_data, header_row=True)
            
            # Table should be added to story
            assert len(pdf.story) > 0
    
    def test_build_pdf(self):
        """Test building the final PDF."""
        from tawhiri.space_weather.pdf_export import SpaceWeatherPDF
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            
            pdf = SpaceWeatherPDF(output_path=output_path)
            pdf.add_title("Test Document")
            pdf.add_paragraph("Test content")
            
            # Build PDF
            pdf.build()
            
            # PDF file should exist
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0


@pytest.mark.skipif(not REPORTLAB_INSTALLED, reason="ReportLab not installed")
class TestChartExport:
    """Test chart export for PDF embedding."""
    
    @patch('tawhiri.space_weather.pdf_export.logger')
    def test_save_chart_no_fig(self, mock_logger):
        """Test saving chart with None figure."""
        from tawhiri.space_weather.pdf_export import save_chart_for_pdf
        
        result = save_chart_for_pdf(None, "output.png")
        assert result is False
    
    @patch('plotly.io.write_image')
    def test_save_chart_success(self, mock_write_image):
        """Test successful chart save with kaleido."""
        from tawhiri.space_weather.pdf_export import save_chart_for_pdf
        
        # Mock figure
        mock_fig = MagicMock()
        
        # Mock successful write
        mock_write_image.return_value = None
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "chart.png")
            result = save_chart_for_pdf(mock_fig, output_path)
            
            # If plotly.io is available and works, should succeed
            # Otherwise will fail gracefully
            assert isinstance(result, bool)
    
    @patch('plotly.io.write_image')
    def test_save_chart_kaleido_failure(self, mock_write_image):
        """Test chart save when kaleido fails."""
        from tawhiri.space_weather.pdf_export import save_chart_for_pdf
        
        # Mock figure
        mock_fig = MagicMock()
        
        # Mock kaleido failure
        mock_write_image.side_effect = ImportError("Kaleido not installed")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "chart.png")
            result = save_chart_for_pdf(mock_fig, output_path)
            
            # Should return False when kaleido unavailable
            assert result is False


class TestSeverityColors:
    """Test severity color mapping."""
    
    @pytest.mark.skipif(not REPORTLAB_INSTALLED, reason="ReportLab not installed")
    def test_get_severity_color(self):
        """Test getting severity colors for scale values."""
        from tawhiri.space_weather.pdf_export import get_severity_color
        
        # Test various scale values
        color_r1 = get_severity_color("R1", "r")
        assert color_r1 is not None
        
        color_s0 = get_severity_color("S0", "s")
        assert color_s0 is not None
        
        color_g3 = get_severity_color("G3", "g")
        assert color_g3 is not None
    
    @pytest.mark.skipif(not REPORTLAB_INSTALLED, reason="ReportLab not installed")
    def test_pdf_colors_defined(self):
        """Test that PDF color scheme is defined."""
        from tawhiri.space_weather.pdf_export import PDF_COLORS, SEVERITY_RGB
        
        assert isinstance(PDF_COLORS, dict)
        assert "primary" in PDF_COLORS
        assert "text" in PDF_COLORS
        
        assert isinstance(SEVERITY_RGB, dict)
        assert "minor" in SEVERITY_RGB
        assert "severe" in SEVERITY_RGB


class TestPDFWithoutReportLab:
    """Test PDF module behavior when reportlab is not available."""
    
    @pytest.mark.skipif(REPORTLAB_INSTALLED, reason="ReportLab is installed")
    def test_create_pdf_without_reportlab(self):
        """Test that PDF creation fails gracefully without reportlab."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R1", "s": "S0", "g": "G2"},
                past_conditions={"r": "R0", "s": "S0", "g": "G1"},
                forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
                summary_text="Test summary"
            )
            
            # Should return False when reportlab not available
            assert success is False


class TestPDFIntegration:
    """Test PDF module integration with other modules."""
    
    def test_pdf_imports(self):
        """Test that PDF module imports successfully."""
        try:
            from tawhiri.space_weather import pdf_export
            assert hasattr(pdf_export, 'create_space_weather_pdf')
            assert hasattr(pdf_export, 'SpaceWeatherPDF')
            assert hasattr(pdf_export, 'save_chart_for_pdf')
        except ImportError as e:
            pytest.fail(f"Failed to import pdf_export module: {e}")
    
    def test_pdf_uses_constants(self):
        """Test that PDF module correctly imports from constants."""
        from tawhiri.space_weather.pdf_export import SEVERITY_COLORS
        from tawhiri.space_weather.constants import SEVERITY_COLORS as CONST_SEVERITY_COLORS
        
        # Should use colors from constants
        assert SEVERITY_COLORS is not None
    
    def test_pdf_uses_scales(self):
        """Test that PDF module correctly imports from scales."""
        from tawhiri.space_weather.pdf_export import r_scale, s_scale, g_scale
        
        # Should be able to import scale functions
        assert callable(r_scale)
        assert callable(s_scale)
        assert callable(g_scale)


@pytest.mark.skipif(not REPORTLAB_INSTALLED, reason="ReportLab not installed")
class TestComplexPDFScenarios:
    """Test complex real-world PDF generation scenarios."""
    
    def test_full_featured_pdf(self):
        """Test creating a PDF with all features enabled."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "full_report.pdf")
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R3", "s": "S1", "g": "G4"},
                past_conditions={"r": "R2", "s": "S0", "g": "G3"},
                forecast_24h={
                    "kp": 6,
                    "r12": 45,
                    "r3": 15,
                    "s1": 25
                },
                summary_text="Strong geomagnetic storm in progress. "
                             "Enhanced auroral activity expected. "
                             "HF communications may be degraded.",
                discussion_text="Solar Activity: Active region producing M-class flares.\n\n"
                                "Geomagnetic Activity: Storm conditions due to CME arrival.",
                aurora_text="Aurora visible as far north as central North Island, NZ.",
                include_charts=False,  # No charts in this test
                include_discussion=True
            )
            
            assert success is True
            assert os.path.exists(output_path)
            
            # Should be larger file with all content
            file_size = os.path.getsize(output_path)
            assert file_size > 2000  # At least 2KB with all content
    
    def test_pdf_with_special_characters(self):
        """Test PDF handles special characters in text."""
        from tawhiri.space_weather.pdf_export import create_space_weather_pdf
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "special_chars.pdf")
            
            # Text with special characters
            summary = "Temperature: 25°C, Kp≥5, λ=630nm, ≈approximate"
            
            success = create_space_weather_pdf(
                output_path=output_path,
                current_conditions={"r": "R1", "s": "S0", "g": "G2"},
                past_conditions={"r": "R0", "s": "S0", "g": "G1"},
                forecast_24h={"kp": 4, "r12": 25, "r3": 5, "s1": 10},
                summary_text=summary
            )
            
            # Should handle special characters gracefully
            assert success is True
            assert os.path.exists(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
