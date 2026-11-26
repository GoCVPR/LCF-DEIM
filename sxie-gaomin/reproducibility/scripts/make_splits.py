"""Create the three image lists for one dataset (CPython 3.8.20)."""
import argparse
import csv
import random
import re
from collections import Counter
from pathlib import Path, PureWindowsPath
from tempfile import TemporaryDirectory

SPLITS = ("train", "val", "test")
SPEC = {
    "visdrone": ("image", 8629, []),
    "uavdt": ("sequence_id", 77819, ["sequence_id"]),
    "codrone": ("group_id", 10004, ["group_id", "phash64"]),
}


def make_splits(dataset, inventory, out):
    unit, expected, extra = SPEC[dataset]
    with inventory.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, strict=True)
        if not {"image", unit, *extra}.issubset(reader.fieldnames or []):
            raise ValueError("Missing required inventory columns")
        rows = list(reader)
    if len(rows) != expected or len({r["image"] for r in rows}) != expected:
        raise ValueError("Check image coverage and duplicate paths")
    for row in rows:
        path = row["image"]
        if (not path or "\\" in path or PureWindowsPath(path).drive
                or any(p in ("", ".", "..") for p in path.split("/"))):
            raise ValueError("Invalid relative image path: %r" % path)
        if not row[unit] or row[unit] != row[unit].strip():
            raise ValueError("Missing or invalid unit ID: " + path)
        if dataset == "codrone" and not re.fullmatch(
                r"[0-9a-f]{16}", row["phash64"] or ""):
            raise ValueError("Invalid 64-bit hash: " + path)
    units = sorted({r[unit] for r in rows})
    n = len(units)
    if dataset == "uavdt" and n != 100:
        raise ValueError("Expected 100 source sequences")
    random.Random(0).shuffle(units)
    a, b = n * 8 // 10, n * 9 // 10
    names = ["train"] * a + ["val"] * (b - a) + ["test"] * (n - b)
    assign = dict(zip(units, names))
    rows.sort(key=lambda row: row["image"])
    for row in rows:
        row["split"] = assign[row[unit]]
    if out.exists():
        raise FileExistsError("Choose a new output directory: " + str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=str(out.parent)) as tmp:
        stage = Path(tmp) / "splits"
        stage.mkdir()
        for split in SPLITS:
            batch = [r for r in rows if r["split"] == split]
            with (stage / (split + ".csv")).open(
                    "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, ["image", "split"] + extra,
                                        extrasaction="ignore", lineterminator="\n")
                writer.writeheader()
                writer.writerows(batch)
            with (stage / (split + ".txt")).open(
                    "w", encoding="utf-8", newline="") as f:
                f.writelines(r["image"] + "\n" for r in batch)
        stage.rename(out)
    counts = Counter(r["split"] for r in rows)
    print(dataset, "seed=0", {s: counts[s] for s in SPLITS})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=SPEC)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("out", type=Path, help="new output directory")
    args = parser.parse_args()
    make_splits(args.dataset, args.inventory, args.out)
