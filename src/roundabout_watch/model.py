"""The shapes that pass between pipeline stages (CLAUDE.md 28, 29).

Each stage takes and returns these types and nothing else, so a stage can be
tested alone and swapped without touching the others: a new detector produces
the same Detection, and the safety maths never learns which detector ran.

Two coordinate systems meet here and must never be mixed (CLAUDE.md, "the
second idea"): Detection.box is in image pixels; everything from TrackPoint
on is in metres on the ground, after calibration.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class RoadUser(str, Enum):
    """What a tracked object is. Narrower than COCO's classes on purpose:
    the safety maths only cares about things that move on the road."""

    CAR = "car"
    TRUCK = "truck"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    PEDESTRIAN = "pedestrian"


@dataclass(frozen=True)
class Detection:
    """One object found in one frame, in image pixels."""

    frame: int
    time_s: float
    kind: RoadUser
    confidence: float
    # (left, top, right, bottom) in pixels, origin at the top-left corner.
    box: tuple[float, float, float, float]

    def __post_init__(self) -> None:
        if self.frame < 0:
            raise ValueError("frame must not be negative")
        if not math.isfinite(self.time_s):
            raise ValueError("time_s must be a finite number")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        left, top, right, bottom = self.box
        if not (right > left and bottom > top):
            raise ValueError("box must have positive width and height")

    @property
    def ground_contact(self) -> tuple[float, float]:
        """The pixel to project onto the road: the middle of the box's
        bottom edge, where the object touches the ground. The box's centre
        would sit above the road and land metres away after projection."""
        left, _, right, bottom = self.box
        return ((left + right) / 2.0, bottom)


@dataclass(frozen=True)
class TrackPoint:
    """Where one tracked object was at one moment, in metres on the ground."""

    time_s: float
    x_m: float
    y_m: float

    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in (self.time_s, self.x_m, self.y_m)):
            raise ValueError("track point values must be finite numbers")


@dataclass(frozen=True)
class Track:
    """One object followed through time, after projection to the ground."""

    track_id: int
    kind: RoadUser
    points: tuple[TrackPoint, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise ValueError("a track needs at least one point")
        times = [p.time_s for p in self.points]
        # Strictly increasing: two points at the same moment would make any
        # speed derived from them a division by zero. strict=False because
        # pairing each time with the next is one pair short by design.
        if any(later <= earlier for earlier, later in zip(times, times[1:], strict=False)):
            raise ValueError("track points must be in strictly increasing time order")


class EventKind(str, Enum):
    NEAR_MISS = "near_miss"
    POSSIBLE_CRASH = "possible_crash"


class ConflictType(str, Enum):
    """How two road users would have met, by the angle between their headings.

    FHWA's SSAM (report FHWA-HRT-08-051): rear-end below 30°, crossing above
    85°, lane change in between. safety.conflict_type decides it."""

    REAR_END = "rear_end"
    LANE_CHANGE = "lane_change"
    CROSSING = "crossing"


class EventStatus(str, Enum):
    """ADR 0002: the software only ever flags; a person confirms or dismisses."""

    FLAGGED = "flagged"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class Event:
    """A moment worth a person's look, and the measures that raised it."""

    kind: EventKind
    track_ids: tuple[int, ...]
    start_s: float
    end_s: float
    # Named safety measures in seconds or m/s² (for example "ttc_s",
    # "pet_s", "drac_mps2"); which ones are present depends on what raised it.
    measures: dict[str, float] = field(default_factory=dict)
    status: EventStatus = EventStatus.FLAGGED

    def __post_init__(self) -> None:
        if not self.track_ids:
            raise ValueError("an event involves at least one track")
        if self.end_s < self.start_s:
            raise ValueError("an event cannot end before it starts")
        if not all(math.isfinite(v) for v in self.measures.values()):
            raise ValueError("measures must be finite numbers")
