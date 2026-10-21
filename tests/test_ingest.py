"""Reading video files into frames."""

from pathlib import Path

import av
import numpy as np
import pytest
from conftest import FPS, HEIGHT, WIDTH, write_squares_video

from roundabout_watch.ingest import VideoFile, quarter_turns


def test_reads_every_frame_in_order(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    write_squares_video(video, frames=10)
    with VideoFile(video) as source:
        frames = list(source.frames())
    assert [f.index for f in frames] == list(range(10))
    # Written at 25 fps, so frame i is at i / 25 seconds.
    assert [f.time_s for f in frames] == pytest.approx([i / FPS for i in range(10)])


def test_frames_are_rgb_at_the_video_size(tmp_path: Path) -> None:
    video = tmp_path / "squares.mp4"
    boxes = write_squares_video(video, frames=3)
    with VideoFile(video) as source:
        assert (source.info.width, source.info.height) == (WIDTH, HEIGHT)
        assert source.info.fps == pytest.approx(FPS)
        frame = next(source.frames())
    assert frame.image.shape == (HEIGHT, WIDTH, 3)
    assert frame.image.dtype == np.uint8
    # H.264 is lossy, so compare loosely: the white square is bright and
    # the corner it isn't in stays dark.
    left, top, right, bottom = (int(v) for v in boxes[0][0])
    assert frame.image[top + 4 : bottom - 4, left + 4 : right - 4].mean() > 200
    assert frame.image[HEIGHT - 4 :, :4].mean() < 30


def test_a_phone_video_filmed_upright_is_turned_upright(tmp_path: Path) -> None:
    # Stored 160 wide and 96 tall, with an iPhone's "turn 90° clockwise"
    # note (-90). Upright it is 96 wide and 160 tall, and the white square
    # stored at the top left (rows and columns 8 to 24) is at the top right:
    # turning clockwise sends stored row r to column 95 - r, so columns 71
    # to 87, and stored column c to row c, so rows 8 to 24.
    video = tmp_path / "upright.mov"
    write_squares_video(video, frames=2, rotation=-90)
    with VideoFile(video) as source:
        assert (source.info.width, source.info.height) == (HEIGHT, WIDTH)
        frame = next(source.frames())
    assert frame.image.shape == (WIDTH, HEIGHT, 3)
    assert frame.image[12:20, 75:83].mean() > 200
    # Where the square was before turning is now dark.
    assert frame.image[12:20, 12:20].mean() < 30


@pytest.mark.parametrize(
    ("degrees", "quarters"), [(0, 0), (-90, -1), (90, 1), (180, 2), (-180, 2)]
)
def test_quarter_turns(degrees: int, quarters: int) -> None:
    assert quarter_turns(degrees) % 4 == quarters % 4


def test_a_tilted_video_is_refused() -> None:
    # Only quarter turns are a phone's; anything else would need resampling.
    with pytest.raises(ValueError):
        quarter_turns(45)


def test_a_file_that_isnt_video_is_refused(tmp_path: Path) -> None:
    not_video = tmp_path / "notes.mp4"
    not_video.write_text("not a video")
    with pytest.raises(av.FFmpegError):
        VideoFile(not_video)
