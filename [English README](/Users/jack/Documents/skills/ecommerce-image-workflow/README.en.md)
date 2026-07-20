# Ecommerce Image Generation Workflow

[中文文档](README.md)

Developer: **QIYU-JACKMAN (启宇跨境)**

Ecommerce Image Generation Workflow is a Codex plugin for structured ecommerce image production. It combines product-fact analysis, reference-image analysis, prompt optimization, customer approval, image generation, per-image quality checks, selective retries, and resumable project records.

Install the plugin once and invoke `ecommerce-image-workflow` to select a workflow, or invoke any specialist Skill directly.

## Shared Workflow

Every image-producing branch follows the same production sequence:

```text
Select a workflow
-> Assign asset responsibilities
-> Lock product facts
-> Create the image task plan
-> Optimize each image prompt
-> Ask the customer to validate prompts
-> Present the complete generation plan
-> Ask the customer to approve the plan
-> Generate images
-> Inspect every result
-> Retry failed items only
-> Save project records
```

Product images determine product structure, color, logos, packaging, accessories, and visible details. Style references contribute composition, palette, lighting, materials, typography, and mood only. They do not provide product facts, specifications, brands, or selling points.

## Nine Workflows

### 1. Automatic Phone Photo Retouch

Use this workflow to turn ordinary smartphone product photos into clean, professional ecommerce images with realistic premium material rendering.

The Skill first asks the customer for one to five original photos showing different sides of the same product. Depending on the product, the most informative views may include front, back, left or right side, logos and labels, ports, functional details, or close-ups of material texture. All views establish shared facts about geometry, color, materials, logos, copy, and accessories; each original is then retouched as a separate image.

Three retouch levels are built in: natural correction, standard ecommerce retouch, and studio upgrade. Corrections cover exposure, white balance, perspective, noise, dust, background distractions, reflections, edges, and clarity, with special emphasis on authentic material quality, micro-texture, surface depth, gloss, and smooth highlight roll-off. The prompt distinguishes matte plastic, glossy plastic, brushed metal, polished metal, glass, leather, fabric, and wood while explicitly avoiding waxy smoothing, synthetic plastic appearance, invented texture, excessive denoising, crunchy sharpening, and HDR halos.

The current photo controls its composition and visible content. Other angles verify product facts only, preventing hidden back-side details from appearing incorrectly in a front view.

### 2. Quick Generate

Use this workflow when the customer already has a rough visual goal and wants 1-10 product images, scene images, or ad creatives quickly.

The customer may provide a prompt and up to five images in a single message. The Skill classifies every image as a product-fact image, style reference, or composition reference, then optimizes the request with the built-in prompt module. Each output is an independent task and generation starts only after prompt and full-plan approval.

### 3. Detail Pages and Main Images

Use this workflow for Amazon image sets, A+ Content, marketplace detail pages, independent-store product pages, and multi-screen selling-point sets.

Assets are collected in two stages. The first stage accepts product images only and analyzes visible facts, error-prone structures, supported selling points, and uncertainties. After the customer confirms the product analysis, the second stage requests optional style or composition references. The Skill then plans the communication goal and storyboard for every screen before optimizing, reviewing, and generating its prompt.

The default is five main images or six detail-page screens. A customer-specified count always takes priority.

### 4. Custom Batch

Use this workflow to turn a free-form brief, role definition, or brand direction into a coherent set of 1-20 images.

Built-in planning roles include ecommerce art director, furniture and interiors, consumer technology, cute collectibles, fashion and beauty, outdoor and sports, and food and lifestyle. Visual-style presets can be combined independently. The decision priority is:

```text
Explicit customer instructions > selected role and style > default ecommerce rules
```

Each screen has one primary communication goal and its own complete, reviewable prompt.

### 5. Exact Replication

Use this workflow to reproduce the composition, camera, lighting, subject scale, layout, and text hierarchy of one reference image while replacing the featured product with the customer's product.

The customer uploads one reference and up to four factual images of the same product directly in the conversation. No input folder is required. Image 1 is always the visual reference; later images establish product identity. Reference brands, specifications, claims, and original copy are excluded by default.

### 6. Style Variation

Use this workflow to extract a reference image's visual language and create 1-10 new compositions with a consistent style.

The customer uploads references and optional product images directly. The Skill extracts a visual DNA covering palette, lighting, camera, materials, layout, negative space, and commercial mood. Each result uses a clearly different composition while preserving the shared visual language without copying reference brands, product facts, or original copy.

### 7. Batch Resize

Use this workflow to adapt 1-20 source images to one or more target aspect ratios such as 1:1, 4:5, and 9:16.

This branch creates a prepared input folder. The customer places source images in `01-待处理原图/` and lists target ratios in `02-目标尺寸.txt`. The Skill scans supported images, applies natural sorting, detects duplicate content, and creates one task for every source-image and target-ratio pair. It preserves the subject, copy, and content while intelligently reflowing composition, extending backgrounds, or applying safe crops.

### 8. Batch SKU

Use this workflow to place 1-20 different SKUs into one shared template and update mapped names, models, sizes, specifications, or short copy.

This branch uses a prepared input folder containing SKU product images, exactly one template, and an optional `sku-mapping.csv`. Mapping uses the exact `product_file` filename and never relies on file order. In every task, Image 1 is the current product and Image 2 is the shared template. Only product identity and explicitly mapped text fields are replaced.

### 9. Local Region Replacement

Use this workflow to modify one local area of a scene, such as replacing a product, changing a worn item, or swapping a selected object while preserving the rest of the image.

The customer uploads exactly one scene image and up to four product images directly in the conversation. No input folder is required. The Skill calculates a square edit region from the request, creates a marked preview for customer confirmation, generates replacement content for the confirmed crop, and composites it back with a feathered mask. The final image retains the exact original dimensions.

## Asset Delivery

| Workflow | Input method |
| --- | --- |
| Automatic Phone Photo Retouch | Upload one to five original photos showing different sides of the same product |
| Quick Generate | Upload images and a prompt directly in the conversation |
| Detail Pages and Main Images | Upload product images first, then optional references after confirmation |
| Custom Batch | Confirm product and role direction before optional references |
| Exact Replication | Upload the reference and product images directly |
| Style Variation | Upload references and product images directly |
| Batch Resize | Use a prepared input folder |
| Batch SKU | Use a prepared input folder and optional CSV mapping |
| Local Region Replacement | Upload the scene and product images directly |

Only Batch Resize and Batch SKU use folder-based delivery. All other workflows accept assets directly in the conversation.

## Prompt Optimization and Approval

Every specialist Skill uses the built-in `gpt-image-2` ecommerce prompt optimizer. It preserves the customer's original intent and may add necessary composition, lighting, subject-scale, text-safe-area, and invariant details. It must not invent product specifications, certifications, performance claims, prices, rankings, or selling points.

Before generation, the customer sees:

- the original request;
- the optimized prompt;
- the responsibility of Image 1 through Image N;
- product facts that must remain unchanged;
- additions made by the optimizer;
- task count, per-image goal, aspect ratio, resolution, and output directory.

The customer may approve the prompt, request a targeted revision, or ask to stay closer to the original request. Unapproved tasks cannot enter real generation.

## Generation and Quality Control

The default model is `gpt-image-2`, the default quality is `high`, and the default resolution tier is `2K`. The workflow prefers Codex's built-in image generation capability and can use the local `codex-imagegen` CLI when needed.

Every generated image is checked for:

- correct product structure, color, logos, packaging, and accessories;
- accurate and readable text;
- leaked reference brands, unsupported claims, or extra products;
- compliance with the planned composition, aspect ratio, and negative space;
- visual consistency across an image set;
- unintended changes outside a confirmed local edit region.

One failed task does not block the rest of a batch. Retries regenerate failed items only and do not overwrite successful results by default.

## Project Records

Every production run is stored under:

```text
<workspace>/output/imagegen/<project-slug>/
|-- project.json
|-- plan.json
|-- manifest.json
|-- images/
`-- work/
```

- `project.json` records the workflow, asset roles, platform, language, and global parameters.
- `plan.json` records the customer-approved image tasks, prompts, and output mapping.
- `manifest.json` records generation status, output paths, sanitized errors, quality results, and retries.
- `images/` contains final deliverables.
- `work/` contains crops, previews, scan reports, and intermediate files.

Existing successful images are skipped by default. Overwriting an existing image requires explicit customer authorization.

## Security and License

The plugin never writes API keys, access tokens, or raw authorization headers to Skills, project files, logs, or error reports. Automated tests perform validation and dry runs only; they do not make paid image-generation requests.

Licensed under the MIT License.
