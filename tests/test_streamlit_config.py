"""The app's Streamlit settings keep everything on this computer (ADR 0011,
0012). Each of these was a default that sent something somewhere."""

import tomllib
from pathlib import Path

CONFIG = Path(__file__).parent.parent / ".streamlit" / "config.toml"


def test_streamlit_config_keeps_everything_local() -> None:
    config = tomllib.loads(CONFIG.read_text())
    # No usage statistics to Streamlit.
    assert config["browser"]["gatherUsageStats"] is False
    # No first-run email prompt: Streamlit posts any address typed to its
    # servers (docs/lessons.md, 2026-10-21).
    assert config["server"]["showEmailPrompt"] is False
    # Reachable from this computer only.
    assert config["server"]["address"] == "localhost"
    # No Deploy button, which publishes the app to Streamlit's cloud.
    assert config["client"]["toolbarMode"] == "minimal"
