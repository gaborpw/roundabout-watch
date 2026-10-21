# 11. The desktop runs it, at home; the Mac is for testing

- **Status:** accepted (Peter's choice, 2026-10-17)
- **Date:** 2026-10-17. Supersedes ADR 0003.

## Context

ADR 0003 put the analysis on a Jetson Orin Nano Super beside the camera.
With its drive, that was $687 of the $798 parts list, and the Jetson was
back-ordered. Peter already has two computers that can do the work. He said,
on 2026-10-17:

> i dont need this lol can i use a raspberry pi or have my mac or desktop
> running it?

> I have a m4 air and a 3080 ti desktop.

> i want to track all crashes and near misses, and record that data and
> visuaize it a lot. i can have that all local this is just for fun

> desktop is near a window yes and i have oing ethernet cords, it can use
> both wifi and ethernet

- **The M4 MacBook Air** runs RF-DETR on Apple's GPU (MPS), but it has no
  fan (general knowledge), so it slows down under hours of load. Fine for
  testing, wrong for running all day.
- **The desktop's RTX 3080 Ti** is an NVIDIA card, which is what PyTorch and
  RF-DETR are built around. It's already paid for, and it sits near a window.
- **Online** would have meant copying flagged events and clips to cloud
  storage, with a small website to see them away from home. Peter chose to
  keep everything at home.

## Decision

- **The Windows desktop runs everything, all day:**
  - go2rtc, the recorder and its sweeper;
  - `roundabout-watch`;
  - the database;
  - the review and chart pages.

  RF-DETR runs on the GPU through PyTorch with CUDA. TensorRT is an option
  only if that turns out too slow (not measured). PyPI's PyTorch for
  Windows has no CUDA, so on Windows only, torch and torchvision come
  from PyTorch's own CUDA 13.0 index, `download.pytorch.org/whl/cu130`
  (added 2026-10-21; `pyproject.toml`). Every other package stays on
  PyPI, and the Mac's packages are unchanged.
- **The M4 MacBook Air is for building and testing.** `replay` runs the
  whole pipeline on a recorded video, with RF-DETR on Apple's GPU. It never
  runs the camera all day.
- **Everything stays at home.** No cloud storage, no website, no accounts.
  The desktop serves the pages to the home network only, so Peter opens them
  on the desktop, or on a phone on the home Wi-Fi. Nothing is forwarded
  through the router.
- **The camera plugs straight into the desktop's Ethernet port** through the
  PoE adapter. The desktop reaches the internet over Wi-Fi.
  - The camera and the desktop's Ethernet port both get fixed addresses with
    no gateway.
  - Windows' Internet Connection Sharing stays off.
  - So nothing routes the camera to the internet (CLAUDE.md 22).

  This rests on general knowledge of how Windows routes. It's checked at
  setup, by confirming the camera can't reach anything outside.
- **How it starts by itself** after a restart or a Windows update (a
  Windows service, Task Scheduler or WSL2) is decided at build step 6, when
  the live pipeline first exists.
- **Python 3.12 or newer.** The 3.10 floor was only for the Jetson's
  JetPack 6 fallback (ADR 0003), and PyAV 19.0.1 needs 3.12.
  `pyproject.toml` and CI move to it in the first pull request that adds
  PyAV or RF-DETR.

## Consequences

- **The parts list drops from $797.98 to $92.99:** the camera and its PoE
  adapter, plus $18.00 of cables if Peter's own are too short. The Jetson
  and its SSD go, and so does the UPS, which was sized for the Jetson
  (`docs/parts.md`).
- **Power:** leaving the desktop on costs roughly $15–30 a month. That is an
  estimate:
  - an average draw of 100–200 W, which isn't measured;
  - at Ohio's average home price of 19.45¢/kWh in July 2026 (EIA).
- **Storage:** the desktop has two 12 TB hard drives (Peter, 2026-10-17).
  A day of recording (ADR 0006) is roughly 45–65 GB, by estimate, so there's
  plenty of room.
- **Results can only be seen at home.** Seeing them from elsewhere would be
  a new decision, with its own ADR.
- **Trade-off:** the desktop is busy all day. A game shares the GPU with the
  detector, and a restart for a Windows update stops recording until the
  pipeline starts again. In exchange, there's nothing to buy beyond the
  camera, and the GPU is far bigger than the Jetson's.
- The desktop's own internet is on Wi-Fi while its Ethernet port serves the
  camera. If it ever needs a cable to the router too, a USB Ethernet adapter
  adds a second port.
- The Mac can't reach the camera, which is cabled to the desktop. Testing on
  the Mac uses recorded video, which is how `replay` already works.

## Sources (read 2026-10-17)

- PyAV 19.0.1 requires Python 3.12: https://pypi.org/project/av/
- PyTorch's index setup for uv, read 2026-10-21:
  https://docs.astral.sh/uv/guides/integration/pytorch/ ; the CUDA 13.0
  Windows build of torch 2.14.1 for Python 3.12:
  https://download.pytorch.org/whl/cu130/torch/
- RF-DETR uses CUDA or Apple's MPS when PyTorch finds one, else the CPU:
  `rfdetr/config.py` in the rfdetr 1.11.2 package from
  https://pypi.org/project/rfdetr/
- Ohio's average residential electricity price, July 2026: EIA, Electric
  Power Monthly, table 5.6.A,
  https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a
- The camera's power and ports: ADR 0005.
