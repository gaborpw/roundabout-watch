"""The Streamlit page runs, refuses bad input, and shows a replay's result.

Streamlit's own test harness (AppTest) runs the page without a browser.
RF-DETR isn't installed in CI, so the detector is a stand-in that reports
the test video's squares (CLAUDE.md 37).
"""

from pathlib import Path

import pytest
from conftest import square_boxes, write_squares_video
from streamlit.testing.v1 import AppTest

import roundabout_watch.trial as trial
from roundabout_watch.model import Detection, Frame, RoadUser

APP = Path(__file__).parent.parent / "src" / "roundabout_watch" / "app.py"


class _Squares:
    def __init__(self) -> None:
        self.boxes = square_boxes(12)

    def detect(self, frame: Frame) -> list[Detection]:
        a, b = self.boxes[frame.index]
        return [
            Detection(frame.index, frame.time_s, RoadUser.CAR, 0.9, a),
            Detection(frame.index, frame.time_s, RoadUser.PEDESTRIAN, 0.9, b),
        ]


def _app() -> AppTest:
    return AppTest.from_file(str(APP), default_timeout=60)


def test_the_page_opens_with_run_disabled() -> None:
    at = _app().run()
    assert not at.exception
    assert at.title[0].value == "Try a video"
    assert at.button(key="run").disabled


def test_a_missing_file_says_so(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(trial, "load_detector", lambda size: _Squares())
    at = _app().run()
    at.radio(key="source").set_value("A file on this computer").run()
    at.text_input(key="path").input(str(tmp_path / "nowhere.mov")).run()
    at.button(key="run").click().run()
    assert not at.exception
    assert "there's no file at" in at.error[0].value


def test_a_video_on_this_computer_shows_its_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(trial, "load_detector", lambda size: _Squares())
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=12)
    at = _app().run()
    at.radio(key="source").set_value("A file on this computer").run()
    at.text_input(key="path").input(str(video)).run()
    at.button(key="run").click().run()
    assert not at.exception
    assert not at.error
    assert at.header[0].value == "squares.mp4"
    metrics = {m.label: m.value for m in at.metric}
    # One car and one person, each joining the tracker on their second frame.
    assert metrics["Road users seen"] == "2"
    assert metrics["Car"] == "1"
    assert metrics["Pedestrian"] == "1"


def test_a_failed_run_clears_the_last_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(trial, "load_detector", lambda size: _Squares())
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=12)
    at = _app().run()
    at.radio(key="source").set_value("A file on this computer").run()
    at.text_input(key="path").input(str(video)).run()
    at.button(key="run").click().run()
    assert at.header[0].value == "squares.mp4"

    def full_disk(*args: object, **kwargs: object) -> None:
        raise OSError("No space left on device")

    monkeypatch.setattr(trial, "run", full_disk)
    at.button(key="run").click().run()
    assert not at.exception
    assert "No space left on device" in at.error[0].value
    # The first video's result is gone, not shown as this run's.
    assert not at.header
