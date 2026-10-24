"""The work behind the "Try a video" page (ADR 0012), kept out of the
Streamlit script so it's tested like any other module.

A video is processed in a temporary folder that is deleted when it's done:
the page keeps only the drawn copy, in memory, until the person leaves or
downloads it. Nothing from a tried video is stored (ADR 0006).
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from roundabout_watch.detect import Detector, RFDETRDetector
from roundabout_watch.model import TrackSpan
from roundabout_watch.replay import Progress, ReplaySummary, replay

# What a phone or a camera saves. Anything else is refused before it is
# written anywhere (CLAUDE.md 17).
VIDEO_SUFFIXES = (".mov", ".mp4", ".m4v", ".mkv", ".avi")

# The tallest the marked-up video is drawn, in pixels, so the charts beside
# and under it fit on a laptop screen with it (Peter, 2026-10-24: "cap it").
PLAYER_MAX_HEIGHT = 480


@dataclass(frozen=True)
class Result:
    name: str
    summary: ReplaySummary
    # The drawn copy, H.264 MP4, small enough to hold: about 4 MB for 30 s
    # of a 1080p phone video.
    video: bytes


def video_suffix(filename: str) -> str:
    """The file's extension, if it's a video's. Only the extension of the
    name a browser sends is used, never the name itself as a path."""
    suffix = Path(filename).suffix.lower()
    if suffix not in VIDEO_SUFFIXES:
        raise ValueError(f"that isn't a video file (use {', '.join(VIDEO_SUFFIXES)})")
    return suffix


@contextmanager
def saved_upload(data: bytes | memoryview, filename: str) -> Iterator[Path]:
    """An uploaded video written to a temporary file, deleted afterwards."""
    suffix = video_suffix(filename)
    with tempfile.TemporaryDirectory(prefix="roundabout-") as folder:
        path = Path(folder) / f"upload{suffix}"
        path.write_bytes(data)
        yield path


def player_width(width: int, height: int) -> int:
    """The player width that keeps a width × height video at most
    PLAYER_MAX_HEIGHT tall. Streamlit's player takes only a width, and never
    draws wider than its column, so a wide video still fills the column."""
    if width <= 0 or height <= 0:
        raise ValueError("a video's size must be positive")
    return max(1, round(PLAYER_MAX_HEIGHT * width / height))


def load_detector(size: str) -> Detector:
    return RFDETRDetector(size=size)


def run(video: Path, name: str, detector: Detector, on_progress: Progress | None = None) -> Result:
    """Replay a video and keep its drawn copy in memory."""
    with tempfile.TemporaryDirectory(prefix="roundabout-") as folder:
        out = Path(folder) / "tracked.mp4"
        summary = replay(video, out, detector, on_progress=on_progress)
        return Result(name=name, summary=summary, video=out.read_bytes())


def timeline(spans: tuple[TrackSpan, ...]) -> list[dict[str, object]]:
    """One row per road user, for the page's table and timeline chart. Times
    are seconds into the video. The names carry no brackets or units, which
    the chart library would read as instructions."""
    return [
        {
            "road user": f"{span.kind.value} {span.track_id}",
            "kind": span.kind.value,
            "arrived": round(span.first_s, 1),
            "left": round(span.last_s, 1),
            "in view": round(span.seconds, 1),
        }
        for span in spans
    ]
