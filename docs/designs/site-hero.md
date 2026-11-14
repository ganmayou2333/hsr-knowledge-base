# 设计文档 · 站点视觉重构（R1）+ 角色 hero 动画（R2）

| 项 | 值 |
|---|---|
| 环节 | Architect（设计） |
| slug | `site-hero` |
| 输入规格 | Lead 工单 R1 / R2（本文 §0 复核了全部仓库事实） |
| 产物 | 本文件（唯一写盘产物；**未修改任何仓库文件**） |
| 下游 | Coder（按 §1–§3 实现）→ Tester（按 §5 验收）→ Reviewer（按 §5 + 冻结面复核） |
| 关键词 | 锐角切角 / 细描边 / 冷色高光 / 数据感排版 / 一次性 hero / 零禁用项 |

---

## 0. 现状事实（全部实测，带 位置）

> 规则：本节每条都能在仓库里点到行；下游不得凭记忆改写。

| # | 事实 | 位置 |
|---|---|---|
| F1 | 生成器 642 行，页面模板集中在 `main()` 尾部的一个 f-string 里 | `wiki/build_wiki.py:549-570` |
| F2 | **首页 `wiki/index.html` 不由生成器产出**（build_wiki.py 中 `index.html` 只出现在两处超链接里，无写出逻辑） | `wiki/build_wiki.py:81`、`:524`；首页实为手写 `wiki/index.html:1-63` |
| F3 | 角色面板 = 服务端静态渲染：`section.cpanel` + 3 组 `button.chip` + `ul.cgrid > li.citem` | `wiki/build_wiki.py:404-455` |
| F4 | 卡片 DOM：`<li class="citem" data-path data-element data-rarity><a class="ccard" href aria-label><img class="cicon">/<div class="icon-fallback cicon-fb">` + 3 个 `span`（`.cname`/`.csub`/`.cstar`） | `wiki/build_wiki.py:437-443`；缺图分支 `:436` |
| F5 | 面板页 head 内 `<noscript><style>.cp-filters{display:none}</style></noscript>`，body 内 `<noscript><p class="cp-noscript">` | `wiki/build_wiki.py:546`、`:454` |
| F6 | 面板页只多引一个脚本：`character-panel.js`（`defer`），且 `theme.js` 在它之前 | `wiki/build_wiki.py:568-569` |
| F7 | 筛选脚本 68 行，只改 `li.hidden`（`.hidden` 属性）+ 计数，**不重排 DOM、不建节点** | `wiki/assets/character-panel.js:26-40`，`:36` |
| F8 | 样式 306 行；token 在 `:1-13`；全局 `:focus-visible` 在 `:94`；动效纪律段 `:184-233`；面板段 `:262-306` | `wiki/assets/style.css` |
| F9 | 全站 reduced-motion 已有两道保险：`:80-82` 与 `:115` 两处 `*{animation:none!important;transition:none!important}`；动效主体又各自包在 `@media (prefers-reduced-motion: no-preference)` 内（`:189`、`:194`、`:222`） | `wiki/assets/style.css` |
| F10 | 主题开关写 `documentElement` 的 `data-theme`，键名 `hsr-theme` | `wiki/assets/theme.js:3`、`:6-9` |
| F11 | 校验器 731 行；`[5]` 扫描目标 = `index.html` + `style.css` + 目录里所有生成页（**不含 `assets/*.js`**） | `tools/verify_site.py:187`、`:704` |
| F12 | `[5]` 六项正则：radius 白名单值、shadow、gradient、img（`assets/icons/` 例外）、外链 script、外链 link。**对原文整段做正则，不剥注释** | `tools/verify_site.py:190-212`；白名单 `:55` |
| F13 | 角色总索引页：`class="citem"` 94 个；`class="cicon` 90 个；`icon-fallback` 4 个 | `wiki/pages/character/角色.html`（实测 grep） |
| F14 | 图标资产：`assets/icons/avatar/{id}.png` 实际 128×128（≈28 KB，90 个）；`assets/icons/character/{id}.png` 实际 256×256（≈103 KB，90 个）；两者 **id 集合完全相同** | 实测 `struct` 读 PNG 头 + `ls \| wc -l` |
| F15 | 无图的 4 张卡（1511/1503/1513/1512）：`avatar` 与 `character` 两个目录**都没有**该 id 的文件 → 只能走剪影降级 | 实测 `[ -f ]` 逐个检查 |
| F16 | 94 张卡的 `href` **末段都是 `数字.html`**（100% 可解析出实体 id） | 实测 `grep class="ccard" href` |
| F17 | 详情页图标由 `inject_icon` 产出；`ICON_CONF` 里角色声明 `96×96` 与 `200×280` 两种，与 F14 的真实像素不一致（既有偏差，不在本次范围） | `wiki/build_wiki.py:222-228`、`:248-249` |
| F18 | 首页仪表盘 DOM 与脚本引用是硬校验对象 | `wiki/index.html:11-29`、`:51-55`；校验 `tools/verify_site.py:498-505` |
| F19 | 生成页总数 6685（`pages/**/*.html`），`titles.js` 条数同为 6685 | 实测（`rglob` + `json.loads`） |

### 0.1 「冻结面」——任何重构都不得改动的字符串

> 这是本文最重要的表。`[5]` 只禁止 6 类 CSS/资源；真正卡住重构的是**校验器对类名字面量的精确匹配**。视觉重构若「顺手给卡片加个类」会直接打挂 6 条断言。

| 冻结项 | 冻结原因（校验器位置） | 对设计的含义 |
|---|---|---|
| `class="citem"` 必须字面如此 | `re.findall(r'class="citem"', page)` 计数须 == 条目数 | **不能**给 `li` 加修饰类（`class="citem citem--hero"` 会漏计）；装饰只能走 `::before/::after` 或运行时加类 |
| `<a class="ccard" href="` 前缀必须字面如此 | `tools/verify_site.py:649` 同一正则取 href 查存在性 | 不能给 `a` 加类；`aria-label` 可保留/微调（不参与匹配） |
| `icon-fallback` 出现次数 ≥ 缺图条目数 | `tools/verify_site.py:675-679` | 缺图分支的类名不能改名 |
| 页面所有 `<img>` 的 `src` 必须含 `assets/icons/` | `tools/verify_site.py:681-687`（`[5]` 同规则 `:201-206`） | 不得引入任何非图标 `<img>`；装饰图只能用 CSS/SVG |
| head 内 `<noscript><style>` 内容必须精确匹配 | `tools/verify_site.py:663-667`（正则尾部紧跟 `</style></noscript>`） | **不能**往这个 style 块追加任何规则（hero 的无 JS 样式必须走 `style.css`） |
| `<noscript>` 后紧跟 `<p class="cp-noscript">`（中间无 `<`） | `tools/verify_site.py:665` | 不能插装饰元素 |
| `<nav class="crumbs">` + `</a> / ` + 文本以「首页 / 」开头 | `tools/verify_site.py:108-118` | 面包屑不能加类、不能改分隔符 |
| `@media(max-width:640px){ … .sidenav{max-height` 的**字面相邻** | `tools/verify_site.py:357-358`（`[^}]*\.sidenav\{max-height`） | 重排小屏段时**不能**把 `.sidenav{` 写成 `.sidenav {` |
| `@media print{}` 块内必须有 `display:none` | `tools/verify_site.py:371-391` | 打印段可重排，但必须保留 display:none |
| theme.js 必须含 `matchMedia` / `max-width:640px` / `.sidenav details` | `tools/verify_site.py:354-356` | 不改 theme.js |
| 首页 `id="dash-root\|dash-version\|dash-pages\|dash-updated\|dash-recent"`、`class="quick"`、`class="quick-a"`（≥2）、`dash-empty`、`<script src="assets/home.js"`、`<script src="data/stats.js"` | `tools/verify_site.py:498-505` | 首页可视化只改 CSS + 可加**不含上述字面量**的新节点；`quick`/`quick-a` 不能加类 |
| `#search` 的 `aria-label="搜索页面标题"`、`role="combobox"`、`aria-controls="results"`；`#results` 的 `role="listbox"` | `tools/verify_site.py:335-347`、`:236-244` | 搜索框只可改样式 |
| `class="tl-item"` 出现次数 == 时间线单元数；`id="timeline-root"` 恰 1 页且在 `<div class="prose` 之前 | `tools/verify_site.py:424-452` | 时间线不加类、不加包装层 |
| `<table>` 之后紧跟 `<thead>` | `tools/verify_site.py:318-327` | 表格不能包裹新容器 |
| `<h1>` 文本 == `<title>` 去后缀 | `tools/verify_site.py:75-103` | 标题文案不动 |

---

## 1. 设计 token

全部以 CSS 变量表达，**追加**到 `wiki/assets/style.css` 末尾（新段），不改 `:1-13` 既有 token（`--bg/--paper/--ink/--muted/--line/--soft/--accent/--dead`）——既有 token 被 `[11][12]`、打印段与 306 行既有规则广泛引用，替换成本高于收益。

### 1.1 颜色（暗 / 亮两套，共 12 个语义槽）

| 变量 | 暗（默认 / 系统暗） | 亮（系统亮 / `data-theme=light`） | 用途 |
|---|---|---|---|
| `--ui-bg` | `#06080C` | `#F1F3F7` | 页面底 |
| `--ui-panel` | `#0C1117` | `#FFFFFF` | 面板/卡片实底 |
| `--ui-panel-2` | `#121926` | `#E7EBF2` | 次级面板、表头 |
| `--ui-surface` | `rgba(255,255,255,.045)` | `rgba(10,13,19,.045)` | **半透明层叠**（替代阴影的唯一手段） |
| `--ui-surface-2` | `rgba(255,255,255,.085)` | `rgba(10,13,19,.085)` | hover / 选中衬底 |
| `--ui-line` | `#232B38` | `#C9D1DC` | 主描边 1px |
| `--ui-line-2` | `#48576B` | `#8A94A3` | 强描边（hover/焦点） |
| `--ui-ink` | `#E6ECF5` | `#0E1319` | 正文 |
| `--ui-ink-2` | `#B4BFD0` | `#3A4453` | 次级正文 |
| `--ui-mute` | `#7C8798` | `#6B7484` | 元信息/标签（对 `--ui-panel` ≥ 4.5:1） |
| `--ui-hi` | `#6FE3FF` | `#0A6E8C` | **冷色高光**（选中、角标、数据强调） |
| `--ui-hi-2` | `#1E4C60` | `#A9DCEE` | 高光弱化层（衬底、扫光） |
| `--ui-warn` / `--ui-danger` | `#FFC24B` / `#FF5D5D` | `#8A5A00` / `#B3121F` | 降级提示 / 死链（沿用既有 `--dead` 语义） |

**决定 D-1：不动 `--accent`（红）与 `--dead`（红）。** 红色继续只表示「可点链接/死链」，新引入的青 `--ui-hi` 专表示「当前选中/高光」。理由：`--accent` 被 `style.css:32,50,52,58,64,91,94,114,151,156,165,204-211,277,296` 等大量规则引用；改色等于同时改 20+ 处语义，且 `[4]` 死链色与打印段联动。**风险降到「只增不改」。**

两套主题的挂载方式复用既有机制：`:root{…}`（暗默认）+ `@media (prefers-color-scheme: light)` + `:root[data-theme="light"]` / `:root[data-theme="dark"]`，与 `style.css:5-13` 同构，保证 `theme.js:6-9` 的三态切换零改动。

### 1.2 几何

| 变量 | 值 | 说明 |
|---|---|---|
| `--ui-cut-sm` | `6px` | chip、按钮角 |
| `--ui-cut` | `8px` | 卡片、提示块 |
| `--ui-cut-lg` | `20px` | hero 主框、首页统计块 |
| `--ui-hair` | `1px` | 常规描边 |
| `--ui-hair-2` | `2px` | 选中/高光描边 |
| `--ui-bracket` | `12px` | L 形角标臂长 |
| `--sp-1…--sp-8` | `4,8,12,16,24,32,48,64px` | 8px 栅格（既有 `style.css:141` 注释已声明 8px 栅格） |
| `--ui-frame` | `1px` | 切角框线宽（见 §1.5 技巧 T-2） |

**切角形状（两个对角切，HSR 味最足且不影响文本包围盒）：**

```css
/* 规格片段：切角多边形（上左 + 下右） */
--cut-hex: polygon(
  var(--ui-cut) 0,
  100% 0,
  100% calc(100% - var(--ui-cut)),
  calc(100% - var(--ui-cut)) 100%,
  0 100%,
  0 var(--ui-cut)
);
/* 小角标用 L 形（左上） */
--cut-bracket-tl: polygon(0 0, 100% 0, 100% var(--ui-hair-2),
  var(--ui-hair-2) var(--ui-hair-2), var(--ui-hair-2) 100%, 0 100%);
```

### 1.3 字号阶（在既有 h1/h2/h3 之上补「数据感」小字阶）

| 变量 | 值 | 用途 |
|---|---|---|
| `--fs-micro` | `11px` | 角标标签、表格序号 |
| `--fs-0` | `12px` | `.csub`/`.cstar`/标签 |
| `--fs-1` | `13px` | 元信息、面包屑 |
| `--fs-2` | `14px` | 表格、列表 |
| `--fs-3` | `16px` | 正文（与 `body` 一致，`style.css:25`） |
| `--fs-4` | `19px` | h3 附近 |
| `--fs-5` | `26px` | h2 |
| `--fs-6` | `40px` | h1 |
| `--ui-track` | `.08em` | 大写小字的字距（数据感） |
| `--ui-num` | `"Helvetica Neue",Helvetica,Arial,sans-serif` + `font-variant-numeric:tabular-nums` | 数字等宽（沿用 `style.css:42`） |

### 1.4 动效

| 变量 | 值 | 用途 |
|---|---|---|
| `--t-0` | `0ms` | reduced-motion 精确值 |
| `--t-1` | `120ms` | 按下反馈（沿用 `style.css:214` 的 `.12s`） |
| `--t-2` | `200ms` | 边框/颜色 |
| `--t-3` | `280ms` | hover、链接下划线（沿用 `style.css:207` 的 `.28s`） |
| `--t-4` | `480ms` | 面板入场 |
| `--t-5` | `700ms` | 既有 `riseIn`（`style.css:111`） |
| `--ease` | `cubic-bezier(.32,.72,0,1)` | 全站主缓动（与既有 `style.css:102,111,149,170,199,207,214` 一致） |
| `--ease-out` | `cubic-bezier(.16,1,.3,1)` | 元素落位（hero 用） |
| `--ease-in` | `cubic-bezier(.4,0,1,1)` | 退场 |
| `--hero-total` | `840ms` | hero 总时长（**唯一可调旋钮**，见 §3.2） |
| `--hero-stagger` | `40ms` | hero 数据条错峰 |

### 1.5 六项禁用项 → 替代技法对照（核心）

> 约束来源 `tools/verify_site.py:190-212`；口径：**六项必须保持 0**，不放宽。

| 禁用项 | 校验正则 | 我们改用什么 | 关键技术 |
|---|---|---|---|
| `border-radius` 非 0 | `:190-194`，值必须在白名单（`:55`） | 直角 + `clip-path` 切角；圆点用 `border-radius:0` + `clip-path:circle(50%)` 或 4px 方块 | **T-1 切角** |
| `box-shadow` | `:195-197`（**连注释里的字面量都会命中**） | ① 1px 双层描边（外层实色 + 内层 1px 内缩实底）② `--ui-surface` 半透明叠层 ③ 角标高光 | **T-2 假框** |
| `linear-gradient`（含 `repeating-`） | `:198-200` | ① 网格/斜线纹理 → **SVG data URI**（`background-image:url("data:image/svg+xml;…")`）② 扫光 → 一个 `background:var(--ui-hi-2)` 的窄条，用 `transform:translateX()` 扫过 ③ 层次 → `rgba()` 纯色叠加 | **T-3 纹理** |
| 非图标 `<img>` | `:201-206`（`assets/icons/` 例外放行） | 装饰图形一律 CSS 伪元素 / 内联 SVG（含 data URI）；`<img>` 仅用于角色图标（`assets/icons/avatar\|character/`） | **T-4 图标唯一性** |
| 外链脚本 | `:207-209` | 只写同源相对路径；hero 的 `<img>` 由 JS 创建且 `src` 含 `assets/icons/` | — |
| 外链样式 | `:210-212` | 不引 CDN/外链字体；字体沿用 `style.css:22` 的系统栈 | — |

**技法 T-2「假框」——在没有阴影、没有圆角的前提下做出描边切角面板：**

```css
/* 规格片段：双伪元素假框（不裁剪交互元素本身） */
.cardlike{ position:relative; isolation:isolate; background:transparent; border:0 }
.cardlike::before{                    /* 外层 = 边框色，被切角 */
  content:""; position:absolute; inset:0; z-index:-1;
  background:var(--ui-line); clip-path:var(--cut-hex);
  transition:background-color var(--t-3) var(--ease);
}
.cardlike::after{                     /* 内层 = 面板色，向内缩 --ui-frame，同形状裁剪 = 1px 框 */
  content:""; position:absolute; inset:var(--ui-frame); z-index:-1;
  background:var(--ui-panel); clip-path:var(--cut-hex);
}
```

**技法 T-3「纹理」——网格/斜纹只准用 SVG data URI：**

```css
/* 规格片段：24px 网格（暗色版；亮色版把 %23FFFFFF 换 %23000000） */
--ui-grid: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'><path d='M24 0H0V24' fill='none' stroke='%23FFFFFF' stroke-opacity='0.06'/></svg>");
.panel-grid{ background-image:var(--ui-grid); background-repeat:repeat }
```

> ⚠️ **注释纪律（H-1）**：`[5]` 对整段原文做正则、不剥注释。所以新写/改写的 CSS 与 JS 里，注释中**不得出现** `box-shadow`、`linear-gradient` 字面量；写「`border-radius`」时冒号后必须是白名单值（`0`），否则 `:190-194` 会把它当命中。既有 `style.css:185` 已按此纪律写作「不引 shadow / gradient / radius」。

---

## 2. 组件规格

> 每个组件给：现状 DOM（不改）→ 关键 CSS 声明 → `[5]` 合规说明。
> 通用规则 **R-1：交互元素（`a`/`button`/`input`）本身不做 `clip-path`**，切角一律由 `::before/::after` 装饰层表达。原因：`clip-path` 会连带裁掉 `outline`，而全局焦点圈依赖 `outline`（`style.css:14-16,52,94`），裁掉即违反键盘可达。

### 2.1 站点头部 `.topbar`

- **DOM（不改）** `wiki/build_wiki.py:554`：`<div class="topbar"><button id="theme-toggle" class="theme-toggle" type="button">跟随系统</button></div>`；首页同构 `wiki/index.html:6`。
- **关键 CSS**

```css
.topbar{ position:sticky; top:0; z-index:20; display:flex; justify-content:flex-end;
  margin:0 0 var(--sp-5); padding:var(--sp-2) 0; background:var(--ui-bg);
  border-bottom:var(--ui-hair) solid var(--ui-line) }
.topbar::before{ content:""; position:absolute; left:0; right:0; bottom:calc(-1 * var(--ui-hair));
  height:var(--ui-hair-2); background:var(--ui-hi); opacity:.55; transform:scaleX(0);
  transform-origin:left; transition:transform var(--t-4) var(--ease) }
.topbar:hover::before{ transform:scaleX(1) }
.theme-toggle{ padding:6px 12px; border:var(--ui-hair) solid var(--ui-line); background:transparent;
  color:var(--ui-ink); clip-path:none }         /* R-1：按钮不裁剪，焦点圈完整 */
.theme-toggle:hover{ border-color:var(--ui-line-2); background:var(--ui-surface) }
.theme-toggle:focus-visible{ outline:var(--ui-hair-2) solid var(--ui-hi); outline-offset:2px }
```

- **`[5]` 说明**：只有 sticky/边框/透明度/transform；青色横线用 `background:var(--ui-hi)` 纯色 + `scaleX` 生长，未用任何 gradient；无阴影、无圆角。`[12]` 打印段继续隐藏 `.topbar`（`style.css:132`），sticky 不影响打印。

### 2.2 侧边导航 `.sidenav`

- **DOM（不改）** `wiki/build_wiki.py:73-83`：`nav.sidenav > details[open] > summary + ul`，`li.cur` 表示当前类。
- **关键 CSS**

```css
.sidenav{ position:relative; margin:0 0 var(--sp-5); padding:var(--sp-3) var(--sp-4);
  border:var(--ui-hair) solid var(--ui-line); background:var(--ui-surface) }
.sidenav summary{ cursor:pointer; font-size:var(--fs-1); font-weight:700; letter-spacing:var(--ui-track) }
.sidenav summary::before{ content:""; display:inline-block; width:6px; height:6px; margin-right:8px;
  background:var(--ui-hi); clip-path:polygon(0 0,100% 50%,0 100%); vertical-align:middle }
details[open] > summary::before{ clip-path:polygon(0 0,100% 0,50% 100%) }  /* 展开=下三角 */
.sidenav li.cur a{ border-left:0; padding-left:var(--sp-2); margin-left:calc(-1 * var(--sp-3));
  background:var(--ui-surface-2); position:relative }
.sidenav li.cur a::before{ content:""; position:absolute; inset:0 auto 0 0; width:var(--ui-hair-2);
  background:var(--ui-hi) }
```

- **`[5]` 说明**：三角用 `clip-path` 多边形，不引图标文件、不引字体；高亮用 2px 纯色块。
- **⚠️ 冻结（`[11]`）**：`tools/verify_site.py:357-358` 要求小屏段内**字面存在** `.sidenav{max-height`。改写 `style.css:129` 时保持 `.sidenav{` 紧跟左花括号，不得写成 `.sidenav {`。

### 2.3 面包屑 `.crumbs`

- **DOM（不改）** `wiki/build_wiki.py:524-526`；冻结正则 `tools/verify_site.py:108-118`。
- **关键 CSS**

```css
.crumbs{ font-size:var(--fs-1); color:var(--ui-mute); margin-bottom:var(--sp-5);
  padding-bottom:var(--sp-2); border-bottom:var(--ui-hair) solid var(--ui-line);
  letter-spacing:.02em }
.crumbs a:hover::after{ height:2px; background:var(--ui-hi) }  /* 覆盖 :204-207 的 1px 红线为 2px 青线 */
.crumbs > strong{ color:var(--ui-ink); font-weight:700 }
.crumbs > span{ color:var(--ui-ink-2) }
```

- **`[5]` 说明**：只改颜色/字号/线宽。**不得**改分隔符 `" / "`、不得给 `<nav>` 加类。

### 2.4 正文容器 `.prose` + 区块标题

- **DOM（不改）** `wiki/build_wiki.py:561-563`；`style.css:109` 已有 `max-width:72ch`。
- **关键 CSS**

```css
.prose{ max-width:72ch; position:relative; counter-reset:sec }
.prose h2{ counter-increment:sec; position:relative; padding-left:var(--sp-5);
  border-left:0; font-size:var(--fs-5); letter-spacing:.01em }
.prose h2::before{ content:counter(sec,decimal-leading-zero); position:absolute; left:0; top:.15em;
  font-size:var(--fs-micro); color:var(--ui-hi); font-variant-numeric:tabular-nums }
.prose h2::after{ content:""; position:absolute; left:0; right:0; bottom:-6px; height:var(--ui-hair);
  background:var(--ui-line) }
```

- **`[5]` 说明**：计数器 + 伪元素，无图片。注意 `h2` 用 `counter` 会自动编号（**纯 CSS，无 JS，无 JS 也有编号**）。
- **风险提示**：编号会出现在打印与 PDF 里；若用户不接受编号，删掉 `::before` 即可，无其它耦合。

### 2.5 表格

- **DOM（不改，冻结 `[9]`）** `style.css:39-42`,`:118`；校验 `<table>` 紧跟 `<thead>`（`tools/verify_site.py:318-327`）。
- **关键 CSS**

```css
table{ border-collapse:collapse; width:100%; margin:var(--sp-5) 0; font-size:var(--fs-2);
  font-variant-numeric:tabular-nums }
th,td{ border:var(--ui-hair) solid var(--ui-line); padding:10px 12px; vertical-align:top }
thead th{ background:var(--ui-panel-2); font-weight:700; letter-spacing:.02em;
  position:sticky; top:0; z-index:1 }        /* 覆盖 :118，改底色 */
thead th::after{ content:""; position:absolute; left:0; right:0; bottom:-1px;
  height:var(--ui-hair-2); background:var(--ui-hi) }   /* 表头下 2px 青色数据线 */
tbody tr:hover td{ background:var(--ui-surface) }
td:first-child{ color:var(--ui-ink-2) }
```

- **`[5]` 说明**：`border-radius` 无（裁剪风险在 `[5]` 里没有，但**表格绝不能上 `clip-path`**——`position:sticky` 的表头在裁剪容器里会失效）。所谓「数据线」是 2px 纯色块。

### 2.6 提示块（`blockquote` / `.dead-banner` / `.missing-note` / `.meta` / `.cp-noscript`）

- **DOM（不改）** `style.css:44,55,65,127,298`。
- **关键 CSS**

```css
blockquote{ border-left:var(--ui-hair-2) solid var(--ui-hi); margin:var(--sp-5) 0;
  padding:var(--sp-2) var(--sp-4); background:var(--ui-surface); color:var(--ui-ink-2); position:relative }
blockquote::before{ content:""; position:absolute; left:0; top:0; width:var(--ui-bracket); height:var(--ui-bracket);
  background:var(--ui-hi); clip-path:var(--cut-bracket-tl) }
.dead-banner{ border:var(--ui-hair) solid var(--ui-danger); color:var(--ui-danger);
  background:var(--ui-surface); padding:var(--sp-2) var(--sp-4) }
.missing-note{ border:var(--ui-hair) solid var(--ui-line); color:var(--ui-mute); padding:0 4px; margin-left:.35em }
.meta{ background:var(--ui-surface); border:var(--ui-hair) solid var(--ui-line); color:var(--ui-mute);
  font-size:var(--fs-1); padding:var(--sp-3) }
```

- **`[5]` 说明**：L 形角标是 `clip-path` 裁的实色方块，不是图片；无阴影。危险色沿用 `--ui-danger`（与 `--dead` 同调，保持"红=问题"语义）。

### 2.7 卡片（角色 / 光锥 / 遗器 / 物品通用）`.ccard`

- **DOM（冻结，不改）** `wiki/build_wiki.py:437-443`。子元素顺序 `img.cicon`(或 `div.icon-fallback.cicon-fb`) + `span.cname` + `span.csub` + `span.cstar`。
- **关键 CSS（切角框 + 角标 + hover 位移，全部走伪元素）**

```css
.cgrid{ --cell-min:132px; display:grid; grid-template-columns:repeat(auto-fill,minmax(var(--cell-min),1fr));
  gap:var(--sp-3) }
.citem{ margin:0; padding:0 }
.citem[hidden]{ display:none }                       /* 必须保留：character-panel.js:36 用隐藏属性 */
.ccard{ position:relative; isolation:isolate; display:block; padding:10px;
  color:inherit; text-decoration:none; border:0; background:transparent;
  transition:transform var(--t-3) var(--ease) }
.ccard::before{ content:""; position:absolute; inset:0; z-index:-1; background:var(--ui-line);
  clip-path:var(--cut-hex); transition:background-color var(--t-3) var(--ease) }
.ccard::after{ content:""; position:absolute; inset:1px; z-index:-1; background:var(--ui-panel);
  clip-path:var(--cut-hex) }
.ccard:hover{ transform:translateY(-2px) }
.ccard:hover::before{ background:var(--ui-hi) }
.ccard:focus-visible{ outline:var(--ui-hair-2) solid var(--ui-hi); outline-offset:2px } /* R-1：不裁剪 a 本身 */
.cicon{ display:block; width:100%; max-width:128px; height:auto; aspect-ratio:1; margin:0 auto 8px;
  background:transparent; object-fit:contain }
.cicon-fb{ width:100%; max-width:128px; aspect-ratio:1; margin:0 auto 8px; background:var(--ui-surface);
  border:var(--ui-hair) dashed var(--ui-line); border-radius:0 }
.cname{ font-size:var(--fs-2); font-weight:700; letter-spacing:.02em }
.csub{ font-size:var(--fs-0); color:var(--ui-mute) }
.cstar{ font-size:var(--fs-0); color:var(--ui-hi); font-variant-numeric:tabular-nums }
```

- **`[5]` 说明**：切角框 = 双伪元素纯色裁剪（T-2），零阴影零渐变；`<img>` 仍是 `assets/icons/` 图标（`[15]:681-687` 与 `[5]:201-206` 都放行）。
- **放大级约束**：`avatar` 实际 128×128（F14），故 `.cicon` **CSS 尺寸上限 128px**；要更大只能换 `character/{id}.png`（256×256），否则放大即模糊。
- **冻结提醒**：`class="citem"` / `<a class="ccard" href="` 不能加类（§0.1）；`.citem[hidden]` 必须继续存在。

### 2.8 角色面板（chips + 网格）

- **DOM（不改）** `wiki/build_wiki.py:404-455`；筛选逻辑 `character-panel.js:26-67`。
- **关键 CSS**

```css
.cpanel{ position:relative; margin:0 0 var(--sp-6); padding:0 0 var(--sp-4);
  border-bottom:var(--ui-hair) solid var(--ui-line) }
.cp-h2{ font-size:var(--fs-5) }
.cp-meta{ font-size:var(--fs-1); color:var(--ui-mute) }
.cp-meta b{ color:var(--ui-hi); font-variant-numeric:tabular-nums }
.cp-row{ gap:var(--sp-2) }
.cp-label{ font-size:var(--fs-micro); color:var(--ui-mute); letter-spacing:var(--ui-track);
  text-transform:none; min-width:2.4em }
.chip{ position:relative; isolation:isolate; font:inherit; font-size:var(--fs-1);
  padding:6px 12px; border:0; background:transparent; color:var(--ui-ink); cursor:pointer;
  transition:color var(--t-2) var(--ease) }
.chip::before{ content:""; position:absolute; inset:0; z-index:-1; background:var(--ui-line);
  clip-path:polygon(var(--ui-cut-sm) 0,100% 0,100% calc(100% - var(--ui-cut-sm)),
    calc(100% - var(--ui-cut-sm)) 100%,0 100%,0 var(--ui-cut-sm)) }
.chip::after{ content:""; position:absolute; inset:1px; z-index:-1; background:var(--ui-surface);
  clip-path:polygon(var(--ui-cut-sm) 0,100% 0,100% calc(100% - var(--ui-cut-sm)),
    calc(100% - var(--ui-cut-sm)) 100%,0 100%,0 var(--ui-cut-sm)) }
.chip:hover::before{ background:var(--ui-line-2) }
.chip[aria-pressed="true"]{ color:var(--ui-hi); font-weight:700 }
.chip[aria-pressed="true"]::before{ background:var(--ui-hi) }        /* 选中=青描边（决定 D-1） */
.chip[aria-pressed="true"]::after{ background:var(--ui-surface-2) }
.chip:focus-visible{ outline:var(--ui-hair-2) solid var(--ui-hi); outline-offset:2px }
.cp-count{ font-variant-numeric:tabular-nums; color:var(--ui-mute) }
```

- **`[5]` 说明**：chip 用 6px 切角 + 1px 假框；`aria-pressed` 状态由既有 JS 维护（`character-panel.js:47-51`），CSS 只读该属性，**不改 JS 的筛选逻辑**。
- **注意**：`.chip` 的 `border` 归零后，`style.css:273-277` 里基于 border 的 hover 需整段替换为新规则（同一选择器块内替换，不新增同名覆盖，避免 specificity 混乱）。

### 2.9 首页仪表盘 `.dash`

- **DOM（冻结 `[14]`）** `wiki/index.html:11-29`；校验 `tools/verify_site.py:498-505`。
- **关键 CSS**

```css
.dash{ position:relative; margin:0 0 var(--sp-6); padding:0 0 var(--sp-4);
  border-bottom:var(--ui-hair) solid var(--ui-line) }
.dash-meta{ display:flex; flex-wrap:wrap; gap:var(--sp-2) var(--sp-6) }
.dash-cell{ position:relative; padding:var(--sp-2) var(--sp-3); isolation:isolate; font-size:var(--fs-1);
  color:var(--ui-mute) }
.dash-cell::before{ content:""; position:absolute; inset:0; z-index:-1; background:var(--ui-line);
  clip-path:polygon(0 0,100% 0,100% calc(100% - var(--ui-cut-sm)),calc(100% - var(--ui-cut-sm)) 100%,0 100%) }
.dash-cell::after{ content:""; position:absolute; inset:1px; z-index:-1; background:var(--ui-panel-2);
  clip-path:polygon(0 0,100% 0,100% calc(100% - var(--ui-cut-sm)),calc(100% - var(--ui-cut-sm)) 100%,0 100%) }
.dash-cell b{ color:var(--ui-hi); font-size:var(--fs-3); font-variant-numeric:tabular-nums }
.quick-a{ position:relative; isolation:isolate; display:inline-block; padding:8px 16px;
  color:var(--ui-ink); font-size:var(--fs-2) }
.quick-a::before{ content:""; position:absolute; inset:0; z-index:-1; background:var(--ui-line); clip-path:var(--cut-hex) }
.quick-a::after{ content:""; position:absolute; inset:1px; z-index:-1; background:var(--ui-surface); clip-path:var(--cut-hex) }
.quick-a:hover::before{ background:var(--ui-hi) }
.dash-item{ border-bottom:var(--ui-hair) solid var(--ui-line) }
.dash-item:hover{ background:var(--ui-surface) }
```

- **`[5]` 说明**：统计块 = 单角切角（更"仪表"）+ 假框；`class="quick"`/`class="quick-a"` 字面量不动（`[14]:501`）。
- **首页是否允许新增节点？** α 方案**不改 index.html**（F2：首页是手写文件，但改它仍属「改仓库文件」，方案 α 定义为「零 HTML 改动」）。装饰全部由伪元素提供，首页因此拿到与内页一致的视觉。

---

## 3. hero 动画规格（R2）

### 3.1 状态机

```
                 ┌──────── guard 失败（修饰键/新标签/storage 不可用/reduced-motion）────────┐
                 │                                            → 原生跳转（无副作用）      │
IDLE ──click/Enter──▶ ENTER ──120ms──▶ HERO ──720ms──▶ NAVIGATE ──▶ (新页面)
  │                    │                 │
  │                    │                 ├─ Esc / 点 overlay / 再点同一卡 → NAVIGATE（跳过）
  │                    └─ 异常 → EXIT（140ms 退场 + 移除 overlay + 放行原生跳转）
  └─ reduced-motion ──▶ STATIC（静态高亮，0ms 延迟）──▶ NAVIGATE（不写 sessionStorage）
```

状态定义（`data-state` 属性用于自检与调试）：

| 状态 | 进入条件 | 退出条件 | 页面可见效果 |
|---|---|---|---|
| `idle` | 初始 / 从 bfcache 恢复后 | 命中一张 `.ccard` | 无 overlay |
| `enter` | 全部 guard 通过 | `--t-1`（120ms）后 | 背板淡入 + 竖线生长 |
| `hero` | `enter` 结束 | 总时长到 / 用户跳过 | 图标、名字、数据条、扫光 |
| `static` | `prefers-reduced-motion:reduce` | 立即 | 卡片描边变青（无动画） |
| `exit` | 动画中途异常 | 140ms 后 | 淡出并移除 |

**为什么要有 `static` 独立状态**：`style.css:80-82`、`:115` 已经全局 `animation:none!important`，任何依赖 `@keyframes` 的「静态高亮」都不会被看到。所以 reduced-motion 路径**连 overlay 都不插**，只给卡片加一个无过渡的描边色（`transition:none`），随后同任务内 `location.assign`。诚实结论：浏览器通常来不及绘制这一帧，**该高亮是 best-effort，不作验收承诺**（§5 只验收「无 overlay、无动画、立即跳转」）。

### 3.2 时序表（T0 = 卡片 click/Enter）

| 区间 (ms) | 元素 | 属性 | 起 → 止 | 缓动 | 备注 |
|---|---|---|---|---|---|
| 0 | `.hero-overlay` | 插入 `body`、去掉 `hidden`、写 `data-state="enter"` | — | — | 只有这步成功才 `preventDefault()` |
| 0–120 | `.hero-overlay` | `opacity` | `0 → 1` | `--ease` | 背板 |
| 0–120 | `.hero-overlay` | `clip-path: inset(0 0 100% 0)` | `inset(0)` | `--ease` | 从下往上"拉开"，纯裁剪 |
| 40–160 | `.hero-spine`（竖线） | `transform: scaleY()` / `transform-origin:top` | `0 → 1` | `--ease` | 数据轴 |
| 120–360 | `.hero-art` | `transform: scale(.86) translateY(8px)` → `scale(1) translateY(0)` | + `opacity 0→1` | `--ease-out` | **两层图**：先显已缓存的 128px avatar，256px character art 加载完再换上 |
| 160–400 | `.hero-frame`（切角框） | `clip-path` 四角 bracket 的 `opacity` 0→1，四个角各延迟 `--hero-stagger` | — | `--ease` | 用 4 个伪/子元素 |
| 260–420 | `.hero-name` | `clip-path: inset(0 100% 0 0)` → `inset(0)` | — | `--ease` | 擦除式入场（无 JS 逐字定时器） |
| 320–560 | `.hero-stat`×3 | `transform: translateX(-10px)` → `0`，`opacity 0→1`，逐个 +40ms | — | `--ease-out` | 属性 / 命途 / 星级 |
| 560–720 | `.hero-sweep` | `transform: translateX(-110%)` → `110%`，`opacity .0→.55→0` | — | `--ease-in` | 冷光扫过（纯色条，**不是** gradient） |
| 720–840 | `.hero-frame` | `transform: scale(1.02)` 背板 + 竖线 `translateY(0)` | — | `--ease` | 收束 |
| **840** | — | `location.assign(href)` | — | — | 或 `--hero-total` |

**时长取舍**：840ms 是「够看一个动作 + 不让人觉得卡」的折中；`@media (prefers-reduced-motion: no-preference)` 外的一切（无 JS、reduced、打印）都不参与。若用户觉得慢，只改 `--hero-total` 一个变量（JS 读 `getComputedStyle` 的该值，CSS 是唯一真相源，避免两处硬编码）。

### 3.3 DOM 结构与无障碍

```html
<!-- 规格片段：overlay 由 hero.js 运行时创建，仅存在于播放期间 -->
<div class="hero-overlay" data-state="hero" aria-hidden="true">
  <div class="hero-stage">
    <span class="hero-frame"></span>            <!-- 切角假框（::before/::after 亦可） -->
    <span class="hero-spine" ></span>           <!-- 竖向数据轴 -->
    <div class="hero-art-wrap">
      <img class="hero-art" src="../../assets/icons/character/1014.png" alt="">
      <span class="hero-art-fb" hidden></span>  <!-- SVG data URI 剪影：error 时替换 -->
    </div>
    <p class="hero-name">Saber</p>
    <ul class="hero-stats">
      <li class="hero-stat"><span class="hero-k">属性</span><b>风</b></li>
      <li class="hero-stat"><span class="hero-k">命途</span><b>毁灭</b></li>
      <li class="hero-stat"><span class="hero-k">星级</span><b>五星</b></li>
    </ul>
    <span class="hero-sweep"></span>
    <p class="hero-hint">Esc / 点击 跳过</p>
  </div>
  <p class="hero-status sr-only" role="status" aria-live="polite"></p>
</div>
```

```css
/* 规格片段：overlay 容器（不锁滚动、不裁交互元素） */
.hero-overlay{ position:fixed; inset:0; z-index:90; contain:layout paint;
  background:var(--ui-bg); /* 实底，不用半透明以掩盖下方内容 */
  background-image:var(--ui-grid); background-repeat:repeat;
  display:grid; place-items:center; cursor:pointer }
.hero-overlay[hidden]{ display:none }
.hero-stage{ position:relative; display:grid; place-items:center; gap:var(--sp-3);
  padding:var(--sp-6) var(--sp-5); text-align:center }
.hero-art-wrap{ position:relative; width:min(256px, 60vmin); aspect-ratio:1; isolation:isolate }
.hero-art{ width:100%; height:100%; object-fit:contain; display:block }
.hero-name{ margin:0; font-size:clamp(22px,5vw,34px); font-weight:700; letter-spacing:.06em;
  color:var(--ui-ink) }
.hero-stats{ display:flex; gap:var(--sp-3); list-style:none; margin:0; padding:0 }
.hero-stat{ position:relative; isolation:isolate; padding:6px 12px; font-size:var(--fs-1);
  font-variant-numeric:tabular-nums; color:var(--ui-ink) }
.hero-k{ color:var(--ui-mute); margin-right:6px; font-size:var(--fs-micro) }
.hero-sweep{ position:absolute; inset:0 auto 0 0; width:38%; background:var(--ui-hi); opacity:0;
  pointer-events:none; mix-blend-mode:screen }
.sr-only{ position:absolute; width:1px; height:1px; margin:-1px; padding:0; overflow:hidden;
  clip-path:inset(50%); white-space:nowrap; border:0 }
```

**无障碍决定（D-2：不移动焦点）**

| 项 | 规格 | 理由 |
|---|---|---|
| 焦点 | 全程留在被点击的 `a.ccard` 上，**不** `focus()` 到 overlay | 移动焦点 + 视觉遮挡 = 键盘用户"我在哪"；不移动则 Tab 顺序不变，且 overlay 生命周期 <1s |
| overlay 语义 | `aria-hidden="true"`，不加 `role="dialog"`/`aria-modal` | 它不是对话框，只是一次性过场；加 modal 语义会诱发"必须能 Tab 出"的期望 |
| 播报 | 一次 `role="status" aria-live="polite"` 文本 `正在打开 <角色名>` | 不影响关键路径；SR 不播也无害 |
| Esc | `document` 捕获阶段监听，`state==='hero'` 时 → 立即 `location.assign(href)` | 「跳过」而非「取消」：用户点击意图明确，取消会让人困惑 |
| 点击 overlay | 同上（跳过 → 跳转） | 幂等 |
| 修饰键 | `metaKey/ctrlKey/shiftKey/altKey` 或 `button!==0` → **完全放行**，`preventDefault` 不调用 | 「新标签打开」等原生能力优先 |
| 滚动锁 | **不加** `body{overflow:hidden}` | 加锁 → 滚动条消失 → 全站横向抖动（`--ui-bg` 宽度变化），风险大于收益 |
| `tabindex` | overlay 内元素一律无 `tabindex` | 保持 Tab 顺序 = 页面原有顺序 |

### 3.4 `sessionStorage` 规格

| 项 | 规格 |
|---|---|
| 键名 | `hsr-hero-v1`（命名空间前缀 `hsr-` 与 `theme.js:3` 的 `hsr-theme` 同族，避免碰撞；`v1` 便于日后废弃） |
| 值 | JSON 字符串数组，元素是实体 id 字符串：`["1014","1404"]` |
| 读 | `try{ var a = JSON.parse(sessionStorage.getItem(K) \|\| "[]"); }catch(e){ a = null }`；`a===null` → 视为 **storage 不可用** |
| 判定 | `a.indexOf(id) >= 0` → 不播（直接原生跳转，不拦截） |
| 写 | **在 `enter` 状态写入（不是动画结束写）**：先 `a.push(id)` 再 `setItem`。中途跳走/返回都不会重播 |
| 容错 | 写入包 `try/catch`（Safari 隐私模式抛异常）；长度 > 300 时重置为 `[id]`（94 个角色远达不到，防脏数据撑爆） |
| storage 不可用 | **退化为「不播动画」**（视为已看）——保守选择：可预测优先，隐私模式下不该每次点击都放动画 |
| 会话语义 | `sessionStorage` 是 **per-tab**，新标签页会各播一次；这是浏览器语义，写进验收口径（§5 A9） |
| reduced-motion 路径 | **不写** storage（没播就不记账，保持语义真实） |
| id 来源 | 见 §3.7 |

### 3.5 交互矩阵

| 场景 | 行为 |
|---|---|
| 首次点击有图角色 | 播完整 840ms → 跳转 |
| 首次点击缺图角色（F15 的 4 个） | 播同动画，`.hero-art` 的 `error` → 换 `hero-art-fb`（SVG 剪影），其余一致 |
| 再次点击同一角色 | 不插 overlay，原生跳转（storage 命中） |
| 首次点击 A，返回后再点 B | B 播一次（A 已记账，互不影响） |
| 动画中再点同一卡 / 点别处 | `state!=='idle'` → 视为「跳过」→ 立即跳转（`navigateOnce` 幂等，重复调用只跳一次） |
| 键盘 Enter（焦点在卡片） | 与点击同路径（`click` 事件 `detail===0`），播完整动画；Esc 可跳过 |
| Shift/Cmd/Ctrl+点击、中键 | 完全不拦截（无 `preventDefault`） |
| 从详情页「返回」 | page 从 bfcache 恢复 → `pageshow`（`event.persisted`）里移除残留 overlay、`state=idle`、不重播（`wiki/assets/app.js:140` 已有 `pageshow` 先例） |
| 无 JS | 卡片就是普通 `<a>`，跳转正常（overlay 只由 JS 创建，DOM 里根本不存在 → 无需 `noscript` 兜底） |
| reduced-motion | 不插 overlay、不写 storage，`location.assign` 立即执行 |

**唯一的强制约束（写进 Coder 工单）**：`e.preventDefault()` 只能在 overlay **插入成功之后**调用；任何异常路径都必须 `return` 并放行原生跳转。这样「动画坏了」的最坏结果是「回到今天的体验」，而不是「点不动」。

### 3.6 降级路径的精确行为

| 路径 | overlay | sessionStorage | 跳转时机 | 验收断言 |
|---|---|---|---|---|
| 全功能 | 有 | 写 | T0+840ms | A9 / A10 |
| `prefers-reduced-motion: reduce` | **无** | **不写** | T0（同一任务内） | A7 |
| 无 JS | **无（不存在）** | 不使用 | 浏览器原生 | A8 |
| storage 不可用 | **无** | 不使用 | T0 原生 | A9 附例 |
| `character/*.png` 404 | 有（剪影兜底） | 写 | T0+840ms | A15 |
| 浏览器不支持 `clip-path` | 有（方角，其余动效照常） | 写 | T0+840ms | 目视 R1 |
| hero.js 加载失败（α 的 bootstrap） | **无** | 不写 | 原生 | A8 附例 |

### 3.7 hero 数据来源（`hero.js` 的读取顺序）

元数据在卡片 DOM 里已有的（`build_wiki.py:437-443`）：`data-path`、`data-element`、`data-rarity`、`aria-label`、`.cname`、`.csub`、`.cstar`、`a.href`、`img.cicon.src`。

**读取顺序（关键设计，使方案 β 日后成为纯增量升级）**：

1. 若卡片带 `data-hero-id` / `data-hero-art`（β 才有的属性）→ 直接用；
2. 否则回退推导：
   - `id` = `href` 最后一个路径段的 `/^(\d+)\.html$/i` 捕获（**实测 94/94 命中**，F16）；
   - `up` = `href` 中 `pages/` 之前的前缀（角色总索引页实测为 `"../../"`）；
   - `artPrimary` = `img.cicon.src`（**已在本页加载，命中缓存，0 新请求**）；
   - `artHero` = `up + "assets/icons/character/" + id + ".png"`（256×256；缺失则 `error` → 剪影）；
   - 名称 = `.cname.textContent`；属性/命途 = `.csub.textContent` 按 `·` 切；星级 = `.cstar.textContent`；
3. 任一步解析失败 → 缺失的数据条整体 `display:none`，动画与跳转不受影响（**降级粒度到"少一行字"，不是"不播"**）。

> 为什么 `artHero` 用 `<img>` 而不是 CSS `background-image`：需要 `error` 事件做缺失兜底；且 `src` 含 `assets/icons/`，即使把 `[5]` 的 `<img>` 规则套到运行时 DOM 也合规。

---

## 4. 改动面与两方案取舍

### 4.1 方案 α —— 只碰 `style.css` + 新增 `assets/hero.js`（生成器零改动）

**文件面**

| 文件 | 改动 | 规模估计 |
|---|---|---|
| `wiki/assets/style.css` | 末尾**追加**一个新段（token + 组件覆写 + hero 样式），既有 306 行中仅替换 `.chip`/`thead th`/`.sidenav li.cur a`/`.cat` 四个选择器块内的声明（同块替换，不叠同名规则） | ≈ +260 行 |
| `wiki/assets/hero.js` | 新增，零依赖，ES5 语法（与 `character-panel.js:7-8` 一致，不用可选链/箭头函数，兼容老浏览器） | ≈ 220 行 / ≤6 KB |
| `wiki/assets/character-panel.js` | 追加 **bootstrap**（见下方三选一） | +6~8 行 |
| 生成产物 | **不重建**（生成 HTML 一个字节都不变） | 0 |

**α 的 bootstrap 三选一（必须由 Lead 拍板，见 §7 U4）**

| 变体 | 做法 | 代价 |
|---|---|---|
| α-1（推荐） | `character-panel.js` 末尾 `document.createElement("script")` 注入 `assets/hero.js`；注入前在 `document` 上先挂 capture 点击监听做「占位直通」 | 多 1 个请求；需处理 ~毫秒级竞态（未就绪 → 直通，即今天的行为） |
| α-2 | 把 hero 逻辑**并入** `character-panel.js` | 零新请求、零竞态；但文件从 68 行涨到 ~290 行，与「新增 hero.js」的工单表述不符 |
| α-3 | 允许改生成器 **1 行**，在 `build_wiki.py:548` 追加 `<script src="{up}assets/hero.js" defer>` | 最干净；但需重跑全量构建（6685 页），且不再是「生成器零改动」 |

**α 对需求的覆盖度**

| 需求 | 覆盖 | 说明 |
|---|---|---|
| R1 全站视觉 | **≈95%** | 六组件全部可做：切角/描边/层叠/高光/字阶/纹理全在 CSS。唯一做不到的是「真实装饰 DOM 节点」（每元素最多 2 个伪元素 + 既有子元素）。检查过实际需求：卡片需要「框 + 角标 + 扫光」三层 → `::before`(框) + `::after`(内底) 已用满，角标改用 `.cname::before`（既有子元素上的伪元素）兜住 |
| R2 hero | **100%** | 94/94 卡片可播（F16 实测）；元数据全部可从 DOM 取；缺图 4 个走剪影（F15） |
| 静态可读 / 无 JS | **100%** | 不改 HTML → `[1][2][9][10][11][12][13][14][15]` 的结构面零风险 |
| 暗/亮主题 | **100%** | 新 token 双套 + `data-theme` 三态复用 |

### 4.2 方案 β —— 改 `build_wiki.py` 卡片渲染 + `index.html` 结构

**文件面**

| 文件 | 改动 |
|---|---|
| `wiki/build_wiki.py` | `:437-443` 给 `li.citem` 加 `data-hero-id` / `data-hero-art` / `data-name`；`:548` 加 hero.js 的 `<script>`；可选：给 `.hero` 区块加装饰 span |
| `wiki/index.html` | 首页 hero 区加装饰层（不得碰 `[14]` 的 id / `class="quick"` / `class="quick-a"`） |
| `wiki/assets/style.css` / `hero.js` | 同 α |
| 生成产物 | **必须全量重建**：6685 个 HTML 文件的字节变化（git diff 巨大） |

**β 的陷阱（实测得出，非推测）**

- 给 `li` 加类 → `[15]:640` 的 `class="citem"` 计数归零 → FAIL；
- 给 `a` 加类 → `[15]:649` 的 `<a class="ccard" href="` 正则失配 → 卡片 href 检查静默跳过（假绿）；
- 改 head `<noscript><style>` 内容（例如加 `.hero-*` 规则）→ `[15]:663-667` 精确匹配失败 → FAIL；
- 任何新 `<img>`（含装饰图）→ `[5]:201-206` 直接命中 → FAIL。

### 4.3 对比与推荐

| 维度 | α | β |
|---|---|---|
| R1 覆盖 | 95%（伪元素上限） | 100%（可加真实装饰层） |
| R2 覆盖 | 100% | 100%（数据由构建期写入，少一层推导） |
| 触碰校验冻结面 | **无** | 有（类名字面量、head noscript、模板重建） |
| 改动文件数 | 2 新增/追加 + 1 处 6 行 bootstrap | 4 个源文件 + 6685 个产物 |
| 重建成本 | 0 | 全量构建 + 重新生成 `titles.js/stats.js/link_report` |
| 回滚 | `git checkout` 2 个文件（产物无需动）→ 秒级 | revert + 重跑构建（产物 diff 上万行）→ 分钟级 |
| `[5]` 风险 | 0（不新增 HTML 元素） | 低但非 0（新增 DOM/属性的审查面） |
| 首屏成本 | +1 请求 ≤6 KB（仅角色总索引页） | 同左 + 模板变大（94 张卡 × ~60 字节 ≈ +5.6 KB HTML，gzip 后≈+1 KB） |
| 与 URL 方案耦合 | 有（`href` 末段数字，被 `[15]:649` 兜底） | 无 |
| 可演化性 | hero.js 先读 `data-hero-*`，为 β 预留 | — |

**推荐：方案 α（α-1 或 α-3，由 Lead 定，见 U4）。**

理由（三条，按权重排序）：

1. **风险与收益错配**：R1 是纯视觉需求，其全部价值都能用 CSS 拿到；而 `[5][9][11][12][13][14][15]` 的冻结面**恰好都长在生成 HTML 的类名字面量上**（§0.1）。β 用「全量重建 6685 页」换「省掉一层 href 推导」——把构建期风险换给了一个不需要构建期能力的特性。
2. **α 已经覆盖 R2 的硬需求**：94/94 卡片可解析出 id（F16），90 张有 256px 立绘（F14），4 张缺失走剪影（F15）——需求边界已闭合，不存在 α 做不到的 R2 项。
3. **β 的收益可以用「读取顺序」提前占位**：§3.7 让 hero.js 优先读 `data-hero-*`。日后若因别的需求必须改生成器，加属性即可，hero.js 无需重写 —— 因此选 α **不产生技术债**。

**分阶段建议**

| 阶段 | 内容 | 门禁 |
|---|---|---|
| P1 | α：token + 六组件 CSS + hero.js + bootstrap | `[5]` 全 0、`[1][2][9][10][11][12][13][14][15]` 全绿、A7–A11 通过 |
| P2（可选） | 若 P1 后确有「装饰层不够用」的具体案例 → 再做 β 的 data-* 部分 | 需求方给出具体做不出来的组件 |

### 4.4 回滚方式

| 方案 | 回滚命令（示意） | 附加 |
|---|---|---|
| α | `git checkout -- wiki/assets/style.css wiki/assets/character-panel.js && rm wiki/assets/hero.js` | 生成产物未变 → 无需重建；秒级 |
| β | `git checkout -- wiki/build_wiki.py wiki/index.html wiki/assets/ && python wiki/build_wiki.py && python tools/verify_site.py` | 必须重建 + 复跑校验 |
| 只关 hero（视觉保留） | `hero.js` 顶部单一开关常量置 `false`（或 `delete`/`hidden` 一个 `<html data-hero="off">` 属性） | 不碰 CSS，不动生成器 |

---

## 5. 验收断言清单

> 口径：**六项必须为 0**（用户已拍板不放宽）。每条给出命令、期望、执行环节。
> 环节代号：C = Coder 自测，T = Tester，R = Reviewer（只读复核），L = Lead 终判。

| # | 断言 | 命令 | 期望 | 环节 |
|---|---|---|---|---|
| **A1** | 六项禁用项全 0 | `python tools/verify_site.py` | `[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0`（`tools/verify_site.py:214-216`），最终 `RESULT: PASS` | C / T / R / L |
| **A2** | 新增 JS 也过同一套正则（`[5]` **不扫** `assets/*.js`，`verify_site.py:187,704`，故需单独补测） | 见下方「A2 脚本」 | 两个列表都为空（或 radius 值全为 `0`） | C / T / R |
| **A3** | 注释陷阱不触发（`[5]` 扫原文不剥注释，`verify_site.py:190-200`） | `grep -nE "box-shadow\|linear-gradient" wiki/assets/style.css wiki/assets/hero.js` ；`grep -nE "border-radius[[:space:]]*:" wiki/assets/style.css` | 第一条无输出；第二条每行值都是 `0`/`0px` | C / R |
| **A4** | 构建页数不缩水 | `python wiki/build_wiki.py && python tools/verify_site.py` | `pages: 6685 个生成页`（基线 F19；α 下产物应完全不变，`git status wiki/pages` 为空） | C / T |
| **A5** | 死链仍 0 | 同 A1 输出 | `[4] 死链: report=0, 独立复算=0 (一致=True)`（`verify_site.py:152-174`） | T |
| **A6** | 面板结构未破 | 同 A1 输出 | `[15] … count/items/citem 相等、head-noscript=True、说明=True、非图标img=0`（`verify_site.py:689-693`） | T / R |
| **A7** | reduced-motion 降级 | DevTools → Rendering → `prefers-reduced-motion: reduce`，刷新 `pages/character/角色.html`，点卡片 | 无 overlay 节点、无动画、立即进入详情页；`document.querySelector('.hero-overlay') === null` | T |
| **A8** | 无 JS 可用 | DevTools 关闭 JavaScript（或 `chrome --disable-javascript`） | 94 张卡片全部可点并能进入详情；筛选 chip 隐藏（`[15]` 的 head noscript 生效）；hero 不存在但**不影响**跳转 | T |
| **A9** | 每会话每角色只播一次 | 控制台：首次点卡片 → `sessionStorage.getItem('hsr-hero-v1')` = `["<id>"]`；返回后再点同角色 → 无 overlay；点另一角色 → 播一次且数组变 2 元素 | 三项全满足；另测隐私模式：storage 抛异常时不报错、不播、正常跳转 | T |
| **A10** | 键盘可达 & 修饰键不劫持 | Tab 到卡片 → Enter（播 + 跳转）；动画中 Esc（立即跳转）；Shift+Enter 与 Cmd/Ctrl+点击 | 新标签打开且**不播**动效；焦点圈可见（`outline` 未被 `clip-path` 裁掉） | T |
| **A11** | 600×900 无横向溢出 | DevTools 600×900 → `document.documentElement.scrollWidth <= window.innerWidth`；`document.body.scrollWidth <= window.innerWidth` | `true`；`.cgrid` 不撑破；`[11] 小屏导航` 仍为 True（`verify_site.py:351-365`） | T |
| **A12** | 明暗主题契约 | 四组合（系统亮/系统暗/`data-theme=light`/`data-theme=dark`）各截图 + 对比度 | `--ui-ink` 对 `--ui-panel`、`--ui-mute` 对 `--ui-panel` ≥ 4.5:1；overlay 与卡片在四组合下均可见 | T / R |
| **A13** | 零外链（hero.js 无 `[13]` 那种兜底检查，需手工） | `grep -nE "(src\|href)[[:space:]]*=[[:space:]]*[\"']https?://" wiki/assets/hero.js wiki/assets/style.css` | 无输出。注：`[13]:433` 只对 `timeline.js` 做了同样检查，hero.js **没有**自动覆盖 | C / R |
| **A14** | 打印不回归 | `verify_site.py` 的 `[12]` + Ctrl+P 预览 | `[12] @media print=True display:none=True`；`.hero-overlay` 打印时 `display:none`；hero 不产生分页空白 | T |
| **A15** | 缺图角色兜底 | 断网/临时重命名 `assets/icons/character/1014.png` 后点 Saber | 剪影显示、动画完成、正常跳转；恢复文件后无残留错误 | T |
| **A16** | 产物未被手改 | `git status --porcelain` | 只有预期源文件变更；`wiki/pages/**` 与 `wiki/data/**` 无改动（α 下） | C / L |

**A2 脚本**（把 `[5]` 的同一套正则套到新增 JS 上；`[5]` 本身只扫 `index.html` + `style.css` + 生成页，见 `tools/verify_site.py:187,704`）

```bash
python - <<'EOF'
import re
s = (open('wiki/assets/hero.js', encoding='utf-8').read()
     + open('wiki/assets/style.css', encoding='utf-8').read())
print('shadow  :', re.findall(r'box-shadow', s, re.I))
print('gradient:', re.findall(r'linear-gradient', s, re.I))
vals = re.findall(r'border-radius\s*:\s*([^;}"\']*)', s, re.I)
print('radius  :', [v.strip() for v in vals])
EOF
# 期望：shadow / gradient 为空列表；radius 每项都属于 {0,0px,0%,0em,0rem,0pt,0pc,0cm,0mm,0in,0q}
```

---

## 6. 风险表

| # | 风险 | 触发条件 | 影响 | 缓解（设计内） | 残留风险 |
|---|---|---|---|---|---|
| R-1 | `clip-path` 在老浏览器/Safari（<13.1 需 `-webkit-` 前缀；更老完全不支持） | Safari 12/旧 Edge/IE | 退化为**方角**（切角不可见） | 装饰全在伪元素上，属性被忽略只丢装饰、不破布局；`style.css:122-124` 已有 `forced-colors` 回退先例，照抄 `@supports (clip-path: polygon(0 0))` 包裹 `--cut-hex` 用法 | 低（视觉退化，功能零损失） |
| R-2 | overlay 抢焦点致键盘困惑 | 若实现时 `focus()` 到 overlay | Tab 顺序被打断、SR 迷宫 | **D-2：不移动焦点**、不加 `role=dialog`、overlay 内无 `tabindex`；Esc 可跳过 | 极低 |
| R-3 | `@keyframes` 造成布局抖动 | 动画 `width/height/top/left/margin` | 全站回流、滚动条跳动 | 只动 `transform/opacity/clip-path`；overlay `contain:layout paint`；**不锁滚动**（避免滚动条消失导致横向 15px 抖动） | 低；A11 兜底 |
| R-4 | 首屏 JS 预算 | α-1 多 1 请求；hero.js 过大 | 角色总索引页 LCP 回归 | hero.js ≤6 KB、零依赖、`defer`、只在 1 个页面加载、**预取 0 张大图**（点卡片才请求 256px），首帧直接用已缓存的 avatar | 中低；A15 + 体积断言 |
| R-5 | 4 个角色无任何图标资产（F15） | 点 1511/1503/1513/1512 | 404 + 空帧 | `<img>` 的 `error` → 立即换 SVG data URI 剪影（`.hero-art-fb`），数据条照常 | 低 |
| R-6 | `sessionStorage` 不可用（隐私模式/被策略禁用） | Safari 隐私、部分企业策略 | 每次点击都播 → 干扰 | 读/写全 `try/catch`；**不可用视为已播**（不播） | 低 |
| R-7 | bfcache 返回残留 overlay | 详情页点「返回」 | 回到面板却见半透明过场层 | `pageshow` + `event.persisted` 清理（`app.js:140` 同法）；`state='idle'` | 低 |
| R-8 | 校验器注释陷阱（`verify_site.py:190-200` 扫原文） | 注释里写 `box-shadow` / `linear-gradient`；或 `border-radius: 4px` 写在注释 | 六项归零被打破 → A1 FAIL | H-1 注释纪律 + A2/A3 专项断言 | 低（有断言） |
| R-9 | 图标放大量级模糊 | `.cicon` CSS 尺寸 >128px，或 hero 用 avatar 放大过 128px | 卡片/hero 发虚 | 卡片 ≤128px；hero 用 256px 的 `character/{id}.png` 且 `min(256px,60vmin)` 封顶；`object-fit:contain` | 中低（需要 Coder 守线） |
| R-10 | forced-colors / 高对比模式 | Windows 高对比 | 纯色装饰被系统色吞掉 | `@media (forced-colors: active){ .ccard::before,.chip::before,…{ border:1px solid } }`（照 `style.css:122-124` 先例） | 低 |
| R-11 | 连点/动画中导航 | 快速双击 | 重复 `location.assign` / 中断 | `navigateOnce` 幂等标志 + `state` 机 | 极低 |
| R-12 | 卡片文案解析脆弱（`（风·毁灭）`、`.csub` 分隔符） | 未来改名/换分隔符 | 数据条错位或缺失 | §3.7 第 3 步：解析失败**只隐藏数据条**，不阻断动画与跳转 | 低 |
| R-13 | 表格 `clip-path` 误用 | 给 `table`/`thead` 加裁剪 | `position:sticky` 表头在裁剪容器内失效（`style.css:118`） | 设计明文：**表格禁用 clip-path**（§2.5） | 低 |
| R-14 | 打印出现空白页 | overlay `position:fixed` 未在 print 中隐藏 | 打印多一页黑底 | `@media print{ .hero-overlay{display:none} }` | 低；A14 |

---

## 7. 未决问题（需 Lead / 用户拍板）

| # | 问题 | 选项 | 我的建议 |
|---|---|---|---|
| U1 | 选中/高光用青（`--ui-hi`）还是沿用红（`--accent`） | A 青为选中、红只为链接（D-1）；B 全站统一红 | A |
| U2 | hero 总时长 840ms 是否接受 | 640 / 840 / 1080ms | 840（可调 `--hero-total`） |
| U3 | 正文 `h2` 是否加自动编号（`00/01/…`） | A 加（数据感强）；B 不加（最小改动） | A，但**保留一键删除**（删 `::before` 即回退） |
| U4 | α 的 bootstrap 落地方式 | α-1 运行时注入（真"生成器零改动"）/ α-2 并入 `character-panel.js` / α-3 生成器加 1 行 `<script>` | α-1（若接受 1 行生成器改动，则 α-3 更干净） |
| U5 | SVG 内 `<linearGradient>` / `<feDropShadow>` 是否也禁 | A 显式禁止并写进 Reviewer 清单；B 不管（正则不命中） | **A**：`[5]` 正则只匹配连字符小写形式（`verify_site.py:198`），SVG 的 `linearGradient` 命中不了 —— 属"合法逃逸但违背三禁精神"，必须用约定封住 |
| U6 | hero 主视觉用 256px 立绘 `character/{id}.png` 还是仅 avatar | A 立绘（更像游戏）；B 仅 avatar（更省） | A（点播、单张 103 KB、90/94 可得） |
| U7 | 缺图 4 角色（1511/1503/1513/1512）是否需要补资产 | A 接受剪影；B 走 `copy_icons.py` 补图 | A（补图属 D-014/D-015 范围外的新决策） |

---

## 附：需求 → 设计 映射（自检）

| 需求 | 设计条目 | 验收断言 |
|---|---|---|
| R1 锐角切角 | §1.2 `--cut-hex`、§1.5 T-1、§2.7/2.8/2.9 伪元素切角 | A1、A12 |
| R1 细描边 | §1.5 T-2 双伪元素假框、§2.1–2.9 | A1 |
| R1 半透明层叠 | §1.1 `--ui-surface/--ui-surface-2`、§2.2/2.6/2.9 | A12 |
| R1 冷色高光 | §1.1 `--ui-hi`、`--ui-hi-2`；§2.2 竖条、§2.5 表头线、§3.2 扫光 | A12 |
| R1 数据感排版 | §1.3 `--fs-micro`/`--ui-track`/`tabular-nums`、§2.4 计数器、§2.9 统计块 | A12、A11 |
| R1 静态可读（无 JS 完整） | 全部视觉在 CSS；hero 只由 JS 创建（§3.3） | A8 |
| R1 不引依赖/外链 | §1.5 T-3/T-4、§2.x 全部 data URI/SVG | A1、A13 |
| R1 暗/亮主题 | §1.1 双套 token + `data-theme` 复用 | A12 |
| R2 首次点击触发 | §3.1 状态机、§3.5 交互矩阵 | A9、A10 |
| R2 每会话每角色一次 | §3.4 `hsr-hero-v1` | A9 |
| R2 reduced-motion 退化 | §3.1 `static`、§3.6 | A7 |
| R2 无 JS 卡片仍是链接 | §3.3（overlay 由 JS 创建，DOM 中不存在）、§3.5 | A8 |
| R2 不用大图 | §3.7 两层图（已缓存 avatar → 256px 立绘）、§6 R-9 尺寸封顶 | A15、R-4 |
| 六禁保持 0 | §1.5 全表 + H-1 注释纪律 | A1、A2、A3 |
| 不改仓库文件（Architect） | 本文件是唯一产物 | A16（Coder 阶段起生效） |

---

## 附录 R｜Lead 裁定（2026-11-14，Tester/Reviewer 交付后）

> 本附录**覆盖**上文与之冲突的措辞；未列项按原文执行。

| # | 事项 | 裁定 | 依据 |
|---|---|---|---|
| R-1 | **A15 图源降级口径**（Reviewer P1-3） | **接受实现**：有 `avatar` 无 `character` 立绘的角色 → 上采样已缓存 avatar（128→256）；**只有 4 个完全没有图的（1511/1503/1513/1512）才用 SVG 剪影**。§A15 与 §6 R-5 的「换 SVG 剪影」措辞作废 | Tester A17 实测：4 个无图角色 `imgs=0`、坏请求 0、剪影正常；Reviewer 确认 `character-panel.js:236-239` 行为 |
| R-2 | **A16 体积口径** | 以 **gzip-9 增量**判定（≤30 KB）：实测 **+10.2 KiB PASS**；raw 增量 **+35.6 KiB** 仅记录、不作判据 | 静态托管实际按 gzip 传输；Reviewer 已记录 raw 值（style.css 18,133→42,756、character-panel.js 2,148→14,022） |
| R-3 | **U3 `h2` 自动编号** | **保留**。理由：实现为 `.prose h2::before` 伪元素，**不改 DOM 文案、不进可复制文本**，仅视觉；打印/PDF 属预期展示 | Reviewer 指「会改 6685 页可见文案」→ 实为伪元素，无原文改动 |
| R-4 | **U1/U2 主题与高光** | 采用 `--ui-hi` 青色高光，`--accent`（红）保持不动；token 默认亮、暗走 `prefers-color-scheme`（与仓库 `style.css:1-4` 真实机制一致，**设计 §1.1「暗为默认」作废**） | Coder 偏离 #1 说明 + Reviewer 探针 |
| R-5 | **假框内层不透明** | 采用 `--ui-panel`/`--ui-panel-2`（不透明）；半透明内层会导致描边色填满形状（实测文字不可见） | Coder 偏离 #2；Reviewer 同意 |
| R-6 | **D-1 / D-2 / D-3 必修** | ①滚动时 `thead th` 被 sticky `.topbar` 压住（P1）；②打印深色条（P2）；③hero 关键帧补 `prefers-reduced-motion: no-preference` 容器（P2） | Tester D-1/D-2/D-3 |
| R-7 | **P1-1 / P1-2 必修** | ①浅色 `--ui-mute` 改 `#55606F`（4 组对比度 ≥4.5）＋ `.ccard:hover::after` 换不透明；②`--hero-total` 做成真旋钮（关键帧 `calc(var(--hero-total)*k)`） | Reviewer P1-1/P1-2 |
| R-8 | **A5 判据** | 改为「**数据区死链 = 0**」；`verify_links` 缺退出码的问题另立 issue，不当本卡 FAIL | Tester U4 |
| R-9 | **A12 标题裁切** | **误报**：Coder 截图为 hero 名字擦除动画中间帧（310ms）；Tester 在 3 页面 × 3 宽度 9 组合实测 `h1.top ≥ topbar.bottom`、无遮挡、祖先无裁剪 | Tester A12 实测；Lead 采纳 |
