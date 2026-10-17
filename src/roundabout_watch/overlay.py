"""Draws the tracks onto the video, so a person can watch the pipeline work.

`replay` writes its output through here: a box and a label ("car 12") on
every tracked road user, and a two-second trail along its ground-contact
point, the bottom-middle of its box, which is the point ground.py will turn
into metres. supervision (MIT) draws; it is already here through trackers.
PyAV writes H.264 with the libx264 it bundles, which is GPL: fine for our own
use, and only a question if the program is ever given to anyone (ADR 0007).
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from types import TracebackType

import av
import numpy as np
import supervision as sv
from numpy.typing import NDArray

from roundabout_watch.model import Frame, TrackedDetection

TRAIL_SECONDS = 2.0


class Overlay:
    def __init__(self, frame_rate: float) -> None:
        self._boxes = sv.BoxAnnotator(color_lookup=sv.ColorLookup.TRACK)
        # smart_position keeps a label inside the frame; a bus whose box
        # touches the top edge otherwise loses its label above the picture.
        self._labels = sv.LabelAnnotator(color_lookup=sv.ColorLookup.TRACK, smart_position=True)
        self._trails = sv.TraceAnnotator(
            color_lookup=sv.ColorLookup.TRACK,
            position=sv.Position.BOTTOM_CENTER,
            trace_length=max(1, round(frame_rate * TRAIL_SECONDS)),
        )

    def draw(self, frame: Frame, tracked: Sequence[TrackedDetection]) -> NDArray[np.uint8]:
        """A copy of the frame with the tracks drawn on, in BGR, the channel
        order supervision draws in and VideoWriter takes."""
        scene: NDArray[np.uint8] = np.ascontiguousarray(frame.image[..., ::-1])
        if not tracked:
            return scene
        found = sv.Detections(
            xyxy=np.array([t.detection.box for t in tracked], dtype=np.float32),
            tracker_id=np.array([t.track_id for t in tracked], dtype=int),
        )
        labels = [f"{t.detection.kind.value} {t.track_id}" for t in tracked]
        scene = self._trails.annotate(scene, found)
        scene = self._boxes.annotate(scene, found)
        return self._labels.annotate(scene, found, labels=labels)


class VideoWriter:
    """Writes BGR frames to an H.264 MP4 with no sound track. Use it in a
    `with` block, so the file is finished even when something fails."""

    def __init__(self, path: Path, width: int, height: int, fps: float) -> None:
        # H.264 in the usual yuv420p needs even sizes; a phone video almost
        # always has them, and an odd one loses its last row or column.
        self._width = width - width % 2
        self._height = height - height % 2
        if self._width <= 0 or self._height <= 0:
            raise ValueError("the video is too small to write")
        self._container = av.open(str(path), mode="w")
        try:
            # A constant rate at the input's average: a phone's slight
            # wander in frame timing doesn't matter for watching.
            stream = self._container.add_stream("h264", rate=Fraction(fps).limit_denominator(1001))
            stream.width = self._width
            stream.height = self._height
            stream.pix_fmt = "yuv420p"
            self._stream = stream
        except BaseException:
            self._container.close()
            raise

    def write(self, bgr: NDArray[np.uint8]) -> None:
        frame = av.VideoFrame.from_ndarray(
            np.ascontiguousarray(bgr[: self._height, : self._width]), format="bgr24"
        )
        for packet in self._stream.encode(frame):
            self._container.mux(packet)

    def close(self) -> None:
        try:
            for packet in self._stream.encode(None):
                self._container.mux(packet)
        finally:
            self._container.close()

    def __enter__(self) -> VideoWriter:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
