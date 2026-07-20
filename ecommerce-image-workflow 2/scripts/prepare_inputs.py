#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


RESIZE_README = """# 批量改尺寸素材说明

必需文件：
1. `01-待处理原图/`：放入 1-20 张 PNG、JPG、JPEG 或 WEBP 图片。
2. `02-目标尺寸.txt`：每行填写一个目标画幅，例如 `1:1`、`4:5`、`9:16`。

建议使用 01、02、03 前缀命名。Skill 会忽略隐藏文件、`.DS_Store` 和非图片文件。
放好后回到对话并回复“已放好”。
"""

SKU_README = """# 批量 SKU 素材说明

必需文件：
1. `01-SKU商品图/`：放入 1-20 张不同 SKU 商品图。
2. `02-SKU模板/`：只能放入 1 张模板图。

可选文件：
3. `03-SKU映射表/sku-mapping.csv`：需要更新名称、型号、尺寸或文案时填写。
4. `04-共用要求/instructions.txt`：填写全批次共用要求。

映射表通过 `product_file` 精确匹配商品图片，不依赖文件顺序。不要从文件名推断认证、性能或规格。
放好后回到对话并回复“已放好”。
"""


def safe_slug(value: str) -> str:
    value = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
        raise ValueError("project-slug must be lowercase hyphen-case")
    return value


def write_if_missing(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_resize(root: Path, force: bool) -> None:
    (root / "01-待处理原图").mkdir(parents=True, exist_ok=True)
    write_if_missing(root / "请先阅读.md", RESIZE_README, force)
    write_if_missing(root / "02-目标尺寸.txt", "1:1\n4:5\n9:16\n", force)


def create_sku(root: Path, force: bool) -> None:
    for name in ("01-SKU商品图", "02-SKU模板", "03-SKU映射表", "04-共用要求"):
        (root / name).mkdir(parents=True, exist_ok=True)
    write_if_missing(root / "请先阅读.md", SKU_README, force)
    write_if_missing(
        root / "03-SKU映射表" / "sku-mapping.csv",
        "product_file,sku_id,product_name,model,size,copy,output_name\n",
        force,
    )
    write_if_missing(root / "04-共用要求" / "instructions.txt", "", force)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a batch input drop folder")
    parser.add_argument("workflow", choices=["batch-resize", "batch-sku"])
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--project-slug", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        slug = safe_slug(args.project_slug)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    root = args.workspace.expanduser().resolve() / "input" / "ecommerce-image-workflow" / slug
    root.mkdir(parents=True, exist_ok=True)
    if args.workflow == "batch-resize":
        create_resize(root, args.force)
    else:
        create_sku(root, args.force)
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
