"""Preview a Lance frame dataset: print row metadata and dump sample frames as PNGs.

Usage:
    uv run view_frames.py data/frames.lance --n 8 --out data/preview
"""

import argparse
from pathlib import Path

import lance
import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Path to the Lance dataset")
    parser.add_argument("--n", type=int, default=8, help="Number of frames to export as PNGs")
    parser.add_argument("--out", type=Path, default=Path("data/preview"), help="Directory to write PNGs into")
    args = parser.parse_args()

    ds = lance.dataset(str(args.dataset))
    print(f"Dataset: {args.dataset}")
    print(f"Rows: {ds.count_rows()}  Versions: {[v['version'] for v in ds.versions()]}")
    print(f"Schema:\n{ds.schema}\n")

    tbl = ds.to_table(limit=args.n)
    args.out.mkdir(parents=True, exist_ok=True)

    for row in tbl.to_pylist():
        img = np.frombuffer(row["image"], dtype=np.uint8).reshape(row["height"], row["width"], 3)
        out_path = args.out / f"frame_{row['frame_index']:06d}.png"
        Image.fromarray(img).save(out_path)
        print(f"  frame_index={row['frame_index']:>6}  t={row['timestamp_sec']:.2f}s  -> {out_path}")

    print(f"\nWrote {min(args.n, tbl.num_rows)} PNGs to {args.out.resolve()}")


if __name__ == "__main__":
    main()
