"""ByteTrack keeps each road user's number from frame to frame."""

import numpy as np
import pytest
from conftest import square_boxes

from roundabout_watch.model import Detection, Frame, RoadUser
from roundabout_watch.track import Tracker


def _frame(index: int) -> Frame:
    return Frame(index=index, time_s=index / 25, image=np.zeros((96, 160, 3), dtype=np.uint8))


def _detections(index: int, boxes: list[tuple[float, float, float, float]]) -> list[Detection]:
    return [
        Detection(frame=index, time_s=index / 25, kind=RoadUser.CAR, confidence=0.9, box=box)
        for box in boxes
    ]


def test_two_road_users_keep_their_own_numbers() -> None:
    tracker = Tracker(frame_rate=25)
    ids_by_frame = []
    for i, (a, b) in enumerate(square_boxes(10)):
        detections = _detections(i, [a, b])
        tracked = tracker.update(_frame(i), detections)
        # Each answer is one of the Detections passed in, not a copy.
        assert all(any(t.detection is d for d in detections) for t in tracked)
        ids_by_frame.append({t.detection.box: t.track_id for t in tracked})
    # A new road user joins once it's been seen in two frames in a row.
    assert ids_by_frame[0] == {}
    a_ids = {ids[a] for ids, (a, _) in zip(ids_by_frame[1:], square_boxes(10)[1:], strict=True)}
    b_ids = {ids[b] for ids, (_, b) in zip(ids_by_frame[1:], square_boxes(10)[1:], strict=True)}
    assert len(a_ids) == 1
    assert len(b_ids) == 1
    assert a_ids != b_ids


def test_a_frame_with_nothing_in_it() -> None:
    assert Tracker(frame_rate=25).update(_frame(0), []) == []


@pytest.mark.parametrize("rate", [0.0, -25.0, float("nan")])
def test_frame_rate_must_be_positive(rate: float) -> None:
    with pytest.raises(ValueError):
        Tracker(frame_rate=rate)
