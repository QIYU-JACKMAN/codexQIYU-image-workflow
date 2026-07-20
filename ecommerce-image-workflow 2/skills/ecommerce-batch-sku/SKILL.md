---
name: ecommerce-batch-sku
description: >-
  把 1-20 张不同 SKU 商品图逐一套入同一个模板，先用内置 gpt-image-2 模块为每个 SKU 优化提示词并请求客户校验，保持整批风格一致，并支持一一对应的商品名称、型号、尺寸或规格文本。用户提到批量 SKU、同模板换产品、批量更新型号名称、统一商品卡片时使用。
---

# 电商批量 SKU

保持内联执行，不使用子代理。

## 输入与硬性映射

这是文件夹批处理工作流。先获取项目名称，运行：

```bash
python3 scripts/prepare_inputs.py batch-sku --workspace <workspace> --project-slug <slug>
```

创建素材投递目录和说明文件。用户一次放入 1-20 张商品图、正好 1 张模板和可选映射表，不逐张上传。用户回复“已放好”后运行：

```bash
python3 scripts/scan_inputs.py batch-sku <input-dir> --out <project-dir>/work/input-report.json
```

SKU 文本可不提供；一旦提供，使用 `sku-mapping.csv` 按 `product_file` 文件名明确匹配，不依赖文件顺序。不要从文件名猜测认证、性能、尺寸或规格。

每个任务中 `image 1` 是当前商品，`image 2` 是统一模板。只替换模板里的商品身份，并按当前任务的 SKU 文本更新明确列出的字段；背景、构图、字体层级和视觉风格保持一致。

## 执行

1. 定位插件根目录并读取公共参考，包括 `gpt-image-2-prompt-optimizer.md`。
2. 创建素材文件夹并报告绝对路径。用户回复“已放好”后运行扫描器，集中检查图片格式、数量、模板数量、CSV 文件名映射和重复文件。
3. 创建 `batch-sku` 项目，在 `workflow_config` 中记录模板 ID 和按明确文件名映射的 SKU 字段。
4. 每个商品创建一个任务，`asset_ids` 严格为当前商品、模板；`original_request` 保存共用替换要求和该商品对应的 SKU 文本。
5. 先展示“商品文件 → SKU 字段 → 输出文件”映射表并请求确认，再优化一份全批次共用提示词。共用提示词批准后为每个 SKU 注入对应字段；只有特殊 SKU 才单独校验提示词。
6. 运行公共校验器。文本映射错误或任一必要提示词未批准时停止，不做模糊匹配。
7. 生成前展示参数和目录，等待完整计划确认。
8. 批准后使用内置图片能力或公共 CLI 执行器。
9. 逐项检查商品身份和对应文本，只重画错误 SKU，不重跑整批。
