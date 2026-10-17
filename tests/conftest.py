"""Small videos made on the spot for the tests.

Every video here is drawn by the test itself, white and grey squares sliding
across black, so no fixture shows a person or a real road (CLAUDE.md 37).
They are written with PyAV directly, not with our own VideoWriter, so the
reader's tests don't lean on the writer they help test.
"""

from fractions import Fraction
from pathlib import Path

import av
import numpy as np

WIDTH, HEIGHT, FPS = 160, 96, 25
SQUARE = 16

Box = tuple[float, float, float, float]


def square_boxes(frames: int) -> list[tuple[Box, Box]]:
    """Where the two squares are in each frame: one starts at the top left
    and moves 4 px right a frame; the other starts at the bottom right and
    moves 4 px left. They never overlap, so a tracker has no excuse to
    swap them."""
    boxes = []
    for i in range(frames):
        a_left = 8.0 + 4 * i
        b_left = float(WIDTH - 8 - SQUARE) - 4 * i
        boxes.append(
            (
                (a_left, 8.0, a_left + SQUARE, 8.0 + SQUARE),
                (b_left, float(HEIGHT - 8 - SQUARE), b_left + SQUARE, float(HEIGHT - 8)),
            )
        )
    return boxes


def write_squares_video(path: Path, frames: int = 10) -> list[tuple[Box, Box]]:
    """Writes the squares as an H.264 MP4 and returns their boxes."""
    boxes = square_boxes(frames)
    with av.open(str(path), mode="w") as container:
        stream = container.add_stream("h264", rate=Fraction(FPS))
        stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
        for a, b in boxes:
            image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            for (left, top, right, bottom), shade in ((a, 255), (b, 160)):
                image[int(top) : int(bottom), int(left) : int(right)] = shade
            for packet in stream.encode(av.VideoFrame.from_ndarray(image, format="rgb24")):
                container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
    return boxes
