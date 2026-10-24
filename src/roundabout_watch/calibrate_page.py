"""The "Calibrate" page (ADR 0012): pair spots in a video with their map
positions, and save calibration.yaml for ground.py.

Pick a frame, click a spot on the road, paste its latitude and longitude
from a map, and repeat. From four spots it shows how well they agree; from
six it can say which one to re-check. The work is in calibrate.py and
ground.py; this file only lays it out.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import av
import numpy as np
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from roundabout_watch import calibrate, trial
from roundabout_watch.ground import (
    MIN_POINTS,
    RECHECK_MIN_POINTS,
    Calibration,
    CalibrationError,
    Ground,
    SurveyPoint,
    load_calibration,
)

log = logging.getLogger("roundabout_watch")

state = st.session_state
state.setdefault("cal_spots", [])

st.title("Calibrate")
st.caption(
    "Teaches the software where things are on the road, so it can measure in "
    "metres. Click a spot that's on the road surface and easy to find on a "
    "map (a curb corner, a crosswalk corner, a manhole, a lamp post's base), "
    "then paste its latitude and longitude. Spread the spots across the "
    "picture. Six or more lets it check itself. Everything stays on this "
    "computer."
)

source = st.radio(
    "Video", ["Upload a file", "A file on this computer"], horizontal=True, key="cal_source"
)
upload = None
path_text = ""
if source == "Upload a file":
    upload = st.file_uploader(
        "Drop a video here",
        type=[s.lstrip(".") for s in trial.VIDEO_SUFFIXES],
        key="cal_upload",
    )
else:
    path_text = st.text_input(
        "Path to the video", placeholder="~/Downloads/IMG_0843.MOV", key="cal_path"
    ).strip()
seconds = st.number_input(
    "Seconds into the video",
    min_value=0.0,
    value=0.0,
    step=1.0,
    help="Pick a moment with no cars hiding the spots you want.",
    key="cal_seconds",
)

if st.button("Show this frame", disabled=upload is None and not path_text, key="cal_show"):
    try:
        if upload is not None:
            with trial.saved_upload(upload.getbuffer(), upload.name) as video:
                frame = calibrate.frame_at(video, seconds)
        else:
            video = Path(path_text).expanduser()
            if not video.is_file():
                raise ValueError(f"there's no file at {video}")
            trial.video_suffix(video.name)
            frame = calibrate.frame_at(video, seconds)
    except (av.FFmpegError, ValueError, OSError) as err:
        log.error("showing a frame failed: %s", type(err).__name__)
        st.error(f"Couldn't use that video: {err}.")
    else:
        state["cal_frame"] = frame.image
        state.pop("cal_pending", None)

if calibrate.CALIBRATION_FILE.is_file() and st.button(
    "Load the saved calibration's spots", key="cal_load"
):
    try:
        saved = load_calibration(calibrate.CALIBRATION_FILE)
    except CalibrationError as err:
        st.error(f"Couldn't read {calibrate.CALIBRATION_FILE}: {err}.")
    else:
        state["cal_spots"] = list(saved.points)
        state["cal_loaded_size"] = (saved.image_width, saved.image_height)
        st.info(
            f"Loaded {len(saved.points)} spots, picked on a "
            f"{saved.image_width}×{saved.image_height} picture."
        )


def _add_spot() -> None:
    # A callback, so the inputs can be emptied before they're drawn again.
    pending = state.get("cal_pending")
    name = str(state.get("cal_name", "")).strip()
    if pending is None:
        return
    try:
        if not name:
            raise CalibrationError("give the spot a name, like 'NE curb corner'")
        if any(spot.name == name for spot in state["cal_spots"]):
            raise CalibrationError(f"there's already a spot called {name!r}")
        lat, lon = calibrate.parse_lat_lon(str(state.get("cal_latlon", "")))
    except CalibrationError as err:
        state["cal_add_error"] = str(err)
        return
    state["cal_spots"] = [
        *state["cal_spots"],
        SurveyPoint(name=name, pixel=pending, lat=lat, lon=lon),
    ]
    state["cal_name"] = ""
    state["cal_latlon"] = ""
    state.pop("cal_pending", None)
    state.pop("cal_add_error", None)


image = state.get("cal_frame")
if isinstance(image, np.ndarray):
    height, width = image.shape[:2]
    spots: list[SurveyPoint] = state["cal_spots"]
    loaded_size = state.get("cal_loaded_size")
    if loaded_size is not None and loaded_size != (width, height):
        # Their pixels belong to the other size. Saving them with this
        # frame's size would give metres that are quietly wrong, so nothing
        # else is offered until they're gone (review of PR #19).
        st.warning(
            f"The loaded spots were picked on a {loaded_size[0]}×{loaded_size[1]} picture "
            f"and this frame is {width}×{height}, so they won't line up. Show a frame "
            "from the same camera view, or remove them and start again."
        )
        if st.button("Remove the loaded spots", key="cal_clear"):
            state["cal_spots"] = []
            state.pop("cal_loaded_size", None)
            state.pop("cal_pending", None)
            st.rerun()
        st.stop()
    left, right = st.columns([3, 2])
    with left:
        click = streamlit_image_coordinates(
            calibrate.mark_spots(image, spots, state.get("cal_pending")),
            width="stretch",
            image_format="JPEG",
            jpeg_quality=90,
            cursor="crosshair",
            key="cal_click",
        )
        st.caption(f"The frame is {width}×{height}. Click a spot to add it.")
    # The component keeps returning its last click on every rerun; only a
    # new one (a new time) is a new spot.
    if isinstance(click, dict) and click.get("unix_time") != state.get("cal_click_seen"):
        state["cal_click_seen"] = click.get("unix_time")
        try:
            state["cal_pending"] = calibrate.image_pixel(click, width, height)
        except ValueError as err:
            log.warning("ignored a click: %s", err)
        st.rerun()

    with right:
        pending = state.get("cal_pending")
        if pending is not None:
            st.subheader(f"New spot at {pending[0]:.0f}, {pending[1]:.0f}")
            st.text_input("Name", placeholder="NE curb corner", key="cal_name")
            st.text_input(
                "Latitude, longitude",
                placeholder="41.48163, -81.72891",
                help="In Google Maps, right-click the spot, then click the numbers "
                "at the top of the pop-up to copy them.",
                key="cal_latlon",
            )
            st.button("Add this spot", type="primary", on_click=_add_spot, key="cal_add")
            if "cal_add_error" in state:
                st.error(state["cal_add_error"])

        if spots:
            st.subheader("Spots")
            st.dataframe(
                [
                    {
                        "spot": f"{n}. {s.name}",
                        "pixel": f"{s.pixel[0]:.0f}, {s.pixel[1]:.0f}",
                        "lat, lon": f"{s.lat:.6f}, {s.lon:.6f}",
                    }
                    for n, s in enumerate(spots, start=1)
                ],
                hide_index=True,
            )
            gone = st.selectbox(
                "Remove a spot", [s.name for s in spots], index=None, key="cal_remove_which"
            )
            if st.button("Remove it", disabled=gone is None, key="cal_remove"):
                state["cal_spots"] = [s for s in spots if s.name != gone]
                if not state["cal_spots"]:
                    # Nothing loaded is left, so the next frame starts fresh.
                    state.pop("cal_loaded_size", None)
                st.rerun()

    if len(spots) < MIN_POINTS:
        st.info(f"Add at least {MIN_POINTS - len(spots)} more spots to see how well they agree.")
    else:
        try:
            calibration = Calibration(image_width=width, image_height=height, points=tuple(spots))
            report = Ground(calibration).report
        except CalibrationError as err:
            st.warning(f"These spots can't be used yet: {err}.")
        else:
            st.subheader("How well the spots agree")
            st.caption(
                "How far each spot lands from its map position once the picture is "
                "fitted to the map. Smaller is better; a spot far worse than the "
                "rest was probably clicked or pasted in the wrong place."
            )
            st.metric("Furthest off", f"{report.fit_max_m:.2f} m")
            st.dataframe(calibrate.report_rows(report), hide_index=True)
            if report.recheck is None:
                st.info(
                    f"With {len(spots)} spots it can't tell which one is off. "
                    f"Add {RECHECK_MIN_POINTS - len(spots)} more so it can check itself."
                )
            else:
                st.caption(
                    f"If one spot is off, it's most likely **{report.recheck}**: without "
                    f"it the others agree to within {report.others_max_m:.2f} m."
                )
            text = calibrate.calibration_yaml(calibration, date.today())
            if st.button("Save as calibration.yaml", type="primary", key="cal_save"):
                try:
                    calibrate.CALIBRATION_FILE.write_text(text, encoding="utf-8")
                except OSError as err:
                    log.error("saving the calibration failed: %s", type(err).__name__)
                    st.error(f"Couldn't save it: {err}.")
                else:
                    st.success(f"Saved to {calibrate.CALIBRATION_FILE.resolve()}.")
            st.download_button(
                "Download calibration.yaml",
                text,
                file_name="calibration.yaml",
                mime="text/yaml",
                key="cal_download",
            )
