"""Pixels to metres on the road (build step 2; CLAUDE.md, the second idea).

A calibration pairs at least four points seen in the video (a lamp post's
base, a crosswalk corner) with where they are on a map, as latitude and
longitude. From those pairs this fits a homography: the one perspective
mapping that takes the flat road in the picture to the flat road on the
map. Every detection's ground-contact pixel then becomes a position in
metres, east and north of the calibration's own centre, which is what
safety.py measures with.

It reports how well the points agree (`FitReport`), and it refuses to run
without a calibration: no calibration means no metres, never guessed ones.
The road is treated as flat; the roundabout's slope bends the mapping a
little, which the fit's errors show.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import yaml
from numpy.typing import NDArray

from roundabout_watch.model import Detection, TrackPoint

# The WGS 84 ellipsoid, the shape GPS and web maps use: its semi-major axis
# and flattening (NGA, https://earth-info.nga.mil/index.php?dir=wgs84&action=wgs84,
# read 2026-10-21).
WGS84_A_M = 6_378_137.0
WGS84_F = 1.0 / 298.257223563

MIN_POINTS = 4
# Saying which point is off needs the others to check each other after it
# is set aside: five left over, one more than a fit needs.
RECHECK_MIN_POINTS = MIN_POINTS + 2

# Our own guards, not outside facts:
# - A perspective is fixed by four points with no three on one line (general
#   knowledge of homographies), and OpenCV doesn't check: four points on one
#   line come back as a meaningless matrix. Three points count as on one
#   line when the narrow spread of the three is under this share of the wide.
MIN_SPREAD_RATIO = 0.05
# - The roundabout is about 30 m across, so points further apart than this
#   are a typo (a swapped latitude and longitude, a dropped minus sign).
MAX_SPREAD_M = 2_000.0


class CalibrationError(ValueError):
    """The calibration is missing or can't be used. Its message says which
    and what to do about it."""


@dataclass(frozen=True)
class SurveyPoint:
    """One spot seen in the video, and where it is on the map."""

    name: str
    # (x, y) in pixels of the upright frame, origin at the top-left corner.
    pixel: tuple[float, float]
    lat: float
    lon: float


@dataclass(frozen=True)
class Calibration:
    """The pairs for one camera view, at one picture size."""

    image_width: int
    image_height: int
    points: tuple[SurveyPoint, ...]

    def __post_init__(self) -> None:
        if self.image_width <= 0 or self.image_height <= 0:
            raise CalibrationError("the picture size must be positive")
        if len(self.points) < MIN_POINTS:
            raise CalibrationError(
                f"a calibration needs at least {MIN_POINTS} points; it has {len(self.points)}"
            )
        names = [p.name for p in self.points]
        if len(set(names)) != len(names):
            raise CalibrationError("each point needs its own name")
        for p in self.points:
            x, y = p.pixel
            if not all(math.isfinite(v) for v in (x, y, p.lat, p.lon)):
                raise CalibrationError(f"point {p.name!r}: every number must be finite")
            if not (-90.0 <= p.lat <= 90.0 and -180.0 <= p.lon <= 180.0):
                raise CalibrationError(f"point {p.name!r}: that isn't a latitude and longitude")
            if not (0.0 <= x <= self.image_width and 0.0 <= y <= self.image_height):
                raise CalibrationError(
                    f"point {p.name!r}: pixel {p.pixel} is outside the "
                    f"{self.image_width}×{self.image_height} picture"
                )

    @property
    def origin(self) -> tuple[float, float]:
        """The latitude and longitude that ground positions are measured
        from: the middle of the points."""
        return (
            sum(p.lat for p in self.points) / len(self.points),
            sum(p.lon for p in self.points) / len(self.points),
        )


def local_metres(
    lat: float, lon: float, origin_lat: float, origin_lon: float
) -> tuple[float, float]:
    """Metres east and north of the origin.

    Uses the ellipsoid's radii of curvature at the origin. Over the few tens
    of metres of a roundabout that is within a millimetre or so of the exact
    answer (tests/test_ground.py checks it against an exact conversion); a
    sphere would be off by up to about 0.3%.
    """
    phi = math.radians(origin_lat)
    e2 = WGS84_F * (2.0 - WGS84_F)
    w = 1.0 - e2 * math.sin(phi) ** 2
    north_radius = WGS84_A_M * (1.0 - e2) / w**1.5
    east_radius = WGS84_A_M / math.sqrt(w)
    east = east_radius * math.cos(phi) * math.radians(lon - origin_lon)
    north = north_radius * math.radians(lat - origin_lat)
    return east, north


def _spread_ratio(points: NDArray[np.float64]) -> float:
    """How far from a straight line a set of points is: the narrow spread
    over the wide one, from 0 (all on one line) to 1."""
    singular = np.linalg.svd(points - points.mean(axis=0), compute_uv=False)
    return float(singular[1] / singular[0]) if singular[0] > 0 else 0.0


def _fixes_a_perspective(points: NDArray[np.float64]) -> bool:
    """Whether some four of the points have no three on one line. Checking
    all the points' spread at once isn't enough: five on a line and one off
    it look spread out, and still don't fix a perspective."""
    for four in itertools.combinations(range(len(points)), 4):
        if all(
            _spread_ratio(points[list(three)]) >= MIN_SPREAD_RATIO
            for three in itertools.combinations(four, 3)
        ):
            return True
    return False


def _fit(pixels: NDArray[np.float64], ground: NDArray[np.float64]) -> NDArray[np.float64]:
    # Method 0: least squares over every point. RANSAC would quietly drop a
    # mistyped point; here a bad point should show up in the errors instead.
    matrix, _ = cv2.findHomography(pixels, ground, 0)
    h = np.asarray(matrix, dtype=np.float64)
    if h.shape != (3, 3) or not np.all(np.isfinite(h)) or abs(np.linalg.det(h)) < 1e-12:
        raise CalibrationError("these points don't fix a mapping; spread them across the road")
    return h


def _apply(h: NDArray[np.float64], pixels: NDArray[np.float64]) -> NDArray[np.float64]:
    """Map pixels through h. Returns x, y and the homogeneous scale w."""
    ones = np.ones((len(pixels), 1))
    out: NDArray[np.float64] = np.hstack([pixels, ones]) @ h.T
    return out


@dataclass(frozen=True)
class FitReport:
    """How well a calibration's points agree, in metres on the ground.

    fit_m: how far each point lands from its map position under the fitted
    mapping. With exactly four points the fit passes through all of them,
    so it is always zero and says nothing; more points make it meaningful.

    recheck: from six points, the one most likely to be misplaced, and
    others_max_m, how well the rest agree without it. Each point is set
    aside in turn; the misplaced one is the one whose absence lets the rest
    agree. (Simply asking which point a fit without it predicts worst
    blames the corners instead, because predicting a corner means
    extrapolating: tests/test_ground.py has the case.) When fit_max_m is
    small, every point is fine and recheck is just the least good.
    """

    fit_m: dict[str, float]
    recheck: str | None
    others_max_m: float | None

    @property
    def fit_max_m(self) -> float:
        return max(self.fit_m.values())


class Ground:
    """A fitted calibration: turns pixels of the upright frame into metres."""

    def __init__(self, calibration: Calibration) -> None:
        self.calibration = calibration
        origin_lat, origin_lon = calibration.origin
        names = [p.name for p in calibration.points]
        pixels = np.array([p.pixel for p in calibration.points], dtype=np.float64)
        ground = np.array(
            [local_metres(p.lat, p.lon, origin_lat, origin_lon) for p in calibration.points],
            dtype=np.float64,
        )
        # The typo check comes first: one point kilometres off also squashes
        # the others into what looks like a line.
        if float(np.max(np.linalg.norm(ground, axis=1))) > MAX_SPREAD_M / 2:
            raise CalibrationError(
                "the points are kilometres apart; check each latitude and longitude for a typo"
            )
        if not (_fixes_a_perspective(pixels) and _fixes_a_perspective(ground)):
            raise CalibrationError(
                "the points lie nearly on one line; pick some across the road as well as along it"
            )
        self._h = _fit(pixels, ground)
        # Which side of the horizon the road is on: a pixel whose scale has
        # the other sign is sky, and would land behind the camera.
        self._road_sign = float(np.sign(np.median(_apply(self._h, pixels)[:, 2])))

        fitted = self._project(pixels)
        fit_m = dict(zip(names, np.linalg.norm(fitted - ground, axis=1).tolist(), strict=True))
        recheck: str | None = None
        others_max_m: float | None = None
        if len(names) >= RECHECK_MIN_POINTS:
            without: dict[str, float] = {}
            for i, name in enumerate(names):
                others = np.arange(len(names)) != i
                # Setting aside the one point off a line can leave the rest
                # unable to fix a perspective; then this one isn't the
                # suspect, since the rest can't vouch for themselves.
                if not (
                    _fixes_a_perspective(pixels[others]) and _fixes_a_perspective(ground[others])
                ):
                    continue
                at = _apply(_fit(pixels[others], ground[others]), pixels[others])
                errors = np.linalg.norm(at[:, :2] / at[:, 2:3] - ground[others], axis=1)
                without[name] = float(errors.max())
            if without:
                recheck = min(without, key=lambda name: without[name])
                others_max_m = without[recheck]
        self.report = FitReport(fit_m=fit_m, recheck=recheck, others_max_m=others_max_m)

    @classmethod
    def from_file(cls, path: Path) -> Ground:
        return cls(load_calibration(path))

    def check_frame(self, width: int, height: int) -> None:
        """Pixels only mean anything at the size they were picked at."""
        if (width, height) != (self.calibration.image_width, self.calibration.image_height):
            raise CalibrationError(
                f"the calibration is for a {self.calibration.image_width}×"
                f"{self.calibration.image_height} picture, and this video is {width}×{height}"
            )

    def _project(self, pixels: NDArray[np.float64]) -> NDArray[np.float64]:
        mapped = _apply(self._h, pixels)
        w = mapped[:, 2:3]
        out: NDArray[np.float64] = np.where(
            w * self._road_sign > 1e-12, mapped[:, :2] / np.where(w == 0, 1.0, w), np.nan
        )
        return out

    def to_ground(self, pixels: NDArray[np.float64]) -> NDArray[np.float64]:
        """Each (x, y) pixel as (east, north) metres. A pixel at or above
        the horizon has no place on the road and comes back as NaN."""
        pixels = np.asarray(pixels, dtype=np.float64).reshape(-1, 2)
        return self._project(pixels)

    def track_point(self, detection: Detection) -> TrackPoint | None:
        """Where a detection touches the road, or None if that's off the
        road (above the horizon)."""
        east, north = self.to_ground(np.array([detection.ground_contact]))[0]
        if not (math.isfinite(east) and math.isfinite(north)):
            return None
        return TrackPoint(time_s=detection.time_s, x_m=float(east), y_m=float(north))


_TOP_KEYS = {"image_size", "points"}
_POINT_KEYS = {"name", "pixel", "lat", "lon"}


def _number(value: Any, what: str) -> float:
    # bool is an int in Python; "yes" in YAML must not become 1.0.
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise CalibrationError(f"{what} must be a number")
    return float(value)


def _pair(value: Any, what: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise CalibrationError(f"{what} must be two numbers, like [812, 455]")
    return _number(value[0], what), _number(value[1], what)


def parse_calibration(data: Any) -> Calibration:
    """A calibration from the parsed YAML, checked field by field
    (CLAUDE.md 17): unknown keys are refused, so a misspelt one can't be
    silently ignored."""
    if not isinstance(data, dict) or set(data) != _TOP_KEYS:
        raise CalibrationError("a calibration has exactly two keys: image_size and points")
    width, height = _pair(data["image_size"], "image_size")
    if not (width.is_integer() and height.is_integer()):
        raise CalibrationError("image_size must be whole pixels")
    if not isinstance(data["points"], list):
        raise CalibrationError("points must be a list")
    points = []
    for i, raw in enumerate(data["points"], start=1):
        if not isinstance(raw, dict) or set(raw) != _POINT_KEYS:
            raise CalibrationError(f"point {i} needs exactly: name, pixel, lat and lon")
        if not isinstance(raw["name"], str) or not raw["name"].strip():
            raise CalibrationError(f"point {i} needs a name")
        points.append(
            SurveyPoint(
                name=raw["name"].strip(),
                pixel=_pair(raw["pixel"], f"point {i}'s pixel"),
                lat=_number(raw["lat"], f"point {i}'s lat"),
                lon=_number(raw["lon"], f"point {i}'s lon"),
            )
        )
    return Calibration(image_width=int(width), image_height=int(height), points=tuple(points))


def load_calibration(path: Path) -> Calibration:
    """Read calibration.yaml. Missing means uncalibrated, and that's an
    error: no speeds or near-misses rather than wrong ones."""
    if not path.is_file():
        raise CalibrationError(
            f"there's no calibration at {path}: speeds and near-misses need one "
            "(calibration.example.yaml shows the shape)"
        )
    try:
        # safe_load: a YAML tag can't make Python build objects.
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        raise CalibrationError(f"{path.name} isn't valid YAML: {err}") from err
    return parse_calibration(data)
