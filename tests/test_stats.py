"""Statistics over hand-built spans: every expected number is worked out in
the comment above it, and none comes from real footage (CLAUDE.md 6)."""

import pytest

from roundabout_watch.model import RoadUser, TrackSpan
from roundabout_watch.stats import (
    arrivals,
    bin_seconds,
    busiest,
    counts_by_kind,
    median_seconds_in_view,
)


def _span(track_id: int, kind: RoadUser, first_s: float, last_s: float) -> TrackSpan:
    return TrackSpan(track_id=track_id, kind=kind, first_s=first_s, last_s=last_s, frames=5)


# Three cars, a pedestrian and a bike across a 30-second clip.
SPANS = (
    _span(0, RoadUser.CAR, 2.0, 6.0),  # in view 4 s
    _span(1, RoadUser.PEDESTRIAN, 3.0, 13.0),  # 10 s
    _span(2, RoadUser.CAR, 12.0, 14.0),  # 2 s
    _span(3, RoadUser.CAR, 15.0, 24.0),  # 9 s
    _span(4, RoadUser.BICYCLE, 18.0, 21.0),  # 3 s
)


def test_counts_by_kind_most_first() -> None:
    # 3 cars, then the bike and pedestrian tied at 1, in RoadUser's order
    # (BICYCLE is declared before PEDESTRIAN).
    assert counts_by_kind(SPANS) == [
        (RoadUser.CAR, 3),
        (RoadUser.BICYCLE, 1),
        (RoadUser.PEDESTRIAN, 1),
    ]


def test_counts_of_nothing() -> None:
    assert counts_by_kind(()) == []


@pytest.mark.parametrize(("video_s", "width"), [(30, 10), (179.9, 10), (180, 60), (600, 60)])
def test_bar_width(video_s: float, width: int) -> None:
    assert bin_seconds(video_s) == width


def test_arrivals_in_ten_second_bars() -> None:
    # 30 s in 10 s bars: arrivals at 2 and 3 s in the first, 12 and 15 s in
    # the second, 18 s... also the second (10–20 s), none in the third.
    assert arrivals(SPANS, 30.0, 10) == [2, 3, 0]


def test_arrivals_at_the_very_end_land_in_the_last_bar() -> None:
    # 20 s exactly is the end of a 20-second video: bar 2 doesn't exist, so
    # it counts in bar 1 (10–20 s).
    assert arrivals((_span(0, RoadUser.CAR, 20.0, 20.0),), 20.0, 10) == [0, 1]


def test_arrivals_on_an_empty_road() -> None:
    assert arrivals((), 0.0, 10) == [0]


def test_arrivals_reject_a_zero_width() -> None:
    with pytest.raises(ValueError):
        arrivals(SPANS, 30.0, 0)


def test_busiest_bar() -> None:
    assert busiest([2, 3, 0]) == (1, 3)
    # A tie goes to the earlier bar.
    assert busiest([3, 3]) == (0, 3)
    assert busiest([0, 0]) is None


def test_median_time_in_view() -> None:
    # Cars were in view 4, 2 and 9 s: the median is 4.
    assert median_seconds_in_view(SPANS) == {
        RoadUser.CAR: 4.0,
        RoadUser.PEDESTRIAN: 10.0,
        RoadUser.BICYCLE: 3.0,
    }
