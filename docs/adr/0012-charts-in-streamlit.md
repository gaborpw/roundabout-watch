# 12. Review and charts in Streamlit, on the home network

- **Status:** accepted (Peter's yes, 2026-10-17)
- **Date:** 2026-10-17

## Context

Peter wants every crash and near-miss recorded and charted, at home:

> i want to track all crashes and near misses, and record that data and
> visuaize it a lot. i can have that all local this is just for fun

Peter then said yes to the pages and the tool below ("3. yes", 2026-10-17).
The review page needs a clip player and confirm and dismiss buttons
(ADR 0002). The charts read the SQLite database (ADR 0008) on the desktop
(ADR 0011).

The options, read on 2026-10-17:

- **Streamlit** 1.66.0, Apache-2.0: pages written in Python, with charts,
  video and buttons built in. Needs Python 3.11 or newer.
- **Grafana**: a separate dashboard server, under AGPL-3.0, the kind of
  licence CLAUDE.md 25 steers away from.
- **A hand-built web page**: no dependency, but every chart is code we write
  and keep up.

## Decision

- **One Streamlit app on the desktop**, with these pages:
  1. **Review:** each flagged event's clip and the measures that raised it.
     Confirm or dismiss, with a reason (ADR 0002).
  2. **Map:** where on the roundabout conflicts happen, coloured by conflict
     type. It is drawn on a still from the camera or a plan in metres, not
     on web map tiles, so the page fetches nothing from outside.
  3. **When:** by hour of the day and day of the week.
  4. **How close:** time to collision and post-encroachment time, with
     SSAM's severity bands.
  5. **Who:** car with car, car with bike, car with pedestrian, and so on.
  6. **Traffic:** road users per hour, speeds through the circle, the usual
     paths, and weekly trends, all from the kept paths (ADR 0006).
  7. **Try a video** (added 2026-10-21, Peter: "how will i be able to upload
     higher and longer videos? can i make some UI for it here, and can i
     make it have statistics"): drop in a video or name one on the
     computer, and get it back drawn on, with counts by kind, arrivals over
     time, time in view and a timeline. A tried video is processed in a
     temporary folder and deleted; nothing from it is stored (ADR 0006).
     It's the first page built, because it needs no camera.
  8. **Calibrate** (added 2026-10-24, Peter: "go ahead with step 2"):
     pick a frame of a video, click spots on the road, paste each one's
     latitude and longitude from a map, see how well they agree, and save
     `calibration.yaml` for `ground.py`. Streamlit can't say where on a
     picture someone clicked, so this page uses
     streamlit-image-coordinates (MIT, pinned; `docs/architecture.md`).
- **Every count of events says whether it is flagged or confirmed**
  (ADR 0002).
- **Usage statistics off.** Streamlit sends them by default; the repo's
  `.streamlit/config.toml` sets `browser.gatherUsageStats = false`.
- **Home network only.** It's served on the desktop's home-network address
  and never forwarded through the router (ADR 0011). Until it runs on the
  desktop, `.streamlit/config.toml` keeps it to the computer it runs on
  (`server.address = "localhost"`), so a laptop on someone else's Wi-Fi
  isn't reachable.
- **No Deploy button.** Streamlit's toolbar offers to publish an app to its
  cloud; `client.toolbarMode = "minimal"` hides it.
- The pages read the database and the clips. They never change the safety
  maths or the thresholds (`config.yaml`).

## Consequences

- Each page is a short Python file. The queries and numbers behind it live
  in plain functions, so they're tested without a browser (CLAUDE.md 36).
- **Trade-off:** Streamlit is a large dependency. It brings pandas, pyarrow,
  altair, starlette, uvicorn and more (PyPI, 2026-10-17), and it reruns a
  page's script on every click. For one person on one desktop, that's fine,
  in exchange for charts and video with almost no code of our own.
- **No sign-in:** anyone on the home Wi-Fi can open the pages, and confirm
  or dismiss. A password is a later decision, if that matters.
- The pages come once there's data to show, from `replay` or from the live
  camera (build step 7, `docs/architecture.md`).

## Sources (read 2026-10-17)

- Streamlit 1.66.0's licence, Python floor and dependencies:
  https://pypi.org/project/streamlit/
- Usage statistics on by default: `streamlit/config.py` in the streamlit
  1.66.0 package (`browser.gatherUsageStats`, `default_val=True`).
- Grafana's licence: https://github.com/grafana/grafana/blob/main/LICENSE
