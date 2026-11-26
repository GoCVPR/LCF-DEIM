"""Group original CODrone images using 64-bit pHash and Hamming distance <= 10."""
import argparse
import csv
import io
import zlib
from pathlib import Path, PureWindowsPath

import imagehash
import numpy as np
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


def group_ids(hashes):
    bits = np.stack([h.hash.ravel() for h in hashes])
    # L1 distance on binary vectors is exactly the Hamming distance.
    pairs = cKDTree(bits).query_pairs(10, p=1, eps=0, output_type="ndarray")
    graph = coo_matrix((np.ones(len(pairs), dtype=np.uint8), pairs.T),
                       shape=(len(bits), len(bits)))
    count, labels = connected_components(graph, directed=False)
    # Input paths are sorted; number groups by their first member.
    ids = {g: f"G{i:06d}" for i, g in enumerate(dict.fromkeys(labels), 1)}
    return [ids[g] for g in labels], count


def read_hash(root, row):
    name = row["image"]
    if (not name or "\\" in name or PureWindowsPath(name).drive
            or any(p in ("", ".", "..") for p in name.split("/"))):
        raise ValueError(f"Invalid relative image path: {name!r}")
    path = (root / name).resolve(strict=True)
    path.relative_to(root)
    data = path.read_bytes()
    if "uncompressed_bytes" in row and len(data) != int(row["uncompressed_bytes"]):
        raise ValueError(f"JPG size mismatch: {name}")
    if "archive_crc32" in row and zlib.crc32(data) != int(row["archive_crc32"], 16):
        raise ValueError(f"JPG CRC32 mismatch: {name}")
    with Image.open(io.BytesIO(data)) as im:
        return imagehash.phash(im, hash_size=8, highfreq_factor=4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    with args.inventory.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "image" not in (reader.fieldnames or []):
            parser.error("Inventory must contain an image column.")
        rows = sorted(reader, key=lambda row: row["image"])
    if not rows or len({row["image"] for row in rows}) != len(rows):
        parser.error("Inventory is empty or contains duplicate image paths.")
    hashes = [read_hash(root, row) for row in rows]
    groups, count = group_ids(hashes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["image", "group_id", "phash64"])
        for row, group, h in zip(rows, groups, hashes):
            writer.writerow([row["image"], group, str(h)])
    print(f"{len(rows)} images, {count} groups")


if __name__ == "__main__":
    main()
