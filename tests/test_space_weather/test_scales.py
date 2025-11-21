"""
Tests for Space Weather Scales Module
======================================

Run with: pytest tests/test_space_weather/test_scales.py -v
"""

import pytest
from tawhiri.space_weather.scales import (
    r_scale,
    s_scale,
    g_scale,
    g_scale_from_kp,
    g_scale_auto,
    ap_to_kp,
    get_severity_class,
)


class TestRScale:
    """Test R-scale (Radio Blackout) calculations."""
    
    def test_r0_quiet(self):
        """Test R0 - quiet conditions."""
        assert r_scale(1e-6) == ("R0", "quiet")
        assert r_scale(5e-6) == ("R0", "quiet")
    
    def test_r1_minor(self):
        """Test R1 - minor event (M1-M4 flares)."""
        assert r_scale(1e-5) == ("R1", "minor")
        assert r_scale(3e-5) == ("R1", "minor")
    
    def test_r2_moderate(self):
        """Test R2 - moderate event (M5-M9 flares)."""
        assert r_scale(5e-5) == ("R2", "moderate")
        assert r_scale(9e-5) == ("R2", "moderate")
    
    def test_r3_strong(self):
        """Test R3 - strong event (X1-X9 flares)."""
        assert r_scale(1e-4) == ("R3", "strong")
        assert r_scale(5e-4) == ("R3", "strong")
    
    def test_r4_severe(self):
        """Test R4 - severe event (X10-X19 flares)."""
        assert r_scale(1e-3) == ("R4", "severe")
        assert r_scale(1.5e-3) == ("R4", "severe")
    
    def test_r5_extreme(self):
        """Test R5 - extreme event (X20+ flares)."""
        assert r_scale(2e-3) == ("R5", "extreme")
        assert r_scale(1e-2) == ("R5", "extreme")


class TestSScale:
    """Test S-scale (Solar Radiation Storm) calculations."""
    
    def test_s0_quiet(self):
        """Test S0 - quiet conditions."""
        assert s_scale(5) == ("S0", "quiet")
        assert s_scale(9.9) == ("S0", "quiet")
    
    def test_s1_minor(self):
        """Test S1 - minor storm (10-99 pfu)."""
        assert s_scale(10) == ("S1", "minor")
        assert s_scale(50) == ("S1", "minor")
    
    def test_s2_moderate(self):
        """Test S2 - moderate storm (100-999 pfu)."""
        assert s_scale(100) == ("S2", "moderate")
        assert s_scale(500) == ("S2", "moderate")
    
    def test_s3_strong(self):
        """Test S3 - strong storm (1,000-9,999 pfu)."""
        assert s_scale(1000) == ("S3", "strong")
        assert s_scale(5000) == ("S3", "strong")
    
    def test_s4_severe(self):
        """Test S4 - severe storm (10,000-99,999 pfu)."""
        assert s_scale(10000) == ("S4", "severe")
        assert s_scale(50000) == ("S4", "severe")
    
    def test_s5_extreme(self):
        """Test S5 - extreme storm (>=100,000 pfu)."""
        assert s_scale(100000) == ("S5", "extreme")
        assert s_scale(500000) == ("S5", "extreme")


class TestGScale:
    """Test G-scale (Geomagnetic Storm) calculations."""
    
    def test_g0_quiet(self):
        """Test G0 - quiet conditions (Kp<5)."""
        assert g_scale(0) == ("G0", "quiet")
        assert g_scale(4.5) == ("G0", "quiet")
    
    def test_g1_minor(self):
        """Test G1 - minor storm (Kp=5)."""
        assert g_scale(5) == ("G1", "minor")
        assert g_scale(5.9) == ("G1", "minor")
    
    def test_g2_moderate(self):
        """Test G2 - moderate storm (Kp=6)."""
        assert g_scale(6) == ("G2", "moderate")
        assert g_scale(6.5) == ("G2", "moderate")
    
    def test_g3_strong(self):
        """Test G3 - strong storm (Kp=7)."""
        assert g_scale(7) == ("G3", "strong")
        assert g_scale(7.8) == ("G3", "strong")
    
    def test_g4_severe(self):
        """Test G4 - severe storm (Kp=8)."""
        assert g_scale(8) == ("G4", "severe")
        assert g_scale(8.7) == ("G4", "severe")
    
    def test_g5_extreme(self):
        """Test G5 - extreme storm (Kp=9)."""
        assert g_scale(9) == ("G5", "extreme")
        assert g_scale(9.5) == ("G5", "extreme")


class TestApToKp:
    """Test Ap to Kp conversion."""
    
    def test_low_ap(self):
        """Test low Ap values."""
        assert ap_to_kp(0) == 0.0
        assert ap_to_kp(5) == 1.0
        assert ap_to_kp(10) == 2.0
    
    def test_moderate_ap(self):
        """Test moderate Ap values."""
        assert ap_to_kp(30) == 4.0
        assert ap_to_kp(50) == 5.0
        assert ap_to_kp(100) == 6.0
    
    def test_high_ap(self):
        """Test high Ap values."""
        assert ap_to_kp(150) == 7.0
        assert ap_to_kp(250) == 8.0
        assert ap_to_kp(450) == 9.0


class TestGScaleAuto:
    """Test automatic G-scale calculation from Kp or Ap."""
    
    def test_from_kp(self):
        """Test calculation from Kp index."""
        assert g_scale_auto(7.2, kind="kp") == ("G3", "strong")
        assert g_scale_auto(5.0, kind="kp") == ("G1", "minor")
    
    def test_from_ap(self):
        """Test calculation from Ap index."""
        # Ap=150 -> Kp=7 -> G3
        assert g_scale_auto(150, kind="ap") == ("G3", "strong")
        # Ap=50 -> Kp=5 -> G1
        assert g_scale_auto(50, kind="ap") == ("G1", "minor")


class TestSeverityClass:
    """Test severity class mapping."""
    
    def test_r_scale_severity(self):
        """Test R-scale severity mapping."""
        assert get_severity_class("R0") == "ok"
        assert get_severity_class("R1") == "caution"
        assert get_severity_class("R2") == "caution"
        assert get_severity_class("R3") == "watch"
        assert get_severity_class("R4") == "severe"
        assert get_severity_class("R5") == "severe"
    
    def test_s_scale_severity(self):
        """Test S-scale severity mapping."""
        assert get_severity_class("S0") == "ok"
        assert get_severity_class("S1") == "caution"
        assert get_severity_class("S3") == "watch"
        assert get_severity_class("S5") == "severe"
    
    def test_g_scale_severity(self):
        """Test G-scale severity mapping."""
        assert get_severity_class("G0") == "ok"
        assert get_severity_class("G1") == "ok"
        assert get_severity_class("G2") == "caution"
        assert get_severity_class("G3") == "watch"
        assert get_severity_class("G5") == "severe"
    
    def test_case_insensitive(self):
        """Test that scale level is case-insensitive."""
        assert get_severity_class("r3") == "watch"
        assert get_severity_class("S2") == "caution"
        assert get_severity_class("g4") == "severe"
    
    def test_invalid_input(self):
        """Test handling of invalid inputs."""
        assert get_severity_class("X9") == "severe"  # Unknown scale
        assert get_severity_class("") == "severe"
        assert get_severity_class(None) == "severe"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
