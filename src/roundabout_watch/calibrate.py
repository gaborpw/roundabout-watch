"""The work behind the "Calibrate" page (ADR 0012), kept out of the
Streamlit script so it's tested like any other module.

The page shows one frame of a video. A person clicks a spot on the road and
pastes where it is from a map; this turns the click into the frame's own
pixels, reads the pasted latitude and longitude, draws the spots, and
writes calibration.yaml in the shape ground.py reads.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

import cv2
import numpy as np
import yaml
from numpy.typing import NDArray

from roundabout_watch.ground import Calibration, CalibrationError, FitReport, SurveyPoint
from roundabout_watch.ingest import VideoFile
from roundabout_watch.model import Frame

# Where ground.py's callers look, relative to the repository's root, which
# is where the README says to start the app.
CALIBRATION_FILE = Path("calibration.yaml")

# Spots on the frame: already paired with the map, and the one just clicked.
SPOT_COLOUR = (255, 200, 0)
PENDING_COLOUR = (255, 60, 60)

# What Google Maps copies when its coordinates are clicked: "41.48163,
# -81.72891" (Google Maps Help, "Search by latitude & longitude", read
# 2026-10-21). A space instead of the comma is accepted too.
_LAT_LON = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(?:,\s*|\s+)(-?\d+(?:\.\d+)?)\s*$")


def frame_at(video: Path, seconds: float) -> Frame:
    """The first frame at least this many seconds into the video, or its
    last frame if it's shorter."""
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("seconds into the video must be zero or more")
    last: Frame | None = None
    start: float | None = None
    with VideoFile(video) as source:
        for frame in source.frames():
            start = frame.time_s if start is None else start
            last = frame
            if frame.time_s - start >= seconds:
                return frame
    if last is None:
        raise ValueError("that video has no frames")
    return last


def parse_lat_lon(text: str) -> tuple[float, float]:
    """Latitude and longitude as pasted from a map."""
    match = _LAT_LON.match(text)
    if match is None:
        raise CalibrationError(
            "paste the latitude and longitude as two numbers, like 41.48163, -81.72891"
        )
    lat, lon = float(match[1]), float(match[2])
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise CalibrationError("that isn't a latitude and longitude; latitude comes first")
    return lat, lon


def image_pixel(
    click: Mapping[str, object], frame_width: int, frame_height: int
) -> tuple[float, float]:
    """Where a click landed, in the frame's own pixels.

    The click component reports the click on the picture as drawn, with the
    drawn size, and the page draws the frame to fit its column; scaling by
    the two sizes undoes that. Its answer comes from the browser, so it is
    checked before it's believed (CLAUDE.md 17).
    """
    values: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        value = click.get(key)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"the click has no usable {key}")
        values[key] = float(value)
    if values["width"] <= 0 or values["height"] <= 0:
        raise ValueError("the click came from a picture with no size")
    x = values["x"] * frame_width / values["width"]
    y = values["y"] * frame_height / values["height"]
    # One decimal is a tenth of a pixel: finer than anyone clicks.
    return (
        round(min(max(x, 0.0), float(frame_width)), 1),
        round(min(max(y, 0.0), float(frame_height)), 1),
    )


def mark_spots(
    image: NDArray[np.uint8],
    spots: Sequence[SurveyPoint],
    pending: tuple[float, float] | None = None,
) -> NDArray[np.uint8]:
    """A copy of the frame with each spot drawn and numbered as in the
    list, and the spot just clicked in another colour."""
    marked = image.copy()
    height, width = marked.shape[:2]
    # Big enough to see on a 4K frame shrunk into a column.
    radius = max(4, round(min(width, height) / 120))
    thick = max(1, radius // 3)
    for number, spot in enumerate(spots, start=1):
        centre = (round(spot.pixel[0]), round(spot.pixel[1]))
        cv2.circle(marked, centre, radius, SPOT_COLOUR, thick)
        cv2.putText(
            marked,
            str(number),
            (centre[0] + radius + 2, centre[1] - radius - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            radius / 10,
            SPOT_COLOUR,
            thick,
        )
    if pending is not None:
        centre = (round(pending[0]), round(pending[1]))
        cv2.circle(marked, centre, radius, PENDING_COLOUR, thick)
        cv2.drawMarker(marked, centre, PENDING_COLOUR, cv2.MARKER_CROSS, radius * 2, thick)
    return marked


def calibration_yaml(calibration: Calibration, made: date) -> str:
    """calibration.yaml's text, in the shape ground.py reads."""
    data = {
        "image_size": [calibration.image_width, calibration.image_height],
        "points": [
            {"name": p.name, "pixel": [p.pixel[0], p.pixel[1]], "lat": p.lat, "lon": p.lon}
            for p in calibration.points
        ],
    }
    header = (
        f"# Made on the Calibrate page on {made.isoformat()}. Each point is a spot in\n"
        "# the video and its latitude and longitude from a map (ground.py).\n"
    )
    return header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def report_rows(report: FitReport) -> list[dict[str, object]]:
    """One row per spot: how far it lands from its map position."""
    return [
        {"spot": f"{number}. {name}", "metres off": round(metres, 2)}
        for number, (name, metres) in enumerate(report.fit_m.items(), start=1)
    ]
