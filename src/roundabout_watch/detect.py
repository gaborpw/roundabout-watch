"""Finds road users in a frame (CLAUDE.md 29, detect → track).

The rest of the pipeline sees only the Detector protocol, so another detector
can replace RF-DETR without touching tracking or the safety maths. RF-DETR
(Apache-2.0, ADR 0004) is the one implementation. It is in the "detector"
extra because it brings PyTorch, which CI never installs (CLAUDE.md 37), so
everything here except loading the model is tested without it.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Protocol

import supervision as sv

from roundabout_watch.model import Detection, Frame, RoadUser

log = logging.getLogger(__name__)

# COCO's names for the classes that move on a road, which is all the safety
# maths needs. Everything else RF-DETR finds (dogs, traffic lights, benches)
# is dropped here. A person riding a bicycle comes out as a person box over a
# bicycle box; telling a cyclist from a pedestrian is a later step.
ROAD_USERS: dict[str, RoadUser] = {
    "person": RoadUser.PEDESTRIAN,
    "bicycle": RoadUser.BICYCLE,
    "car": RoadUser.CAR,
    "motorcycle": RoadUser.MOTORCYCLE,
    "bus": RoadUser.BUS,
    "truck": RoadUser.TRUCK,
}

# Only the Apache-2.0 sizes. Atto to Pico, XL and 2XL are under Roboflow's
# PML 1.0 licence and are never loaded (ADR 0004).
MODEL_SIZES = ("nano", "small", "medium", "large")

# ByteTrack keeps a track alive through a moment of occlusion with boxes the
# detector is less sure of (trackers' ByteTrack docs: its second, low-score
# stage), so the detector hands over boxes down to 0.3. Only boxes of 0.7 or
# more start a new track (the trackers package's default).
DEFAULT_THRESHOLD = 0.3


class Detector(Protocol):
    def detect(self, frame: Frame) -> list[Detection]: ...


def to_detections(frame: Frame, found: sv.Detections) -> tuple[list[Detection], int]:
    """A detector's boxes as Detections, and how many boxes were unusable.

    Keeps road users only, and clips each box to the frame. A box that is
    empty or not a number after clipping is dropped and counted rather than
    trusted (CLAUDE.md 17).
    """
    names = found.data.get("class_name")
    if names is None:
        raise ValueError("the detector's output carries no class names")
    if found.confidence is None:
        raise ValueError("the detector's output carries no confidences")
    detections: list[Detection] = []
    dropped = 0
    for box, confidence, name in zip(found.xyxy, found.confidence, names, strict=True):
        kind = ROAD_USERS.get(str(name))
        if kind is None:
            continue
        left, top, right, bottom = (float(v) for v in box)
        score = float(confidence)
        if not all(math.isfinite(v) for v in (left, top, right, bottom, score)):
            dropped += 1
            continue
        left, right = max(left, 0.0), min(right, float(frame.width))
        top, bottom = max(top, 0.0), min(bottom, float(frame.height))
        if right <= left or bottom <= top:
            dropped += 1
            continue
        detections.append(
            Detection(
                frame=frame.index,
                time_s=frame.time_s,
                kind=kind,
                # Rounding can put a score a hair outside 0–1.
                confidence=min(max(score, 0.0), 1.0),
                box=(left, top, right, bottom),
            )
        )
    return detections, dropped


class _Model(Protocol):
    """The part of an RF-DETR model this module uses."""

    def predict(self, images: Any, threshold: float = ..., **kwargs: Any) -> Any: ...


class RFDETRDetector:
    """RF-DETR, pretrained on COCO, on whatever PyTorch finds: CUDA on the
    desktop, Apple's GPU on the Mac, else the CPU.

    The first run downloads the weights (368 MB for Small) from Roboflow's
    public storage into ~/.roboflow/models. No account or key is needed
    (rfdetr 1.11.2's source; its key is only for uploading models).
    """

    def __init__(
        self, size: str = "small", threshold: float = DEFAULT_THRESHOLD, model: _Model | None = None
    ) -> None:
        if size not in MODEL_SIZES:
            raise ValueError(f"model size must be one of {', '.join(MODEL_SIZES)}")
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self._threshold = threshold
        self._model = model if model is not None else _load(size)
        # Boxes dropped as unusable, for the run's summary (CLAUDE.md 35).
        self.dropped = 0

    def detect(self, frame: Frame) -> list[Detection]:
        found = self._model.predict(
            frame.image, threshold=self._threshold, include_source_image=False
        )
        if not isinstance(found, sv.Detections):
            raise TypeError("RF-DETR returned something other than detections")
        detections, dropped = to_detections(frame, found)
        self.dropped += dropped
        return detections


def _load(size: str) -> _Model:
    try:
        import rfdetr
    except ImportError as err:
        raise RuntimeError(
            "RF-DETR isn't installed. Run `uv sync --extra detector` first (README)."
        ) from err
    sizes: dict[str, Any] = {
        "nano": rfdetr.RFDETRNano,
        "small": rfdetr.RFDETRSmall,
        "medium": rfdetr.RFDETRMedium,
        "large": rfdetr.RFDETRLarge,
    }
    model: _Model = sizes[size]()
    log.info("RF-DETR %s loaded", size)
    return model
