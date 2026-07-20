# 电商生图工作流

[English documentation](README.en.md)

英文名称：**Ecommerce Image Generation Workflow**  
开发者：**启宇跨境**
跨境毒蛇说-JACKMAN
亚马逊官方合作讲师
亚马逊多年卖家
AI+电商融合落地顾问
V+AMZdudu888

电商生图工作流是一套运行在 Codex 中的电商图片生产插件。它把商品事实分析、参考图拆解、提示词优化、客户确认、图片生成、逐图质检、失败项重做和项目记录组织成一套可重复执行的流程。

安装一次插件后，可以调用总入口 `ecommerce-image-workflow` 选择工作流，也可以直接调用对应的专业 Skill。

## 总体流程

所有需要生成图片的分支遵循同一条主流程：

```text
选择工作流
→ 登记素材职责
→ 锁定商品事实
→ 创建图片任务计划
→ 优化逐图提示词
→ 客户校验提示词
→ 展示完整生成计划
→ 客户确认计划
→ 生成图片
→ 逐张质检
→ 只重做失败项
→ 保存项目记录
```

商品图负责确定商品结构、颜色、Logo、包装、配件和可见细节。风格参考图只负责构图、配色、光线、材质、排版和氛围，不提供商品事实、参数、品牌或卖点。

## 九种工作流

### 1. 手机照片自动精修

适合把普通手机拍摄的商品照片自动精修成质感真实、干净专业的电商成片。

Skill 会先提示用户上传同一商品不同面的 1-5 张原始照片，根据商品特点选择正面、背面、左右侧面、Logo/标签、接口、功能细节或材质纹理等信息量最大的角度。所有角度共同用于锁定商品结构、颜色、材质、Logo、文字和配件事实，然后按原图逐张精修。

内置自然修复、标准电商精修和影棚升级三档强度。精修重点包括曝光、白平衡、透视、噪点、灰尘、背景、反光、边缘与清晰度，并特别恢复真实的材质质感、微纹理、表面深度、光泽和高光过渡。它会区分哑光塑料、亮面塑料、拉丝金属、抛光金属、玻璃、皮革、织物和木材等材料响应，禁止磨皮塑料感、虚构纹理、过度降噪、过度锐化和 HDR 光晕。

每张照片独立生成一个精修结果。当前照片控制构图和可见内容，其他角度只负责核验商品事实，不会把背面细节错误画到正面。

### 2. 快捷生成

适合已经知道大致画面目标，希望快速生成 1-10 张商品图、场景图或广告图的任务。

用户可以在一条消息中直接提供提示词和最多 5 张图片。Skill 先判断每张图片是商品事实图、风格参考图还是构图参考图，再基于内置模板优化用户提示词。每个结果都是一个独立任务，用户确认提示词和完整计划后才开始生成。

### 3. 一键详情与主图

适合 Amazon 主图、A+ 页面、淘宝详情页、独立站详情页和多屏卖点套图。

素材分两阶段收集。第一阶段只接收商品图，分析商品事实、易画错结构、可证明卖点和不确定信息，并请用户确认。商品分析确认后，第二阶段才询问是否提供风格或构图参考图。随后先规划每一屏的沟通目标和分镜，再逐屏优化提示词、确认并生成。

默认主图组为 5 屏，详情页为 6 屏；用户指定数量时以用户要求为准。

### 4. 自定分批

适合根据一段自由要求、角色定位或品牌方向规划 1-20 屏连贯套图。

Skill 内置电商视觉总监、家具家居、3C 科技、萌物潮玩、时尚美妆、户外运动和食品生活方式等规划角色，并提供可组合的视觉风格预设。执行优先级固定为：

```text
用户明确指令 > 用户选择的角色与风格 > 默认电商规则
```

每一屏只承担一个主要沟通目标，并拥有独立、完整、可校验的提示词。

### 5. 一比一复刻

适合参照一张图片复刻其构图、镜头、光影、主体比例、版式和文字层级，同时替换成用户自己的商品。

用户直接在对话中上传 1 张参考图和最多 4 张同一商品的事实图，不需要素材文件夹。固定映射中，Image 1 是参考图，后续图片提供商品身份。参考图中的品牌、商品参数、卖点和原文案默认不会继承。

### 6. 风格裂变

适合提取参考图的视觉语言，并生成 1-10 个风格一致、构图不同的新版本。

用户直接上传参考图和可选商品图。Skill 提取配色、光线、镜头、材质、排版、留白和商业氛围等视觉 DNA，然后为每个结果规划一个明显不同的构图方向。风格保持统一，但不会复制参考品牌、商品事实或原文案。

### 7. 批量改尺寸

适合将 1-20 张原图统一适配到一个或多个目标画幅，例如 1:1、4:5 和 9:16。

该分支先创建预制素材文件夹。用户一次性把待处理图片放入 `01-待处理原图/`，并在 `02-目标尺寸.txt` 中填写目标画幅。Skill 自动扫描图片、自然排序、检查重复文件，并按“每张原图 × 每个目标画幅”创建任务。生成时保持主体、文字和内容不变，只进行智能重排、背景扩展或安全裁切。

### 8. 批量 SKU

适合让 1-20 个不同 SKU 共用同一个商品模板，并替换对应的名称、型号、尺寸、规格或短文案。

该分支使用预制素材文件夹。用户一次性放入 SKU 商品图、正好 1 张模板图，以及可选的 `sku-mapping.csv`。映射表通过 `product_file` 与商品文件名精确匹配，不依赖文件顺序。每个任务中 Image 1 是当前商品，Image 2 是统一模板；只替换商品身份和明确指定的文字字段。

### 9. 局部迁移

适合只修改场景图中的一个局部区域，例如局部换产品、佩戴替换或替换指定物体，同时保持原图其他区域不变。

用户直接在对话中上传 1 张场景图和最多 4 张商品图，不需要素材文件夹。Skill 根据自然语言定位方形编辑区域，先生成带选框预览供用户确认。区域确认后裁取局部、生成替换内容，并使用羽化遮罩合成回原图。最终图片宽高与原场景图完全一致。

## 素材交付方式

| 工作流 | 素材提交方式 |
| --- | --- |
| 手机照片自动精修 | 对话中上传同一商品不同面的 1-5 张原始照片 |
| 快捷生成 | 对话中直接上传图片和提示词 |
| 一键详情与主图 | 先上传商品图，确认后再上传可选参考图 |
| 自定分批 | 先确认商品和角色方向，再提供可选参考图 |
| 一比一复刻 | 对话中直接上传参考图和商品图 |
| 风格裂变 | 对话中直接上传参考图和商品图 |
| 批量改尺寸 | 使用预制素材文件夹 |
| 批量 SKU | 使用预制素材文件夹和可选 CSV |
| 局部迁移 | 对话中直接上传场景图和商品图 |

只有批量改尺寸和批量 SKU 使用文件夹批处理。其他工作流都通过对话直接交付素材。

## 提示词优化与确认

每个专业 Skill 都使用内置的 `gpt-image-2` 电商提示词优化模块。优化器会保留客户原始需求，补充必要的构图、光线、主体比例、文字安全区和不可改动项，但不会虚构商品参数、认证、性能、价格、排名或卖点。

出图前会展示：

- 用户原始需求；
- 优化后的完整提示词；
- Image 1 到 Image N 的职责映射；
- 必须保持不变的商品事实；
- 优化器新增的内容；
- 任务数、逐图目标、画幅、分辨率和输出目录。

用户可以批准提示词、要求单点修改，或要求尽量保留原始提示词。未批准的任务不会进入真实生成。

## 生成与质检

默认模型为 `gpt-image-2`，默认质量为 `high`，默认分辨率档位为 `2K`。工作流优先使用 Codex 内置图片能力；需要 CLI 执行时使用本机 `codex-imagegen`。

每张图片生成后独立检查：

- 商品结构、颜色、Logo、包装和配件是否准确；
- 文字是否拼写正确、清晰可读；
- 是否出现参考品牌、错误参数或额外商品；
- 构图、画幅和留白是否符合计划；
- 套图之间是否保持统一的视觉语言；
- 局部修改是否影响了选区外内容。

单个任务失败不会阻塞整批任务。重做时只处理失败图片，不重复覆盖已经成功的结果。

## 项目记录

每次正式工作保存到：

```text
<workspace>/output/imagegen/<project-slug>/
├── project.json
├── plan.json
├── manifest.json
├── images/
└── work/
```

- `project.json`：工作流、素材职责、平台、语言和全局参数。
- `plan.json`：客户确认后的独立图片任务、提示词和输出映射。
- `manifest.json`：生成状态、输出路径、错误摘要、质检结果和重画记录。
- `images/`：最终交付图片。
- `work/`：裁区、预览、扫描报告和其他中间文件。

已经存在且成功的图片默认跳过。覆盖旧文件必须得到用户明确授权。

## 安全与许可

插件不会把 API Key、访问令牌或授权头写入 Skill、项目文件、日志或错误报告。自动测试只执行校验和 dry-run，不会产生付费图片。

本项目使用 MIT License。

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

