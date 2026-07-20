# Prompt construction

Use the plugin's `GPT Image 2 Ecommerce Prompt Optimizer` module before this
construction checklist. The optimizer preserves the original customer request,
produces the task prompt, and requires customer validation before generation.

Write every task prompt as a standalone instruction in this order:

1. Commercial objective and exact product identity.
2. Scene, composition, camera angle, and subject scale.
3. Lighting, shadows, materials, palette, and visual hierarchy.
4. Exact short on-image copy, if any, including language.
5. Reference-image responsibilities and numbered mapping.
6. Product-preservation constraints grounded in visible evidence.
7. Negative constraints and the single-image requirement.

Product images control shape, color, texture, logo, packaging text, accessory
count, ports, buttons, and asymmetric details. Style references may influence
layout, lighting, color, typography hierarchy, and pacing, but must not donate
their brand, claims, specifications, or product structure.

Do not invent certifications, rankings, prices, medical effects, materials,
dimensions, performance claims, or guarantees. Mark unreadable product text as
uncertain rather than guessing it.

Keep generated text short. When exact long-form typography is business-critical,
generate a clean composition with reserved text space and recommend deterministic
typesetting after image generation.

For a set, keep typography hierarchy, palette, light direction, product scale,
and spacing logic coherent while varying composition and communication role.
Every task must explicitly request one complete image, not a collage, grid,
contact sheet, or long page.
