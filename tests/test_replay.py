"""replay end to end, with a stand-in for RF-DETR that reports exactly
where the test video's squares are."""

from pathlib import Path

from conftest import square_boxes, write_squares_video

from roundabout_watch.ingest import VideoFile
from roundabout_watch.model import Detection, Frame, RoadUser
from roundabout_watch.replay import replay


class _SquareDetector:
    """Calls the top square a car (a truck in one frame, as a real detector
    sometimes would) and the bottom one a bicycle."""

    def __init__(self, frames: int) -> None:
        self.boxes = square_boxes(frames)

    def detect(self, frame: Frame) -> list[Detection]:
        a, b = self.boxes[frame.index]
        a_kind = RoadUser.TRUCK if frame.index == 5 else RoadUser.CAR
        return [
            Detection(frame.index, frame.time_s, a_kind, 0.9, a),
            Detection(frame.index, frame.time_s, RoadUser.BICYCLE, 0.9, b),
        ]


def test_replay_tracks_and_writes_a_copy(tmp_path: Path) -> None:
    video, out = tmp_path / "squares.mp4", tmp_path / "squares.tracked.mp4"
    write_squares_video(video, frames=12)
    summary = replay(video, out, _SquareDetector(12), progress_every=5)
    assert summary.frames == 12
    # 12 frames at 25 fps: the last starts 11 / 25 s after the first.
    assert abs(summary.video_seconds - 11 / 25) < 1e-6
    # Two road users; the one called a truck once still counts as a car.
    assert summary.tracks == {RoadUser.CAR: 1, RoadUser.BICYCLE: 1}
    with VideoFile(out) as copy:
        assert len(list(copy.frames())) == 12
    # Both join the tracker on their second frame, 1/25 s in, and stay to
    # the last, 11/25 s in: 10/25 = 0.4 s in view, over 11 frames.
    car, bicycle = sorted(summary.spans, key=lambda s: s.kind.value)[::-1]
    assert (car.kind, bicycle.kind) == (RoadUser.CAR, RoadUser.BICYCLE)
    for span in summary.spans:
        assert abs(span.first_s - 1 / 25) < 1e-6
        assert abs(span.seconds - 10 / 25) < 1e-6
        assert span.frames == 11


def test_replay_reports_progress(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=3)
    seen: list[tuple[int, int | None]] = []
    replay(
        video,
        tmp_path / "out.mp4",
        _SquareDetector(3),
        on_progress=lambda d, t: seen.append((d, t)),
    )
    # The file says how many frames it holds, so the total is known.
    assert seen == [(1, 3), (2, 3), (3, 3)]


def test_an_empty_road(tmp_path: Path) -> None:
    class _Nothing:
        def detect(self, frame: Frame) -> list[Detection]:
            return []

    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=3)
    summary = replay(video, tmp_path / "out.mp4", _Nothing())
    assert summary.frames == 3
    assert summary.tracks == {}
