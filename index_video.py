"""Decode a video into frames and write them to a Lance dataset.

Usage:
    uv run index_video.py data/big_buck_bunny_720p_5mb.webm --fps 1 --out data/frames.lance
"""

import argparse
from pathlib import Path

import av
import lance
import numpy as np
import pyarrow as pa


def extract_frames(video_path: Path, sample_fps: float):
    container = av.open(str(video_path))
    stream = container.streams.video[0]
    video_fps = float(stream.average_rate)
    step = max(1, round(video_fps / sample_fps))

    for i, frame in enumerate(container.decode(stream)):
        if i % step != 0:
            continue
        img = frame.to_ndarray(format="rgb24")
        yield {
            "frame_index": i,
            "timestamp_sec": float(frame.time or 0.0),
            "height": img.shape[0],
            "width": img.shape[1],
            "image": img.tobytes(),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="Path to the source video file")
    parser.add_argument("--fps", type=float, default=1.0, help="Frames per second to sample")
    parser.add_argument("--out", type=Path, default=Path("data/frames.lance"), help="Output Lance dataset path")
    args = parser.parse_args()

    rows = list(extract_frames(args.video, args.fps))
    print(f"Extracted {len(rows)} frames at ~{args.fps} fps from {args.video}")

    table = pa.table(
        {
            "frame_index": pa.array([r["frame_index"] for r in rows], type=pa.int64()),
            "timestamp_sec": pa.array([r["timestamp_sec"] for r in rows], type=pa.float32()),
            "height": pa.array([r["height"] for r in rows], type=pa.int32()),
            "width": pa.array([r["width"] for r in rows], type=pa.int32()),
            "image": pa.array([r["image"] for r in rows], type=pa.binary()),
        }
    )

    ds = lance.write_dataset(table, str(args.out), mode="overwrite")
    print(f"Wrote Lance dataset to {args.out} ({ds.count_rows()} rows, version {ds.version})")


if __name__ == "__main__":
    main()
