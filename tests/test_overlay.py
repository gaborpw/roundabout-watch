"""Drawing the tracks, and writing the result as a video."""

from pathlib import Path

import numpy as np
import pytest

from roundabout_watch.ingest import VideoFile
from roundabout_watch.model import Detection, Frame, RoadUser, TrackedDetection
from roundabout_watch.overlay import Overlay, VideoWriter


def _frame(rgb: tuple[int, int, int] = (0, 0, 0)) -> Frame:
    image = np.zeros((96, 160, 3), dtype=np.uint8)
    image[:, :] = rgb
    return Frame(index=0, time_s=0.0, image=image)


def test_nothing_tracked_gives_the_frame_back_in_bgr() -> None:
    # Pure red in RGB is (0, 0, 255) in BGR.
    drawn = Overlay(frame_rate=25).draw(_frame((255, 0, 0)), [])
    assert drawn.shape == (96, 160, 3)
    assert tuple(drawn[50, 50]) == (0, 0, 255)


def test_a_tracked_road_user_is_drawn() -> None:
    frame = _frame()
    car = Detection(frame=0, time_s=0.0, kind=RoadUser.CAR, confidence=0.9, box=(40, 30, 90, 70))
    drawn = Overlay(frame_rate=25).draw(frame, [TrackedDetection(track_id=3, detection=car)])
    # The box's edge is drawn; the far corner of the frame is untouched.
    assert drawn[30:71, 40].any()
    assert not drawn[90:, 150:].any()
    # The frame itself is left as it was.
    assert not frame.image.any()


def test_written_video_reads_back(tmp_path: Path) -> None:
    out = tmp_path / "out.mp4"
    # An odd size loses its last row and column: H.264's yuv420p needs even.
    with VideoWriter(out, width=161, height=97, fps=25) as writer:
        for _ in range(5):
            writer.write(np.full((97, 161, 3), 128, dtype=np.uint8))
    with VideoFile(out) as source:
        assert (source.info.width, source.info.height) == (160, 96)
        assert len(list(source.frames())) == 5


def test_a_video_too_small_to_write_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        VideoWriter(tmp_path / "out.mp4", width=1, height=1, fps=25)
