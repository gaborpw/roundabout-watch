"""Surrogate safety measures: how close two road users came to colliding.

Pure maths on tracks already projected to the ground, in metres and seconds:
no camera, no GPU, no files (CLAUDE.md 30). flag.py decides what is worth a
person's look; this module only measures.

Definitions follow FHWA's Surrogate Safety Assessment Model (SSAM, report
FHWA-HRT-08-051, read 2026-10-17):

- TTC, time to collision: if both keep their current velocity, how long until
  they touch. A conflict's TTC is the minimum over the conflict.
- PET, post-encroachment time: the gap between one road user leaving a place
  and the other reaching it. The minimum over the two paths.
- DeltaS: the size of the difference between the two velocity vectors.
- Conflict angle: rear-end below 30°, crossing above 85°, otherwise a lane
  change.
- DRAC, the deceleration needed to avoid a crash, isn't defined by SSAM; the
  formula here is the usual closing-speed one (see `deceleration_to_avoid`).

Road users are discs, and the caller passes the collision radius: the
distance between centres at which two of them touch. SSAM uses rectangles,
which follow a car's shape more closely; a disc wide enough to cover a car's
length also covers more than its width, so it flags a few side-by-side passes
a rectangle wouldn't. The trade-off is simplicity: a disc needs no heading,
which is the least reliable thing a tracker reports. Rectangles (2D-TTC) can
replace it here without any other module changing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from roundabout_watch.model import ConflictType, Track

# SSAM's conflict-angle classes, in degrees (FHWA-HRT-08-051, chapter 2).
# These are definitions, not tuning thresholds, so they don't live in config.
REAR_END_BELOW_DEG = 30.0
CROSSING_ABOVE_DEG = 85.0


@dataclass(frozen=True)
class MotionState:
    """Where a road user is and how it's moving at one moment, on the ground."""

    time_s: float
    x_m: float
    y_m: float
    vx_mps: float
    vy_mps: float


def motion_states(track: Track) -> list[MotionState]:
    """A velocity for every point of a track, from its neighbours.

    Inner points use the central difference (the point before to the point
    after), which cancels some of the jitter in tracked positions; the first
    and last points use the one neighbour they have. A one-point track has no
    velocity, so it gives no states.
    """
    points = track.points
    if len(points) < 2:
        return []
    states = []
    for i, point in enumerate(points):
        before = points[max(i - 1, 0)]
        after = points[min(i + 1, len(points) - 1)]
        dt = after.time_s - before.time_s
        states.append(
            MotionState(
                time_s=point.time_s,
                x_m=point.x_m,
                y_m=point.y_m,
                vx_mps=(after.x_m - before.x_m) / dt,
                vy_mps=(after.y_m - before.y_m) / dt,
            )
        )
    return states


def time_to_collision(a: MotionState, b: MotionState, radius_m: float) -> float | None:
    """Seconds until the two touch if neither changes velocity, or None if
    they never would. 0 when they already touch.

    Solves |d + w·t| = radius for the earliest t ≥ 0, where d is b's position
    relative to a and w is b's velocity relative to a.
    """
    _check_radius(radius_m)
    dx, dy = b.x_m - a.x_m, b.y_m - a.y_m
    wx, wy = b.vx_mps - a.vx_mps, b.vy_mps - a.vy_mps
    gap_sq = dx * dx + dy * dy - radius_m * radius_m
    if gap_sq <= 0:
        return 0.0
    speed_sq = wx * wx + wy * wy
    if speed_sq == 0:
        return None
    half_b = dx * wx + dy * wy
    discriminant = half_b * half_b - speed_sq * gap_sq
    if discriminant < 0:
        return None
    # They aren't touching now, so both roots have the same sign: if the
    # earlier one is in the past, they are moving apart.
    t = (-half_b - math.sqrt(discriminant)) / speed_sq
    return t if t >= 0 else None


def minimum_ttc(a: Track, b: Track, radius_m: float) -> tuple[float, float] | None:
    """The lowest TTC over the moments both tracks were seen, as
    (time it happened, TTC), or None if they were never on a collision course.

    Tracks from one camera share frame timestamps, so moments are matched
    exactly; a moment only one of them was seen at is skipped.
    """
    _check_radius(radius_m)
    b_by_time = {s.time_s: s for s in motion_states(b)}
    lowest: tuple[float, float] | None = None
    for state_a in motion_states(a):
        state_b = b_by_time.get(state_a.time_s)
        if state_b is None:
            continue
        ttc = time_to_collision(state_a, state_b, radius_m)
        if ttc is not None and (lowest is None or ttc < lowest[1]):
            lowest = (state_a.time_s, ttc)
    return lowest


def post_encroachment_time(a: Track, b: Track, radius_m: float) -> float | None:
    """The shortest time between the two being at the same place: the
    smallest gap in time between any point of a and any point of b that are
    within radius_m of each other. None if their paths never come that close.

    Two road users following each other in one lane also pass the same
    places, so for them this is just their time headway: PET measures
    crossing and lane-change conflicts, and TTC is the measure for rear-end
    ones.
    """
    _check_radius(radius_m)
    radius_sq = radius_m * radius_m
    lowest: float | None = None
    for pa in a.points:
        for pb in b.points:
            dx, dy = pb.x_m - pa.x_m, pb.y_m - pa.y_m
            if dx * dx + dy * dy > radius_sq:
                continue
            gap = abs(pb.time_s - pa.time_s)
            if lowest is None or gap < lowest:
                lowest = gap
    return lowest


def deceleration_to_avoid(a: MotionState, b: MotionState, radius_m: float) -> float | None:
    """DRAC, in m/s²: how hard the two would have to brake against each other
    to stop closing before they touch: closing speed² / (2 × gap).

    None when they aren't closing, and when they already touch (the TTC of 0
    says that). SSAM doesn't define DRAC; this is the usual closing-speed form,
    and the 3.35 m/s² threshold often quoted for it is still to be verified
    (docs/research/verify.md).
    """
    _check_radius(radius_m)
    dx, dy = b.x_m - a.x_m, b.y_m - a.y_m
    distance = math.hypot(dx, dy)
    gap = distance - radius_m
    if gap <= 0:
        return None
    wx, wy = b.vx_mps - a.vx_mps, b.vy_mps - a.vy_mps
    # Closing speed is the part of the relative velocity pointing from b back
    # towards a; sideways motion doesn't close the gap.
    closing = -(dx * wx + dy * wy) / distance
    if closing <= 0:
        return None
    return closing * closing / (2 * gap)


def speed_difference(a: MotionState, b: MotionState) -> float:
    """SSAM's DeltaS, in m/s: the size of the difference between the two
    velocity vectors, so a head-on pass at 10 m/s each is 20."""
    return math.hypot(b.vx_mps - a.vx_mps, b.vy_mps - a.vy_mps)


def conflict_angle(first: tuple[float, float], second: tuple[float, float]) -> float:
    """The angle in degrees from the first road user's heading to the
    second's, in (-180, 180], counterclockwise positive.

    SSAM approximates each heading by the change in position over the
    conflict and takes the angle from the first road user to arrive at the
    conflict point; the caller passes those two displacements, in that order.
    """
    if first == (0.0, 0.0) or second == (0.0, 0.0):
        raise ValueError("a heading needs a movement, not a standstill")
    angle = math.degrees(math.atan2(second[1], second[0]) - math.atan2(first[1], first[0]))
    while angle <= -180.0:
        angle += 360.0
    while angle > 180.0:
        angle -= 360.0
    return angle


def conflict_type(angle_deg: float) -> ConflictType:
    """SSAM's classes, by the size of the conflict angle."""
    size = abs(angle_deg)
    if size < REAR_END_BELOW_DEG:
        return ConflictType.REAR_END
    if size > CROSSING_ABOVE_DEG:
        return ConflictType.CROSSING
    return ConflictType.LANE_CHANGE


def _check_radius(radius_m: float) -> None:
    if not (math.isfinite(radius_m) and radius_m > 0):
        raise ValueError("the collision radius must be a positive number of metres")
