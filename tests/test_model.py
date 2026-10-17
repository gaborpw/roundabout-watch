"""The shared types refuse shapes that would poison every later stage."""

import math

import pytest

from roundabout_watch.model import (
    Detection,
    Event,
    EventKind,
    EventStatus,
    RoadUser,
    Track,
    TrackPoint,
)


def _detection(**overrides: object) -> Detection:
    values: dict[str, object] = {
        "frame": 0,
        "time_s": 0.0,
        "kind": RoadUser.CAR,
        "confidence": 0.9,
        "box": (100.0, 50.0, 140.0, 80.0),
    }
    values.update(overrides)
    return Detection(**values)  # type: ignore[arg-type]


def test_detection_ground_contact_is_bottom_middle() -> None:
    # Box from x 100 to 140 and y 50 to 80: bottom-middle is (120, 80).
    assert _detection().ground_contact == (120.0, 80.0)


@pytest.mark.parametrize(
    "overrides",
    [
        {"confidence": 1.5},
        {"confidence": -0.1},
        {"frame": -1},
        {"time_s": math.nan},
        {"box": (140.0, 50.0, 100.0, 80.0)},  # right edge left of left edge
        {"box": (100.0, 80.0, 140.0, 80.0)},  # zero height
    ],
)
def test_detection_rejects_impossible_values(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _detection(**overrides)


def test_track_rejects_time_going_backwards() -> None:
    points = (TrackPoint(1.0, 0.0, 0.0), TrackPoint(0.5, 1.0, 0.0))
    with pytest.raises(ValueError):
        Track(track_id=1, kind=RoadUser.CAR, points=points)


def test_track_rejects_two_points_at_the_same_moment() -> None:
    points = (TrackPoint(1.0, 0.0, 0.0), TrackPoint(1.0, 1.0, 0.0))
    with pytest.raises(ValueError):
        Track(track_id=1, kind=RoadUser.CAR, points=points)


def test_track_rejects_no_points() -> None:
    with pytest.raises(ValueError):
        Track(track_id=1, kind=RoadUser.CAR, points=())


def test_track_point_rejects_infinity() -> None:
    with pytest.raises(ValueError):
        TrackPoint(0.0, math.inf, 0.0)


def test_new_event_is_only_flagged() -> None:
    # ADR 0002: nothing the software raises starts life confirmed.
    event = Event(kind=EventKind.NEAR_MISS, track_ids=(1, 2), start_s=10.0, end_s=11.5)
    assert event.status is EventStatus.FLAGGED


def test_event_rejects_ending_before_it_starts() -> None:
    with pytest.raises(ValueError):
        Event(kind=EventKind.POSSIBLE_CRASH, track_ids=(3,), start_s=5.0, end_s=4.0)


def test_event_rejects_no_tracks() -> None:
    with pytest.raises(ValueError):
        Event(kind=EventKind.NEAR_MISS, track_ids=(), start_s=0.0, end_s=1.0)


def test_event_rejects_nan_measure() -> None:
    with pytest.raises(ValueError):
        Event(
            kind=EventKind.NEAR_MISS,
            track_ids=(1, 2),
            start_s=0.0,
            end_s=1.0,
            measures={"ttc_s": math.nan},
        )
