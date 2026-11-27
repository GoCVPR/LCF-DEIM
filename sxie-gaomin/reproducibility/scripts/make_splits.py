"""Generate train, validation, and test manifests from dataset inventories (CPython 3.8)."""
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

IMAGE_TARGETS = {
    "visdrone": (6903, 863, 863),
    "uavdt": (62375, 7612, 7832),
    "codrone": (8021, 987, 996),
}
# (sequence, seeded subset, reference subset), for this inventory only.
UAVDT_MOVES = (
    ("M1304", "train", "test"), ("S0306", "train", "val"),
    ("M1003", "val", "test"), ("M1007", "val", "train"),
    ("M1004", "test", "train"), ("S0308", "test", "val"),
)


def match_image_counts(dataset, assign, sizes):
    """Reassign whole units for this release while preserving seed-0 unit counts."""
    targets = dict(zip(SPLITS, IMAGE_TARGETS[dataset]))
    unit_counts = Counter(assign.values())
    if dataset == "uavdt":
        for sequence, source, destination in UAVDT_MOVES:
            if assign.get(sequence) != source:
                raise ValueError("Unexpected starting subset for " + sequence)
            assign[sequence] = destination
    elif dataset == "codrone":
        # Dictionary order is the shuffled seed-0 unit order.
        for source in ("val", "test"):
            current = sum(sizes[u] for u in assign if assign[u] == source)
            excess = current - targets[source]
            # Each pair exchanged reduces this subset by exactly one image.
            pairs = [u for u in assign if assign[u] == source and sizes[u] == 2]
            singles = [u for u in assign if assign[u] == "train" and sizes[u] == 1]
            if not 0 <= excess <= min(len(pairs), len(singles)):
                raise ValueError("CODrone group sizes differ from the release inventory")
            for pair, single in zip(pairs[:excess], singles[:excess]):
                assign[pair], assign[single] = "train", source
    image_counts = Counter()
    for unit_id, subset in assign.items():
        image_counts[subset] += sizes[unit_id]
    if image_counts != targets or Counter(assign.values()) != unit_counts:
        raise ValueError("Reference image or unit counts do not match")


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
    match_image_counts(dataset, assign, Counter(row[unit] for row in rows))
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
