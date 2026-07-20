#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workflow_lib import (
    WorkflowError,
    derive_project_status,
    load_manifest,
    sanitize_error,
    upsert_result,
    validate_project_dir,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a built-in provider result or QA review")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--task", required=True, type=int)
    parser.add_argument(
        "--status", choices=["queued", "running", "success", "failed", "skipped"]
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--provider", default="codex-builtin-imagegen")
    parser.add_argument("--error")
    parser.add_argument("--qa", choices=["pending", "pass", "fail"])
    parser.add_argument("--notes")
    args = parser.parse_args()

    project_dir = args.project_dir.expanduser().resolve()
    try:
        project, plan = validate_project_dir(project_dir)
    except WorkflowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.task < 1 or args.task > len(plan["tasks"]):
        print("ERROR: unknown task ID", file=sys.stderr)
        return 1
    if args.status in {"queued", "running", "success"} and not plan["approved"]:
        print("ERROR: image generation results require plan.approved=true", file=sys.stderr)
        return 1
    values = {}
    if args.status:
        values["status"] = args.status
    if args.output:
        output = args.output.expanduser().resolve()
        if args.status == "success" and (not output.is_file() or output.stat().st_size == 0):
            print("ERROR: successful output must be a non-empty file", file=sys.stderr)
            return 1
        values["output"] = str(output)
    if args.error:
        values["error"] = sanitize_error(args.error)
    if args.qa:
        values["qa_status"] = args.qa
    if args.notes is not None:
        values["qa_notes"] = args.notes
    if not values:
        print("ERROR: provide a status, output, error, QA status, or notes", file=sys.stderr)
        return 1

    manifest = load_manifest(project_dir, project)
    manifest["provider"] = args.provider
    upsert_result(manifest, args.task, values)
    write_json(project_dir / "manifest.json", manifest)
    project["status"] = derive_project_status(plan, manifest)
    write_json(project_dir / "project.json", project)
    print(f"recorded task {args.task}: {project_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
