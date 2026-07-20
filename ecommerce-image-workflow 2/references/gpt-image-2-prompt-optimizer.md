# GPT Image 2 Ecommerce Prompt Optimizer

Internal template version: `gpt-image-2-ecommerce-v1`.

Use this module in every specialist workflow before approving an image task.
Codex performs the rewrite itself; do not call a separate text-model API.

## Internal optimizer instruction

Act as a senior ecommerce image prompt architect for `gpt-image-2`. Convert the
customer's original request into a concise, production-ready image specification
without changing intent or inventing product facts.

### Input contract

Use only:

- the customer's original request;
- confirmed product facts and visible evidence;
- the intended asset type and marketplace context;
- exact customer-supplied copy;
- the ordered input-image role map;
- explicit must-keep and must-avoid constraints.

Do not include model name, output size, quality, image count, file paths, API
settings, or billing parameters in the optimized prompt. Those remain task
parameters outside the creative instruction.

### Rewrite policy

1. Preserve every explicit customer requirement. If two requirements conflict,
   surface the conflict instead of silently choosing one.
2. If the request is already detailed, normalize and organize it. Do not inflate
   it with decorative language.
3. If the request is sparse, add only details that materially improve commercial
   usability: intended use, practical scene, framing, lighting, subject scale,
   visual hierarchy, and reasonable negative space.
4. Keep image references in actual submission order and state each responsibility
   explicitly: `Image 1: product identity`, `Image 2: style only`, and so on.
   Treat a solid-color or meaningless image as no usable reference only after
   visually inspecting it; never infer this from its filename or metadata.
5. Product images control structure, color, texture, logo, packaging, ports,
   buttons, accessory count, and asymmetric details. Style references never donate
   product facts, brands, claims, specifications, or copy.
6. Do not invent prices, rankings, certifications, medical effects, dimensions,
   materials, performance, guarantees, slogans, or extra characters and objects.
7. Quote exact short on-image copy verbatim. For difficult words, preserve the
   exact spelling. If long or typography-critical copy is requested, reserve a
   clean text area and flag deterministic typesetting as the reliable follow-up.
8. For edits, state invariants twice: what changes, and what must remain unchanged.
9. Every task requests one complete image, never a collage, contact sheet, grid,
   multi-panel composite, or full detail-page long image.
10. Write the optimized prompt in the customer's requested language. Preserve
    brand names, product names, and exact quoted copy in their original language.

### Structured output

Return only the optimized prompt using the useful fields below. Omit empty fields.

```text
Use case: <product-mockup | ads-marketing | identity-preserve |
  precise-object-edit | style-transfer | compositing | text-localization>
Asset type: <main image, detail screen, SKU card, local edit, etc.>
Primary request: <faithful normalized request>
Input images: <ordered image roles>
Scene/backdrop: <environment>
Subject: <product/person and essential visible details>
Style/medium: <commercial photo, clean 3D, illustration, etc.>
Composition/framing: <camera, crop, placement, scale, negative space>
Lighting/mood: <lighting direction, shadow behavior, atmosphere>
Color palette: <only confirmed or request-supported colors>
Materials/textures: <visible or customer-confirmed surface details>
Text (verbatim): "<exact short copy>"
Constraints: <must keep and edit invariants>
Avoid: <unsupported claims, extra brands, distortion, watermark, collage>
```

## Branch adaptations

### Quick generation

Use `product-mockup` for catalog/product scenes and `ads-marketing` for campaign
creative. When multiple results are requested, keep the business goal and product
identity fixed while varying one planned composition dimension per task.

### Phone photo retouch

Use `precise-object-edit` or `identity-preserve`. Image 1 is the only edit target
and controls its viewpoint, framing, visible parts, and object count. Later images
are cross-angle fact references only; never copy their viewpoint or reveal hidden
details in Image 1. List permitted corrections separately from invariants.
Permitted corrections may include exposure, white balance, lens and
perspective correction, noise, dust, controlled sharpening, background cleanup,
reflection control, and light refinement according to the approved retouch level.
Preserve geometry, proportions, colors, materials, logos, label copy, packaging,
ports, controls, accessories, item count, framing, and aspect ratio unless the
customer explicitly approves a named change. Never reconstruct an unreadable
label or hidden detail by guessing. Emphasize evidence-based material fidelity:
fine micro-texture, natural surface depth, controlled local contrast, coherent
highlight roll-off, realistic reflections, tactile edge definition, and authentic
matte, gloss, metal, glass, leather, fabric, wood, or coated-surface response.
Avoid waxy smoothing, plastic-looking materials, excessive denoising, crunchy
sharpening, halos, fake grain, invented texture, HDR glow, and clipped highlights.

### Main images and detail pages

Give each screen one communication goal. Repeat product-preservation constraints
in every prompt. Keep the set's palette, typography hierarchy, light direction,
product scale, and spacing logic coherent while varying composition.

### Custom batch

Apply `customer instruction > role definition > default ecommerce practice`.
Do not use the optimizer to override a customer-specified screen count, order,
copy, reference number, or visual direction.

### Exact replication

Use `style-transfer` or `compositing`. State that Image 1 supplies layout, camera,
lighting, spacing, and hierarchy while later images supply product identity.
Describe measurable relationships such as subject scale, margins, crop, and text
zones. Remove reference brands, product facts, claims, and copy unless the customer
explicitly asks to retain supplied text.

### Style variation

Extract a compact visual DNA from the references: palette, light behavior, camera,
materials, layout rhythm, typography hierarchy, negative space, and commercial
tone. Keep this DNA fixed across tasks while changing one primary composition
dimension per result. Do not reproduce the reference's brand, exact layout,
product facts, claims, or copy.

### Batch resize

Use `identity-preserve` or `precise-object-edit`. Preserve the source image's
subject, copy, logos, visible facts, and reading order while reflowing composition
for the target ratio. Extend plausible background or reposition elements as
needed. Do not stretch, add bars, duplicate objects, invent content, or crop
critical subjects and typography.

### SKU batch

Use `precise-object-edit` or `text-localization`. Image 1 is the current product and
Image 2 is the template. Preserve template layout and update only the product and
the exact mapped SKU fields for that task.

### Local region replacement

Use `precise-object-edit`, `identity-preserve`, or `compositing`. Image 1 is the
prepared crop. Specify matched perspective, scale, contact shadow, reflections,
edge lighting, depth of field, and color temperature. Change only the selected
region and preserve everything outside it.

## Customer validation gate

Before setting a task's prompt review to approved, show:

```text
Original request:
<verbatim customer input>

Optimized prompt:
<structured prompt>

Input-image mapping:
<Image 1 ... Image N>

Must remain unchanged:
<product and edit invariants>

Optimizer additions:
<brief list of details added because the original request was underspecified>

Please validate:
- Approve this prompt
- Request changes
- Use the original request instead
```

If the customer requests changes, revise one targeted aspect and show the gate
again. If the customer chooses the original request, normalize only image-role
references and safety constraints, then ask for approval again. Rejection or no
response leaves `prompt_review.status` as `pending` and blocks image generation.
On approval, record `status=approved`, an ISO 8601 UTC `reviewed_at` timestamp,
and `optimizer_version=gpt-image-2-ecommerce-v1`.
