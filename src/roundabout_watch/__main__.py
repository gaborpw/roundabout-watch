"""The command line: `python -m roundabout_watch replay VIDEO`.

`run` (the live camera) and `calibrate` arrive with their build steps
(docs/architecture.md).
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import av

from roundabout_watch.detect import MODEL_SIZES, RFDETRDetector
from roundabout_watch.replay import replay

log = logging.getLogger("roundabout_watch")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m roundabout_watch")
    commands = parser.add_subparsers(dest="command", required=True)
    replay_cmd = commands.add_parser(
        "replay",
        help="track road users in a recorded video and write a copy with them drawn on",
    )
    replay_cmd.add_argument("video", type=Path, help="the video to read, such as a phone video")
    replay_cmd.add_argument(
        "--out",
        type=Path,
        help="where to write the copy (default: next to the video, ending .tracked.mp4)",
    )
    replay_cmd.add_argument(
        "--model",
        choices=MODEL_SIZES,
        default="small",
        help="RF-DETR size: bigger finds more, slower (default: small)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    video: Path = args.video
    if not video.is_file():
        parser.error(f"there's no video at {video}")
    out: Path = args.out or video.with_name(f"{video.stem}.tracked.mp4")
    if out.resolve() == video.resolve():
        parser.error("--out would overwrite the video")

    try:
        detector = RFDETRDetector(size=args.model)
    except RuntimeError as err:
        print(err, file=sys.stderr)
        return 1
    try:
        summary = replay(video, out, detector)
    except (av.FFmpegError, ValueError) as err:
        # The detail goes to the log; the sentence is for the person.
        log.error("replay of %s failed: %s", video.name, err)
        print(f"Couldn't read {video.name} as a video. The log above says why.", file=sys.stderr)
        return 1

    print(f"Done: {summary.frames} frames, {summary.video_seconds:.0f} s of video")
    print(f"in {summary.wall_seconds:.0f} s. Wrote {out}")
    for kind, count in sorted(summary.tracks.items(), key=lambda item: -item[1]):
        print(f"  {kind.value}: {count}")
    if detector.dropped:
        log.warning("%d detector boxes were unusable and skipped", detector.dropped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
