# lance-playground

Small experiment: index a video's frames into a [Lance](https://lancedb.github.io/lance/) dataset and browse it with Streamlit.

## Setup

```bash
uv sync
```

Download a sample video (e.g. [Big Buck Bunny, 720p, ~5MB](https://upload.wikimedia.org/wikipedia/commons/e/e7/Big_buck_bunny_720p_5mb.webm)) into `data/`.

## Usage

```bash
# Decode the video and write sampled frames into a Lance dataset
uv run index_video.py data/<your-video>.webm --fps 2 --out data/frames.lance

# Dump a few frames as PNGs to eyeball them directly
uv run view_frames.py data/frames.lance --n 8 --out data/preview

# Browse interactively (frame viewer + paginated thumbnail grid)
uv run streamlit run app.py
```

`data/` is gitignored — everything in it is reproducible from the source video via the scripts above.
