"""The Roundabout Watch app: Streamlit, on this computer only (ADR 0012).

Run from the repository's root, so Streamlit finds .streamlit/config.toml
and the Calibrate page saves calibration.yaml where ground.py looks:

    uv run streamlit run src/roundabout_watch/app.py

This file only lists the pages; each is its own script beside it.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Roundabout Watch", page_icon="🚦", layout="wide")

st.navigation(
    [
        st.Page("try_video.py", title="Try a video", icon="🎬", default=True),
        st.Page("calibrate_page.py", title="Calibrate", icon="📐"),
    ]
).run()
