"""Browse a Lance dataset of video frames: single-frame viewer + thumbnail grid."""

import numpy as np
import lance
import streamlit as st

st.set_page_config(page_title="Lance frame viewer", page_icon=":material/movie:", layout="wide")


@st.cache_resource
def get_dataset(path: str) -> lance.LanceDataset:
    return lance.dataset(path)


@st.cache_data
def get_summary(path: str) -> dict:
    ds = get_dataset(path)
    first = ds.to_table(columns=["height", "width", "timestamp_sec"], limit=1).to_pylist()[0]
    last = ds.to_table(columns=["timestamp_sec"], offset=ds.count_rows() - 1, limit=1).to_pylist()[0]
    return {
        "rows": ds.count_rows(),
        "height": first["height"],
        "width": first["width"],
        "duration_sec": last["timestamp_sec"],
    }


@st.cache_data
def load_row(path: str, offset: int) -> dict:
    ds = get_dataset(path)
    row = ds.to_table(offset=offset, limit=1).to_pylist()[0]
    row["array"] = np.frombuffer(row["image"], dtype=np.uint8).reshape(row["height"], row["width"], 3)
    del row["image"]
    return row


@st.cache_data
def load_page(path: str, offset: int, limit: int) -> list[dict]:
    ds = get_dataset(path)
    rows = ds.to_table(offset=offset, limit=limit).to_pylist()
    for row in rows:
        row["array"] = np.frombuffer(row["image"], dtype=np.uint8).reshape(row["height"], row["width"], 3)
        del row["image"]
    return rows


st.title("Lance frame viewer")

with st.sidebar:
    dataset_path = st.text_input("Dataset path", value="data/frames.lance")

try:
    summary = get_summary(dataset_path)
except (FileNotFoundError, ValueError):
    st.error(f"No Lance dataset found at `{dataset_path}`.")
    st.stop()

with st.container(horizontal=True):
    st.metric("Frames", summary["rows"])
    st.metric("Resolution", f"{summary['width']}×{summary['height']}")
    st.metric("Duration", f"{summary['duration_sec']:.1f}s")

viewer_tab, grid_tab = st.tabs(["Frame viewer", "Thumbnail grid"])

with viewer_tab:
    position = st.slider("Frame position", 0, summary["rows"] - 1, 0)
    row = load_row(dataset_path, position)
    st.image(
        row["array"],
        caption=f"frame_index={row['frame_index']}  t={row['timestamp_sec']:.2f}s",
        width="stretch",
    )

with grid_tab:
    page_size = st.selectbox("Thumbnails per page", [12, 24, 48], index=1)
    num_pages = max(1, -(-summary["rows"] // page_size))
    with st.container(horizontal_alignment="right"):
        page = st.pagination(num_pages, key="grid_page")

    offset = (page - 1) * page_size
    rows = load_page(dataset_path, offset, page_size)

    cols = st.columns(6)
    for i, row in enumerate(rows):
        with cols[i % 6]:
            st.image(row["array"], caption=f"t={row['timestamp_sec']:.2f}s", width="stretch")
