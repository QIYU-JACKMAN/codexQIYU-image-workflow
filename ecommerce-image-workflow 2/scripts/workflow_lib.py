#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
WORKFLOWS = {
    "quick-generate",
    "phone-photo-retouch",
    "detail-main-images",
    "custom-batch",
    "exact-replication",
    "style-variation",
    "batch-resize",
    "batch-replication",
    "batch-sku",
    "local-region-replacement",
}
ASSET_ROLES = {
    "product",
    "style_reference",
    "composition_reference",
    "reference",
    "template",
    "scene",
    "logo",
    "mask",
    "source",
}
QUALITIES = {"low", "medium", "high", "auto"}
RESOLUTIONS = {"1K", "2K", "4K"}
STATUSES = {"planned", "approved", "running", "partial", "completed", "failed"}
PROMPT_REVIEW_STATUSES = {"pending", "approved", "rejected"}


class WorkflowError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise WorkflowError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkflowError(f"{path.name} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def parse_ratio(value: str) -> tuple[int, int]:
    if value == "auto":
        return (1, 1)
    match = re.fullmatch(r"([1-9]\d*):([1-9]\d*)", value)
    if not match:
        raise WorkflowError(f"invalid aspect_ratio: {value}")
    return int(match.group(1)), int(match.group(2))


def _round16(value: float) -> int:
    return max(16, int(round(value / 16.0)) * 16)


def size_for(aspect_ratio: str, resolution: str) -> str:
    if aspect_ratio == "auto":
        return "auto"
    if resolution not in RESOLUTIONS:
        raise WorkflowError(f"invalid resolution: {resolution}")
    rw, rh = parse_ratio(aspect_ratio)
    short_edge = {"1K": 1024, "2K": 1536, "4K": 2048}[resolution]
    if rw >= rh:
        width, height = short_edge * rw / rh, short_edge
    else:
        width, height = short_edge, short_edge * rh / rw
    scale = min(1.0, 3840 / max(width, height), math.sqrt(8_294_400 / (width * height)))
    width, height = _round16(width * scale), _round16(height * scale)
    while width * height > 8_294_400:
        if width >= height:
            width -= 16
        else:
            height -= 16
    return f"{width}x{height}"


def _assets_by_role(project: dict[str, Any], role: str) -> list[dict[str, Any]]:
    return [asset for asset in project["assets"] if asset["role"] == role]


def _validate_asset_paths(assets: list[dict[str, Any]], require_files: bool) -> None:
    seen: set[str] = set()
    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            raise WorkflowError(f"asset {index} must be an object")
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", asset_id):
            raise WorkflowError(f"asset {index} has an invalid id")
        if asset_id in seen:
            raise WorkflowError(f"duplicate asset id: {asset_id}")
        seen.add(asset_id)
        if asset.get("role") not in ASSET_ROLES:
            raise WorkflowError(f"asset {asset_id} has an invalid role")
        path = Path(str(asset.get("path", ""))).expanduser()
        if not path.is_absolute():
            raise WorkflowError(f"asset {asset_id} path must be absolute")
        if require_files and not path.is_file():
            raise WorkflowError(f"asset {asset_id} does not exist: {path}")


def _validate_defaults(defaults: Any) -> None:
    if not isinstance(defaults, dict):
        raise WorkflowError("project defaults must be an object")
    model = defaults.get("model")
    if not isinstance(model, str) or not model.strip():
        raise WorkflowError("defaults.model must be a non-empty string")
    if defaults.get("quality") not in QUALITIES:
        raise WorkflowError("defaults.quality must be low, medium, high, or auto")
    if defaults.get("resolution") not in RESOLUTIONS:
        raise WorkflowError("defaults.resolution must be 1K, 2K, or 4K")
    parse_ratio(str(defaults.get("aspect_ratio", "")))


def _validate_tasks(project: dict[str, Any], plan: dict[str, Any]) -> None:
    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise WorkflowError("plan.tasks must be a non-empty array")
    asset_ids = {asset["id"] for asset in project["assets"]}
    defaults = project["defaults"]
    for expected, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise WorkflowError(f"task {expected} must be an object")
        if task.get("id") != expected:
            raise WorkflowError(f"task IDs must be continuous; expected {expected}")
        if not isinstance(task.get("prompt"), str) or not task["prompt"].strip():
            raise WorkflowError(f"task {expected} prompt must be non-empty")
        if not isinstance(task.get("original_request"), str) or not task[
            "original_request"
        ].strip():
            raise WorkflowError(f"task {expected} original_request must be non-empty")
        if not isinstance(task.get("optimized_prompt"), str) or not task[
            "optimized_prompt"
        ].strip():
            raise WorkflowError(f"task {expected} optimized_prompt must be non-empty")
        if task["prompt"] != task["optimized_prompt"]:
            raise WorkflowError(
                f"task {expected} prompt must equal the customer-reviewed optimized_prompt"
            )
        prompt_review = task.get("prompt_review")
        if not isinstance(prompt_review, dict):
            raise WorkflowError(f"task {expected} prompt_review must be an object")
        if prompt_review.get("status") not in PROMPT_REVIEW_STATUSES:
            raise WorkflowError(f"task {expected} prompt_review status is invalid")
        if not isinstance(prompt_review.get("optimizer_version"), str) or not prompt_review[
            "optimizer_version"
        ].strip():
            raise WorkflowError(f"task {expected} optimizer_version must be non-empty")
        if prompt_review["status"] == "approved":
            reviewed_at = prompt_review.get("reviewed_at")
            if not isinstance(reviewed_at, str) or not reviewed_at.strip():
                raise WorkflowError(
                    f"task {expected} approved prompt_review requires reviewed_at"
                )
        if plan.get("approved") and task.get("enabled", True) is not False:
            if prompt_review["status"] != "approved":
                raise WorkflowError(
                    f"task {expected} prompt must be customer-approved before plan approval"
                )
        lowered = task["prompt"].lower()
        if "same as above" in lowered or "同上" in task["prompt"]:
            raise WorkflowError(f"task {expected} prompt must be standalone")
        refs = task.get("asset_ids")
        if not isinstance(refs, list) or any(not isinstance(item, str) for item in refs):
            raise WorkflowError(f"task {expected} asset_ids must be an array of strings")
        unknown = [item for item in refs if item not in asset_ids]
        if unknown:
            raise WorkflowError(f"task {expected} references unknown assets: {unknown}")
        if len(refs) > 5:
            raise WorkflowError(f"task {expected} may use at most 5 images")
        ratio = str(task.get("aspect_ratio", defaults["aspect_ratio"]))
        resolution = str(task.get("resolution", defaults["resolution"]))
        quality = task.get("quality", defaults["quality"])
        parse_ratio(ratio)
        if resolution not in RESOLUTIONS:
            raise WorkflowError(f"task {expected} has an invalid resolution")
        if quality not in QUALITIES:
            raise WorkflowError(f"task {expected} has an invalid quality")
        output_name = task.get("output_name")
        if not isinstance(output_name, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*\.png", output_name
        ):
            raise WorkflowError(f"task {expected} output_name must be a safe PNG filename")


def _validate_branch(project: dict[str, Any], plan: dict[str, Any]) -> None:
    workflow = project["workflow"]
    tasks = plan["tasks"]
    products = _assets_by_role(project, "product")
    config = project.get("workflow_config", {})
    if not isinstance(config, dict):
        raise WorkflowError("workflow_config must be an object")

    if workflow == "quick-generate":
        if not 1 <= len(tasks) <= 10:
            raise WorkflowError("quick-generate requires 1 to 10 tasks")
        if len(project["assets"]) > 5:
            raise WorkflowError("quick-generate accepts at most 5 input images")
    elif workflow == "phone-photo-retouch":
        if not 1 <= len(products) <= 5:
            raise WorkflowError("phone-photo-retouch requires 1 to 5 product photos")
        if len(project["assets"]) != len(products):
            raise WorkflowError("phone-photo-retouch accepts only product photo assets")
        if config.get("retouch_level") not in {"natural", "ecommerce", "studio"}:
            raise WorkflowError(
                "phone-photo-retouch retouch_level must be natural, ecommerce, or studio"
            )
        if len(tasks) != len(products):
            raise WorkflowError("phone-photo-retouch requires one task per product photo")
        product_ids = [product["id"] for product in products]
        for task, product in zip(tasks, products):
            expected_assets = [product["id"], *[item for item in product_ids if item != product["id"]]]
            if task["asset_ids"] != expected_assets:
                raise WorkflowError(
                    f"retouch task {task['id']} must map its edit target first, then all cross-angle references"
                )
    elif workflow == "detail-main-images":
        if not 1 <= len(products) <= 5:
            raise WorkflowError("detail-main-images requires 1 to 5 product images")
        if not 1 <= len(tasks) <= 20:
            raise WorkflowError("detail-main-images requires 1 to 20 tasks")
    elif workflow == "custom-batch":
        if len(products) > 5:
            raise WorkflowError("custom-batch accepts at most 5 product images")
        if not 1 <= len(tasks) <= 20:
            raise WorkflowError("custom-batch requires 1 to 20 tasks")
    elif workflow == "exact-replication":
        references = _assets_by_role(project, "reference")
        if len(references) != 1:
            raise WorkflowError("exact-replication requires exactly one reference image")
        if len(products) > 4:
            raise WorkflowError("exact-replication accepts at most 4 product images")
        if len(project["assets"]) != 1 + len(products):
            raise WorkflowError(
                "exact-replication accepts only one reference and optional product images"
            )
        if len(tasks) != 1:
            raise WorkflowError("exact-replication requires exactly one task")
        expected_assets = [references[0]["id"], *[asset["id"] for asset in products]]
        if tasks[0]["asset_ids"] != expected_assets:
            raise WorkflowError(
                "exact-replication task must map the reference first, then product images"
            )
    elif workflow == "style-variation":
        references = [
            asset
            for asset in project["assets"]
            if asset["role"] in {"style_reference", "composition_reference", "reference"}
        ]
        if not 1 <= len(references) <= 5:
            raise WorkflowError("style-variation requires 1 to 5 reference images")
        if len(project["assets"]) > 5:
            raise WorkflowError("style-variation accepts at most 5 input images total")
        if not 1 <= len(tasks) <= 10:
            raise WorkflowError("style-variation requires 1 to 10 tasks")
        expected_assets = [asset["id"] for asset in project["assets"]]
        for task in tasks:
            if task["asset_ids"] != expected_assets:
                raise WorkflowError(
                    f"style variation task {task['id']} must preserve the confirmed input-image order"
                )
    elif workflow == "batch-resize":
        sources = _assets_by_role(project, "source")
        if not 1 <= len(sources) <= 20:
            raise WorkflowError("batch-resize requires 1 to 20 source images")
        if len(project["assets"]) != len(sources):
            raise WorkflowError("batch-resize accepts only source image assets")
        targets = config.get("targets")
        if not isinstance(targets, list) or not 1 <= len(targets) <= 5:
            raise WorkflowError("batch-resize targets must contain 1 to 5 aspect ratios")
        normalized_targets: list[str] = []
        for target in targets:
            if not isinstance(target, str):
                raise WorkflowError("batch-resize targets must be aspect-ratio strings")
            parse_ratio(target)
            normalized_targets.append(target)
        if len(set(normalized_targets)) != len(normalized_targets):
            raise WorkflowError("batch-resize targets must be unique")
        if len(tasks) != len(sources) * len(normalized_targets):
            raise WorkflowError("batch-resize requires one task per source and target pair")
        expected_pairs = [
            (source["id"], target) for source in sources for target in normalized_targets
        ]
        actual_pairs = [
            (task["asset_ids"][0] if len(task["asset_ids"]) == 1 else None,
             str(task.get("aspect_ratio", project["defaults"]["aspect_ratio"])))
            for task in tasks
        ]
        if actual_pairs != expected_pairs:
            raise WorkflowError(
                "batch-resize tasks must follow source order, then target order, with one source each"
            )
    elif workflow == "batch-replication":
        references = _assets_by_role(project, "reference")
        if not 1 <= len(references) <= 20:
            raise WorkflowError("batch-replication requires 1 to 20 reference images")
        if len(products) > 4:
            raise WorkflowError("batch-replication accepts at most 4 product images")
        if config.get("mode") not in {"replicate", "resize"}:
            raise WorkflowError("batch-replication mode must be replicate or resize")
        if len(tasks) != len(references):
            raise WorkflowError("batch-replication requires one task per reference image")
        product_ids = [asset["id"] for asset in products]
        for task, reference in zip(tasks, references):
            if task["asset_ids"] != [reference["id"], *product_ids]:
                raise WorkflowError(
                    f"replication task {task['id']} must map its reference first, then products"
                )
    elif workflow == "batch-sku":
        templates = _assets_by_role(project, "template")
        if not 1 <= len(products) <= 20:
            raise WorkflowError("batch-sku requires 1 to 20 product images")
        if len(templates) != 1:
            raise WorkflowError("batch-sku requires exactly one template image")
        sku_texts = config.get("sku_texts", [])
        if not isinstance(sku_texts, list) or len(sku_texts) not in {0, len(products)}:
            raise WorkflowError("sku_texts must be empty or match the product image count")
        sku_fields = config.get("sku_fields", {})
        if not isinstance(sku_fields, dict):
            raise WorkflowError("sku_fields must be an object keyed by product asset ID")
        product_ids = {asset["id"] for asset in products}
        if sku_fields and set(sku_fields) != product_ids:
            raise WorkflowError("sku_fields must map every product asset ID exactly once")
        if any(not isinstance(fields, dict) for fields in sku_fields.values()):
            raise WorkflowError("each sku_fields value must be an object")
        if config.get("template_asset_id") != templates[0]["id"]:
            raise WorkflowError("template_asset_id must identify the template asset")
        if len(tasks) != len(products):
            raise WorkflowError("batch-sku requires one task per product image")
        for task, product in zip(tasks, products):
            if task["asset_ids"] != [product["id"], templates[0]["id"]]:
                raise WorkflowError(
                    f"SKU task {task['id']} must map its product first and template second"
                )
    elif workflow == "local-region-replacement":
        scenes = _assets_by_role(project, "scene")
        if len(scenes) != 1:
            raise WorkflowError("local replacement requires exactly one scene image")
        if len(products) > 4:
            raise WorkflowError("local replacement accepts at most 4 product images")
        if len(tasks) != 1:
            raise WorkflowError("local replacement requires exactly one task")
        expected_assets = [scenes[0]["id"], *[asset["id"] for asset in products]]
        if tasks[0]["asset_ids"] != expected_assets:
            raise WorkflowError(
                "local replacement task must map the scene first, then product images"
            )
        region = config.get("region")
        if not isinstance(region, dict):
            raise WorkflowError("local replacement requires workflow_config.region")
        for field in ("x", "y", "size"):
            if not isinstance(region.get(field), int):
                raise WorkflowError(f"region.{field} must be an integer")
        if region["x"] < 0 or region["y"] < 0 or region["size"] <= 0:
            raise WorkflowError("region coordinates must be non-negative and size positive")
        for field in ("inset", "feather"):
            if field in region and (
                not isinstance(region[field], int) or region[field] < 0
            ):
                raise WorkflowError(f"region.{field} must be a non-negative integer")


def validate_project_dir(
    project_dir: Path, *, require_files: bool = True
) -> tuple[dict[str, Any], dict[str, Any]]:
    project_dir = project_dir.expanduser().resolve()
    project = read_json(project_dir / "project.json")
    plan = read_json(project_dir / "plan.json")
    if project.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError("project.json must use schema_version 1.0")
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise WorkflowError("plan.json must use schema_version 1.0")
    if project.get("workflow") not in WORKFLOWS:
        raise WorkflowError("project workflow is not supported")
    slug = project.get("project_slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise WorkflowError("project_slug must be lowercase hyphen-case")
    if project.get("status") not in STATUSES:
        raise WorkflowError("project status is invalid")
    assets = project.get("assets")
    if not isinstance(assets, list):
        raise WorkflowError("project assets must be an array")
    _validate_asset_paths(assets, require_files)
    _validate_defaults(project.get("defaults"))
    if not isinstance(plan.get("approved"), bool):
        raise WorkflowError("plan.approved must be true or false")
    _validate_tasks(project, plan)
    _validate_branch(project, plan)
    return project, plan


def detect_cli_provider() -> str | None:
    return "codex-imagegen" if shutil.which("codex-imagegen") else None


def sanitize_error(value: str) -> str:
    value = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", value)
    value = re.sub(
        r"(?i)(authorization|api[_-]?key|token)\s*[:=]\s*\S+",
        r"\1=[REDACTED]",
        value,
    )
    return value.strip()[-1200:]


def load_manifest(project_dir: Path, project: dict[str, Any]) -> dict[str, Any]:
    path = project_dir / "manifest.json"
    if path.exists():
        manifest = read_json(path)
        if manifest.get("schema_version") != SCHEMA_VERSION:
            raise WorkflowError("manifest.json must use schema_version 1.0")
        return manifest
    return {
        "schema_version": SCHEMA_VERSION,
        "project_slug": project["project_slug"],
        "workflow": project["workflow"],
        "provider": None,
        "results": [],
    }


def upsert_result(
    manifest: dict[str, Any], task_id: int, values: dict[str, Any]
) -> dict[str, Any]:
    results = manifest.setdefault("results", [])
    existing = next((item for item in results if item.get("task_id") == task_id), None)
    if existing is None:
        existing = {"task_id": task_id, "retry_count": 0, "qa_status": "pending"}
        results.append(existing)
    elif values.get("status") == "running":
        existing["retry_count"] = int(existing.get("retry_count", 0)) + 1
    existing.update(values)
    results.sort(key=lambda item: item.get("task_id", 0))
    return existing


def derive_project_status(plan: dict[str, Any], manifest: dict[str, Any]) -> str:
    enabled_ids = {
        task["id"] for task in plan["tasks"] if task.get("enabled", True) is not False
    }
    results = {
        item.get("task_id"): item.get("status") for item in manifest.get("results", [])
    }
    statuses = [results.get(task_id) for task_id in enabled_ids]
    if statuses and all(status in {"success", "skipped"} for status in statuses):
        return "completed"
    if any(status in {"queued", "running"} for status in statuses):
        return "running"
    terminal = [status for status in statuses if status in {"success", "skipped", "failed"}]
    if terminal and all(status == "failed" for status in terminal) and len(terminal) == len(statuses):
        return "failed"
    if terminal:
        return "partial"
    return "approved" if plan.get("approved") else "planned"
