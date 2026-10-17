"""The command line refuses mistakes before any work starts."""

import importlib.util
from pathlib import Path

import pytest
from conftest import write_squares_video

import roundabout_watch.__main__ as cli
from roundabout_watch.model import Detection, Frame


class _NoDetector:
    """Stands in for RF-DETR, which CI doesn't install."""

    def __init__(self, size: str = "small") -> None:
        self.dropped = 0

    def detect(self, frame: Frame) -> list[Detection]:
        return []


def test_a_missing_video_is_a_usage_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as stopped:
        cli.main(["replay", str(tmp_path / "nowhere.mp4")])
    assert stopped.value.code == 2


def test_the_copy_may_not_overwrite_the_video(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=2)
    with pytest.raises(SystemExit) as stopped:
        cli.main(["replay", str(video), "--out", str(video)])
    assert stopped.value.code == 2


def test_only_apache_model_sizes_are_offered(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=2)
    with pytest.raises(SystemExit) as stopped:
        cli.main(["replay", str(video), "--model", "xlarge"])
    assert stopped.value.code == 2


def test_a_file_that_isnt_video_fails_with_a_sentence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "RFDETRDetector", _NoDetector)
    not_video = tmp_path / "notes.mp4"
    not_video.write_text("not a video")
    assert cli.main(["replay", str(not_video)]) == 1
    assert "Couldn't read notes.mp4 as a video" in capsys.readouterr().err


def test_a_replay_writes_next_to_the_video(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "RFDETRDetector", _NoDetector)
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=3)
    assert cli.main(["replay", str(video)]) == 0
    assert (tmp_path / "squares.tracked.mp4").is_file()
    assert "Done: 3 frames" in capsys.readouterr().out


@pytest.mark.skipif(
    importlib.util.find_spec("rfdetr") is not None,
    reason="RF-DETR is installed here; loading it would download its weights",
)
def test_without_the_detector_it_says_how_to_install_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=2)
    assert cli.main(["replay", str(video)]) == 1
    assert "uv sync --extra detector" in capsys.readouterr().err
