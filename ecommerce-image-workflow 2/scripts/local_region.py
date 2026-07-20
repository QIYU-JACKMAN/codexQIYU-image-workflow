#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workflow_lib import WorkflowError, validate_project_dir


def load_local_config(project_dir: Path):
    project, plan = validate_project_dir(project_dir)
    if project["workflow"] != "local-region-replacement":
        raise WorkflowError("project is not a local-region-replacement workflow")
    scene = next(asset for asset in project["assets"] if asset["role"] == "scene")
    region = project["workflow_config"]["region"]
    return project, plan, Path(scene["path"]), region


def prepare(project_dir: Path, output: Path | None = None) -> Path:
    try:
        from PIL import Image
    except ImportError as exc:
        raise WorkflowError("Pillow is required; run with `uv run --with pillow`") from exc
    _, _, scene_path, region = load_local_config(project_dir)
    x, y, size = region["x"], region["y"], region["size"]
    output = output or project_dir / "work" / "region-input.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(scene_path) as image:
        if x + size > image.width or y + size > image.height:
            raise WorkflowError(
                f"region exceeds scene bounds {image.width}x{image.height}: "
                f"x={x}, y={y}, size={size}"
            )
        image.convert("RGBA").crop((x, y, x + size, y + size)).save(output, "PNG")
    return output


def preview(project_dir: Path, output: Path | None = None) -> Path:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise WorkflowError("Pillow is required; run with `uv run --with pillow`") from exc
    _, _, scene_path, region = load_local_config(project_dir)
    x, y, size = region["x"], region["y"], region["size"]
    output = output or project_dir / "work" / "region-preview.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(scene_path) as scene_image:
        if x + size > scene_image.width or y + size > scene_image.height:
            raise WorkflowError(
                f"region exceeds scene bounds {scene_image.width}x{scene_image.height}: "
                f"x={x}, y={y}, size={size}"
            )
        image = scene_image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle((x, y, x + size - 1, y + size - 1), fill=(255, 64, 64, 40))
        line_width = max(2, min(image.size) // 300)
        draw.rectangle(
            (x, y, x + size - 1, y + size - 1), outline=(255, 48, 48, 255), width=line_width
        )
        Image.alpha_composite(image, overlay).save(output, "PNG")
    return output


def composite(project_dir: Path, generated: Path, output: Path | None = None) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ImportError as exc:
        raise WorkflowError("Pillow is required; run with `uv run --with pillow`") from exc
    _, plan, scene_path, region = load_local_config(project_dir)
    if not generated.is_file():
        raise WorkflowError(f"generated region does not exist: {generated}")
    x, y, size = region["x"], region["y"], region["size"]
    inset = region.get("inset", 24 if size < 500 else 50)
    feather = region.get("feather", 12 if size < 500 else 25)
    if inset * 2 >= size:
        raise WorkflowError("region inset is too large for the selected size")
    output = output or project_dir / "images" / plan["tasks"][0]["output_name"]
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(scene_path) as scene_image, Image.open(generated) as generated_image:
        scene = scene_image.convert("RGBA")
        if x + size > scene.width or y + size > scene.height:
            raise WorkflowError("region exceeds scene bounds")
        replacement = generated_image.convert("RGBA").resize(
            (size, size), Image.Resampling.LANCZOS
        )
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rectangle(
            (inset, inset, size - inset - 1, size - inset - 1), fill=255
        )
        if feather:
            mask = mask.filter(ImageFilter.GaussianBlur(feather))
        scene.paste(replacement, (x, y), mask)
        if output.suffix.lower() in {".jpg", ".jpeg"}:
            scene.convert("RGB").save(output, quality=95)
        else:
            scene.save(output, "PNG")
        if scene.size != scene_image.size:
            raise WorkflowError("composited image dimensions changed unexpectedly")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or composite a local image region")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("project_dir", type=Path)
    prepare_parser.add_argument("--output", type=Path)
    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument("project_dir", type=Path)
    preview_parser.add_argument("--output", type=Path)
    composite_parser = subparsers.add_parser("composite")
    composite_parser.add_argument("project_dir", type=Path)
    composite_parser.add_argument("--generated", required=True, type=Path)
    composite_parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    project_dir = args.project_dir.expanduser().resolve()
    try:
        if args.command == "prepare":
            output = prepare(project_dir, args.output)
        elif args.command == "preview":
            output = preview(project_dir, args.output)
        else:
            output = composite(project_dir, args.generated.expanduser().resolve(), args.output)
    except WorkflowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
