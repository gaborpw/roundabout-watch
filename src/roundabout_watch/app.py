"""The Roundabout Watch app: Streamlit, on this computer only (ADR 0012).

Run from the repository's root, so Streamlit finds .streamlit/config.toml:

    uv run streamlit run src/roundabout_watch/app.py

Today it has one page, "Try a video": drop in a video, and get it back with
every road user boxed, numbered and trailed, plus what was seen. The work is
in trial.py and stats.py; this file only lays it out.
"""

from __future__ import annotations

import logging
from pathlib import Path

import altair as alt
import av
import streamlit as st

from roundabout_watch import stats, trial
from roundabout_watch.detect import MODEL_SIZES, Detector

log = logging.getLogger("roundabout_watch")

st.set_page_config(page_title="Roundabout Watch", page_icon="🚦", layout="wide")


@st.cache_resource(show_spinner="Loading the detector (the first time downloads it)…")
def detector(size: str) -> Detector:
    # Kept across runs, so a second video doesn't reload a 368 MB model.
    return trial.load_detector(size)


st.title("Try a video")
st.caption(
    "Everything runs on this computer. The video is processed in a temporary "
    "folder and deleted; only the result stays, until you leave this page."
)

source = st.radio(
    "Video", ["Upload a file", "A file on this computer"], horizontal=True, key="source"
)
upload = None
path_text = ""
if source == "Upload a file":
    upload = st.file_uploader(
        "Drop a video here", type=[s.lstrip(".") for s in trial.VIDEO_SUFFIXES], key="upload"
    )
else:
    path_text = st.text_input(
        "Path to the video", placeholder="~/Downloads/IMG_0843.MOV", key="path"
    ).strip()
size = st.selectbox(
    "Detector size",
    MODEL_SIZES,
    index=MODEL_SIZES.index("small"),
    help="Bigger finds more, and runs slower.",
    key="size",
)

if st.button("Run", type="primary", disabled=upload is None and not path_text, key="run"):
    bar = st.progress(0.0, text="Starting…")

    def progress(done: int, total: int | None) -> None:
        if total:
            bar.progress(min(done / total, 1.0), text=f"Frame {done} of {total}")
        elif done % 30 == 0:
            bar.progress(0.0, text=f"Frame {done}")

    try:
        found = detector(size)
        if upload is not None:
            with trial.saved_upload(upload.getbuffer(), upload.name) as video:
                result = trial.run(video, upload.name, found, progress)
        else:
            video = Path(path_text).expanduser()
            if not video.is_file():
                raise ValueError(f"there's no file at {video}")
            trial.video_suffix(video.name)
            result = trial.run(video, video.name, found, progress)
    except RuntimeError as err:
        # Our own sentence, such as how to install the detector, or PyTorch
        # running out of memory on a large detector size.
        st.session_state.pop("result", None)
        log.error("trying a video failed: %s", type(err).__name__)
        st.error(str(err))
    except (av.FFmpegError, ValueError, OSError) as err:
        # A failed run must not leave the last video's result on screen as
        # if it were this one's. OSError covers a full disk or a file this
        # computer won't let us read.
        st.session_state.pop("result", None)
        log.error("trying a video failed: %s", type(err).__name__)
        st.error(f"Couldn't use that video: {err}.")
    else:
        st.session_state["result"] = result
    finally:
        bar.empty()

shown = st.session_state.get("result")
if isinstance(shown, trial.Result):
    summary = shown.summary
    st.header(shown.name)
    st.caption(
        f"{summary.frames} frames, {summary.video_seconds:.0f} s of video, processed in "
        f"{summary.wall_seconds:.0f} s. These are road users the detector and tracker saw: "
        "it can miss one or split one in two. Speeds and near-misses come with calibration."
    )
    left, right = st.columns([3, 2])
    with left:
        st.video(shown.video, format="video/mp4")
        st.download_button(
            "Download the marked-up video",
            shown.video,
            file_name=f"{Path(shown.name).stem}.tracked.mp4",
            mime="video/mp4",
        )
    with right:
        counts = stats.counts_by_kind(summary.spans)
        st.metric("Road users seen", len(summary.spans))
        if counts:
            for column, (kind, count) in zip(st.columns(len(counts)), counts, strict=True):
                column.metric(kind.value.capitalize(), count)

        width = stats.bin_seconds(summary.video_seconds)
        bars = stats.arrivals(summary.spans, summary.video_seconds, width)
        st.subheader(f"Arrivals every {width} s")
        windows = [f"{i * width:>4}–{(i + 1) * width} s" for i in range(len(bars))]
        st.bar_chart({"window": windows, "arrivals": bars}, x="window", y="arrivals")
        top = stats.busiest(bars)
        if top is not None:
            st.caption(f"Busiest: {top[0] * width}–{(top[0] + 1) * width} s, with {top[1]}.")

        medians = stats.median_seconds_in_view(summary.spans)
        if medians:
            st.subheader("Time in view (median)")
            st.dataframe(
                [{"kind": k.value, "seconds": round(s, 1)} for k, s in medians.items()],
                hide_index=True,
            )

    rows = trial.timeline(summary.spans)
    if rows:
        st.subheader("Timeline")
        st.caption("When each road user was in view, in seconds from the start of the video.")
        st.altair_chart(
            alt.Chart({"values": rows})
            .mark_bar()
            .encode(
                x=alt.X("arrived:Q", title="seconds into the video"),
                x2="left:Q",
                y=alt.Y("road user:N", sort=None, title=None),
                color=alt.Color("kind:N", title=None),
                tooltip=["road user:N", "arrived:Q", "left:Q", "in view:Q"],
            ),
            width="stretch",
        )
        st.dataframe(rows, hide_index=True)
