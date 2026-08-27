# SRR 全量图包 · 来源说明

> 本文件记录 StarRailRes 图包（icon / image / font）的获取来源与目录结构，供知识库引用图片时溯源。

---

## 一、图包概览

| 属性 | 值 |
|---|---|
| 数据源 | [StarRailRes](https://github.com/Mar-7th/StarRailRes)（Mar-7th 维护的《崩坏：星穹铁道》开放数据仓库） |
| 数据版本 | v4.5.0 |
| 提交 | `f1b6436` ✨ Update to version 4.5 |
| 本地路径 | `G:\HSR\StarRailRes_repo\`（sparse-checkout：index_new/cn + icon + image + font） |
| 获取时间 | 2026-08-27 |
| 总占用 | **约 974 MB**（icon 86 MB + image 861 MB + font 26 MB） |

---

## 二、目录结构与统计

### icon/（4,311 个，86.1 MB）— 小图标

| 子目录 | 数量 | 对应数据 |
|---|---|---|
| `icon/avatar/` | 297 | 头像图鉴（avatars.json） |
| `icon/block/` | 30 | 模拟宇宙区块（simulated_blocks.json） |
| `icon/character/` | 97 | 角色头像/图标（characters.json `icon`） |
| `icon/curio/` | 84 | 模拟宇宙奇物（simulated_curios.json） |
| `icon/deco/` | 51 | 摆件/装饰 |
| `icon/element/` | 14 | 属性图标（elements.json） |
| `icon/item/` | 1,609 | 物品图标（items.json `icon`，如 `icon/item/900001.png`） |
| `icon/light_cone/` | 165 | 光锥图标（light_cones.json `icon`） |
| `icon/logo/` | 6 | 平台/游戏 Logo |
| `icon/path/` | 32 | 命途图标（paths.json） |
| `icon/property/` | 28 | 属性参数图标（properties.json） |
| `icon/relic/` | 244 | 遗器图标（relics.json `icon`，含各部位） |
| `icon/sign/` | 203 | 符号/标记 |
| `icon/skill/` | 1,451 | 技能/星魂图标（character_skills.json / character_ranks.json） |

### image/（614 个，861.4 MB）— 高清大图

| 子目录 | 数量 | 对应数据 |
|---|---|---|
| `image/character_portrait/` | 97 | 角色立绘（高清） |
| `image/character_preview/` | 95 | 角色立绘（预览） |
| `image/light_cone_portrait/` | 166 | 光锥图（高清） |
| `image/light_cone_preview/` | 165 | 光锥图（预览） |
| `image/simulated_event/` | 91 | 模拟宇宙事件图 |

### font/（14 个，26.4 MB）— 游戏字体

`RPG_CN.ttf` / `RPG_JP.ttf` / `RPG_KR.ttf` 等 14 个字体文件（中/日/韩/泰/越南语等）。

---

## 三、图标路径 ↔ 数据字段对应

图标路径直接存储在 `index_new/cn/*.json` 的 `icon` 字段中，引用方式：

```
items.json         → icon: "icon/item/900001.png"   （星琼）
characters.json    → icon: "icon/character/xxx.png"
light_cones.json   → icon: "icon/light_cone/xxx.png"
relics.json        → icon: "icon/relic/xxx.png"
character_ranks.json → icon: "icon/skill/xxx.png"   （星魂）
character_skills.json → icon: "icon/skill/xxx.png"
avatars.json       → icon: "icon/avatar/xxx.png"
```

## 四、知识库引用方式（Obsidian）

图包位于 vault 外（`G:\HSR\StarRailRes_repo\`），如需在 md 中引用，两种方式：

1. **复制到 vault 内**：将需要的图标复制到 `G:\HSR\`（vault 根）下的 `assets/` 目录，再以 `![[xxx.png]]` 引用。
2. **相对路径引用**：`![物品图标](../../StarRailRes_repo/icon/item/xxx.png)`。

> 建议：日常引用图标只需 `icon/` 目录（86 MB）；`image/` 大图仅在需要高清立绘时使用；`font/` 一般不用于知识库。

---

*生成时间：2026-08-27*
