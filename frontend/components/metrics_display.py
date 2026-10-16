"""
Frontend Component: Metrics Display
Renders clean, minimalist stat cards for ITF PSNR, stability delta, and crop metrics.
"""

import streamlit as st
from typing import Dict, Any


def render_kpi_cards(results: Dict[str, Any]) -> None:
    """Renders 4 minimalist metric tiles."""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Input Fidelity (ITF)</div>
                <div class="stat-value">{results['itf_original']:.2f}<span class="stat-unit">dB</span></div>
                <div class="stat-subtext">Raw inter-frame PSNR</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Stabilized Fidelity</div>
                <div class="stat-value">{results['itf_stabilized']:.2f}<span class="stat-unit">dB</span></div>
                <div class="stat-subtext">Smoothed temporal consistency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        delta = results["itf_improvement"]
        sign = "+" if delta >= 0 else ""
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Net Stability Gain</div>
                <div class="stat-value stat-gain">{sign}{delta:.2f}<span class="stat-unit">dB</span></div>
                <div class="stat-subtext stat-gain">Jitter attenuation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        crop_pct = results["cropping_ratio"] * 100.0
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Preserved Area</div>
                <div class="stat-value">{crop_pct:.1f}<span class="stat-unit">%</span></div>
                <div class="stat-subtext">Cropped: {results['crop_loss_pct']:.1f}% (1.04x zoom)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
