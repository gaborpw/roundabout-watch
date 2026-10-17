"""Links detections across frames into tracks (CLAUDE.md 29, detect → track).

ByteTrack from Roboflow's trackers package (Apache-2.0, ADR 0004). It
predicts where each road user's box goes next with a Kalman filter and
matches the new boxes to those predictions by overlap. A second pass uses the
detector's less certain boxes to keep a track alive while something passes
in front of it. The output is still in pixels; ground.py comes next.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import supervision as sv
from trackers import ByteTrackTracker

from roundabout_watch.model import Detection, Frame, TrackedDetection


class Tracker:
    def __init__(self, frame_rate: float) -> None:
        if not (math.isfinite(frame_rate) and frame_rate > 0):
            raise ValueError("frame_rate must be a positive number of frames a second")
        # frame_rate scales how long a lost track is remembered; each update
        # passes the frame's own time, so an uneven phone video still works.
        self._bytetrack = ByteTrackTracker(frame_rate=frame_rate)

    def update(self, frame: Frame, detections: Sequence[Detection]) -> list[TrackedDetection]:
        """This frame's detections that belong to a track. A new road user
        joins after it has been seen in two frames in a row (the trackers
        package's default), which keeps one-frame false alarms out."""
        boxes = np.array([d.box for d in detections], dtype=np.float32).reshape(-1, 4)
        found = sv.Detections(
            xyxy=boxes,
            confidence=np.array([d.confidence for d in detections], dtype=np.float32),
            # Each box's position in `detections`, which survives ByteTrack's
            # reordering, so its answer maps back to our own Detection.
            data={"index": np.arange(len(detections))},
        )
        tracked = self._bytetrack.update(found, timestamp=frame.time_s)
        if tracked.tracker_id is None or "index" not in tracked.data:
            return []
        return [
            TrackedDetection(track_id=int(track_id), detection=detections[int(index)])
            for track_id, index in zip(tracked.tracker_id, tracked.data["index"], strict=True)
            if track_id >= 0
        ]
