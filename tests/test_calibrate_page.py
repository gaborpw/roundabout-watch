"""The Calibrate page runs, turns a pending click into a spot, reports how
well the spots agree, and saves calibration.yaml.

Streamlit's test harness can't click the picture (it's a custom
component), so the tests put the click where the page keeps it,
state["cal_pending"], as the click handler would.
"""

from pathlib import Path

import numpy as np
import pytest
from conftest import write_squares_video
from streamlit.testing.v1 import AppTest
from test_ground import PERSPECTIVE_POINTS, _perspective_calibration

from roundabout_watch.ground import load_calibration

APP = Path(__file__).parent.parent / "src" / "roundabout_watch" / "app.py"


def _page() -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    at.switch_page("calibrate_page.py").run()
    return at


def test_the_page_opens() -> None:
    at = _page()
    assert not at.exception
    assert at.title[0].value == "Calibrate"
    assert at.button(key="cal_show").disabled


def test_a_frame_from_a_video_on_this_computer(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=12)
    at = _page()
    at.radio(key="cal_source").set_value("A file on this computer").run()
    at.text_input(key="cal_path").input(str(video)).run()
    at.button(key="cal_show").click().run()
    assert not at.exception
    assert not at.error
    assert at.session_state["cal_frame"].shape == (96, 160, 3)
    assert "Add at least 4 more spots" in at.info[0].value


def _with_frame(at: AppTest) -> AppTest:
    at.session_state["cal_frame"] = np.zeros((1080, 1920, 3), dtype=np.uint8)
    return at.run()


def test_a_click_becomes_a_spot() -> None:
    at = _with_frame(_page())
    at.session_state["cal_pending"] = (812.0, 455.0)
    at.run()
    at.text_input(key="cal_name").input("NE curb corner")
    at.text_input(key="cal_latlon").input("41.48163, -81.72891")
    at.button(key="cal_add").click().run()
    assert not at.exception
    (spot,) = at.session_state["cal_spots"]
    assert (spot.name, spot.pixel, spot.lat, spot.lon) == (
        "NE curb corner",
        (812.0, 455.0),
        41.48163,
        -81.72891,
    )
    assert "cal_pending" not in at.session_state


def test_a_bad_position_is_explained_and_not_added() -> None:
    at = _with_frame(_page())
    at.session_state["cal_pending"] = (812.0, 455.0)
    at.run()
    at.text_input(key="cal_name").input("NE curb corner")
    at.text_input(key="cal_latlon").input("by the tree")
    at.button(key="cal_add").click().run()
    assert not at.exception
    assert at.session_state["cal_spots"] == []
    assert "two numbers" in at.error[0].value


def test_six_spots_are_checked_and_saved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The page saves calibration.yaml in the folder the app runs from.
    monkeypatch.chdir(tmp_path)
    at = _with_frame(_page())
    at.session_state["cal_spots"] = list(_perspective_calibration().points)
    at.run()
    assert not at.exception
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Furthest off"] == "0.00 m"
    at.button(key="cal_save").click().run()
    assert not at.exception
    assert "Saved to" in at.success[0].value
    saved = load_calibration(tmp_path / "calibration.yaml")
    assert [p.name for p in saved.points] == [n for n, _, _ in PERSPECTIVE_POINTS]
    assert (saved.image_width, saved.image_height) == (1920, 1080)


def test_four_spots_ask_for_two_more() -> None:
    at = _with_frame(_page())
    at.session_state["cal_spots"] = list(_perspective_calibration(PERSPECTIVE_POINTS[:4]).points)
    at.run()
    assert not at.exception
    assert any("Add 2 more so it can check itself" in i.value for i in at.info)


def test_a_spot_can_be_removed() -> None:
    at = _with_frame(_page())
    at.session_state["cal_spots"] = list(_perspective_calibration().points)
    at.run()
    at.selectbox(key="cal_remove_which").set_value("drain").run()
    at.button(key="cal_remove").click().run()
    assert not at.exception
    assert "drain" not in [s.name for s in at.session_state["cal_spots"]]
    assert len(at.session_state["cal_spots"]) == 5
