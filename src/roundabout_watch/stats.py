"""Statistics about what a replay saw, for the "Try a video" page (ADR 0012).

Pure: spans in, numbers out, so they're tested without a video or a browser
(CLAUDE.md 30). They count road users the detector and tracker saw, and a
tracker can miss one or split one in two, so the page says they are what
was seen. Speeds and directions wait for metres (ground.py).
"""

from __future__ import annotations

import math
import statistics
from collections import Counter
from collections.abc import Sequence

from roundabout_watch.model import RoadUser, TrackSpan


def counts_by_kind(spans: Sequence[TrackSpan]) -> list[tuple[RoadUser, int]]:
    """How many of each kind, most first; kinds tied on count keep RoadUser's
    order, so the page doesn't reshuffle between runs."""
    counts = Counter(span.kind for span in spans)
    order = list(RoadUser)
    return sorted(counts.items(), key=lambda item: (-item[1], order.index(item[0])))


def bin_seconds(video_seconds: float) -> int:
    """Width of the arrivals chart's bars: 10 s for a clip under three
    minutes, so a 30-second phone video gets several bars, else a minute."""
    return 10 if video_seconds < 180 else 60


def arrivals(spans: Sequence[TrackSpan], video_seconds: float, width_s: int) -> list[int]:
    """Road users arriving in each width_s-long stretch of the video, from
    its start. Always at least one bar, even for an empty road."""
    if width_s <= 0:
        raise ValueError("the bar width must be a positive number of seconds")
    bars = [0] * max(1, math.ceil(video_seconds / width_s))
    for span in spans:
        bars[min(int(span.first_s // width_s), len(bars) - 1)] += 1
    return bars


def busiest(bars: Sequence[int]) -> tuple[int, int] | None:
    """The first bar with the most arrivals, as (its index, its count), or
    None when nobody arrived."""
    if not bars or max(bars) == 0:
        return None
    top = max(bars)
    return bars.index(top), top


def median_seconds_in_view(spans: Sequence[TrackSpan]) -> dict[RoadUser, float]:
    """For each kind, the median time one was in view. The median rather
    than the mean, so one car parked in view all video doesn't swamp it."""
    by_kind: dict[RoadUser, list[float]] = {}
    for span in spans:
        by_kind.setdefault(span.kind, []).append(span.seconds)
    return {kind: statistics.median(times) for kind, times in by_kind.items()}
