---
name: ecommerce-local-region-replacement
description: >-
  只修改场景图中的一个方形区域，先用内置 gpt-image-2 模块优化局部编辑提示词并请求客户校验，再结合最多 4 张商品图生成替换内容，以羽化遮罩合成回原图并保持原始尺寸。用户提到局部裁切、局部迁移、局部换产品、佩戴替换、快速换脸或只改图片一小块时使用。
---

# 电商局部裁切与迁移

保持内联执行，不使用子代理。

## 输入

不创建素材文件夹。用户直接在对话中上传正好 1 张场景图、0-4 张商品图，并用自然语言说明修改对象、位置、必须保留和禁止修改内容。已有素材不重复索取。

Skill 根据自然语言和图像内容计算内部方形区域 `x/y/size`，先生成带选框预览让客户确认、移动或调整。没有区域确认不能生成。默认接缝：小于 500 px 时内收 24 px、羽化 12 px；否则内收 50 px、羽化 25 px。

## 计划与区域确认

1. 定位插件根目录并读取公共参考，包括 `gpt-image-2-prompt-optimizer.md`。
2. 创建 `local-region-replacement` 项目；`workflow_config.region` 记录坐标，计划只含一个任务。任务的 `asset_ids` 先场景图、后商品图，但实际生成时用准备好的裁区替代完整场景图。
3. 保存客户局部修改原话为 `original_request`，用内置优化器生成 `precise-object-edit`、`identity-preserve` 或 `compositing` 提示词，明确改变内容和所有不变量。
4. 展示原需求、优化提示词、Image 1 裁区与后续商品图映射、区域外不可改动项和优化器补充，请客户校验。批准后令 `prompt` 等于审阅结果并标记 `prompt_review.status=approved`。
5. 运行公共校验器，并用 Pillow 生成裁区预览：

```bash
uv run --with pillow python scripts/local_region.py preview <project-dir>
```

6. 展示预览、区域坐标、已批准提示词、图片映射、参数和输出目录。用户确认区域和完整计划后才把 `plan.approved` 改为 `true`。

## 生成与合成

1. 准备正方形裁区：

```bash
uv run --with pillow python scripts/local_region.py prepare <project-dir>
```

2. 把 `work/region-input.png` 作为 `image 1`，商品图作为 `image 2` 到 `image 5`，使用内置图片能力或 `codex-imagegen edit` 生成 `work/region-generated.png`，固定画幅 `1:1`。
3. 检查生成区域没有选框残留且商品、透视、尺度和光向正确。
4. 合成回原图：

```bash
uv run --with pillow python scripts/local_region.py composite <project-dir> --generated <project-dir>/work/region-generated.png
```

5. 确认最终宽高与原场景完全一致，用 `record_result.py` 记录生成和 QA。重试只替换裁区缓存，不覆盖原场景图。
