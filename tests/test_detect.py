"""Turning the detector's boxes into Detections.

RF-DETR itself needs its weights and PyTorch, which CI doesn't install
(CLAUDE.md 37), so these tests hand-build what it returns.
"""

import importlib.util
import math
from typing import Any

import numpy as np
import pytest
import supervision as sv

from roundabout_watch.detect import ROAD_USERS, RFDETRDetector, to_detections
from roundabout_watch.model import Frame, RoadUser


def _frame(width: int = 200, height: int = 100) -> Frame:
    return Frame(index=7, time_s=1.5, image=np.zeros((height, width, 3), dtype=np.uint8))


def _found(rows: list[tuple[tuple[float, float, float, float], float, str]]) -> sv.Detections:
    return sv.Detections(
        xyxy=np.array([r[0] for r in rows], dtype=np.float32).reshape(-1, 4),
        confidence=np.array([r[1] for r in rows], dtype=np.float32),
        data={"class_name": np.array([r[2] for r in rows])},
    )


def test_road_users_cover_every_kind() -> None:
    assert set(ROAD_USERS.values()) == set(RoadUser)


def test_keeps_road_users_and_drops_the_rest() -> None:
    found = _found([((10, 10, 50, 40), 0.9, "car"), ((60, 10, 80, 40), 0.8, "dog")])
    detections, dropped = to_detections(_frame(), found)
    assert [d.kind for d in detections] == [RoadUser.CAR]
    # A dog isn't unusable, just not a road user: it isn't counted as dropped.
    assert dropped == 0
    car = detections[0]
    assert (car.frame, car.time_s, car.box) == (7, 1.5, (10.0, 10.0, 50.0, 40.0))
    assert car.confidence == pytest.approx(0.9)


def test_boxes_are_clipped_to_the_frame() -> None:
    # A bus hanging off the left and bottom edges of a 200 × 100 frame.
    found = _found([((-20, 60, 50, 130), 0.9, "bus")])
    detections, _ = to_detections(_frame(), found)
    assert detections[0].box == (0.0, 60.0, 50.0, 100.0)


@pytest.mark.parametrize(
    ("box", "score"),
    [
        ((250, 10, 300, 40), 0.9),  # entirely right of the frame
        ((10, 10, 10, 40), 0.9),  # no width
        # supervision refuses a NaN box itself, but lets a NaN score through.
        ((10, 10, 50, 40), math.nan),
    ],
)
def test_unusable_boxes_are_dropped_and_counted(
    box: tuple[float, float, float, float], score: float
) -> None:
    detections, dropped = to_detections(_frame(), _found([(box, score, "car")]))
    assert detections == []
    assert dropped == 1


def test_a_score_a_hair_over_one_is_kept() -> None:
    # float32 rounding can give 1.0000001; Detection only accepts 0 to 1.
    found = sv.Detections(
        xyxy=np.array([[10, 10, 50, 40]], dtype=np.float32),
        confidence=np.array([1.0000001], dtype=np.float64),
        data={"class_name": np.array(["car"])},
    )
    detections, _ = to_detections(_frame(), found)
    assert detections[0].confidence == 1.0


def test_output_without_class_names_is_refused() -> None:
    found = sv.Detections(
        xyxy=np.array([[10, 10, 50, 40]], dtype=np.float32),
        confidence=np.array([0.9], dtype=np.float32),
    )
    with pytest.raises(ValueError):
        to_detections(_frame(), found)


class _FakeModel:
    def __init__(self, found: sv.Detections) -> None:
        self.found = found
        self.calls: list[tuple[Any, float]] = []

    def predict(self, images: Any, threshold: float = 0.5, **kwargs: Any) -> Any:
        self.calls.append((images, threshold))
        return self.found


def test_detector_passes_the_rgb_image_and_threshold() -> None:
    model = _FakeModel(_found([((10, 10, 50, 40), 0.9, "car"), ((300, 0, 310, 5), 0.9, "car")]))
    detector = RFDETRDetector(threshold=0.4, model=model)
    frame = _frame()
    detections = detector.detect(frame)
    assert model.calls == [(frame.image, 0.4)]
    assert len(detections) == 1
    assert detector.dropped == 1


@pytest.mark.parametrize("size", ["pico", "xlarge", "2xlarge", "huge"])
def test_only_apache_sizes_are_loaded(size: str) -> None:
    # Atto to Pico, XL and 2XL are under PML 1.0 (ADR 0004).
    with pytest.raises(ValueError):
        RFDETRDetector(size=size, model=_FakeModel(_found([])))


@pytest.mark.parametrize("threshold", [0.0, 1.0, -0.1])
def test_threshold_must_be_a_probability(threshold: float) -> None:
    with pytest.raises(ValueError):
        RFDETRDetector(threshold=threshold, model=_FakeModel(_found([])))


@pytest.mark.skipif(
    importlib.util.find_spec("rfdetr") is not None,
    reason="RF-DETR is installed here; loading it would download its weights",
)
def test_a_missing_detector_says_how_to_install_it() -> None:
    with pytest.raises(RuntimeError, match="--extra detector"):
        RFDETRDetector()
