"""ground.py: pixels to metres, checked against hand-built scenarios.

Every scenario here is made up for the test (CLAUDE.md 6): a camera whose
mapping from the road to the picture is chosen by hand, so the right answer
is known before the code runs.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from roundabout_watch.ground import (
    WGS84_A_M,
    WGS84_F,
    Calibration,
    CalibrationError,
    Ground,
    SurveyPoint,
    load_calibration,
    local_metres,
    parse_calibration,
)
from roundabout_watch.model import Detection, RoadUser

REPO = Path(__file__).resolve().parents[1]

# An origin near Cleveland's latitude, so the ellipsoid's curvature matters
# the way it will for the real roundabout. Not a surveyed place.
LAT0 = 41.48
LON0 = -81.73


def _ecef(lat: float, lon: float) -> NDArray[np.float64]:
    """Earth-centred coordinates of a point on the WGS 84 ellipsoid: the
    exact conversion, an independent check on local_metres' shortcut."""
    phi, lam = math.radians(lat), math.radians(lon)
    e2 = WGS84_F * (2 - WGS84_F)
    n = WGS84_A_M / math.sqrt(1 - e2 * math.sin(phi) ** 2)
    return np.array(
        [
            n * math.cos(phi) * math.cos(lam),
            n * math.cos(phi) * math.sin(lam),
            n * (1 - e2) * math.sin(phi),
        ]
    )


def _exact_east_north(lat: float, lon: float) -> tuple[float, float]:
    """East and north of (LAT0, LON0) by rotating the exact Earth-centred
    difference into the origin's local frame."""
    phi, lam = math.radians(LAT0), math.radians(LON0)
    d = _ecef(lat, lon) - _ecef(LAT0, LON0)
    east = -math.sin(lam) * d[0] + math.cos(lam) * d[1]
    north = (
        -math.sin(phi) * math.cos(lam) * d[0]
        - math.sin(phi) * math.sin(lam) * d[1]
        + math.cos(phi) * d[2]
    )
    return east, north


def test_local_metres_at_the_equator_by_hand() -> None:
    # At the equator, 0.001° of longitude is a × 0.001° in radians:
    # 6 378 137 × 1.745329e-5 = 111.3195 m. North, the radius is
    # a(1 − e²) = 6 378 137 × 0.99330562 = 6 335 439 m, so 0.001° of
    # latitude is 110.5743 m.
    east, north = local_metres(0.001, 0.001, 0.0, 0.0)
    assert east == pytest.approx(111.3195, abs=1e-3)
    assert north == pytest.approx(110.5743, abs=1e-3)


@pytest.mark.parametrize(
    ("lat", "lon"),
    [
        (LAT0 + 0.0005, LON0),  # about 55 m north
        (LAT0, LON0 + 0.0007),  # about 58 m east
        (LAT0 - 0.0004, LON0 - 0.0006),  # about 65 m south-west
    ],
)
def test_local_metres_agrees_with_the_exact_conversion(lat: float, lon: float) -> None:
    # Within 2 mm at roundabout distances: far below what a map click or a
    # detector's box can resolve.
    east, north = local_metres(lat, lon, LAT0, LON0)
    exact_east, exact_north = _exact_east_north(lat, lon)
    assert east == pytest.approx(exact_east, abs=0.002)
    assert north == pytest.approx(exact_north, abs=0.002)


# Metres per degree at the test origin. local_metres is linear in the
# difference for a fixed origin, so these turn metres back into degrees.
_EAST_PER_DEG = local_metres(LAT0, LON0 + 1e-3, LAT0, LON0)[0] / 1e-3
_NORTH_PER_DEG = local_metres(LAT0 + 1e-3, LON0, LAT0, LON0)[1] / 1e-3


def _survey(name: str, pixel: tuple[float, float], east: float, north: float) -> SurveyPoint:
    return SurveyPoint(
        name=name,
        pixel=pixel,
        lat=LAT0 + north / _NORTH_PER_DEG,
        lon=LON0 + east / _EAST_PER_DEG,
    )


def _top_down(east: float, north: float) -> tuple[float, float]:
    """A camera looking straight down: 20 pixels a metre, north up, the
    ground's (0, 0) at the picture's centre."""
    return 960 + 20 * east, 540 - 20 * north


def _perspective(east: float, north: float) -> tuple[float, float]:
    """A camera looking north at a slant: things further north are smaller
    and higher up. Ground to picture is the matrix
    [[40, 0, 960], [0, -20, 700], [0, 0.02, 1]], so
    x = (40e + 960) / (0.02n + 1) and y = (700 − 20n) / (0.02n + 1).
    Far north, y tends to −20 / 0.02 = −1000: the horizon is 1000 pixels
    above the picture's top edge."""
    w = 0.02 * north + 1
    return (40 * east + 960) / w, (700 - 20 * north) / w


# (name, east, north) in metres. Their mean is (5/6, 80/6): east
# (−15 + 15 + 15 − 15 + 0 + 5) / 6, north (−5 − 5 + 30 + 30 + 10 + 20) / 6.
# That becomes the origin, so ground.py reports positions relative to it.
PERSPECTIVE_POINTS = [
    ("near left", -15.0, -5.0),
    ("near right", 15.0, -5.0),
    ("far right", 15.0, 30.0),
    ("far left", -15.0, 30.0),
    ("middle", 0.0, 10.0),
    ("drain", 5.0, 20.0),
]
MEAN_EAST = 5 / 6
MEAN_NORTH = 80 / 6


def _perspective_calibration(
    points: list[tuple[str, float, float]] = PERSPECTIVE_POINTS,
    nudge: dict[str, tuple[float, float]] | None = None,
) -> Calibration:
    survey = []
    for name, east, north in points:
        x, y = _perspective(east, north)
        dx, dy = (nudge or {}).get(name, (0.0, 0.0))
        survey.append(_survey(name, (x + dx, y + dy), east, north))
    return Calibration(image_width=1920, image_height=1080, points=tuple(survey))


def test_top_down_camera_by_hand() -> None:
    # Corners at (±10, ±8) m and the centre: their mean is (0, 0), so the
    # origin is the picture's centre. Pixel (1060, 440) is 100 px right and
    # 100 px up from it: 5 m east and 5 m north.
    spots = [(-10.0, -8.0), (10.0, -8.0), (10.0, 8.0), (-10.0, 8.0), (0.0, 0.0)]
    calibration = Calibration(
        image_width=1920,
        image_height=1080,
        points=tuple(_survey(f"p{i}", _top_down(e, n), e, n) for i, (e, n) in enumerate(spots)),
    )
    ground = Ground(calibration)
    east, north = ground.to_ground(np.array([[1060.0, 440.0]]))[0]
    assert east == pytest.approx(5.0, abs=1e-3)
    assert north == pytest.approx(5.0, abs=1e-3)
    assert ground.report.fit_max_m == pytest.approx(0.0, abs=1e-3)


def test_perspective_camera_recovers_the_road() -> None:
    ground = Ground(_perspective_calibration())
    # A point not used in the fit: 8 m east and 25 m north, which is
    # (8 − 5/6, 25 − 80/6) = (7.1667, 11.6667) from the origin.
    pixel = np.array([_perspective(8.0, 25.0)])
    east, north = ground.to_ground(pixel)[0]
    assert east == pytest.approx(8.0 - MEAN_EAST, abs=1e-3)
    assert north == pytest.approx(25.0 - MEAN_NORTH, abs=1e-3)
    # A perfect camera: every point agrees.
    assert ground.report.fit_max_m == pytest.approx(0.0, abs=1e-3)
    assert ground.report.others_max_m == pytest.approx(0.0, abs=1e-3)


def test_above_the_horizon_is_off_the_road() -> None:
    # The horizon is at y = −1000 (see _perspective); y = −1500 is sky.
    ground = Ground(_perspective_calibration())
    out = ground.to_ground(np.array([[960.0, -1500.0], [960.0, 540.0]]))
    assert np.all(np.isnan(out[0]))
    assert np.all(np.isfinite(out[1]))


@pytest.mark.parametrize(
    ("name", "nudge"),
    [
        # "drain" clicked 30 pixels right of where it is. Asking which point
        # a fit without it predicts worst blames "far left" here (9.9 m
        # against drain's 1.0 m), because predicting a corner is
        # extrapolating; that's why the report doesn't ask it that way.
        ("drain", (30.0, 0.0)),
        ("middle", (0.0, 20.0)),
        ("near left", (25.0, 0.0)),
        ("far right", (0.0, 15.0)),
    ],
)
def test_a_misplaced_point_is_named_for_rechecking(name: str, nudge: tuple[float, float]) -> None:
    # Without the misplaced point, the other five come from a perfect
    # camera, so they agree exactly.
    report = Ground(_perspective_calibration(nudge={name: nudge})).report
    assert report.recheck == name
    assert report.others_max_m == pytest.approx(0.0, abs=1e-3)
    assert report.fit_max_m > 0.05


@pytest.mark.parametrize("count", [4, 5])
def test_under_six_points_cannot_say_which_is_off(count: int) -> None:
    # Four points always fit exactly, misplaced or not.
    ground = Ground(_perspective_calibration(PERSPECTIVE_POINTS[:count]))
    assert ground.report.recheck is None
    assert ground.report.others_max_m is None
    if count == 4:
        nudged = Ground(
            _perspective_calibration(PERSPECTIVE_POINTS[:4], nudge={"far left": (40.0, 0.0)})
        )
        assert nudged.report.fit_max_m == pytest.approx(0.0, abs=1e-4)


def test_track_point_uses_the_bottom_middle_of_the_box() -> None:
    ground = Ground(_perspective_calibration())
    # The box's bottom-middle is the pixel of (0, 10) m, the "middle" point:
    # (0 − 5/6, 10 − 80/6) from the origin.
    x, y = _perspective(0.0, 10.0)
    detection = Detection(
        frame=3,
        time_s=0.1,
        kind=RoadUser.CAR,
        confidence=0.9,
        box=(x - 40, y - 30, x + 40, y),
    )
    point = ground.track_point(detection)
    assert point is not None
    assert point.time_s == 0.1
    assert point.x_m == pytest.approx(-MEAN_EAST, abs=1e-3)
    assert point.y_m == pytest.approx(10.0 - MEAN_NORTH, abs=1e-3)


def test_track_point_above_the_horizon_is_none() -> None:
    ground = Ground(_perspective_calibration())
    detection = Detection(
        frame=0, time_s=0.0, kind=RoadUser.CAR, confidence=0.9, box=(900, -1600, 1000, -1500)
    )
    assert ground.track_point(detection) is None


def test_a_different_picture_size_is_refused() -> None:
    ground = Ground(_perspective_calibration())
    ground.check_frame(1920, 1080)
    with pytest.raises(CalibrationError, match="1920×1080"):
        ground.check_frame(1080, 1920)


def test_points_on_one_line_are_refused() -> None:
    # OpenCV returns a meaningless matrix for these rather than failing.
    line = [(f"p{i}", 0.0, float(i * 5)) for i in range(5)]
    with pytest.raises(CalibrationError, match="one line"):
        Ground(_perspective_calibration(line))


def test_five_on_a_line_and_one_off_are_refused() -> None:
    # Spread out as a whole, but any four of them include three on the
    # line at north 0, so no four fix a perspective.
    points = [(f"line {i}", float(i * 6 - 12), 0.0) for i in range(5)] + [("off", 0.0, 20.0)]
    with pytest.raises(CalibrationError, match="one line"):
        Ground(_perspective_calibration(points))


def test_recheck_skips_a_point_the_rest_cannot_do_without() -> None:
    # Four near points on one line, plus two far ones. Without "far left",
    # the rest is four on a line plus "far right": no four of them fix a
    # perspective, so that removal is skipped rather than an error. Without
    # the misplaced "near b", the rest agree exactly.
    points = [
        ("near a", -15.0, -5.0),
        ("near b", -5.0, -5.0),
        ("near c", 5.0, -5.0),
        ("near d", 15.0, -5.0),
        ("far left", -15.0, 30.0),
        ("far right", 15.0, 30.0),
    ]
    report = Ground(_perspective_calibration(points, nudge={"near b": (0.0, 15.0)})).report
    assert report.recheck == "near b"


def test_a_typo_kilometres_away_is_refused() -> None:
    calibration = _perspective_calibration()
    far = SurveyPoint(name="typo", pixel=(960.0, 540.0), lat=LAT0 + 0.5, lon=LON0)
    with pytest.raises(CalibrationError, match="kilometres"):
        Ground(Calibration(1920, 1080, calibration.points + (far,)))


@pytest.mark.parametrize(
    ("points", "message"),
    [
        (PERSPECTIVE_POINTS[:3], "at least 4"),
        ([*PERSPECTIVE_POINTS[:4], ("near left", 1.0, 1.0)], "own name"),
    ],
)
def test_too_few_or_repeated_points_are_refused(
    points: list[tuple[str, float, float]], message: str
) -> None:
    with pytest.raises(CalibrationError, match=message):
        _perspective_calibration(points)


def test_a_pixel_outside_the_picture_is_refused() -> None:
    points = list(_perspective_calibration().points)
    points[0] = SurveyPoint(name="off", pixel=(2500.0, 10.0), lat=LAT0, lon=LON0)
    with pytest.raises(CalibrationError, match="outside"):
        Calibration(1920, 1080, tuple(points))


def test_a_latitude_out_of_range_is_refused() -> None:
    points = list(_perspective_calibration().points)
    points[0] = SurveyPoint(name="bad", pixel=(10.0, 10.0), lat=95.0, lon=LON0)
    with pytest.raises(CalibrationError, match="latitude"):
        Calibration(1920, 1080, tuple(points))


def _yaml_data() -> dict[str, object]:
    return {
        "image_size": [1920, 1080],
        "points": [
            {"name": p.name, "pixel": list(p.pixel), "lat": p.lat, "lon": p.lon}
            for p in _perspective_calibration().points
        ],
    }


def test_parse_reads_a_well_formed_calibration() -> None:
    calibration = parse_calibration(_yaml_data())
    assert calibration.image_width == 1920
    assert [p.name for p in calibration.points] == [n for n, _, _ in PERSPECTIVE_POINTS]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d.update(extra=1), "exactly two keys"),
        (lambda d: d.update(image_size=[1920.5, 1080]), "whole pixels"),
        (lambda d: d["points"][0].update(lat=True), "number"),
        (lambda d: d["points"][0].update(pixel=[1, 2, 3]), "two numbers"),
        (lambda d: d["points"][0].update(colour="red"), "exactly: name"),
        (lambda d: d["points"][0].update(name="  "), "needs a name"),
        (lambda d: d.update(points="none"), "must be a list"),
    ],
)
def test_parse_refuses_bad_shapes(change: object, message: str) -> None:
    data = _yaml_data()
    assert callable(change)
    change(data)
    with pytest.raises(CalibrationError, match=message):
        parse_calibration(data)


def test_no_calibration_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(CalibrationError, match="no calibration"):
        load_calibration(tmp_path / "calibration.yaml")


def test_broken_yaml_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "calibration.yaml"
    path.write_text("points: [unclosed", encoding="utf-8")
    with pytest.raises(CalibrationError, match="isn't valid YAML"):
        load_calibration(path)


def test_yaml_cannot_build_python_objects(tmp_path: Path) -> None:
    # safe_load refuses tags like this one, which a plain yaml.load would
    # run (CLAUDE.md 17).
    path = tmp_path / "calibration.yaml"
    path.write_text("!!python/object/apply:os.system ['echo hi']\n", encoding="utf-8")
    with pytest.raises(CalibrationError, match="isn't valid YAML"):
        load_calibration(path)


def test_the_example_file_loads_and_fits() -> None:
    # So the example can't drift from what the code reads.
    ground = Ground.from_file(REPO / "calibration.example.yaml")
    assert len(ground.calibration.points) == 5
    assert ground.report.recheck is None
