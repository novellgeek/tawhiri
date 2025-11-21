"""
Tests for Tawhiri common utilities.

Tests logging, TLE parsing, file I/O, time utilities, and math functions.
"""

import pytest
import tempfile
import io
import json
from pathlib import Path
from datetime import datetime, timezone
import math

from tawhiri.common import (
    # Constants
    EARTH_RADIUS_KM, MU_EARTH, GEO_ALTITUDE,
    # Logging
    setup_logger, get_logger,
    # File I/O
    load_json, save_json, _lines_from_source,
    # TLE parsing
    validate_tle, parse_tle_line1, parse_tle_line2,
    load_tles, read_multi_epoch_tle_file,
    # Time
    utc_now, format_timestamp, parse_timestamp,
    # Math
    deg_to_rad, rad_to_deg, normalize_angle, haversine_distance
)


# Sample TLE data for testing
SAMPLE_TLE_ISS = [
    "ISS (ZARYA)",
    "1 25544U 98067A   25326.50000000  .00016717  00000-0  10270-3 0  9005",
    "2 25544  51.6400 208.5800 0002571  89.2100  53.4900 15.54225995123456"
]

SAMPLE_TLE_2LINE = [
    "1 25544U 98067A   25326.50000000  .00016717  00000-0  10270-3 0  9005",
    "2 25544  51.6400 208.5800 0002571  89.2100  53.4900 15.54225995123456"
]


class TestConstants:
    """Test that constants are defined correctly."""
    
    def test_earth_constants(self):
        """Test Earth physical constants."""
        assert EARTH_RADIUS_KM > 0
        assert MU_EARTH > 0
        assert GEO_ALTITUDE > 0
        assert GEO_ALTITUDE == 35786
    
    def test_constant_relationships(self):
        """Test relationships between constants."""
        # GEO altitude should be about 35,786 km
        assert 35000 < GEO_ALTITUDE < 36000


class TestLogging:
    """Test logging utilities."""
    
    def test_setup_logger(self):
        """Test logger creation."""
        logger = setup_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
    
    def test_get_logger(self):
        """Test getting existing logger."""
        logger1 = setup_logger("test_get_logger")
        logger2 = get_logger("test_get_logger")
        assert logger1 is logger2
    
    def test_logger_with_file(self):
        """Test logger with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger("test_file_logger", log_file=str(log_file))
            logger.info("Test message")
            
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content


class TestFileIO:
    """Test file I/O utilities."""
    
    def test_lines_from_string_path(self):
        """Test reading lines from file path."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("line 1\nline 2\n\nline 3\n")
            f.flush()
            temp_path = f.name
        
        try:
            lines = _lines_from_source(temp_path)
            assert len(lines) == 3
            assert lines[0] == "line 1"
            assert lines[2] == "line 3"
        finally:
            Path(temp_path).unlink()
    
    def test_lines_from_path_object(self):
        """Test reading lines from Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("line 1\nline 2\n")
            
            lines = _lines_from_source(path)
            assert len(lines) == 2
    
    def test_lines_from_bytes(self):
        """Test reading lines from bytes."""
        data = b"line 1\nline 2\nline 3\n"
        lines = _lines_from_source(data)
        assert len(lines) == 3
        assert lines[1] == "line 2"
    
    def test_lines_from_filelike(self):
        """Test reading lines from file-like object."""
        data = io.StringIO("line 1\nline 2\n")
        lines = _lines_from_source(data)
        assert len(lines) == 2
    
    def test_lines_from_invalid_source(self):
        """Test error handling for invalid source."""
        with pytest.raises(ValueError):
            _lines_from_source(12345)  # Invalid type
    
    def test_load_json_success(self):
        """Test loading valid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            test_data = {"key": "value", "number": 42}
            json_file.write_text(json.dumps(test_data))
            
            loaded = load_json(json_file)
            assert loaded == test_data
    
    def test_load_json_missing_file(self):
        """Test loading non-existent JSON file."""
        result = load_json("/nonexistent/file.json", default={"default": True})
        assert result == {"default": True}
    
    def test_load_json_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "invalid.json"
            json_file.write_text("{invalid json}")
            
            result = load_json(json_file, default=None)
            assert result is None
    
    def test_save_json_success(self):
        """Test saving JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "output.json"
            test_data = {"test": "data"}
            
            success = save_json(test_data, json_file)
            assert success is True
            assert json_file.exists()
            
            # Verify content
            loaded = json.loads(json_file.read_text())
            assert loaded == test_data


class TestTLEParsing:
    """Test TLE parsing functions."""
    
    def test_validate_tle_valid(self):
        """Test validation of valid TLE."""
        line1, line2 = SAMPLE_TLE_ISS[1], SAMPLE_TLE_ISS[2]
        assert validate_tle(line1, line2) is True
    
    def test_validate_tle_too_short(self):
        """Test validation rejects short lines."""
        assert validate_tle("short", "lines") is False
    
    def test_validate_tle_wrong_line_numbers(self):
        """Test validation checks line numbers."""
        line1 = "2" + " " * 68  # Wrong line number
        line2 = "2 25544  51.6400 208.5800 0002571  89.2100  53.4900 15.54225995123456"
        assert validate_tle(line1, line2) is False
    
    def test_parse_tle_line1(self):
        """Test parsing TLE line 1."""
        line1 = SAMPLE_TLE_ISS[1]
        data = parse_tle_line1(line1)
        
        assert data['line_number'] == 1
        assert data['norad_id'] == "25544"
        assert data['classification'] == 'U'
        assert 'epoch_year' in data
        assert 'epoch_day' in data
    
    def test_parse_tle_line2(self):
        """Test parsing TLE line 2."""
        line2 = SAMPLE_TLE_ISS[2]
        data = parse_tle_line2(line2)
        
        assert data['line_number'] == 2
        assert data['norad_id'] == "25544"
        assert 50 < data['inclination'] < 52
        assert 15 < data['mean_motion'] < 16
        assert 0 <= data['eccentricity'] < 1
    
    def test_load_tles_3line_format(self):
        """Test loading 3-line TLE format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tle_file = Path(tmpdir) / "tles.txt"
            tle_file.write_text('\n'.join(SAMPLE_TLE_ISS))
            
            tles = load_tles(tle_file)
            assert len(tles) == 1
            assert "25544" in tles
            
            name, line1, line2 = tles["25544"]
            assert "ISS" in name
            assert line1.startswith("1 ")
            assert line2.startswith("2 ")
    
    def test_load_tles_2line_format(self):
        """Test loading 2-line TLE format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tle_file = Path(tmpdir) / "tles.txt"
            tle_file.write_text('\n'.join(SAMPLE_TLE_2LINE))
            
            tles = load_tles(tle_file)
            assert len(tles) == 1
            
            name, line1, line2 = tles["25544"]
            assert name == "Unknown"  # No name in 2-line format
    
    def test_load_tles_from_bytes(self):
        """Test loading TLEs from bytes."""
        data = '\n'.join(SAMPLE_TLE_ISS).encode('utf-8')
        tles = load_tles(data)
        assert len(tles) == 1
        assert "25544" in tles
    
    def test_load_tles_invalid_format(self):
        """Test handling of invalid TLE format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tle_file = Path(tmpdir) / "invalid.txt"
            tle_file.write_text("invalid\ntle\ndata\n")
            
            tles = load_tles(tle_file)
            # Should handle gracefully, might be empty
            assert isinstance(tles, dict)
    
    def test_read_multi_epoch_tle_file(self):
        """Test loading multi-epoch TLE file."""
        # Create multi-epoch TLE data (same satellite, different epochs)
        multi_epoch_data = SAMPLE_TLE_ISS + [
            "ISS (ZARYA)",
            "1 25544U 98067A   25327.50000000  .00016717  00000-0  10270-3 0  9006",
            "2 25544  51.6400 208.5800 0002571  89.2100  53.4900 15.54225995123457"
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tle_file = Path(tmpdir) / "multi_epoch.txt"
            tle_file.write_text('\n'.join(multi_epoch_data))
            
            tles = read_multi_epoch_tle_file(tle_file)
            assert "ISS (ZARYA)" in tles
            assert len(tles["ISS (ZARYA)"]) == 2  # Two epochs


class TestTimeUtilities:
    """Test time utility functions."""
    
    def test_utc_now(self):
        """Test UTC now function."""
        now = utc_now()
        assert isinstance(now, datetime)
        assert now.tzinfo == timezone.utc
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2025, 11, 22, 10, 30, 0, tzinfo=timezone.utc)
        formatted = format_timestamp(dt)
        assert "2025-11-22" in formatted
        assert "10:30:00" in formatted
    
    def test_format_timestamp_custom_format(self):
        """Test custom timestamp format."""
        dt = datetime(2025, 11, 22, 10, 30, 0)
        formatted = format_timestamp(dt, "%Y/%m/%d")
        assert formatted == "2025/11/22"
    
    def test_parse_timestamp_valid(self):
        """Test parsing valid timestamp."""
        dt = parse_timestamp("2025-11-22 10:30:00")
        assert isinstance(dt, datetime)
        assert dt.year == 2025
        assert dt.month == 11
        assert dt.day == 22
    
    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        dt = parse_timestamp("invalid")
        assert dt is None


class TestMathUtilities:
    """Test math utility functions."""
    
    def test_deg_to_rad(self):
        """Test degree to radian conversion."""
        assert abs(deg_to_rad(0) - 0) < 1e-10
        assert abs(deg_to_rad(180) - math.pi) < 1e-10
        assert abs(deg_to_rad(360) - 2*math.pi) < 1e-10
    
    def test_rad_to_deg(self):
        """Test radian to degree conversion."""
        assert abs(rad_to_deg(0) - 0) < 1e-10
        assert abs(rad_to_deg(math.pi) - 180) < 1e-10
        assert abs(rad_to_deg(2*math.pi) - 360) < 1e-10
    
    def test_deg_rad_roundtrip(self):
        """Test degree/radian conversion round trip."""
        angle = 123.456
        assert abs(rad_to_deg(deg_to_rad(angle)) - angle) < 1e-10
    
    def test_normalize_angle_positive(self):
        """Test angle normalization for positive angles."""
        assert normalize_angle(370) == 10.0
        assert normalize_angle(720) == 0.0
        assert normalize_angle(180) == 180.0
    
    def test_normalize_angle_negative(self):
        """Test angle normalization for negative angles."""
        assert normalize_angle(-10) == 350.0
        assert normalize_angle(-370) == 350.0
    
    def test_normalize_angle_custom_range(self):
        """Test angle normalization with custom range."""
        assert normalize_angle(190, -180, 180) == -170.0
        assert normalize_angle(370, -180, 180) == 10.0
    
    def test_haversine_distance_zero(self):
        """Test haversine distance between same point."""
        dist = haversine_distance(0, 0, 0, 0)
        assert abs(dist) < 1e-6
    
    def test_haversine_distance_known(self):
        """Test haversine distance for known locations."""
        # Wellington to Auckland (approx 640 km)
        wellington_lat, wellington_lon = -41.28, 174.78
        auckland_lat, auckland_lon = -36.85, 174.76
        
        dist = haversine_distance(
            wellington_lat, wellington_lon,
            auckland_lat, auckland_lon
        )
        
        # Should be approximately 640 km
        assert 600 < dist < 680
    
    def test_haversine_distance_equator(self):
        """Test haversine distance along equator."""
        # 1 degree longitude at equator ≈ 111 km
        dist = haversine_distance(0, 0, 0, 1)
        assert 100 < dist < 120


class TestIntegration:
    """Integration tests for common utilities."""
    
    def test_tle_workflow(self):
        """Test complete TLE loading and parsing workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create TLE file
            tle_file = Path(tmpdir) / "sats.txt"
            tle_file.write_text('\n'.join(SAMPLE_TLE_ISS))
            
            # Load TLEs
            tles = load_tles(tle_file)
            assert len(tles) > 0
            
            # Get ISS TLE
            name, line1, line2 = tles["25544"]
            
            # Validate
            assert validate_tle(line1, line2)
            
            # Parse
            data1 = parse_tle_line1(line1)
            data2 = parse_tle_line2(line2)
            
            # Check parsed data
            assert data1['norad_id'] == "25544"
            assert data2['norad_id'] == "25544"
            assert 0 <= data2['eccentricity'] < 1
    
    def test_json_roundtrip(self):
        """Test JSON save and load roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            
            original_data = {
                "string": "value",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "list": [1, 2, 3],
                "nested": {"key": "value"}
            }
            
            # Save
            success = save_json(original_data, json_file)
            assert success
            
            # Load
            loaded_data = load_json(json_file)
            assert loaded_data == original_data
    
    def test_logging_and_file_io(self):
        """Test logging with file I/O operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger("test_integration", log_file=str(log_file))
            
            # Create and log TLE file operations
            tle_file = Path(tmpdir) / "tles.txt"
            tle_file.write_text('\n'.join(SAMPLE_TLE_ISS))
            
            logger.info("Loading TLEs")
            tles = load_tles(tle_file)
            logger.info(f"Loaded {len(tles)} TLEs")
            
            # Check log file
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "Loading TLEs" in log_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
