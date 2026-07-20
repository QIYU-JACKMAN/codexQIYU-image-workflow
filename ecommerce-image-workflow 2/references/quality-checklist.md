# Image quality gate

Inspect every generated file before delivery.

## Common checks

- File is non-empty and dimensions match the approved task.
- Output is one complete image, not a collage, grid, or accidental long page.
- Product identity, structure, color, logo, packaging, and accessory count remain
  faithful to the product assets.
- Text is legible, uses the requested language, and contains no extra brand or
  unsupported claim.
- Perspective, contact shadow, reflections, hand interaction, and scene scale are
  physically coherent.
- A multi-image set uses one visual language without repeating the same layout.

## Branch checks

- Detail/main images: each screen has one primary communication goal and the set
  covers the approved selling points.
- Replication: reference layout and style are recognizable, but reference brand
  and product facts do not leak into the result.
- Resize: no stretching, blank bars, cropped critical copy, or missing subject.
- SKU: the correct product and corresponding SKU text appear in each mapped task.
- Local replacement: no selection-box residue or hard seam; original canvas
  dimensions are unchanged.

Mark failures in `manifest.json`. Retry only failed task IDs. Never regenerate a
successful batch wholesale unless the user explicitly requests it.
