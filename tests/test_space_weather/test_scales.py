"""
Tests for Space Weather Scale Classifications

Run with: pytest tests/test_space_weather/test_scales.py -v
"""

import pytest
from tawhiri.space_weather.scales import r_scale, s_scale, g_scale, ap_to_kp


class TestRScale:
    """Tests for R-scale (Radio Blackout) classification"""
    
    def test_r0_quiet(self):
        """Test quiet conditions (below R1 threshold)"""
        level, severity = r_scale(1e-6)
        assert level == "R0"
        assert severity == "quiet"
    
    def test_r1_minor(self):
        """Test R1 minor event (M1-M4 flares)"""
        level, severity = r_scale(1.5e-5)
        assert level == "R1"
        assert severity == "minor"
    
    def test_r2_moderate(self):
        """Test R2 moderate event (M5-M9 flares)"""
        level, severity = r_scale(7e-5)
        assert level == "R2"
        assert severity == "moderate"
    
    def test_r3_strong(self):
        """Test R3 strong event (X1-X9 flares)"""
        level, severity = r_scale(5e-4)
        assert level == "R3"
        assert severity == "strong"
    
    def test_r4_severe(self):
        """Test R4 severe event (X10-X19 flares)"""
        level, severity = r_scale(1.5e-3)
        assert level == "R4"
        assert severity == "severe"
    
    def test_r5_extreme(self):
        """Test R5 extreme event (X20+ flares)"""
        level, severity = r_scale(3e-3)
        assert level == "R5"
        assert severity == "extreme"
    
    def test_threshold_boundary(self):
        """Test exact threshold values"""
        # Exactly at R1 threshold
        level, severity = r_scale(1e-5)
        assert level == "R1"
        
        # Just below R1 threshold
        level, severity = r_scale(9.9e-6)
        assert level == "R0"


class TestSScale:
    """Tests for S-scale (Solar Radiation Storm) classification"""
    
    def test_s0_quiet(self):
        """Test quiet conditions (below S1 threshold)"""
        level, severity = s_scale(5.0)
        assert level == "S0"
        assert severity == "quiet"
    
    def test_s1_minor(self):
        """Test S1 minor event (10-99 pfu)"""
        level, severity = s_scale(50.0)
        assert level == "S1"
        assert severity == "minor"
    
    def test_s2_moderate(self):
        """Test S2 moderate event (100-999 pfu)"""
        level, severity = s_scale(500.0)
        assert level == "S2"
        assert severity == "moderate"
    
    def test_s3_strong(self):
        """Test S3 strong event (1000-9999 pfu)"""
        level, severity = s_scale(5000.0)
        assert level == "S3"
        assert severity == "strong"
    
    def test_s4_severe(self):
        """Test S4 severe event (10000-99999 pfu)"""
        level, severity = s_scale(50000.0)
        assert level == "S4"
        assert severity == "severe"
    
    def test_s5_extreme(self):
        """Test S5 extreme event (>=100000 pfu)"""
        level, severity = s_scale(150000.0)
        assert level == "S5"
        assert severity == "extreme"


class TestGScale:
    """Tests for G-scale (Geomagnetic Storm) classification"""
    
    def test_g0_quiet(self):
        """Test quiet conditions (Kp < 5)"""
        level, severity = g_scale(3.0)
        assert level == "G0"
        assert severity == "quiet"
    
    def test_g1_minor(self):
        """Test G1 minor storm (Kp 5)"""
        level, severity = g_scale(5.0)
        assert level == "G1"
        assert severity == "minor"
    
    def test_g2_moderate(self):
        """Test G2 moderate storm (Kp 6)"""
        level, severity = g_scale(6.0)
        assert level == "G2"
        assert severity == "moderate"
    
    def test_g3_strong(self):
        """Test G3 strong storm (Kp 7)"""
        level, severity = g_scale(7.0)
        assert level == "G3"
        assert severity == "strong"
    
    def test_g4_severe(self):
        """Test G4 severe storm (Kp 8)"""
        level, severity = g_scale(8.0)
        assert level == "G4"
        assert severity == "severe"
    
    def test_g5_extreme(self):
        """Test G5 extreme storm (Kp 9)"""
        level, severity = g_scale(9.0)
        assert level == "G5"
        assert severity == "extreme"


class TestApToKp:
    """Tests for Ap to Kp conversion"""
    
    def test_quiet_conditions(self):
        """Test quiet geomagnetic conditions"""
        kp = ap_to_kp(5)
        assert kp == 1.0
    
    def test_moderate_ap(self):
        """Test moderate Ap values"""
        kp = ap_to_kp(50)
        assert kp == 5.0
    
    def test_high_ap(self):
        """Test high Ap values"""
        kp = ap_to_kp(150)
        assert kp == 7.0
    
    def test_extreme_ap(self):
        """Test extreme Ap values"""
        kp = ap_to_kp(500)
        assert kp == 9.0
    
    def test_ap_thresholds(self):
        """Test Ap threshold boundaries"""
        assert ap_to_kp(2) == 0.0
        assert ap_to_kp(3) == 1.0
        assert ap_to_kp(27) == 4.0
        assert ap_to_kp(48) == 5.0
        assert ap_to_kp(400) == 9.0


# Historical event tests (real data validation)
class TestHistoricalEvents:
    """Tests using historical space weather events"""
    
    def test_halloween_storm_2003(self):
        """Halloween Storm 2003 - X28+ flare"""
        # Estimated X-ray flux for X28 flare
        flux = 2.8e-3
        level, severity = r_scale(flux)
        assert level == "R5"  # Should be extreme
    
    def test_carrington_event_equivalent(self):
        """Carrington Event equivalent - would be G5"""
        # Estimated Kp for Carrington-class event
        kp = 9.0
        level, severity = g_scale(kp)
        assert level == "G5"
        assert severity == "extreme"
    
    def test_typical_quiet_day(self):
        """Typical quiet day conditions"""
        # Background X-ray flux
        r_level, _ = r_scale(1e-8)
        # Quiet proton flux
        s_level, _ = s_scale(0.1)
        # Quiet Kp
        g_level, _ = g_scale(2.0)
        
        assert r_level == "R0"
        assert s_level == "S0"
        assert g_level == "G0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
