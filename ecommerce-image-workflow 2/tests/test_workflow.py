from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from local_region import composite, prepare, preview  # noqa: E402
from scan_inputs import scan_resize, scan_sku  # noqa: E402
from workflow_lib import (  # noqa: E402
    WorkflowError,
    detect_cli_provider,
    read_json,
    validate_project_dir,
    write_json,
)


WORKFLOW_SKILLS = {
    "phone-photo-retouch": "ecommerce-phone-photo-retouch",
    "quick-generate": "ecommerce-quick-generate",
    "detail-main-images": "ecommerce-detail-main-images",
    "custom-batch": "ecommerce-custom-batch",
    "exact-replication": "ecommerce-exact-replication",
    "style-variation": "ecommerce-style-variation",
    "batch-resize": "ecommerce-batch-resize",
    "batch-sku": "ecommerce-batch-sku",
    "local-region-replacement": "ecommerce-local-region-replacement",
}


def make_image(path: Path, size: tuple[int, int] = (160, 120), color=(40, 80, 120)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, "PNG")
    return path.resolve()


class ProjectFactory:
    def __init__(self, root: Path):
        self.root = root
        self.assets_dir = root / "fixtures"
        self.counter = 0

    def asset(self, role: str, label: str) -> dict:
        self.counter += 1
        path = make_image(self.assets_dir / f"{label}.png")
        return {"id": label, "role": role, "path": str(path), "label": label}

    def create(self, workflow: str) -> Path:
        project_dir = self.root / workflow
        project_dir.mkdir(parents=True)
        product = self.asset("product", f"{workflow}-product")
        assets = [product]
        config = {}
        tasks = []
        if workflow == "quick-generate":
            tasks = [self.task(1, [product["id"]])]
        elif workflow == "phone-photo-retouch":
            product2 = self.asset("product", "retouch-product-back")
            assets = [product, product2]
            config = {"retouch_level": "ecommerce"}
            tasks = [
                self.task(1, [product["id"], product2["id"]]),
                self.task(2, [product2["id"], product["id"]]),
            ]
        elif workflow == "detail-main-images":
            tasks = [self.task(1, [product["id"]]), self.task(2, [product["id"]])]
        elif workflow == "custom-batch":
            tasks = [self.task(1, [product["id"]]), self.task(2, [product["id"]])]
        elif workflow == "exact-replication":
            reference = self.asset("reference", "exact-reference")
            assets = [reference, product]
            tasks = [self.task(1, [reference["id"], product["id"]])]
        elif workflow == "style-variation":
            reference = self.asset("style_reference", "style-reference")
            assets = [reference, product]
            tasks = [
                self.task(1, [reference["id"], product["id"]]),
                self.task(2, [reference["id"], product["id"]]),
            ]
        elif workflow == "batch-resize":
            source1 = self.asset("source", "resize-source-1")
            source2 = self.asset("source", "resize-source-2")
            assets = [source1, source2]
            config = {"targets": ["1:1", "4:5"]}
            tasks = [
                self.task(1, [source1["id"]], aspect_ratio="1:1"),
                self.task(2, [source1["id"]], aspect_ratio="4:5"),
                self.task(3, [source2["id"]], aspect_ratio="1:1"),
                self.task(4, [source2["id"]], aspect_ratio="4:5"),
            ]
        elif workflow == "batch-replication":
            ref1 = self.asset("reference", "replication-reference-1")
            ref2 = self.asset("reference", "replication-reference-2")
            assets = [product, ref1, ref2]
            config = {"mode": "replicate"}
            tasks = [
                self.task(1, [ref1["id"], product["id"]]),
                self.task(2, [ref2["id"], product["id"]]),
            ]
        elif workflow == "batch-sku":
            product2 = self.asset("product", "sku-product-2")
            template = self.asset("template", "sku-template")
            assets = [product, product2, template]
            config = {
                "template_asset_id": template["id"],
                "sku_texts": ["Model A", "Model B"],
                "sku_fields": {
                    product["id"]: {"model": "Model A"},
                    product2["id"]: {"model": "Model B"},
                },
            }
            tasks = [
                self.task(1, [product["id"], template["id"]]),
                self.task(2, [product2["id"], template["id"]]),
            ]
        elif workflow == "local-region-replacement":
            scene = self.asset("scene", "local-scene")
            make_image(Path(scene["path"]), (200, 160), (220, 220, 220))
            assets = [scene, product]
            config = {"region": {"x": 30, "y": 20, "size": 80, "inset": 8, "feather": 4}}
            tasks = [self.task(1, [scene["id"], product["id"]])]
        project = {
            "schema_version": "1.0",
            "project_name": workflow,
            "project_slug": workflow,
            "workflow": workflow,
            "platform": "test",
            "language": "en-US",
            "status": "planned",
            "defaults": {
                "model": "gpt-image-2",
                "quality": "high",
                "resolution": "2K",
                "aspect_ratio": "1:1",
            },
            "assets": assets,
            "workflow_config": config,
        }
        plan = {"schema_version": "1.0", "approved": False, "approved_at": None, "tasks": tasks}
        write_json(project_dir / "project.json", project)
        write_json(project_dir / "plan.json", plan)
        return project_dir

    @staticmethod
    def task(
        task_id: int, asset_ids: list[str], *, aspect_ratio: str = "1:1"
    ) -> dict:
        optimized = (
            "Use case: product-mockup\n"
            "Primary request: Create one complete ecommerce image.\n"
            "Constraints: preserve product identity.\n"
            "Avoid: collage, grid, watermark."
        )
        return {
            "id": task_id,
            "role": f"role-{task_id}",
            "title": f"Task {task_id}",
            "enabled": True,
            "original_request": "Create one ecommerce image.",
            "optimized_prompt": optimized,
            "prompt": optimized,
            "prompt_review": {
                "status": "pending",
                "reviewed_at": None,
                "notes": "",
                "optimizer_version": "gpt-image-2-ecommerce-v1",
            },
            "asset_ids": asset_ids,
            "aspect_ratio": aspect_ratio,
            "resolution": "2K",
            "quality": "high",
            "output_name": f"{task_id:02d}-result.png",
            "metadata": {},
        }

    @staticmethod
    def approve(project_dir: Path) -> None:
        plan = read_json(project_dir / "plan.json")
        for task in plan["tasks"]:
            if task.get("enabled", True) is not False:
                task["prompt_review"]["status"] = "approved"
                task["prompt_review"]["reviewed_at"] = "2026-07-19T00:00:00Z"
        plan["approved"] = True
        plan["approved_at"] = "2026-07-19T00:00:00Z"
        write_json(project_dir / "plan.json", plan)
        project = read_json(project_dir / "project.json")
        project["status"] = "approved"
        write_json(project_dir / "project.json", project)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.factory = ProjectFactory(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_all_nine_workflows_validate(self):
        for workflow in WORKFLOW_SKILLS:
            with self.subTest(workflow=workflow):
                project_dir = self.factory.create(workflow)
                project, plan = validate_project_dir(project_dir)
                self.assertEqual(project["workflow"], workflow)
                self.assertGreaterEqual(len(plan["tasks"]), 1)

    def test_router_has_exact_nine_options_and_routes(self):
        path = PLUGIN_ROOT / "skills" / "ecommerce-image-workflow" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        for number in range(1, 10):
            self.assertIn(f"{number}.", text)
        self.assertEqual(text.count("ecommerce-image-workflow:ecommerce-"), 9)
        first_option = text.index("1. 手机照片精修")
        quick_option = text.index("2. 快捷生成")
        self.assertLess(first_option, quick_option)

    def test_all_specialist_skill_files_exist(self):
        for skill in WORKFLOW_SKILLS.values():
            path = PLUGIN_ROOT / "skills" / skill / "SKILL.md"
            self.assertTrue(path.is_file(), skill)
            text = path.read_text(encoding="utf-8")
            self.assertIn("保持内联执行", text)
            self.assertTrue(
                "gpt-image-2-prompt-optimizer.md" in text or "内置优化器" in text
            )
            self.assertTrue("客户" in text or "用户" in text)

    def test_legacy_replication_projects_still_validate(self):
        project_dir = self.factory.create("batch-replication")
        project, plan = validate_project_dir(project_dir)
        self.assertEqual(project["workflow"], "batch-replication")
        self.assertEqual(len(plan["tasks"]), 2)

    def test_phone_retouch_requires_target_first_then_cross_angles(self):
        project_dir = self.factory.create("phone-photo-retouch")
        plan = read_json(project_dir / "plan.json")
        plan["tasks"][0]["asset_ids"].reverse()
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "edit target first"):
            validate_project_dir(project_dir)

    def test_phone_retouch_level_is_validated(self):
        project_dir = self.factory.create("phone-photo-retouch")
        project = read_json(project_dir / "project.json")
        project["workflow_config"]["retouch_level"] = "beautify"
        write_json(project_dir / "project.json", project)
        with self.assertRaisesRegex(WorkflowError, "retouch_level"):
            validate_project_dir(project_dir)

    def test_phone_retouch_skill_emphasizes_material_fidelity(self):
        path = PLUGIN_ROOT / "skills" / "ecommerce-phone-photo-retouch" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        for phrase in ("不同面", "微纹理", "Material fidelity", "waxy smoothing"):
            self.assertIn(phrase, text)

    def test_sku_text_count_must_match_products(self):
        project_dir = self.factory.create("batch-sku")
        project = read_json(project_dir / "project.json")
        project["workflow_config"]["sku_texts"] = ["only one"]
        write_json(project_dir / "project.json", project)
        with self.assertRaisesRegex(WorkflowError, "sku_texts"):
            validate_project_dir(project_dir)

    def test_sku_fields_must_map_every_product(self):
        project_dir = self.factory.create("batch-sku")
        project = read_json(project_dir / "project.json")
        first_id = next(iter(project["workflow_config"]["sku_fields"]))
        project["workflow_config"]["sku_fields"] = {first_id: {"model": "A"}}
        write_json(project_dir / "project.json", project)
        with self.assertRaisesRegex(WorkflowError, "sku_fields"):
            validate_project_dir(project_dir)

    def test_exact_replication_requires_reference_first(self):
        project_dir = self.factory.create("exact-replication")
        plan = read_json(project_dir / "plan.json")
        plan["tasks"][0]["asset_ids"].reverse()
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "reference first"):
            validate_project_dir(project_dir)

    def test_batch_resize_requires_complete_source_target_matrix(self):
        project_dir = self.factory.create("batch-resize")
        plan = read_json(project_dir / "plan.json")
        plan["tasks"].pop()
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "one task per source and target"):
            validate_project_dir(project_dir)

    def test_prepare_input_folders(self):
        for workflow, expected in (
            ("batch-resize", "01-待处理原图"),
            ("batch-sku", "03-SKU映射表/sku-mapping.csv"),
        ):
            with self.subTest(workflow=workflow):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS / "prepare_inputs.py"),
                        workflow,
                        "--workspace",
                        str(self.root),
                        "--project-slug",
                        f"test-{workflow}",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                input_dir = Path(result.stdout.strip())
                self.assertTrue((input_dir / expected).exists())

    def test_resize_scanner_natural_sort_and_targets(self):
        root = self.root / "resize-input"
        make_image(root / "01-待处理原图" / "10.png", color=(10, 0, 0))
        make_image(root / "01-待处理原图" / "2.png", color=(20, 0, 0))
        (root / "02-目标尺寸.txt").write_text("1:1\n1080x1350\n", encoding="utf-8")
        report = scan_resize(root)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual([Path(item).name for item in report["images"]], ["2.png", "10.png"])
        self.assertEqual(
            [item["aspect_ratio"] for item in report["targets"]], ["1:1", "4:5"]
        )
        self.assertEqual(len(report["mappings"]), 4)

    def test_resize_scanner_rejects_duplicate_content(self):
        root = self.root / "resize-duplicates"
        first = make_image(root / "01-待处理原图" / "1.png")
        second = root / "01-待处理原图" / "2.png"
        second.write_bytes(first.read_bytes())
        (root / "02-目标尺寸.txt").write_text("1:1\n", encoding="utf-8")
        report = scan_resize(root)
        self.assertFalse(report["valid"])
        self.assertTrue(any("duplicate source" in item for item in report["errors"]))

    def test_sku_scanner_maps_by_filename_and_rejects_unsafe_output(self):
        root = self.root / "sku-input"
        make_image(root / "01-SKU商品图" / "sku-2.png", color=(2, 0, 0))
        make_image(root / "01-SKU商品图" / "sku-10.png", color=(10, 0, 0))
        make_image(root / "02-SKU模板" / "template.png", color=(0, 10, 0))
        mapping = root / "03-SKU映射表" / "sku-mapping.csv"
        mapping.parent.mkdir(parents=True)
        mapping.write_text(
            "product_file,model,output_name\n"
            "sku-10.png,M10,../bad.png\n"
            "sku-2.png,M2,sku-2-card.png\n",
            encoding="utf-8",
        )
        report = scan_sku(root)
        self.assertFalse(report["valid"])
        self.assertEqual(
            [Path(item["product"]).name for item in report["mappings"]],
            ["sku-2.png", "sku-10.png"],
        )
        self.assertEqual(report["mappings"][0]["fields"]["model"], "M2")
        self.assertTrue(any("unsafe output_name" in item for item in report["errors"]))

    def test_unknown_asset_reference_is_rejected(self):
        project_dir = self.factory.create("quick-generate")
        plan = read_json(project_dir / "plan.json")
        plan["tasks"][0]["asset_ids"] = ["missing"]
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "unknown assets"):
            validate_project_dir(project_dir)

    def test_local_region_bounds_are_checked(self):
        project_dir = self.factory.create("local-region-replacement")
        project = read_json(project_dir / "project.json")
        project["workflow_config"]["region"] = {"x": 180, "y": 100, "size": 80}
        write_json(project_dir / "project.json", project)
        with self.assertRaisesRegex(WorkflowError, "exceeds scene bounds"):
            prepare(project_dir)

    def test_local_region_preview_prepare_and_composite_preserve_dimensions(self):
        project_dir = self.factory.create("local-region-replacement")
        preview_path = preview(project_dir)
        crop_path = prepare(project_dir)
        generated = make_image(project_dir / "work" / "region-generated.png", (128, 128), (220, 20, 20))
        output = composite(project_dir, generated)
        self.assertTrue(preview_path.is_file())
        with Image.open(crop_path) as crop_image:
            self.assertEqual(crop_image.size, (80, 80))
        with Image.open(output) as output_image:
            self.assertEqual(output_image.size, (200, 160))

    def test_dry_run_writes_manifest_without_provider(self):
        project_dir = self.factory.create("quick-generate")
        env = dict(os.environ)
        env["PATH"] = "/usr/bin:/bin"
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "run_plan.py"), str(project_dir), "--dry-run"],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = read_json(project_dir / "manifest.json")
        self.assertEqual(manifest["provider"], "unavailable-dry-run")
        self.assertEqual(manifest["results"][0]["status"], "dry-run")

    def test_real_run_requires_approval_before_provider(self):
        project_dir = self.factory.create("quick-generate")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "run_plan.py"), str(project_dir)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("approved=true", result.stderr)

    def test_plan_approval_requires_customer_prompt_review(self):
        project_dir = self.factory.create("quick-generate")
        plan = read_json(project_dir / "plan.json")
        plan["approved"] = True
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "customer-approved"):
            validate_project_dir(project_dir)

    def test_generation_prompt_must_equal_reviewed_optimized_prompt(self):
        project_dir = self.factory.create("quick-generate")
        plan = read_json(project_dir / "plan.json")
        plan["tasks"][0]["prompt"] = "unreviewed replacement"
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "must equal"):
            validate_project_dir(project_dir)

    def test_approved_prompt_review_requires_timestamp(self):
        project_dir = self.factory.create("quick-generate")
        plan = read_json(project_dir / "plan.json")
        plan["tasks"][0]["prompt_review"]["status"] = "approved"
        write_json(project_dir / "plan.json", plan)
        with self.assertRaisesRegex(WorkflowError, "reviewed_at"):
            validate_project_dir(project_dir)

    def test_existing_output_is_skipped(self):
        project_dir = self.factory.create("quick-generate")
        output = make_image(project_dir / "images" / "01-result.png")
        self.assertTrue(output.is_file())
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "run_plan.py"), str(project_dir), "--dry-run"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = read_json(project_dir / "manifest.json")
        self.assertEqual(manifest["results"][0]["status"], "skipped")

    def test_provider_detection(self):
        with mock.patch("workflow_lib.shutil.which", return_value="/usr/local/bin/codex-imagegen"):
            self.assertEqual(detect_cli_provider(), "codex-imagegen")
        with mock.patch("workflow_lib.shutil.which", return_value=None):
            self.assertIsNone(detect_cli_provider())

    def test_failed_task_does_not_block_later_tasks(self):
        project_dir = self.factory.create("detail-main-images")
        self.factory.approve(project_dir)
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        fake = fake_bin / "codex-imagegen"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import pathlib, sys\n"
            "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1])\n"
            "if out.name.startswith('01-'):\n"
            "    print('simulated provider failure', file=sys.stderr)\n"
            "    raise SystemExit(2)\n"
            "out.parent.mkdir(parents=True, exist_ok=True)\n"
            "out.write_bytes(b'png')\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{fake_bin}:{env.get('PATH', '')}"
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "run_plan.py"), str(project_dir)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        manifest = read_json(project_dir / "manifest.json")
        self.assertEqual(manifest["results"][0]["status"], "failed")
        self.assertEqual(manifest["results"][1]["status"], "success")
        self.assertEqual(read_json(project_dir / "project.json")["status"], "partial")

    def test_builtin_provider_result_can_be_recorded(self):
        project_dir = self.factory.create("quick-generate")
        self.factory.approve(project_dir)
        output = make_image(project_dir / "images" / "01-result.png")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "record_result.py"),
                str(project_dir),
                "--task",
                "1",
                "--status",
                "success",
                "--output",
                str(output),
                "--qa",
                "pass",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = read_json(project_dir / "manifest.json")
        self.assertEqual(manifest["provider"], "codex-builtin-imagegen")
        self.assertEqual(manifest["results"][0]["qa_status"], "pass")
        self.assertEqual(read_json(project_dir / "project.json")["status"], "completed")


if __name__ == "__main__":
    unittest.main()
