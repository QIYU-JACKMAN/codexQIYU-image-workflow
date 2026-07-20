---
name: ecommerce-image-workflow
description: >-
  电商图片工作流总入口。用户说要做电商图、商品图、手机照片精修、主图、详情页套图、复刻、裂变、批量改尺寸、批量 SKU 或局部替换，但尚未直接调用某个专业分支时使用。启动后必须先展示九种工作流供用户选择，再路由到对应专业 skill；不要在总入口直接规划或生成图片。
---

# 电商图片工作流

这是内联路由入口。不要设置 `context: fork`，也不要启动子代理。

## 固定开场

无论用户描述是否看起来已经明确，调用本入口时都先显示下面九项并等待选择：

```text
这次要做哪一种电商图？
1. 手机照片精修：上传商品不同面的手机照片，自动诊断并精修质感
2. 快捷生成：提示词或少量参考图，快速生成 1-10 张
3. 一键详情/主图：商品分析后规划一整套主图或详情页
4. 自定分批：按角色定位和自由指令拆成 1-20 屏
5. 一比一复刻：参考图和商品图直接上传，严格复刻构图版式
6. 风格裂变：提取参考图视觉语言，生成不同构图的新版本
7. 批量改尺寸：用素材文件夹批量适配一个或多个目标画幅
8. 批量 SKU：用素材文件夹让多个商品套用同一个模板
9. 局部迁移：直接上传场景图，确认选框后只修改局部区域
```

不要把提示词优化、素材库、历史记录或保存目录列成额外工作流；它们是九条流程的共用能力。视频不在范围内。

## 路由

用户选择后，加载插件内对应的专业 skill，并把用户已经给出的目标、素材和参数原样传递：

- 1 → `ecommerce-image-workflow:ecommerce-phone-photo-retouch`
- 2 → `ecommerce-image-workflow:ecommerce-quick-generate`
- 3 → `ecommerce-image-workflow:ecommerce-detail-main-images`
- 4 → `ecommerce-image-workflow:ecommerce-custom-batch`
- 5 → `ecommerce-image-workflow:ecommerce-exact-replication`
- 6 → `ecommerce-image-workflow:ecommerce-style-variation`
- 7 → `ecommerce-image-workflow:ecommerce-batch-resize`
- 8 → `ecommerce-image-workflow:ecommerce-batch-sku`
- 9 → `ecommerce-image-workflow:ecommerce-local-region-replacement`

如果用户直接调用某个专业 skill，该 skill 自行开始，不再返回本菜单。
