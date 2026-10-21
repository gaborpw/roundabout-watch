"""Reads video into Frames: the first stage (CLAUDE.md 29, ingest → detect).

File mode only, for `replay` on a recorded video. Live mode, reading
go2rtc's copy of the camera's stream with a packet buffer for clips, comes at
build step 6 (ADR 0007). PyAV bundles FFmpeg, so a phone's H.264 or HEVC
video works without installing anything else.

Only the video track is decoded. A phone video's sound is never decoded or
kept (CLAUDE.md 20).

A phone held upright stores its picture sideways, with a note saying how far
to turn it (the display matrix). Frames are turned upright here, because
RF-DETR finds sideways cars badly: on Peter's first iPhone video the two cars
scored 0.44–0.74 sideways and 0.85–0.95 upright (docs/lessons.md).
"""

from __future__ import annotations

import itertools
import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import av
import numpy as np

from roundabout_watch.model import Frame

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class VideoInfo:
    width: int
    height: int
    # The stream's average rate. A phone's rate can wander; each Frame's own
    # time_s is what the tracker uses, so this only sizes things like trails.
    fps: float


def quarter_turns(degrees: float) -> int:
    """How many quarter turns counterclockwise make a frame upright, from
    PyAV's VideoFrame.rotation (degrees counterclockwise; an iPhone held
    upright writes -90). Anything but a quarter turn is refused: a phone
    never writes one, and turning by it would mean resampling the picture."""
    quarters = round(degrees / 90)
    if abs(degrees - quarters * 90) > 1:
        raise ValueError(f"the video asks to be turned {degrees:.0f}°, not a quarter turn")
    return quarters % 4


class VideoFile:
    """A video file opened for reading. Use it in a `with` block, so the file
    closes even when decoding stops early."""

    def __init__(self, path: Path) -> None:
        self._container = av.open(str(path))
        try:
            if not self._container.streams.video:
                raise ValueError("the file has no video track")
            self._stream = self._container.streams.video[0]
            # Lets FFmpeg decode on several cores; frames still come out in order.
            self._stream.thread_type = "AUTO"
            rate = self._stream.average_rate
            if rate is None or rate <= 0:
                raise ValueError("the video's frame rate is unknown")
            # The turn is only known once a frame is decoded, so the first
            # one is read now and handed out first by frames().
            self._decoded = self._container.decode(self._stream)
            first = next(self._decoded, None)
            self._quarters = 0 if first is None else quarter_turns(first.rotation)
            if first is not None:
                self._decoded = itertools.chain([first], self._decoded)
            width, height = self._stream.width, self._stream.height
            if self._quarters % 2:
                width, height = height, width
            self.info = VideoInfo(width=width, height=height, fps=float(rate))
        except BaseException:
            self._container.close()
            raise

    def frames(self) -> Iterator[Frame]:
        """Every frame in order, as RGB and upright. A frame with no
        timestamp can't be placed in time, so it's skipped and counted."""
        skipped = 0
        index = 0
        for decoded in self._decoded:
            if decoded.time is None:
                skipped += 1
                continue
            # rgb24 is already one byte a channel, so this copies nothing; it
            # tells the type checker what PyAV's general return type doesn't.
            image = np.asarray(decoded.to_ndarray(format="rgb24"), dtype=np.uint8)
            if self._quarters:
                image = np.ascontiguousarray(np.rot90(image, k=self._quarters))
            yield Frame(index=index, time_s=float(decoded.time), image=image)
            index += 1
        if skipped:
            log.warning("skipped %d frames with no timestamp", skipped)

    def close(self) -> None:
        self._container.close()

    def __enter__(self) -> VideoFile:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
