#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SAFE_OUTPUT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.png")


def natural_key(path: Path):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def images_in(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    return sorted(
        [
            item.resolve()
            for item in path.iterdir()
            if item.is_file() and not item.name.startswith(".") and item.suffix.lower() in IMAGE_EXTENSIONS
        ],
        key=natural_key,
    )


def duplicate_groups(images: list[Path]) -> list[list[str]]:
    by_digest: dict[str, list[str]] = {}
    for image in images:
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        by_digest.setdefault(digest, []).append(image.name)
    return [names for names in by_digest.values() if len(names) > 1]


def parse_target(value: str) -> dict[str, str]:
    value = value.strip()
    ratio = re.fullmatch(r"([1-9]\d*):([1-9]\d*)", value)
    dimensions = re.fullmatch(r"([1-9]\d*)[xX]([1-9]\d*)", value)
    if ratio:
        width, height = int(ratio.group(1)), int(ratio.group(2))
    elif dimensions:
        width, height = int(dimensions.group(1)), int(dimensions.group(2))
    else:
        raise ValueError(f"invalid target size: {value}")
    if max(width, height) / min(width, height) > 3:
        raise ValueError(f"target ratio exceeds 3:1: {value}")
    divisor = math.gcd(width, height)
    return {"input": value, "aspect_ratio": f"{width // divisor}:{height // divisor}"}


def scan_resize(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    images = images_in(root / "01-待处理原图")
    if not 1 <= len(images) <= 20:
        errors.append("01-待处理原图 must contain 1 to 20 supported images")
    duplicates = duplicate_groups(images)
    if duplicates:
        errors.append(f"duplicate source image content: {duplicates}")
    target_file = root / "02-目标尺寸.txt"
    targets = []
    if not target_file.is_file():
        errors.append("02-目标尺寸.txt is missing")
    else:
        for line in target_file.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                targets.append(parse_target(line))
            except ValueError as exc:
                errors.append(str(exc))
    unique = []
    seen = set()
    for target in targets:
        if target["aspect_ratio"] in seen:
            warnings.append(f"duplicate target ignored: {target['aspect_ratio']}")
            continue
        seen.add(target["aspect_ratio"])
        unique.append(target)
    targets = unique
    if not 1 <= len(targets) <= 5:
        errors.append("provide 1 to 5 unique target sizes")
    mappings = [
        {
            "source": str(image),
            "target": target["aspect_ratio"],
            "output_name": f"{image.stem}-{target['aspect_ratio'].replace(':', 'x')}.png",
        }
        for image in images
        for target in targets
    ]
    return {
        "workflow": "batch-resize",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "images": [str(image) for image in images],
        "targets": targets,
        "mappings": mappings,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def scan_sku(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    products = images_in(root / "01-SKU商品图")
    templates = images_in(root / "02-SKU模板")
    if not 1 <= len(products) <= 20:
        errors.append("01-SKU商品图 must contain 1 to 20 supported images")
    if len(templates) != 1:
        errors.append("02-SKU模板 must contain exactly one supported image")
    duplicates = duplicate_groups(products)
    if duplicates:
        errors.append(f"duplicate SKU product image content: {duplicates}")
    mapping_path = root / "03-SKU映射表" / "sku-mapping.csv"
    rows = read_csv(mapping_path)
    product_names = {item.name for item in products}
    row_names = [row.get("product_file", "").strip() for row in rows if any(row.values())]
    if len(row_names) != len(set(row_names)):
        errors.append("sku-mapping.csv contains duplicate product_file values")
    unknown = sorted(set(row_names) - product_names)
    missing = sorted(product_names - set(row_names)) if row_names else []
    if unknown:
        errors.append(f"mapping references unknown product files: {unknown}")
    if missing:
        errors.append(f"mapping is missing product files: {missing}")
    instructions = root / "04-共用要求" / "instructions.txt"
    row_by_name = {row.get("product_file", "").strip(): row for row in rows if any(row.values())}
    for row in rows:
        output_name = row.get("output_name", "").strip()
        if output_name and not SAFE_OUTPUT.fullmatch(output_name):
            errors.append(f"unsafe output_name in sku-mapping.csv: {output_name}")
    mappings = [
        {
            "product": str(product),
            "template": str(templates[0]) if len(templates) == 1 else None,
            "fields": row_by_name.get(product.name, {}),
            "output_name": row_by_name.get(product.name, {}).get("output_name") or f"{product.stem}.png",
        }
        for product in products
    ]
    if not rows:
        warnings.append("no SKU field mapping supplied; tasks will replace product identity only")
    return {
        "workflow": "batch-sku",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "products": [str(item) for item in products],
        "template": str(templates[0]) if len(templates) == 1 else None,
        "instructions": instructions.read_text(encoding="utf-8") if instructions.is_file() else "",
        "mappings": mappings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan and validate a batch input folder")
    parser.add_argument("workflow", choices=["batch-resize", "batch-sku"])
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    root = args.input_dir.expanduser().resolve()
    report = scan_resize(root) if args.workflow == "batch-resize" else scan_sku(root)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
