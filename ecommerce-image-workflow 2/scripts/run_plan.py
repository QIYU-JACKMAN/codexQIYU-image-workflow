#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from workflow_lib import (
    WorkflowError,
    derive_project_status,
    detect_cli_provider,
    load_manifest,
    sanitize_error,
    size_for,
    upsert_result,
    validate_project_dir,
    write_json,
)


def parse_selection(value: str | None, task_count: int) -> set[int] | None:
    if value is None:
        return None
    try:
        selected = {int(item.strip()) for item in value.split(",") if item.strip()}
    except ValueError as exc:
        raise WorkflowError("--only must contain comma-separated integers") from exc
    invalid = sorted(item for item in selected if item < 1 or item > task_count)
    if invalid:
        raise WorkflowError(f"--only contains unknown task IDs: {invalid}")
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an approved ecommerce image plan")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--only", help="comma-separated task IDs")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--provider", choices=["auto", "codex-imagegen"], default="auto")
    args = parser.parse_args()

    project_dir = args.project_dir.expanduser().resolve()
    try:
        project, plan = validate_project_dir(project_dir)
        selected = parse_selection(args.only, len(plan["tasks"]))
    except WorkflowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if project["workflow"] == "local-region-replacement":
        print("ERROR: use local_region.py for local-region-replacement", file=sys.stderr)
        return 1
    if not args.dry_run and not plan["approved"]:
        print("ERROR: real generation requires plan.approved=true", file=sys.stderr)
        return 1

    provider = detect_cli_provider()
    if args.provider == "codex-imagegen" and provider is None and not args.dry_run:
        print("ERROR: codex-imagegen is not available in PATH", file=sys.stderr)
        return 1
    if provider is None and not args.dry_run:
        print(
            "ERROR: no CLI provider available; use Codex built-in image generation "
            "and record results with record_result.py",
            file=sys.stderr,
        )
        return 1

    if not args.dry_run:
        project["status"] = "running"
        write_json(project_dir / "project.json", project)

    assets = {asset["id"]: Path(asset["path"]) for asset in project["assets"]}
    images_dir = project_dir / "images"
    work_dir = project_dir / "work"
    images_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(project_dir, project)
    manifest["provider"] = provider or "unavailable-dry-run"
    failures = 0

    for task in plan["tasks"]:
        task_id = task["id"]
        if selected is not None and task_id not in selected:
            continue
        if task.get("enabled", True) is False:
            upsert_result(manifest, task_id, {"status": "disabled"})
            continue
        output = images_dir / task["output_name"]
        if output.exists() and output.stat().st_size > 0 and not args.force:
            upsert_result(
                manifest,
                task_id,
                {"status": "skipped", "output": str(output), "qa_status": "pending"},
            )
            print(f"task {task_id}: skipped existing {output.name}")
            continue

        defaults = project["defaults"]
        ratio = task.get("aspect_ratio", defaults["aspect_ratio"])
        resolution = task.get("resolution", defaults["resolution"])
        quality = task.get("quality", defaults["quality"])
        model = defaults["model"]
        image_paths = [assets[item] for item in task["asset_ids"]]
        size = size_for(ratio, resolution)
        record = {
            "status": "dry-run" if args.dry_run else "running",
            "output": str(output),
            "size": size,
            "quality": quality,
            "image_count": len(image_paths),
            "qa_status": "pending",
        }
        upsert_result(manifest, task_id, record)
        write_json(project_dir / "manifest.json", manifest)
        operation = "edit" if image_paths else "generate"
        print(f"task {task_id}: {operation} -> {output.name} ({size}, {quality})")
        if args.dry_run:
            continue

        command = [
            "codex-imagegen",
            operation,
            "--model",
            model,
            "--prompt",
            task["prompt"],
            "--size",
            size,
            "--quality",
            quality,
            "--output-format",
            "png",
            "--out",
            str(output),
        ]
        if args.force:
            command.append("--force")
        for image in image_paths:
            command.extend(["--image", str(image)])
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode == 0 and output.is_file() and output.stat().st_size > 0:
            upsert_result(manifest, task_id, {"status": "success", "error": None})
        else:
            failures += 1
            message = result.stderr or result.stdout or "provider returned no output file"
            upsert_result(
                manifest,
                task_id,
                {"status": "failed", "error": sanitize_error(message)},
            )
        write_json(project_dir / "manifest.json", manifest)

    write_json(project_dir / "manifest.json", manifest)
    if not args.dry_run:
        project["status"] = derive_project_status(plan, manifest)
        write_json(project_dir / "project.json", project)
    print(f"manifest: {project_dir / 'manifest.json'}")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
