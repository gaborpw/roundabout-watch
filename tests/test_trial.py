"""The work behind the "Try a video" page."""

from pathlib import Path

import pytest
from conftest import write_squares_video

from roundabout_watch.model import Detection, Frame, RoadUser, TrackSpan
from roundabout_watch.trial import Result, run, saved_upload, timeline, video_suffix


@pytest.mark.parametrize(("name", "suffix"), [("IMG_0843.MOV", ".mov"), ("clip.mp4", ".mp4")])
def test_video_suffix(name: str, suffix: str) -> None:
    assert video_suffix(name) == suffix


@pytest.mark.parametrize("name", ["notes.txt", "video", "evil.mov.sh", "../../etc/passwd"])
def test_anything_but_a_video_is_refused(name: str) -> None:
    with pytest.raises(ValueError):
        video_suffix(name)


def test_an_upload_is_deleted_afterwards() -> None:
    # The browser's file name is never used as a path: only its extension.
    with saved_upload(b"not really a video", "../../IMG_0001.MOV") as path:
        assert path.name == "upload.mov"
        assert path.read_bytes() == b"not really a video"
        folder = path.parent
    assert not folder.exists()


class _Nothing:
    def detect(self, frame: Frame) -> list[Detection]:
        return []


def test_run_keeps_only_the_drawn_copy(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=4)
    seen: list[tuple[int, int | None]] = []
    result = run(video, "squares.mp4", _Nothing(), lambda done, total: seen.append((done, total)))
    assert isinstance(result, Result)
    assert result.summary.frames == 4
    # An MP4 starts with an "ftyp" box four bytes in.
    assert result.video[4:8] == b"ftyp"
    assert [done for done, _ in seen] == [1, 2, 3, 4]


def test_timeline_rows() -> None:
    span = TrackSpan(track_id=7, kind=RoadUser.CAR, first_s=1.25, last_s=4.0, frames=60)
    assert timeline((span,)) == [
        {
            "road user": "car 7",
            "kind": "car",
            "arrived": 1.2,
            "left": 4.0,
            "in view": 2.8,
        }
    ]
