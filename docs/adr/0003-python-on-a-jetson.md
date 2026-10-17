# 3. Python, on a Jetson next to the camera

- **Status:** proposed (waiting on Peter's yes, `docs/next.md`)
- **Date:** 2026-10-17

## Context

The work is video decoding, a neural-network detector, tracking and some
geometry, running all day on one camera's stream. Peter's other project is
Go and TypeScript, but every detector, tracker and safety-measure library
worth using here is Python (`docs/research/references.md`). The video should
not leave the property: uploading 24/7 footage costs bandwidth and puts
people's movements on someone else's server.

## Decision

- **Python**, typed and checked with `mypy --strict`, managed with uv.
- **On an NVIDIA Jetson Orin Nano Super** beside the camera, so footage
  stays local. TensorRT runs the detector at FP16.
- **JetPack 7.2.1** (Jetson Linux r39.2.1: Ubuntu 24.04, Python 3.12,
  CUDA 13.2, TensorRT 10.16), because NVIDIA's own quick-start guide for the
  developer kit now installs it: "the latest JetPack release for the
  developer kit". A kit with factory firmware older than 36.0 must go
  through the JetPack 6.x update first, as the guide says.
- **The code stays compatible with Python 3.10** (`requires-python =
  ">=3.10"`), so JetPack 6.2.x (Ubuntu 22.04, Python 3.10, CUDA 12.6,
  TensorRT 10.3) remains a fallback. CI tests both 3.10 and 3.12.
- PyTorch and ONNX Runtime on the Jetson come from NVIDIA's Jetson AI Lab
  package index, not PyPI. Its JetPack 6 index (`jp6/cu126`) has torch
  2.11.0 and onnxruntime-gpu 1.24.0 for Python 3.10. The JetPack 7 index
  isn't checked yet (`docs/research/verify.md`).

## Consequences

- Code can't use syntax newer than 3.10 while the fallback stands. Dropping
  the fallback is a one-line change plus this ADR.
- On the 3.10 fallback, some libraries are capped: numpy at 2.2.x, PyAV at
  17.1.x, ONNX Runtime at 1.24.x.
- **Trade-off:** a second language beside Peter's Go and TypeScript, in
  exchange for using the libraries that already solve detection and
  tracking.
- The alternative, an x86 PC with an RTX card, is faster and simpler to
  install packages on, but bigger, louder and uses far more power for a box
  that runs all day (`docs/parts.md`).

## Sources (read 2026-10-17)

- NVIDIA, Jetson Orin Nano Developer Kit quick start (installs JetPack
  7.2.1; firmware older than 36.0 needs the 6.x path):
  https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/quick_start.html
- JetPack 7.2.1: https://developer.nvidia.com/embedded/jetpack/downloads/archive-7.2.1
- JetPack 6.2.3: https://developer.nvidia.com/embedded/jetpack-sdk-623
- Ubuntu 22.04's Python: https://packages.ubuntu.com/jammy/python3
- Jetson AI Lab JetPack 6 index contents: checked by listing
  https://pypi.jetson-ai-lab.io/jp6/cu126
