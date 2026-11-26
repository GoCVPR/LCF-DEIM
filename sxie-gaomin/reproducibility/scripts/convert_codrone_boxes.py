"""Convert original CODrone DOTA quadrilaterals to COCO horizontal boxes.

Ignored regions are retained in an extension for the loader/evaluator.
Standard COCOeval does not automatically mask those regions.
"""
import argparse
import csv
import json
import math
import os
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

from PIL import Image

CLASSES = ("car", "truck", "traffic-sign", "people", "motor", "bicycle",
           "traffic-light", "tricycle", "bridge", "bus", "boat", "ship")


def load_categories(path):
    # Default reference IDs follow Table II of the dataset paper, starting at 1.
    if path is None:
        return {name: i for i, name in enumerate(CLASSES, 1)}
    table = json.loads(path.read_text(encoding="utf-8-sig"))
    mapping = {item["name"]: item["id"] for item in table}
    if (len(table) != len(CLASSES) or set(mapping) != set(CLASSES)
            or any(type(v) is not int or v < 0 for v in mapping.values())
            or len(set(mapping.values())) != len(CLASSES)):
        raise ValueError("Expected exactly one unique integer ID for each class")
    return mapping


def read_images(manifest):
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        names = [row["image"] for row in reader]
    if not names or len(set(names)) != len(names):
        raise ValueError("Empty manifest or duplicate image path")
    return sorted(names)


def annotation_paths(root, name):
    p = PurePosixPath(name)
    if (len(p.parts) != 3 or p.parts[0] not in {"train", "val", "test"}
            or p.parts[1] != "images" or p.as_posix() != name
            or p.name == ".." or "\\" in name or PureWindowsPath(name).drive):
        raise ValueError(f"Expected original subset/images/filename: {name}")
    image = (root / p).resolve(strict=True)
    label = (root / p.parts[0] / "annfile" / p.with_suffix(".txt").name)
    label = label.resolve(strict=True)
    for path in (image, label):
        path.relative_to(root)
    return image, label


def convert(root, manifest, categories):
    images, objects, ignored, degenerate = [], [], [], []
    for image_id, name in enumerate(read_images(manifest), 1):
        image, label = annotation_paths(root, name)
        with Image.open(image) as im:
            width, height = im.size
        images.append(dict(id=image_id, file_name=name, width=width, height=height))
        for line_no, line in enumerate(label.read_text(encoding="utf-8-sig").splitlines(), 1):
            parts = line.split()
            if not parts or parts[0].startswith(("imagesource:", "gsd:")):
                continue
            if len(parts) != 10 or parts[9] not in ("0", "1"):
                raise ValueError(f"{label}:{line_no}: expected 8 coordinates, class, difficulty")
            xy = list(map(float, parts[:8]))
            cls, difficulty = parts[8], int(parts[9])
            if not all(map(math.isfinite, xy)) or (cls != "ignored" and cls not in categories):
                raise ValueError(f"{label}:{line_no}: invalid coordinates or unknown class")
            x, y = xy[::2], xy[1::2]
            box = [min(x), min(y), max(x) - min(x), max(y) - min(y)]
            area = box[2] * box[3]
            if not math.isfinite(area):
                raise ValueError(f"{label}:{line_no}: non-finite box area")
            record = dict(image_id=image_id, bbox=box, difficulty=difficulty)
            if box[2] == 0 or box[3] == 0 or cls == "ignored":
                record.update(source_line=line_no, polygon=xy)
                if box[2] == 0 or box[3] == 0:
                    record["class"] = cls
                    degenerate.append(record)
                else:
                    ignored.append(record)
            else:
                record.update(id=len(objects) + 1, category_id=categories[cls],
                              area=area, iscrowd=0)
                objects.append(record)
    return dict(info={"description": "CODrone horizontal boxes, original pixels"},
                images=images, annotations=objects,
                categories=[dict(id=v, name=k) for k, v in categories.items()],
                codrone_ignored_regions=ignored, codrone_degenerate_regions=degenerate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Extracted original CODrone directory")
    parser.add_argument("manifest", type=Path, help="Subset CSV containing image")
    parser.add_argument("output", type=Path, help="New COCO JSON file")
    parser.add_argument("--categories", type=Path, help="COCO list of {id,name}")
    args = parser.parse_args()
    data = convert(args.root.resolve(strict=True), args.manifest,
                   load_categories(args.categories))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp:
        staged = Path(temp) / "boxes.json"
        with staged.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, separators=(",", ":"), allow_nan=False)
        os.link(staged, args.output)
    print(len(data["images"]), "images,", len(data["annotations"]), "objects")


if __name__ == "__main__":
    main()
