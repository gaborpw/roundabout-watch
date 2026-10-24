"""`replay`: the pipeline on a recorded video, on any computer.

This is how the code gets developed (docs/architecture.md). Today it runs as
far as tracking (ingest → detect → track) and writes a copy of the video with
the tracks drawn on. There are no near-miss numbers yet: those need metres,
and metres need the calibration in build step 2 (CLAUDE.md, the second idea).
"""

from __future__ import annotations

import logging
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from roundabout_watch.detect import Detector
from roundabout_watch.ingest import VideoFile
from roundabout_watch.model import RoadUser, TrackSpan
from roundabout_watch.overlay import Overlay, VideoWriter
from roundabout_watch.track import Tracker

log = logging.getLogger(__name__)

# Called with the frames done so far and the total the file claims, if any.
Progress = Callable[[int, int | None], None]


@dataclass(frozen=True)
class ReplaySummary:
    frames: int
    # The picture's size as it plays upright, in pixels.
    width: int
    height: int
    video_seconds: float
    wall_seconds: float
    # One per road user the tracker followed, in order of arrival.
    spans: tuple[TrackSpan, ...]

    @property
    def tracks(self) -> dict[RoadUser, int]:
        """Distinct road users of each kind."""
        return dict(Counter(span.kind for span in self.spans))


@dataclass
class _Seen:
    first_s: float
    last_s: float
    frames: int
    kinds: Counter[RoadUser]


def replay(
    video: Path,
    out: Path,
    detector: Detector,
    *,
    progress_every: int = 250,
    on_progress: Progress | None = None,
) -> ReplaySummary:
    started = time.monotonic()
    seen: dict[int, _Seen] = {}
    frames = 0
    first_s: float | None = None
    last_s = 0.0
    with VideoFile(video) as source:
        info = source.info
        log.info("replaying %s: %dx%d at %.1f fps", video.name, info.width, info.height, info.fps)
        tracker = Tracker(info.fps)
        overlay = Overlay(info.fps)
        with VideoWriter(out, info.width, info.height, info.fps) as writer:
            for frame in source.frames():
                tracked = tracker.update(frame, detector.detect(frame))
                writer.write(overlay.draw(frame, tracked))
                first_s = frame.time_s if first_s is None else first_s
                last_s = frame.time_s
                # Seconds from the start of the video: a phone file's first
                # timestamp needn't be zero.
                at = frame.time_s - first_s
                for t in tracked:
                    entry = seen.get(t.track_id)
                    if entry is None:
                        entry = seen[t.track_id] = _Seen(at, at, 0, Counter())
                    entry.last_s = at
                    entry.frames += 1
                    entry.kinds[t.detection.kind] += 1
                frames += 1
                if on_progress is not None:
                    on_progress(frames, info.frames)
                if frames % progress_every == 0:
                    log.info(
                        "%d frames (%.0f s of video) in %.0f s, %d tracks so far",
                        frames,
                        last_s - first_s,
                        time.monotonic() - started,
                        len(seen),
                    )
    spans = tuple(
        sorted(
            (
                # A track the detector called a car in some frames and a
                # truck in others counts as whichever it was called most.
                TrackSpan(
                    track_id=track_id,
                    kind=entry.kinds.most_common(1)[0][0],
                    first_s=entry.first_s,
                    last_s=entry.last_s,
                    frames=entry.frames,
                )
                for track_id, entry in seen.items()
            ),
            key=lambda span: (span.first_s, span.track_id),
        )
    )
    return ReplaySummary(
        frames=frames,
        width=info.width,
        height=info.height,
        video_seconds=0.0 if first_s is None else last_s - first_s,
        wall_seconds=time.monotonic() - started,
        spans=spans,
    )
