# 7. go2rtc in front of the camera, PyAV to read, clips without re-encoding

- **Status:** proposed (waiting on Peter's yes, `docs/next.md`)
- **Date:** 2026-10-17

## Context

Three things want the camera's stream at once: the analyser, the recorder,
and a person checking the live view. Many cameras allow only a few RTSP
connections and behave badly when that limit is reached.

Clips must start a few seconds **before** an event, which is only known
after it happens. And the Orin Nano has no hardware video encoder (NVIDIA's
multimedia guide lists its encoding as software only), so re-encoding video
there would take CPU time the analyser needs.

## Decision

- **go2rtc** (MIT) is the only thing that connects to the camera. Everything
  else reads go2rtc's copy of the stream.
- **PyAV** (BSD) reads the stream in Python. It keeps the last ~30 seconds of
  **compressed packets** in memory and decodes frames for the detector.
- **Clips are cut from those packets** and written as MP4 without
  re-encoding. They start at a keyframe, so set the camera's keyframe
  interval (I-frame interval or GOP) to 1 second.
- The recorder is ffmpeg copying the stream into 5-minute files, also
  without re-encoding.
- **Not now:** GStreamer hardware decoding (`nvv4l2decoder`). We switch to
  it only if the Orin Nano's CPU can't keep up with decoding. The PyPI build
  of OpenCV has no GStreamer, so that switch means building OpenCV or
  calling GStreamer directly.
- **Not now:** NVIDIA DeepStream. Its Python bindings are deprecated from
  9.0 ("no more wheel files"), and its licence is NVIDIA's own EULA.

## Consequences

- One stream from the camera, however many readers.
- Clips cost almost no CPU, and keep the camera's original quality.
- **Trade-off:** software decoding uses CPU time on a small board; it needs
  measuring on the Jetson (build step 6) before we trust it.
- PyAV's aarch64 wheel bundles libx264 and libx265, which are GPL. That is
  general knowledge, not checked against the libraries' own pages. Check
  before giving a device image to anyone.

## Sources (read 2026-10-17)

- go2rtc: https://github.com/AlexxIT/go2rtc
- Jetson multimedia guide: https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/SD/Multimedia/AcceleratedGstreamer.html
- DeepStream Python bindings: https://github.com/NVIDIA-AI-IOT/deepstream_python_apps
- PyAV wheel contents: inspected the av 17.1.0 aarch64 wheel.
