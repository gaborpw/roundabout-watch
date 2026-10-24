"""The work behind the Calibrate page: clicks to pixels, pasted map
positions, the drawn spots and the saved file. The spots and positions here
are made up for the test (CLAUDE.md 6)."""

from datetime import date
from pathlib import Path

import numpy as np
import pytest
import yaml
from conftest import FPS, HEIGHT, WIDTH, write_squares_video

from roundabout_watch.calibrate import (
    PENDING_COLOUR,
    SPOT_COLOUR,
    calibration_yaml,
    frame_at,
    image_pixel,
    mark_spots,
    parse_lat_lon,
    report_rows,
)
from roundabout_watch.ground import (
    Calibration,
    CalibrationError,
    FitReport,
    SurveyPoint,
    parse_calibration,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # As Google Maps copies it.
        ("41.48163, -81.72891", (41.48163, -81.72891)),
        ("  41.48163,-81.72891 ", (41.48163, -81.72891)),
        ("41.48163 -81.72891", (41.48163, -81.72891)),
        ("-33.8, 151", (-33.8, 151.0)),
    ],
)
def test_parse_lat_lon(text: str, expected: tuple[float, float]) -> None:
    assert parse_lat_lon(text) == expected


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "two numbers"),
        ("41.48163", "two numbers"),
        ("41°28'53.9\"N 81°43'44.1\"W", "two numbers"),
        ("41.48, -81.72, 3", "two numbers"),
        # No latitude passes 90. (A Cleveland pair pasted the other way
        # round, -81.7 then 41.5, is in range; ground.py's "kilometres
        # apart" check catches that one instead.)
        ("95, 10", "latitude comes first"),
        ("41.5, 181", "latitude comes first"),
    ],
)
def test_parse_lat_lon_refuses(text: str, message: str) -> None:
    with pytest.raises(CalibrationError, match=message):
        parse_lat_lon(text)


def test_image_pixel_scales_the_drawn_click_to_the_frame() -> None:
    # A 1920 × 1080 frame drawn 960 × 540 in its column: a click at
    # (100, 50) on the drawn picture is (200, 100) on the frame.
    click = {"x": 100, "y": 50, "width": 960, "height": 540, "unix_time": 1}
    assert image_pixel(click, 1920, 1080) == (200.0, 100.0)


def test_image_pixel_keeps_a_click_on_the_edge_inside() -> None:
    # A click on the last drawn pixel can land a hair past the edge.
    click = {"x": 961, "y": -1, "width": 960, "height": 540}
    assert image_pixel(click, 1920, 1080) == (1920.0, 0.0)


@pytest.mark.parametrize(
    "click",
    [
        {"x": 1, "y": 1, "width": 0, "height": 540},
        {"x": "1", "y": 1, "width": 960, "height": 540},
        {"x": True, "y": 1, "width": 960, "height": 540},
        {"y": 1, "width": 960, "height": 540},
    ],
)
def test_image_pixel_refuses_a_bad_click(click: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        image_pixel(click, 1920, 1080)


def test_frame_at_picks_the_moment(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=12)
    # At 25 fps, frame 5 is the first at least 0.2 s in (5 / 25 = 0.2).
    assert frame_at(video, 0.2).index == 5
    assert frame_at(video, 0.0).index == 0
    # Past the end: the last frame.
    assert frame_at(video, 60.0).index == 11
    assert frame_at(video, 0.0).image.shape == (HEIGHT, WIDTH, 3)
    assert FPS == 25


def test_frame_at_refuses_negative_seconds(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="zero or more"):
        frame_at(tmp_path / "unused.mp4", -1.0)


def _spots() -> list[SurveyPoint]:
    return [
        SurveyPoint("NE curb", (40.0, 30.0), 10.0, 20.0),
        SurveyPoint("SW curb", (120.0, 70.0), 10.0001, 20.0001),
    ]


def test_mark_spots_draws_on_a_copy() -> None:
    image = np.zeros((96, 160, 3), dtype=np.uint8)
    marked = mark_spots(image, _spots(), pending=(80.0, 50.0))
    # The frame itself is untouched; the copy has both colours on it.
    assert not image.any()
    colours = {tuple(int(v) for v in px) for px in marked.reshape(-1, 3)}
    assert SPOT_COLOUR in colours
    assert PENDING_COLOUR in colours


def test_calibration_yaml_reads_back() -> None:
    spots = [
        SurveyPoint("a", (100.0, 900.0), 10.0, 20.0),
        SurveyPoint("b", (1800.0, 900.5), 10.0, 20.0003),
        SurveyPoint("c", (1300.0, 400.0), 10.00025, 20.0003),
        SurveyPoint("d, with a comma: and a colon", (600.0, 400.0), 10.00025, 20.0),
    ]
    calibration = Calibration(1920, 1080, tuple(spots))
    text = calibration_yaml(calibration, date(2026, 10, 24))
    assert text.startswith("# Made on the Calibrate page on 2026-10-24.")
    assert parse_calibration(yaml.safe_load(text)) == calibration


def test_report_rows_number_the_spots() -> None:
    report = FitReport(fit_m={"a": 0.123, "b": 1.0}, recheck=None, others_max_m=None)
    assert report_rows(report) == [
        {"spot": "1. a", "metres off": 0.12},
        {"spot": "2. b", "metres off": 1.0},
    ]
