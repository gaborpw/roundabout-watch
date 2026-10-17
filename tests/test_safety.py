"""Safety measures against scenarios worked out by hand.

Every scenario is made up for the test, not measured (CLAUDE.md 6), and its
expected answer is worked out in the comment above it.
"""

import math

import pytest

from roundabout_watch.model import ConflictType, RoadUser, Track, TrackPoint
from roundabout_watch.safety import (
    MotionState,
    conflict_angle,
    conflict_type,
    deceleration_to_avoid,
    minimum_ttc,
    motion_states,
    post_encroachment_time,
    speed_difference,
    time_to_collision,
)


def _state(x: float, y: float, vx: float, vy: float, t: float = 0.0) -> MotionState:
    return MotionState(time_s=t, x_m=x, y_m=y, vx_mps=vx, vy_mps=vy)


def _track(track_id: int, points: list[tuple[float, float, float]]) -> Track:
    return Track(
        track_id=track_id,
        kind=RoadUser.CAR,
        points=tuple(TrackPoint(t, x, y) for t, x, y in points),
    )


# --- time to collision -----------------------------------------------------


def test_ttc_head_on() -> None:
    # 50 m apart, closing at 10 + 10 = 20 m/s, touching at 2 m apart:
    # (50 - 2) / 20 = 2.4 s.
    a = _state(0, 0, 10, 0)
    b = _state(50, 0, -10, 0)
    assert time_to_collision(a, b, radius_m=2) == pytest.approx(2.4)


def test_ttc_crossing_at_right_angles() -> None:
    # a heads north and b heads east, both 20 m from the same corner at
    # 10 m/s. Seen from a, b comes straight at it along the diagonal:
    # distance 20√2 ≈ 28.284 m at a relative speed of 10√2 ≈ 14.142 m/s, so
    # (28.284 - 2) / 14.142 ≈ 1.8586 s.
    a = _state(0, -20, 0, 10)
    b = _state(-20, 0, 10, 0)
    expected = (20 * math.sqrt(2) - 2) / (10 * math.sqrt(2))
    assert time_to_collision(a, b, radius_m=2) == pytest.approx(expected)


def test_ttc_rear_end() -> None:
    # a at 15 m/s is 20 m behind b at 10 m/s: closing at 5 m/s, and with a
    # 4 m collision radius the gap is 16 m, so 16 / 5 = 3.2 s.
    a = _state(0, 0, 15, 0)
    b = _state(20, 0, 10, 0)
    assert time_to_collision(a, b, radius_m=4) == pytest.approx(3.2)


def test_ttc_none_when_they_pass_wide() -> None:
    # Head-on but 5 m apart sideways, with a 2 m radius: they never touch.
    a = _state(0, 0, 10, 0)
    b = _state(50, 5, -10, 0)
    assert time_to_collision(a, b, radius_m=2) is None


def test_ttc_none_when_moving_apart() -> None:
    a = _state(0, 0, -10, 0)
    b = _state(50, 0, 10, 0)
    assert time_to_collision(a, b, radius_m=2) is None


def test_ttc_none_at_the_same_velocity() -> None:
    # Driving side by side at the same speed: the gap never changes.
    a = _state(0, 0, 10, 0)
    b = _state(0, 3, 10, 0)
    assert time_to_collision(a, b, radius_m=2) is None


def test_ttc_zero_when_already_touching() -> None:
    a = _state(0, 0, 10, 0)
    b = _state(1, 0, 0, 0)
    assert time_to_collision(a, b, radius_m=2) == 0.0


@pytest.mark.parametrize("radius", [0.0, -1.0, math.nan, math.inf])
def test_ttc_rejects_impossible_radius(radius: float) -> None:
    with pytest.raises(ValueError):
        time_to_collision(_state(0, 0, 1, 0), _state(5, 0, 0, 0), radius_m=radius)


# --- velocities from a track ------------------------------------------------


def test_motion_states_central_difference() -> None:
    # 10 m every second along x: every point is moving at 10 m/s.
    track = _track(1, [(0, 0, 0), (1, 10, 0), (2, 20, 0)])
    states = motion_states(track)
    assert [s.vx_mps for s in states] == pytest.approx([10, 10, 10])
    assert [s.vy_mps for s in states] == pytest.approx([0, 0, 0])


def test_motion_states_smooths_a_jitter() -> None:
    # The middle point is 1 m off the line; the central difference at it
    # looks past it ((20 - 0) / 2 = 10 m/s), while the ends see the jump.
    track = _track(1, [(0, 0, 0), (1, 11, 0), (2, 20, 0)])
    states = motion_states(track)
    assert states[1].vx_mps == pytest.approx(10)
    assert states[0].vx_mps == pytest.approx(11)
    assert states[2].vx_mps == pytest.approx(9)


def test_motion_states_needs_two_points() -> None:
    assert motion_states(_track(1, [(0, 0, 0)])) == []


# --- minimum TTC over two tracks --------------------------------------------


def test_minimum_ttc_over_shared_moments() -> None:
    # Head-on at 10 m/s each, starting 50 m apart, seen at t = 0, 1, 2 s.
    # With a 2 m radius the TTC falls by 1 s a second: 2.4, 1.4, 0.4. The
    # lowest is 0.4 s, at t = 2.
    a = _track(1, [(0, 0, 0), (1, 10, 0), (2, 20, 0)])
    b = _track(2, [(0, 50, 0), (1, 40, 0), (2, 30, 0)])
    result = minimum_ttc(a, b, radius_m=2)
    assert result is not None
    when, ttc = result
    assert when == 2
    assert ttc == pytest.approx(0.4)


def test_minimum_ttc_skips_moments_only_one_saw() -> None:
    # b was only seen at t = 1 and 2, so t = 0 can't be compared.
    a = _track(1, [(0, 0, 0), (1, 10, 0), (2, 20, 0)])
    b = _track(2, [(1, 40, 0), (2, 30, 0)])
    result = minimum_ttc(a, b, radius_m=2)
    assert result is not None
    assert result[0] == 2


def test_minimum_ttc_none_without_a_collision_course() -> None:
    a = _track(1, [(0, 0, 0), (1, 10, 0)])
    b = _track(2, [(0, 0, 10), (1, 10, 10)])
    assert minimum_ttc(a, b, radius_m=2) is None


# --- post-encroachment time -------------------------------------------------


def test_pet_crossing_paths() -> None:
    # a drives north through the corner (0, 0) at t = 2; b drives east
    # through it at t = 3.5. With a tiny radius only those two points meet:
    # PET = 3.5 - 2 = 1.5 s.
    a = _track(1, [(t, 0, -20 + 10 * t) for t in (0, 0.5, 1, 1.5, 2, 2.5, 3)])
    b = _track(2, [(t, -35 + 10 * t, 0) for t in (2.5, 3, 3.5, 4, 4.5)])
    assert post_encroachment_time(a, b, radius_m=0.1) == pytest.approx(1.5)


def test_pet_none_when_paths_never_meet() -> None:
    a = _track(1, [(0, 0, 0), (1, 10, 0)])
    b = _track(2, [(0, 0, 50), (1, 10, 50)])
    assert post_encroachment_time(a, b, radius_m=2) is None


def test_pet_zero_when_together_at_the_same_moment() -> None:
    # Both at (5, 5) at t = 1: the same place at the same time.
    a = _track(1, [(0, 0, 5), (1, 5, 5)])
    b = _track(2, [(0, 5, 0), (1, 5, 5)])
    assert post_encroachment_time(a, b, radius_m=0.5) == 0


# --- deceleration to avoid a crash ------------------------------------------


def test_drac_rear_end() -> None:
    # Closing at 5 m/s with a 16 m gap (20 m apart, 4 m radius):
    # 5² / (2 × 16) = 0.78125 m/s².
    a = _state(0, 0, 15, 0)
    b = _state(20, 0, 10, 0)
    assert deceleration_to_avoid(a, b, radius_m=4) == pytest.approx(0.78125)


def test_drac_head_on() -> None:
    # Closing at 20 m/s with a 48 m gap: 20² / (2 × 48) ≈ 4.1667 m/s².
    a = _state(0, 0, 10, 0)
    b = _state(50, 0, -10, 0)
    assert deceleration_to_avoid(a, b, radius_m=2) == pytest.approx(400 / 96)


def test_drac_ignores_sideways_motion() -> None:
    # b is 10 m ahead and drifting sideways at 3 m/s: nothing closes the gap.
    a = _state(0, 0, 0, 0)
    b = _state(10, 0, 0, 3)
    assert deceleration_to_avoid(a, b, radius_m=2) is None


def test_drac_none_when_touching() -> None:
    a = _state(0, 0, 10, 0)
    b = _state(1, 0, 0, 0)
    assert deceleration_to_avoid(a, b, radius_m=2) is None


# --- speed difference and conflict type -------------------------------------


def test_speed_difference_head_on() -> None:
    # 10 m/s each, opposite ways: SSAM's DeltaS is 20 m/s.
    assert speed_difference(_state(0, 0, 10, 0), _state(5, 0, -10, 0)) == pytest.approx(20)


@pytest.mark.parametrize(
    ("second", "angle", "kind"),
    [
        ((1.0, 0.0), 0.0, ConflictType.REAR_END),  # same way
        ((1.0, 0.25), math.degrees(math.atan(0.25)), ConflictType.REAR_END),  # ~14°
        ((1.0, 1.0), 45.0, ConflictType.LANE_CHANGE),
        ((0.0, 1.0), 90.0, ConflictType.CROSSING),  # from the right, turning left
        ((0.0, -1.0), -90.0, ConflictType.CROSSING),
        ((-1.0, 0.0), 180.0, ConflictType.CROSSING),  # head-on: SSAM's crossing class
    ],
)
def test_conflict_angle_and_type(
    second: tuple[float, float], angle: float, kind: ConflictType
) -> None:
    measured = conflict_angle((1.0, 0.0), second)
    assert measured == pytest.approx(angle)
    assert conflict_type(measured) is kind


def test_conflict_type_boundaries() -> None:
    # SSAM: rear-end below 30°, crossing above 85°; exactly 30 and 85 are
    # lane changes.
    assert conflict_type(29.9) is ConflictType.REAR_END
    assert conflict_type(30.0) is ConflictType.LANE_CHANGE
    assert conflict_type(85.0) is ConflictType.LANE_CHANGE
    assert conflict_type(85.1) is ConflictType.CROSSING


def test_conflict_angle_needs_movement() -> None:
    with pytest.raises(ValueError):
        conflict_angle((0.0, 0.0), (1.0, 0.0))
