"""
Tests for Space Weather Data Fetchers Module
============================================

Run with: pytest tests/test_space_weather/test_data_fetchers.py -v
"""

import pytest
from unittest.mock import patch, Mock
from tawhiri.space_weather.data_fetchers import (
    fetch_json,
    fetch_text,
    parse_three_day_full,
    parse_three_day_for_next24,
    get_noaa_rsg_now_and_past,
    make_summary,
)


class TestFetchFunctions:
    """Test core fetch functions with mocked requests."""
    
    @patch('tawhiri.space_weather.data_fetchers.requests.get')
    def test_fetch_json_success(self, mock_get):
        """Test successful JSON fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetch_json("http://example.com/test.json")
        
        assert result == {"test": "data"}
        mock_get.assert_called_once()
    
    @patch('tawhiri.space_weather.data_fetchers.requests.get')
    def test_fetch_json_failure(self, mock_get):
        """Test JSON fetch handles errors gracefully."""
        mock_get.side_effect = Exception("Network error")
        
        result = fetch_json("http://example.com/test.json")
        
        assert result is None
    
    @patch('tawhiri.space_weather.data_fetchers.requests.get')
    def test_fetch_text_success(self, mock_get):
        """Test successful text fetch."""
        mock_response = Mock()
        mock_response.text = "Sample text content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fetch_text("http://example.com/test.txt")
        
        assert result == "Sample text content"
    
    @patch('tawhiri.space_weather.data_fetchers.requests.get')
    def test_fetch_text_failure(self, mock_get):
        """Test text fetch handles errors gracefully."""
        mock_get.side_effect = Exception("Network error")
        
        result = fetch_text("http://example.com/test.txt")
        
        assert result == ""


class TestThreeDayParsing:
    """Test 3-day forecast parsing functions."""
    
    def test_parse_three_day_full_basic(self):
        """Test parsing basic 3-day forecast."""
        sample_text = """
        R1-R2 10% 15% 20%
        R3 or greater 1% 2% 3%
        S1 or greater 5% 10% 15%
        00-03UT 4.0 5.0 6.0
        03-06UT 4.5 5.5 6.5
        """
        
        result = parse_three_day_full(sample_text)
        
        assert "days" in result
        assert len(result["days"]) == 3
        
        # Check day 1
        day1 = result["days"][0]
        assert day1["r12"] == 10
        assert day1["r3"] == 1
        assert day1["s1"] == 5
        assert day1["kp"] == 4.5  # Max from column 1
        assert day1["g"] in ["G0", "G1", "G2", "G3", "G4", "G5"]
    
    def test_parse_three_day_full_no_data(self):
        """Test parsing when no forecast data present."""
        result = parse_three_day_full("No forecast data available")
        
        assert "days" in result
        assert len(result["days"]) == 3
        
        # All days should have zero/None values
        for day in result["days"]:
            assert day["r12"] == 0
            assert day["r3"] == 0
            assert day["s1"] == 0
    
    def test_parse_three_day_for_next24_basic(self):
        """Test parsing focused on next 24h."""
        sample_text = """
        R1-R2 25% 15% 10%
        R3 or greater 5% 2% 1%
        S1 or greater 15% 10% 5%
        00-03UT 6.0 5.0 4.0
        """
        
        result = parse_three_day_for_next24(sample_text)
        
        assert result["r12_prob"] == 25
        assert result["r3_prob"] == 5
        assert result["s1_prob"] == 15
        assert result["kp_max"] == "6.00"
        assert result["r_bucket"] == "R1"  # r12 >= 10
        assert result["s_bucket"] == "S1"  # s1 >= 10
        assert result["g_bucket"] in ["G0", "G1", "G2", "G3"]
    
    def test_parse_three_day_for_next24_high_activity(self):
        """Test parsing with high activity forecast."""
        sample_text = """
        R1-R2 80% 60% 40%
        R3 or greater 25% 15% 5%
        S1 or greater 50% 30% 10%
        00-03UT 7.5 7.0 6.0
        """
        
        result = parse_three_day_for_next24(sample_text)
        
        assert result["r_bucket"] == "R2"  # r3 >= 1
        assert result["s_bucket"] == "S1"  # s1 >= 10
        assert float(result["kp_max"]) >= 7.0


class TestNOAARSGData:
    """Test NOAA R/S/G current and past data fetching."""
    
    @patch('tawhiri.space_weather.data_fetchers.fetch_json')
    def test_get_noaa_rsg_quiet_conditions(self, mock_fetch):
        """Test getting R/S/G data during quiet conditions."""
        # Mock quiet conditions data
        mock_fetch.side_effect = [
            # Kp data
            [{"kp_index": 2.0}, {"kp_index": 2.3}, {"kp_index": 2.1}],
            # X-ray data
            [{"flux": 1e-7}, {"flux": 2e-7}, {"flux": 1.5e-7}],
            # Proton data
            [{"flux": 0.5}, {"flux": 0.8}, {"flux": 0.6}],
        ]
        
        past, current = get_noaa_rsg_now_and_past()
        
        # Should be quiet conditions
        assert current["r"] == "R0"
        assert current["s"] == "S0"
        assert current["g"] == "G0"
        assert current["r_status"] == "No"
        assert current["s_status"] == "No"
        assert current["g_status"] == "No"
    
    @patch('tawhiri.space_weather.data_fetchers.fetch_json')
    def test_get_noaa_rsg_active_conditions(self, mock_fetch):
        """Test getting R/S/G data during active conditions."""
        # Mock active conditions
        mock_fetch.side_effect = [
            # Kp data - geomagnetic storm
            [{"kp_index": 6.5}, {"kp_index": 7.0}, {"kp_index": 6.8}],
            # X-ray data - M-class flare
            [{"flux": 5e-5}, {"flux": 8e-5}, {"flux": 6e-5}],
            # Proton data - elevated
            [{"flux": 50}, {"flux": 80}, {"flux": 60}],
        ]
        
        past, current = get_noaa_rsg_now_and_past()
        
        # Should show activity
        assert current["r"] in ["R1", "R2"]
        assert current["s"] == "S1"
        assert current["g"] in ["G2", "G3"]
        assert current["r_status"] == "Active"
        assert current["s_status"] == "Active"
        assert current["g_status"] == "Active"
    
    @patch('tawhiri.space_weather.data_fetchers.fetch_json')
    def test_get_noaa_rsg_handles_failures(self, mock_fetch):
        """Test that failures return safe defaults."""
        # Mock all failures
        mock_fetch.return_value = None
        
        past, current = get_noaa_rsg_now_and_past()
        
        # Should return quiet conditions as default
        assert current["r"] == "R0"
        assert current["s"] == "S0"
        assert current["g"] == "G0"


class TestSummaryGeneration:
    """Test summary text generation."""
    
    def test_make_summary_quiet(self):
        """Test summary during quiet conditions."""
        current = {
            "r": "R0",
            "s": "S0",
            "g": "G0"
        }
        next24 = {
            "g_bucket": "G0",
            "kp_max": "2.5",
            "r12_prob": 5,
            "r3_prob": 0,
            "s1_prob": 2
        }
        
        summary = make_summary(current, next24)
        
        assert "R0/S0/G0" in summary
        assert "Nominal" in summary
        assert "G0" in summary
    
    def test_make_summary_active(self):
        """Test summary during active conditions."""
        current = {
            "r": "R2",
            "s": "S1",
            "g": "G2"
        }
        next24 = {
            "g_bucket": "G3",
            "kp_max": "7.2",
            "r12_prob": 45,
            "r3_prob": 15,
            "s1_prob": 25
        }
        
        summary = make_summary(current, next24)
        
        assert "R2/S1/G2" in summary
        assert "risk" in summary.lower() or "watch" in summary.lower()
        assert "G3" in summary
        assert "7.2" in summary


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_parse_three_day_malformed_text(self):
        """Test parsing with malformed input."""
        malformed_text = "RANDOM TEXT WITH NO FORECAST DATA %%% $$$ @@@"
        
        result = parse_three_day_full(malformed_text)
        
        # Should not crash and return valid structure
        assert "days" in result
        assert len(result["days"]) == 3
    
    def test_parse_three_day_empty_text(self):
        """Test parsing with empty input."""
        result = parse_three_day_full("")
        
        assert "days" in result
        assert len(result["days"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
