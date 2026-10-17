# 7. go2rtc in front of the camera, PyAV to read, clips without re-encoding

- **Status:** accepted (Peter's yes, 2026-10-17)
- **Date:** 2026-10-17

## Context

Three things want the camera's stream at once: the analyser, the recorder,
and a person checking the live view. Many cameras allow only a few RTSP
connections and behave badly when that limit is reached.

Clips must start a few seconds **before** an event, which is only known
after it happens. Re-encoding video to cut a clip would cost time and
quality the analyser doesn't need to spend. (This ADR was written for a
Jetson Orin Nano, which has no hardware encoder at all; ADR 0011 replaced it
with Peter's desktop.)

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
- **Not now:** hardware video decoding. One 4 MP stream is decoded on the
  desktop's CPU; the GPU's decoder is the next step only if that's too
  slow.
- **Not now:** NVIDIA DeepStream. Its Python bindings are deprecated from
  9.0 ("no more wheel files"), and its licence is NVIDIA's own EULA.

## Consequences

- One stream from the camera, however many readers.
- Clips cost almost no CPU, and keep the camera's original quality.
- **Trade-off:** software decoding uses CPU time; it gets measured on the
  desktop (build step 6) before we trust it.
- PyAV's wheels bundle FFmpeg's encoders, including libx264 and libx265,
  which are GPL (general knowledge from the aarch64 wheel; not checked
  against the libraries' own pages). It matters only if the program is ever
  given to someone else.

## Sources (read 2026-10-17)

- go2rtc: https://github.com/AlexxIT/go2rtc
- DeepStream Python bindings: https://github.com/NVIDIA-AI-IOT/deepstream_python_apps
- PyAV wheel contents: inspected the av 17.1.0 aarch64 wheel.
