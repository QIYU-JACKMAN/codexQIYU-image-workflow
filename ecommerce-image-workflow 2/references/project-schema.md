# Project record contract

Each run lives under `<workspace>/output/imagegen/<project-slug>/` and contains
`project.json`, `plan.json`, `manifest.json`, `images/`, and `work/`.

## project.json

```json
{
  "schema_version": "1.0",
  "project_name": "Portable blender summer campaign",
  "project_slug": "portable-blender-summer",
  "workflow": "detail-main-images",
  "platform": "Amazon US",
  "language": "en-US",
  "status": "planned",
  "defaults": {
    "model": "gpt-image-2",
    "quality": "high",
    "resolution": "2K",
    "aspect_ratio": "1:1"
  },
  "assets": [
    {
      "id": "product-1",
      "role": "product",
      "path": "/absolute/path/product.png",
      "label": "front product photo"
    }
  ],
  "workflow_config": {}
}
```

Allowed workflows are `quick-generate`, `phone-photo-retouch`, `detail-main-images`, `custom-batch`,
`exact-replication`, `style-variation`, `batch-resize`, `batch-sku`, and
`local-region-replacement`. `batch-replication` remains accepted only for old
projects created before the three replication modes were separated.

Allowed asset roles are `product`, `style_reference`, `composition_reference`,
`reference`, `template`, `scene`, `logo`, `mask`, and `source`. Product assets
establish facts. Reference assets establish visual direction only unless their
role says otherwise. `source` is the original image in a batch-resize task.

## plan.json

```json
{
  "schema_version": "1.0",
  "approved": false,
  "approved_at": null,
  "tasks": [
    {
      "id": 1,
      "role": "hero",
      "title": "Primary product image",
      "enabled": true,
      "original_request": "Put this product on a clean white background",
      "optimized_prompt": "Use case: product-mockup...",
      "prompt": "Use case: product-mockup...",
      "prompt_review": {
        "status": "pending",
        "reviewed_at": null,
        "notes": "",
        "optimizer_version": "gpt-image-2-ecommerce-v1"
      },
      "asset_ids": ["product-1"],
      "aspect_ratio": "1:1",
      "resolution": "2K",
      "quality": "high",
      "output_name": "01-hero.png",
      "metadata": {}
    }
  ]
}
```

Task IDs are continuous integers starting at 1. Every prompt must be complete;
never use phrases such as "same as above". `asset_ids` determines image order.
When a prompt says `image 1`, it refers to the first ID in this array.

`original_request` preserves the customer's words. `optimized_prompt` is the
customer-facing rewrite produced with the built-in optimizer module. `prompt`
must equal the reviewed `optimized_prompt`; it is the exact instruction submitted
to image generation. Every enabled task requires `prompt_review.status=approved`
before the whole plan may be approved.

Set `approved` to `true` only after the customer explicitly confirms every enabled
task prompt and the displayed plan. Real generation refuses an unapproved plan or
any enabled task whose prompt review is not approved.

## Workflow-specific config

- `phone-photo-retouch`: one to five `product` assets, exactly one task per
  product photo, and `workflow_config.retouch_level` set to `natural`,
  `ecommerce`, or `studio`. Each task maps its edit target first, followed by all
  other product angles in confirmed asset order as fact-only references.
- `exact-replication`: one `reference` asset, zero to four `product` assets, and
  one task whose image order is reference first, then products.
- `style-variation`: one to five visual references, no more than five total input
  images, and one to ten tasks that preserve the confirmed input-image order.
- `batch-resize`: one to twenty `source` assets and `workflow_config.targets`
  containing one to five unique aspect ratios. Tasks are ordered by source, then
  target, with exactly one source per task.
- `batch-replication`: legacy compatibility only; `workflow_config.mode` is
  `replicate` or `resize`.
- `batch-sku`: `workflow_config.template_asset_id` is required. `sku_fields` may
  map every product asset ID to structured fields. Legacy `sku_texts` remains
  accepted when empty or aligned with the product count.
- `local-region-replacement`: `workflow_config.region` contains integer `x`,
  `y`, and `size`, plus optional non-negative `inset` and `feather`.

## manifest.json

The scripts create this file. It records the provider and one result per task:
status, output path, dimensions, error summary, QA status, QA notes, and retry
count. Errors are sanitized before persistence. Do not add credentials, request
headers, or provider responses containing authentication data.
