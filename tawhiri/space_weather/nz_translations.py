"""
NZ-Specific Translations

Converts technical space weather descriptions into plain English,
NZ-relevant operational impacts.

TODO: Migrate your rewrite_to_nz() and _nz_risk_phrase() functions here.
"""
# migration done 18 Nov 25

def rewrite_to_nz(section: str, text: str, *,
                  r_now="R0", s_now="S0", g_now="G0",
                  day1=None) -> str:
    tx = (text or "").strip()
    if not tx:
        base = "No significant activity reported."
    else:
        low = tx.lower()
        if section == "solar_activity":
            if _any(low, "x-class", "major flare", "significant flare"):
                base = "Major solar flares noted — higher chance of radio/GNSS issues across New Zealand."
            elif _any(low, "m-class", "moderate"):
                base = "Moderate solar flares observed — brief HF/GNSS hiccups possible over NZ."
            elif _any(low, "c-class", "low", "quiet"):
                base = "The Sun is fairly quiet — only small flares, negligible impact for NZ."
            else:
                base = "Solar activity is mixed but not unusual for the cycle; NZ impacts limited."
        elif section == "solar_wind":
            if _any(low, "cme", "shock", "sheath"):
                base = "A CME is influencing the solar wind — conditions can stir up NZ geomagnetic activity."
            elif _any(low, "high speed", "coronal hole", "600 km/s", "elevated"):
                base = "Solar wind is running fast — may unsettle Earth’s field; aurora possible in the far south."
            else:
                base = "Solar wind conditions are near normal — minimal impact expected over NZ."
        elif section == "geospace":
            if _any(low, "g2", "g3", "storm"):
                base = "Geomagnetic storming occurred — GNSS accuracy could dip; aurora chances improve in Southland."
            elif _any(low, "active", "unsettled"):
                base = "Field was unsettled — small GNSS wobbles possible; low aurora chance."
            else:
                base = "Geomagnetic field is quiet for NZ — comms and GNSS are stable."
        else:
            if _any(low, "elevated", "enhanced", "storm"):
                base = "Energetic particles elevated — low operational impact for NZ; monitor polar routes."
            else:
                base = "Radiation environment looks normal for NZ operations."

    # Choose ONLY the relevant risk line for this section
    if section == "solar_activity":
        r_cls = _r_class(r_now)
        main_risk = _nz_risk_phrase("R", _class_to_level(r_cls))
        return f"{base}{_NZ_REGIONAL_HINT}\n• {main_risk}"
    elif section == "solar_wind":
        s_cls = _s_class(s_now)
        main_risk = _nz_risk_phrase("S", _class_to_level(s_cls))
        return f"{base}{_NZ_REGIONAL_HINT}\n• {main_risk}"
    elif section == "geospace":
        g_cls = _g_class(g_now)
        main_risk = _nz_risk_phrase("G", _class_to_level(g_cls))
        return f"{base}{_NZ_REGIONAL_HINT}\n• {main_risk}"
    else:
        # fallback: just base (for energetic particle etc)
        return f"{base}{_NZ_REGIONAL_HINT}"
