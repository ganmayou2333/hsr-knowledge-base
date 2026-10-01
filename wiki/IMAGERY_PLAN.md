# W-4.6-13 · SRR 素材图片接入方案（**只出方案，不实施**）

> 状态：草案，待用户拍板后实施。零复制、零改码、零提交。

## 1. 素材盘点（实测）

### `icon/` 子目录

| 子目录 | 文件数 | 体积 | 用途 |
|---|---|---|---|
| avatar | 297 | 7.51 MB | 角色头像（按角色ID.png） |
| light_cone | 165 | 4.84 MB | 光锥立绘缩略（按光锥ID.png） |
| character | 97 | 10.86 MB | 角色立绘大图 |
| relic | 244 | 6.00 MB | 遗器图标（套装ID.png + 部位ID_0~3.png） |
| item | 1,609 | 31.43 MB | 物品/材料图标（按物品ID.png） |
| skill | 1,451 | 19.46 MB | 技能图标 |
| curio | 84 | 1.77 MB | 模拟宇宙奇物 |
| sign | 203 | 0.87 MB | 角色星魂/命座图 |
| path | 32 | 0.56 MB | 命途图标（Abundance/Destruction/...，英文名） |
| element | 14 | 0.29 MB | 属性图标（Ice/Fire/...，英文名） |
| property | 28 | 0.08 MB | 属性词条图标 |
| block | 30 | 0.39 MB | 未知 |
| deco | 51 | 1.15 MB | 装饰 |
| logo | 6 | 0.91 MB | 官方 logo |
| **合计** | **4,311** | **~86 MB** | |

- `image/`：614 个文件（大幅大图，含角色立绘、活动 banner）
- `guide/`：不存在
- `.gitignore` 已排除全部 StarRailRes-* 克隆

### 图标覆盖率矩阵（实测）

| KB 类别 | KB 实体数 | SRR 图标数 | 覆盖率 | 缺口 | 处置 |
|---|---|---|---|---|---|
| 角色（小头像） | 118 | 297（SRR 总数） | 按需复制命中 | 4.6 新角色真珠无图标 | 占位降级 |
| 角色（立绘大图） | 118 | 97 | ~82% | 21 个旧角色无立绘 + 真珠 | 占位降级 |
| 光锥 | 205 | 165 | ~80% | 40 个（含 4.6 新光锥） | 占位降级 |
| 遗器（套装） | 65 | 60 | ~92% | 5 个（含 4.6 新遗器 133/134） | 占位降级 |
| 物品 | 3,876 | 1,609 | ~42% | 2,267 个旧物品无图标 | 占位降级 |

## 2. ID 映射规则表

| KB 类别 | 头部字段 | SRR 路径 | 文件命名 | 实测命中样例 | 缺失降级 |
|---|---|---|---|---|---|
| 角色 | `实体ID：1503` | `icon/avatar/<ID>.png` | 纯数字 | `icon/avatar/1001.png`（三月七） | 4.6 新角色真珠 1503 **暂无图标** |
| 光锥 | `实体ID：23055` | `icon/light_cone/<ID>.png` | 纯数字 | `icon/light_cone/20000.png` | 4.6 新光锥 23055 **暂无图标** |
| 遗器 | `实体ID：133` | `icon/relic/<ID>.png`（套装）/ `<ID>_0.png`~`<ID>_3.png`（部位） | 数字 + 部位后缀 | `icon/relic/101.png`、`icon/relic/101_0.png` | 4.6 新遗器 133/134 **暂无图标** |
| 物品 | `实体ID：110111` | `icon/item/<ID>.png` | 纯数字 | `icon/item/110111.png`（破碎残刃）✓ | 按 ID 直查 |
| 命途（索引页） | 命途名 | `icon/path/<命途英文名>.png` | 英文名 | `icon/path/Destruction.png` | 需命途中→英映射表 |
| 属性（索引页） | 属性名 | `icon/element/<属性英文名>.png` | 英文名 | `icon/element/Ice.png` | 需属性中→英映射表 |
| 奇物 | 实体ID | `icon/curio/<ID>.png` | 纯数字 | 待抽样 | 按 ID 直查 |

**4.6 新内容图标缺口**：真珠（1503）、献给明日的色彩（23055）、戏梦点星的伶人（133）、贪噬禁果的异端（134）在本地 SRR master 中**均无对应 PNG**——SRR 仓库尚未同步 4.6 资源。实施时这些条目走降级占位。

## 3. 候选方案对比

| 维度 | A · 图标子集入库 | B · CI 拉取 SRR | C · 外链 jsDelivr |
|---|---|---|---|
| 仓库体积增量 | ~15 MB（仅 avatar+light_cone+relic+item 子集，约 1.2k 文件） | 0 | 0 |
| Pages 可用性 | ✅ 本地文件 | ✅ Actions 浅克隆后复制 | ✅ CDN |
| 离线 file:// 预览 | ✅ | ❌（CI 路径不在本地） | ❌ |
| 版权风险 | ⚠️ 图标随仓库公开 | ⚠️ Actions 临时拉取，不入库但站点仍分发 | ⚠️ 第三方 CDN 分发米哈游素材 |
| 构建复杂度 | 低（复制文件） | 中（workflow 加浅克隆步骤） | 低（直接写 URL） |
| 4.6 新图标 | 需手动更新 | 自动（SRR 更新即拉到） | 自动 |
| 依赖外部网络 | 否 | 是（CI 需访问 GitHub） | 是（用户浏览器需访问 jsDelivr） |

### 推荐：**方案 B（CI 拉取）**

理由：
1. 仓库零体积增量，符合现有 `.gitignore`「版权素材不入库」的既定决策
2. SRR 更新后 CI 自动拿到最新图标，无需手动同步
3. 构建时把所需图标复制进 `wiki/assets/icons/`（生成物，gitignore），页面用相对路径引用
4. 缺点：本地 `file://` 预览时图标不显示（需本地跑 build 前先复制 SRR 图标——可在 build_wiki.py 里加一段：本地有 SRR 就复制，没有就跳过）

## 4. 模板（可落地但不实施）

### 4.1 生成器注入规则（伪代码）

```python
# build_wiki.py 渲染时，读头部 meta 里的"实体ID"
ENTITY_ICON_MAP = {
    "character": ("icon/avatar", "{id}.png"),
    "lightcone": ("icon/light_cone", "{id}.png"),
    "relic": ("icon/relic", "{id}.png"),
    "items": ("icon/item", "{id}.png"),
}

def inject_icon(meta, rel_path, depth):
    # rel_path 形如 "character/欢愉/真珠_冰_五星"
    if "实体ID" not in meta: return ""
    eid = meta["实体ID"]
    if eid.startswith("无"): return ""
    top = rel_path.split("/")[0]  # character / items / relic ...
    for kb_cat, (srr_dir, name_tpl) in ENTITY_ICON_MAP.items():
        if top.startswith(kb_cat):
            icon_path = f"assets/icons/{srr_dir}/{name_tpl.format(id=eid)}"
            return f'<img class="entity-icon" src="{up}{icon_path}" alt="{eid}" loading="lazy" width="96" height="96">'
    return ""
```

### 4.2 HTML 片段

```html
<!-- 角色详情页：头像卡 -->
<div class="entity-card">
  <img class="entity-icon" src="../../assets/icons/icon/avatar/1001.png" alt="三月七" loading="lazy" width="96" height="96">
  <h1>三月七</h1>
</div>

<!-- 索引页：图标行 -->
<div class="icon-row">
  <a href="..."><img src="..." alt="真珠" loading="lazy" width="48" height="48"><span>真珠</span></a>
  ...
</div>
```

### 4.3 CSS 片段

```css
.entity-icon {
  border-radius: 12px;
  background: var(--card-bg);
  object-fit: cover;
}
.icon-row {
  display: flex; flex-wrap: wrap; gap: 12px;
}
.icon-row a {
  display: flex; flex-direction: column; align-items: center;
  text-decoration: none; width: 72px;
}
.icon-row img { width: 48px; height: 48px; }
/* 宽高占位由 HTML 属性 width/height 提供，防 CLS 抖动 */
```

### 4.4 缺图降级

```python
# 找不到图标时不写 <img>，改占位符
fallback = f'<div class="icon-fallback" style="width:96px;height:96px;border-radius:12px;background:#444;">?</div>'
```

### 4.5 alt 文本规则

- 角色：`alt="<角色名>"`
- 物品：`alt="<物品名>"`
- 遗器：`alt="<套装名>套装图标"`
- 命途/属性：`alt="<命途中文名>命途"`
- **禁止** alt 留空或写 "icon"

## 5. 版权与体积风险评估 + 待拍板项

### 版权风险
- SRR 是第三方米哈游素材仓库，图标版权归米哈游
- 无论 A/B/C 哪个方案，**公网 Pages 站点都会分发这些图标**
- `.gitignore` 现有注释写明「含版权素材，不入库」——方案 B 虽然不入库，但站点公开后等效分发
- **需用户确认**：是否接受在公开 GitHub Pages 上展示游戏图标（合理使用范围内的攻略站通常如此，但需用户知情）

### 体积风险
- 方案 B：CI 临时拉取 SRR（约 200MB+），构建后丢弃，不入库
- 本地产物：复制约 1,200 个图标到 `wiki/assets/icons/`（约 15MB），gitignore 不发布

### 待用户拍板项
1. **选哪个方案**（A 入库子集 / B CI 拉取 / C 外链 CDN）？
2. **版权是否接受**：公开 Pages 上展示游戏图标？
3. **4.6 新内容无图标**（真珠/23055/133/134）：接受占位符，还是等 SRR 同步后再补？
4. **是否要大图**（`icon/character/` 10.86MB 角色立绘），还是仅小图标？

---

> 本文件为方案草案，用户拍板前不实施。
