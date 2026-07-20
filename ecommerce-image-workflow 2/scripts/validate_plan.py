#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from workflow_lib import WorkflowError, validate_project_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an ecommerce image project")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument(
        "--allow-missing-assets",
        action="store_true",
        help="validate structure without requiring asset files to exist",
    )
    args = parser.parse_args()
    try:
        project, plan = validate_project_dir(
            args.project_dir, require_files=not args.allow_missing_assets
        )
    except WorkflowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    enabled = sum(task.get("enabled", True) is not False for task in plan["tasks"])
    print(
        f"VALID: {project['workflow']} | {len(project['assets'])} assets | "
        f"{enabled}/{len(plan['tasks'])} enabled tasks | approved={plan['approved']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
