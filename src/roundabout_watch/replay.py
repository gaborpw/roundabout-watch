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
from dataclasses import dataclass
from pathlib import Path

from roundabout_watch.detect import Detector
from roundabout_watch.ingest import VideoFile
from roundabout_watch.model import RoadUser
from roundabout_watch.overlay import Overlay, VideoWriter
from roundabout_watch.track import Tracker

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReplaySummary:
    frames: int
    video_seconds: float
    wall_seconds: float
    # Distinct tracks of each kind. A track the detector called a car in
    # some frames and a truck in others counts as whichever it was called
    # most often.
    tracks: dict[RoadUser, int]


def replay(
    video: Path, out: Path, detector: Detector, *, progress_every: int = 250
) -> ReplaySummary:
    started = time.monotonic()
    kinds: dict[int, Counter[RoadUser]] = {}
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
                for t in tracked:
                    kinds.setdefault(t.track_id, Counter())[t.detection.kind] += 1
                frames += 1
                first_s = frame.time_s if first_s is None else first_s
                last_s = frame.time_s
                if frames % progress_every == 0:
                    elapsed = time.monotonic() - started
                    log.info(
                        "%d frames (%.0f s of video) in %.0f s, %d tracks so far",
                        frames,
                        last_s - first_s,
                        elapsed,
                        len(kinds),
                    )
    tracks = Counter(counts.most_common(1)[0][0] for counts in kinds.values())
    return ReplaySummary(
        frames=frames,
        video_seconds=0.0 if first_s is None else last_s - first_s,
        wall_seconds=time.monotonic() - started,
        tracks=dict(tracks),
    )
