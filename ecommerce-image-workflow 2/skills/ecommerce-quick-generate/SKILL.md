---
name: ecommerce-quick-generate
description: >-
  快速生成一张或多张电商图片，支持纯文字、最多 5 张参考图和 1-10 个独立结果，并在出图前用内置 gpt-image-2 模块优化提示词、请求客户校验。用户已经知道大致想画什么，要求快捷出图、换场景、做少量商品图或基于少量参考图生成时使用。多屏详情页、批量复刻、批量 SKU 和局部裁切不要使用本技能。
---

# 电商图片快捷生成

保持内联执行，不使用子代理。

## 输入

最高优先级支持用户直接在一条消息中上传图片和原始提示词。先消费已提供信息，不要重复询问或要求填写完整表单。

- 图片 + 提示词：立即查看图片、判断职责并进入提示词优化。
- 只有提示词：按纯文生图处理。
- 只有图片：先判断图片职责，只询问“希望生成或修改什么”。
- 两者都没有：才要求用户补充输入。

随后只补齐真正缺失的数量 1-10、画幅、分辨率、语言和必须保留/禁止内容。

图片按实际提交顺序登记。商品图建立商品事实；风格或构图参考图只提供视觉方向。默认 `gpt-image-2`、`high`、`2K`、`1:1`。

## 计划

1. 从当前 `SKILL.md` 路径向上两级定位插件根目录，读取公共参考目录中的项目格式、`gpt-image-2-prompt-optimizer.md`、提示词和质量检查文档。
2. 在 `<workspace>/output/imagegen/<project-slug>/` 创建完整项目结构。
3. 写入 `project.json`，工作流固定为 `quick-generate`。
4. 为每个结果创建独立任务。用户没有要求重复图时，让不同任务采用互补构图而不是机械复制。
5. 对每个任务保存客户原话为 `original_request`，用内置优化器生成 `optimized_prompt`，并令 `prompt` 与优化结果一致。初始 `prompt_review.status` 为 `pending`。
6. 按内置优化器的客户校验格式展示原需求、优化结果、图片映射、不可改动项和新增补充，请客户批准、修改或选择原需求。未批准时停在这里；修改后重新展示。
7. 客户批准后把对应 `prompt_review.status` 改为 `approved`，再写入仍未批准的完整 `plan.json`，运行：

```bash
python3 scripts/validate_plan.py <project-dir>
```

8. 展示任务数、逐图目标、图片编号、参数和输出目录，等待用户对完整计划再次明确确认。

## 生成与质检

确认后才把 `approved` 改为 `true`。优先加载并遵循 Codex 自带 `imagegen` 能力；如果不可用但 PATH 中存在 `codex-imagegen`，运行：

```bash
python3 scripts/run_plan.py <project-dir> --dry-run
python3 scripts/run_plan.py <project-dir>
```

使用内置图片能力时，按任务把图片保存到 `images/`，并用 `record_result.py` 登记结果。逐张检查商品一致性、文字、品牌、尺寸和单图约束；用同一脚本写入 QA 状态。只重做失败任务。
