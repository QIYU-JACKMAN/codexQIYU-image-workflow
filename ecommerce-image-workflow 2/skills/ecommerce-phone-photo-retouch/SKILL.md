---
name: ecommerce-phone-photo-retouch
description: >-
  引导用户上传同一商品不同面的 1-5 张普通手机照片，综合锁定商品事实后逐张自动精修，重点改善真实材质质感、光泽、微纹理、边缘、曝光、白平衡、透视、噪点、灰尘、背景和反光。用户提到手机拍摄商品图精修、随手拍变电商图、自动修商品照片、提升产品质感或影棚级优化时使用。创建新场景、复刻参考图、只改局部区域或批量改画幅时不要使用本技能。
---

# 手机商品照片自动精修

保持内联执行，不使用子代理，不创建素材投递文件夹。

## 素材引导

先请用户直接在对话中上传同一商品不同面的 1-5 张手机照片。根据商品特点优先选择正面、背面、左右侧面、顶部/底部、Logo/标签、接口或功能细节、材质纹理、包装与配件中最有信息量的角度。商品结构简单时不强求凑齐五张；已有照片不重复索取。

要求尽量使用原图，不要先加滤镜、截图或压缩。不同 SKU 不要混在同一批；多个 SKU 转到批量 SKU 或分项目处理。

## 自动诊断

先综合所有角度建立一份商品事实表，再逐张检查曝光、动态范围、白平衡、偏色、透视、水平线、镜头畸变、噪点、压缩痕迹、对焦清晰度、灰尘污点、背景干扰、阴影、反光、材质表现和裁切空间。把问题分为：可安全修复、需要生成式重建、无法从照片确认。

同时登记不可改动的商品事实：外形与比例、部件位置、颜色、材质、表面纹理、光泽类型、Logo、标签文字、包装、接口、按钮、配件数量和任何不对称细节。看不清的事实标记为不确定，不猜测或补造。

材质诊断必须区分并描述真实的光学表现，例如：哑光塑料的细腻漫反射、亮面塑料的受控高光、拉丝金属的方向性纹理、抛光金属的干净反射、玻璃的透光与边缘高光、皮革或织物的细微纹理、木材的自然纹路。只使用照片可见或用户确认的材质事实。

## 精修强度

根据照片问题推荐一档并让用户确认；用户未指定时推荐“标准电商精修”。

1. `natural` 自然修复：只修曝光、色温、噪点、轻微透视、灰尘和清晰度，保留真实拍摄环境与自然质感。
2. `ecommerce` 标准电商精修：在自然修复基础上整理背景、优化光影层次和商品边缘，使画面达到干净专业的电商成片水平，但不更换场景或重设计商品。
3. `studio` 影棚升级：重建为可信的商业影棚光线和干净背景，同时保持原构图意图和全部商品事实。若用户要求新场景或营销创意，转到快捷生成。

默认保持原始画幅、主体位置、可见文字和商品数量。裁切、移除道具、更换背景颜色、删除阴影或大幅改变构图必须单独列出并获得确认。

## 计划与确认

1. 定位插件根目录，读取公共项目 schema、`gpt-image-2-prompt-optimizer.md` 和质检规则。
2. 先展示逐图诊断、商品事实、不确定项和推荐精修强度，请用户确认或调整。
3. 创建 `phone-photo-retouch` 项目，每张输入照片登记为一个 `product` asset，并严格创建一个对应任务。每个任务中 Image 1 是当前待精修照片；其余角度按确认顺序作为商品结构、颜色、材质、Logo 和文字核验参考，不提供当前画面的构图或可见内容。
4. 把用户要求和确认后的诊断保存为 `original_request`。使用下方内置精修提示词模块生成 `precise-object-edit` 或 `identity-preserve` 提示词，分别写明允许修改项和不可修改项。
5. 展示每张图的原需求、优化提示词、Image 1 映射、修复清单和不变量，请用户批准或提出单点修改。未批准任务保持 `pending`。
6. 所有启用任务提示词批准后，展示任务数、逐图精修目标、强度、画幅、分辨率、输出名和目录，等待完整计划确认。
7. 用户明确确认完整计划后才设置 `plan.approved=true` 并生成。优先使用 Codex 内置图片能力，否则调用公共 `run_plan.py`。

## 质检与重做

逐张对比原图，检查商品几何结构、颜色、Logo、标签文字、配件数量和原始画幅是否保持；同时检查曝光、白平衡、透视、噪点、边缘、背景、反光和清晰度是否改善。任何商品事实漂移都判定为失败。

只对失败图片重做，并把失败原因改写为一个针对性的修正要求。不得覆盖原始手机照片；最终结果和 QA 记录保存到标准项目目录。

## 内置质感精修提示词

根据每张照片的实际诊断删减空项，不机械堆砌。把 `<...>` 替换为已确认内容：

```text
Use case: precise-object-edit
Asset type: ecommerce product photo retouch
Primary request: Retouch Image 1 into a clean, premium, photorealistic ecommerce product photograph while preserving the exact product identity and the original photographic intent.
Input images: Image 1 is the only edit target and controls the current view, pose, framing, visible parts, and object count. Images 2-N are cross-angle fact references only for verifying geometry, color, material, surface texture, logos, labels, ports, controls, packaging, and accessories; do not copy their viewpoint or reveal details that are hidden in Image 1.
Corrections: <approved exposure, white balance, perspective, lens distortion, noise, dust, background, reflection, edge, and sharpness corrections>.
Material fidelity: Render physically believable premium material response based only on confirmed evidence. Preserve the product's real base color and material category. Recover fine micro-texture, clean edge definition, subtle tonal separation, natural surface depth, and controlled local contrast. Keep matte surfaces softly diffused without waxy smoothing; glossy surfaces with clean, shaped highlights without blown glare; brushed metal with fine directional grain; polished metal with coherent reflections; glass with realistic transmission and crisp edge highlights; leather, fabric, wood, and coated surfaces with their authentic small-scale texture. Make the product feel tactile, substantial, and professionally photographed, never synthetic or overprocessed.
Lighting: Refine into soft commercial studio-quality light with coherent direction, smooth highlight roll-off, readable shadow detail, natural contact shadow, and dimensional separation. Control harsh phone-flash hotspots and color casts without flattening the object or inventing new reflections.
Detail and sharpness: Improve perceived clarity through restrained micro-contrast and edge acuity. Preserve natural antialiasing and texture variation. Do not hallucinate unreadable text, hidden components, new seams, grain, scratches, embossing, or decorative details.
Background: <preserve and clean the existing environment | simplify to a clean neutral ecommerce background | approved background treatment>. Keep realistic grounding and edge integration.
Constraints: Preserve exact geometry, proportions, silhouette, viewpoint, crop, aspect ratio, product count, part placement, colors, materials, logos, label spelling, packaging, ports, controls, accessories, asymmetry, and all confirmed product facts. Change only the approved photographic defects and background treatment.
Avoid: product redesign, geometry drift, color shift, fake texture, plastic-looking smoothing, excessive denoising, crunchy oversharpening, halos, HDR glow, clipped highlights, crushed shadows, floating product, invented text, invented features, extra objects, watermark, collage, or changing details outside the approved corrections.
```
