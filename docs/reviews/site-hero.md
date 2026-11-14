# 代码审查报告 · 站点视觉重构（R1）+ 角色 hero 动画（R2 / issue #13）

| 项 | 值 |
|---|---|
| 环节 | Reviewer（只读审查） |
| slug | `site-hero` |
| 审查对象 | 未提交改动：`git diff -- wiki/assets/style.css wiki/assets/character-panel.js`（2 文件 / +733 −36） |
| 对照基线 | `docs/designs/site-hero.md`（Architect，758 行，含 §0.1 冻结面 / §1–§3 规格 / §5 验收断言） |
| 本产物 | 本文件（唯一写盘产物；**未修改任何仓库文件、未运行 `build_wiki.py`**） |
| 复算环境 | `G:\HSR` @ `main` / HEAD `29b51331f` |
| 审查时间 | 2026-10-03 |

---

## 0. 裁定

> **有条件通过（Conditional Pass）**

| 轴 | 判定 | 一句话依据 |
|---|---|---|
| **A 轴**：仓库约定 / 硬约束 / 安全 | **通过** | `python tools/verify_site.py` → `RESULT: PASS`，`[5]` 六项全 0；冻结面三处字面量未被触碰（`[15]`全绿、`[11]`真）；五语数据 0 改动；零外链、零 CDN、零新请求；`build_wiki.py` / `index.html` 零改动 ⇒ 无 JS 行为 100% 不变 |
| **B 轴**：逐条需求对应 | **有条件通过** | R1 §1 token + §2 九类组件**全部落地**；R2 §3 状态机 / 时序 / `hsr-hero-v1` / 4 个无立绘降级 / reduced-motion **逐条对应**；6 处偏离**全部判为可接受**。但发现 **3 条 P1**（1 条对比度实测不达标、1 条设计旋钮名不副实、1 条与设计 A15 断言冲突的口径分歧），需在 Tester 出结论前处置 |

**放行条件（3 条 P1，缺一不可）：**

1. **P1-1** 浅色主题 `--ui-mute` 实测对比度 3.53–4.24:1，未达 WCAG AA 4.5:1（正文 11–13px 小字，命中面包屑 / 面板元信息 / chip 标签 / hero 数据标签 / 首页 meta）→ 调 token 或改依赖它的规则；
2. **P1-2** `--hero-total`（与 `--hero-stagger`）在 CSS 中**零引用**，设计 §3.2「唯一可调旋钮 / CSS 是唯一真相源」不成立 → 要么把关键帧总时长安到该变量上，要么在设计文档里删掉这句承诺；
3. **P1-3** `character/{id}.png` 404 时实现保留 128px avatar（2× 上采样），设计 §3.6 / A15 规定显示 SVG 剪影 → **Tester 按设计断言会判 FAIL**，必须先由 Lead 统一口径（我倾向接受实现、改设计口径，理由见 §6.3）。

P2 共 12 条，可排期，不阻塞本阶段。

---

## 1. 问题清单（P0 / P1 / P2）

### P0（阻断，0 条）

无。逐条排除：

| P0 判据 | 结论 | 证据 |
|---|---|---|
| 六项禁用项被判违例（含 SVG 变相绕过） | 否 | §2.1 |
| 冻结面被改（`class="citem"` / `<a class="ccard"` / head-noscript / `@media(max-width:640px){`+`.sidenav{max-height`） | 否 | §2.2 |
| 五语数据 / 生成产物被改 | 否 | §2.3 |
| 引入外链 / CDN / 网络请求 | 否 | §2.4 |
| 无 JS 时卡片不可点 / 行为改变 | 否 | §2.6 |
| 主路径运行时崩溃（overlay 建不出来 / 点击失效） | 否 | §4.2 静态走查 + `node --check` |

### P1（须处置后放行，3 条）

| # | 位置 | 问题 | 依据（实测） | 建议 |
|---|---|---|---|---|
| **P1-1** | `wiki/assets/style.css:362-369`（`:root` 浅色 token）；消费点 `:466` `.crumbs`、`:282` `.cp-meta`、`:287` `.cp-label`、`:304` `.cp-count`、`:330` `.csub`、`:334` `.cp-noscript`、`:537` `.dash-cell`、`:545` `.dash-sub`、`:619` `.hero-k`、`:623` `.hero-hint`；`.ccard:hover::after` @ `:320` | 浅色主题下 `--ui-mute`(#6B7484) 的**实际使用底色**对比度不足 4.5:1 | 复算（WCAG 2.x 相对亮度）：`mute/bg(#F1F3F7)=4.24`、`mute/panel-2(#E7EBF2)=3.94`、`mute/card-hover 衬底(#DDDFE4)=3.53`。命中文字均为 11–13px（`.crumbs` 13px、`.cp-label` 11px、`.cp-meta`/`.cp-count` 13px、`.hero-k` 11px、`.hero-hint` 11px、`.dash-meta` 13px、`.csub` 12px）。注：设计 A12 只承诺「`--ui-mute` **对 `--ui-panel`** ≥4.5」，该口径成立（4.71），但真实文字几乎不落在 `--ui-panel` 上 | 浅色 `--ui-mute` 由 `#6B7484` 调深到 **`#55606F`**（复算：bg 5.75 / panel 6.39 / panel-2 5.34 / hover 衬底 4.79，四对全 ≥4.5）；并把 `.ccard:hover::after` 的 `var(--ui-surface-2)`（`style.css:320`）换成**不透明** `var(--ui-panel-2)`，避免击中「半透明衬底 + 浅灰字」最差组合 |
| **P1-2** | `wiki/assets/style.css:410`（`--hero-total:840ms; --hero-stagger:40ms;`）vs 关键帧 `:639-654`（`240ms`/`160ms`/`720ms`/`320ms/360ms/400ms` 全为字面量） | 设计 §3.2 称「840ms 是**唯一可调旋钮**，只改 `--hero-total` 一个变量」「CSS 是时长的唯一真相源，避免两处硬编码」——**实现不成立**：CSS 里 `var(--hero-total)` 出现 **0 次**，`var(--hero-stagger)` 也是 **0 次**。JS 只读该变量决定**跳转时点**（`character-panel.js:134-141`、`:326`） | 若把 `--hero-total` 改成 640ms：动画仍在 840ms 走完（扫光 560–720、收束 720–840 被跳转硬切）；改成 1080ms：720–840 之后空等 240ms。同理四角 stagger（`:643-646`）与数据条 stagger（`:650-652`）均为硬编码 40ms 步进，`--hero-stagger` 是死 token | 二选一：**(a)** 把 `.hero-frame`/`.hero-sweep`/`.hero-stat` 的 delay 改成 `calc(var(--hero-stagger)*n)`、把总时长挂到 `--hero-total`（`animation-duration` 用 `calc(var(--hero-total) - Xms)` 亦可）；**(b)** 在设计文档 §3.2 删掉「唯一可调旋钮 / CSS 唯一真相源」的表述，改为「JS 读 `--hero-total` 决定跳转时点，关键帧时长独立硬编码」 |
| **P1-3** | `wiki/assets/character-panel.js:236-239`（`top.onerror`） | **未申报的偏离**：`assets/icons/character/{id}.png` 404 时，实现只是移除上层 `<img>`，**露出下面 128×128 的 avatar 并按 256px 盒子上采样 2×**；设计 §3.6 与 A15 写的是「→ 换 SVG data URI 剪影 `.hero-art-fb`」 | 设计 `docs/designs/site-hero.md:553`（A15 行：「剪影显示、动画完成、正常跳转」）、`:713`（R-5「`error` → 立即换 SVG data URI 剪影」）。当前实现永远不会产出剪影兜底给「有 avatar 但无立绘」的角色；剪影分支只服务**无 avatar 图标的那 4 个**（`:242-245`）。⇒ Tester 按设计原文测 A15 会判 FAIL | 由 Lead 拍板：**(A)** 接受实现（有真图优先于剪影），改设计 §3.6 / A15 口径为「404 → 回退已缓存的 128px avatar（可辨识，略模糊），剪影仅用于本就无图标的 4 个角色」；**(B)** 要求实现按设计补 `hero-art-fb` 剪影。我建议 A（可辨识度更高，且不新增请求） |

### P2（记录 / 排期，12 条）

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `character-panel.js:283-296`（`announce`）+ `:302-310`（`navigateOnce` → `clearTimers()`） | `.sr-only` 播报节点**泄漏**：移除定时器被塞进 `timers`，而跳转时 `clearTimers()` 一定把它取消，节点永久留在 body；从 bfcache 返回（`onPageShow` → `dropOverlay`）也不会清 | `dropOverlay()` 里顺带清掉 `body > .sr-only[role=status]`；或不要把播报移除塞进 `timers` |
| P2-2 | `character-panel.js:285-289` | 同一任务内「建节点 + 写 textContent」，部分读屏（NVDA / VoiceOver）对**新建** live region 的首次内容不播报 | 先 append 空节点，再 `setTimeout(...,0)` 或 `requestAnimationFrame` 后写文本 |
| P2-3 | `style.css:579`→`:580`（`.hero-overlay[hidden]{display:none}`） | 死规则：JS 从不设 `hidden`，overlay 靠 append/remove 管理 | 删除，或改由 JS 用 `hidden` 控制（二选一即可） |
| P2-4 | `character-panel.js:323-325` | `data-state` 只实现 `enter` / `hero` 两态，设计 §3.1 的五态（`idle`/`enter`/`hero`/`static`/`exit`）缺 3 态；bfcache 恢复后也不复位 `data-state` | 仅调试属性，可在设计文档标注「只落地 2 态」，或补齐 |
| P2-5 | `style.css`：`.topbar`(17 & 437)、`.sidenav`(85 & 451)、`.crumbs`(31 & 466)、`table`(39 & 486)、`th,td`(40 & 487)、`blockquote`(44 & 498)、`.meta`(55 & 508)、`body`(20 & 431)、`h1`(34 & 482)、`h3`(36 & 483) | 同名选择器各被声明 2 次（追加段整体覆盖前段）。设计 §2.8 只要求 4 个选择器「同块替换」，其余属新增覆盖 | 可接受（追加段策略），但建议下轮把重复项合并，避免以后改前段无效 |
| P2-6 | `style.css:362-427`（token 定义段） | 死 token 8 个：`--ui-warn`(0 引用)、`--t-0`、`--t-5`、`--hero-stagger`、`--fs-6`、`--sp-7`、`--sp-8`；设计 §1.3 的 `--ui-num` **未定义**（改用 19 处直写 `font-variant-numeric:tabular-nums`） | 删死 token 或补用途；`--ui-num` 在文档里标注「以直写属性替代」 |
| P2-7 | `character-panel.js:277`（`o.appendChild(.hero-sweep)`）+ `style.css:621` | **未申报的偏离**：`.hero-sweep` 挂在 overlay（全视口高度、全宽 38%）而非设计 §3.2/§3.3 的 stage 内部 | 视觉差异可接受（横扫更「仪表」），但需在设计文档记录 |
| P2-8 | `character-panel.js:302-310` | `nav` 幂等标志只由 bfcache 复位：若 `location.assign` 被拦（策略/扩展），本页所有卡片点击**永久失效** | `nav` 设超时复位（如 `setTimeout(()=>nav=false, 2000)`） |
| P2-9 | `character-panel.js:210` + `:609-610`（`hero-hint`） | D-2 固有后果：overlay 无焦点陷阱，键盘仍可 Tab 到被遮挡的卡片并按 Enter 跳走；`.hero-hint`（「Esc / 点击 跳过」）在 `aria-hidden="true"` 内，读屏用户拿不到跳过提示 | 设计已接受 D-2；建议把跳过提示改成 overlay 外的一句 `sr-only` 文本，随 `announce` 一起播报 |
| P2-10 | `style.css:679-684`（新增 `@media print` 段） | 打印时 `.ccard{border:1px solid #000}` 但伪元素框被清成透明 → 卡片退化为无填充 1px 黑框 | 目视确认可接受；如需保留底色，在打印段给 `.ccard::after` 单独的 `background:#FFF`（`clip-path:none` 已设） |
| P2-11 | 工作区 | **范围污染**：`M 协作要求与行动准则.md`、`?? scripts/mimo_batch.py`、`?? docs/评测_MiMo-V2.6-Flash_2026-10-03.md` 与本工单无关却在同一工作区。设计 A16「`git status --porcelain` 只有预期源文件变更」严格口径下**不通过** | 提交时 `git add` 只写显式路径（只 add 两个 assets 文件 + 本报告），其余留给对应工单 |
| P2-12 | `style.css` 体积 | 18,133 → 42,756 字节（**+24,623 / +136%**），是 6685 页**全部**引用的 render-blocking 单文件；设计 §4.1 估算「style.css ≈ +260 行」，实际 +414 行 / 619 行占位 | 与设计 R-4 的 JS 预算对齐补一条 CSS 预算；若要压缩，可把 hero 段（`:340-684`，约 17KB）拆成只在角色页引用的第二张表（但那需要改生成器，属 β，不建议现在做） |

---

## 2. A 轴：仓库约定 / 硬约束 / 安全

### 2.1 `[5]` 六项禁用项 —— 逐条 grep 复查 + 变相绕过扫描

| 禁用项 | 校验口径 | 我的复算 | 结论 |
|---|---|---|---|
| `border-radius` 只能为 `0` | `verify_site.py:190-194` + 白名单 `:46` | 全文件共 10 处 `border-radius`，值全为 `0`（`style.css:14,46,47,55,60,65,69,70,71,157`，**全部为基线既有行**）；新增段 **0 处** | ✅ 合规 |
| 无 `box-shadow` | `:195-197`（扫原文含注释） | `grep -niE "box-shadow|linear-gradient" style.css character-panel.js` → **无输出** | ✅ 合规 |
| 无 `linear-gradient`（含 `repeating-`） | `:198-200` | 同上无输出；另扫 `radial-gradient` / `conic-gradient` / `repeating-` → 无输出 | ✅ 合规 |
| 无非图标 `<img>` | `:201-206`（`assets/icons/` 放行） | CSS/JS 内 `<img` 出现 0 次；运行时仅 `character-panel.js:227,240` 建 `<img>`，`src` 分别为卡片原有 `assets/icons/avatar/*.png` 与 `up + "assets/icons/character/*.png"` | ✅ 合规（运行时也守线） |
| 无外链脚本 | `:207-209` | `<script src="https?:` → 无 | ✅ 合规 |
| 无外链样式 | `:210-212` | `<link href="https?:` → 无；`@import` → 无 | ✅ 合规 |

**变相绕过专项（设计 U5 要求显式封住）**：扫 `linearGradient` / `radialGradient` / `feDropShadow` / `<filter` / `filter=` / `<image` / `drop-shadow` / `backdrop-filter` / `text-shadow` —— **全部 0 命中**。两处 SVG 只用 `<path>` / `<circle>` + `fill` / `stroke` 纯色（`style.css:425`、`:427`），没有渐变、没有滤镜。

**结论：六项 + 5 类变相绕过全部为 0，未发现任何绕过。**

### 2.2 冻结面（设计 §0.1）—— 逐项核对

| 冻结项 | 校验位置 | 复算 | 结论 |
|---|---|---|---|
| `class="citem"` 字面量计数 == 条目数 | `verify_site.py:640` | `grep -o 'class="citem"' 角色.html \| wc -l` → **94**；`[15] citem=94`、`items=94` | ✅ 未动 |
| `<a class="ccard" href="` 字面前缀 | `:649` | `grep -o` → **94**；`[15] 卡片href错=0` | ✅ 未动 |
| `icon-fallback` ≥ 缺图条目数 | `:675-679` | `grep -o` → **4**；`[15] fallback=4 缺图img=0` | ✅ 未动 |
| head 内 `<noscript><style>.cp-filters{display:none}</style></noscript>` 尾部精确匹配 | `:663-667` | `[15] head-noscript=True` | ✅ 未动 |
| `@media(max-width:640px){` + `.sidenav{max-height` 字面相邻 | `:357-358` | `[11] style.css 小屏.sidenav{max-height=True`；实际在 `style.css:138`（单行 `@media (max-width:640px){ .sidenav{max-height:40vh;overflow:auto} }`，**本次未触碰**） | ✅ 未动 |
| `<table>` 紧跟 `<thead>` | `:318-327` | `[9] table=9168 thead=9168 紧跟thead=9168` | ✅ 未动 |
| 首页 `id="dash-*"` / `class="quick"` / `class="quick-a"` | `:498-505` | `[14] … 容器齐=True quick=True` | ✅ 未动（`wiki/index.html` 零改动） |
| `h1` 文本 == `title` | `:75-103` | `[1] H1: 6685/6685 合规` | ✅ 未动 |
| 新增同名 CSS 段的写法风险 | 设计 §2.2 警告「不得写 `.sidenav {`」 | 新增小屏段（`style.css:669`）为 `@media (max-width:640px){`（**带空格**），且不含 `.sidenav{max-height`，不影响 `[11]` 正则取的是 `:138` 那一条 | ✅ 安全 |

### 2.3 数据零改动

| 目录 | 结果 |
|---|---|
| `wiki/data` | **0 改动** |
| `zh_cn` / `en_us` / `zh_tw` / `ja_jp` / `ko_kr` | **各 0 改动** |
| `wiki/pages`（6685 生成页） | **0 改动** |
| `wiki/build_wiki.py` / `wiki/index.html` / `wiki/assets/theme.js` / 其它 assets | **0 改动** |

`git status --porcelain` 的 `M` 只有 `wiki/assets/style.css`、`wiki/assets/character-panel.js`（+ 1 个与本工单无关的 md，见 P2-11）。

### 2.4 零依赖 / 零外链

| 检查 | 结果 |
|---|---|
| 全文 `http(s)://` 出现处 | 仅 2 处，均为 SVG **命名空间标识符**：`style.css:425`、`:427` 的 `xmlns='http://www.w3.org/2000/svg'` |
| 为什么这两处合法 | ① 它们是 `data:image/svg+xml` URI **内部**的 XML 命名空间字面量，浏览器把它当字符串保留、**从不解析也不请求**；② `[5]` 的外链正则分别锁在 `<script … src="https?:`（`:207`）与 `<link … href="https?:`（`:210`），`url("data:…")` 的 scheme 是 `data:`，不命中；③ 两处 URI 内容全部做了 `<`/`>`/`#` 百分号编码（`%3C`/`%3E`/`%23`），CSS 解析安全 |
| CDN / 外链字体 / `@import` | 0 |
| XHR / `fetch` / `import()` / `sendBeacon` | 0 |
| 新增网络请求 | **0**：该页 `<script>`/`<link>` 仍为 `style.css` + `theme.js` + `character-panel.js`（无 `hero.js`，方案 α-2 生效）。256px 立绘为**点击时点播**，`img` 的 `src` 指向同源 `assets/icons/character/` |

### 2.5 可及性

| 项 | 核对方式 | 结论 |
|---|---|---|
| **overlay `aria-hidden` 是否会连带屏蔽 `role=status` 播报节点** | 静态追踪 DOM 创建顺序：`character-panel.js:316` `document.body.appendChild(o)`（overlay）→ `:321` `announce(...)` → `:289` `document.body.appendChild(st)` | ✅ **不会**。播报节点是 `body` 的**兄弟节点**（overlay 之后 append），不在 `aria-hidden="true"` 子树内。Coder 所述属实，且修的是设计 §3.3 样例自身的缺陷（设计把 `role=status` 放进了 `aria-hidden` 的 overlay 里，那样确实读不到） |
| 焦点管理 | `character-panel.js` 全文无 `focus()` / `tabindex` 写入 | ✅ 符合 D-2「不移动焦点」；`outline` 未被裁（交互元素自身不上 `clip-path`，切角全在 `::before/::after`） |
| Esc | `:368-374`，`document` 捕获阶段，仅 `overlay` 存在时生效 | ✅ 生效，且是「跳过并跳转」语义 |
| 修饰键 / 中键 | `:332-333` | ✅ 完全不拦截 |
| **`prefers-reduced-motion` 分支是否真的不写 `sessionStorage`** | `:346-350` 命中即 `return`；`writeStore` 唯一调用点在 `:320`（`startHero` 内），该路径不可达 | ✅ **确实不写**，且不插 overlay、不 `preventDefault`（原生跳转） |
| 对比度 | 见 **P1-1**（实测 3.53–4.24 不达标） | ⚠️ |
| 非文本对比（组件边界） | `--ui-line` 对底色：浅色 1.39:1、暗色 1.41:1，低于 WCAG 1.4.11 的 3:1 | 记录（**非本次回归**：基线 `--line` 同为 ~1.4:1），但新设计把 1px 假框当作「替代阴影的唯一手段」，建议下轮一起调 |
| 暗色卡片层次 | `--ui-panel`(#0C1117) 对 `--ui-bg`(#06080C) 亮度差仅 0.003（对比 1.06:1）——暗色下卡片「内层填充」几乎不可见，靠 1px 描边成形 | 记录（设计 §1.1 自选的取值，非 Coder 偏离） |

### 2.6 降级（无 JS 时卡片行为是否 100% 不变）

| 证据 | 结论 |
|---|---|
| `wiki/build_wiki.py` 零改动（`git status` 无该文件） | 生成 HTML 一个字节未变 |
| `wiki/pages/**` 零改动 | 6685 页产物未重建/未手改 |
| 卡片 DOM 仍是 `<a class="ccard" href="../../pages/character/…/1014.html" aria-label="…"><img class="cicon" src="../../assets/icons/avatar/1014.png" …></a>`（实测 `角色.html`） | 是普通链接，overlay 只由 JS 运行时创建 → DOM 里根本不存在 |
| 4 个缺图卡仍是 `<div class="icon-fallback cicon-fb"></div>` | 同上，无 JS 时只是空占位，不影响跳转 |
| head 内 `<noscript><style>.cp-filters{display:none}</style></noscript>` 保持 | 无 JS 时筛选按钮仍被隐藏（`[15] head-noscript=True`） |
| 新 CSS 是否会在无 JS 下改变卡片可用性 | 否：`.ccard` 仍是 `display:block` 的链接，`::before/::after` 为装饰层（`pointer-events` 默认跟随伪元素宿主，`z-index:-1` 位于内容之下，不拦截点击）；`.citem[hidden]`（`style.css:310`）保留，筛选逻辑依赖仍在 |

**结论：无 JS 时卡片行为 100% 不变。**

---

## 3. B 轴：逐条需求对应

### 3.1 R1 视觉重构 —— 设计 §1 token 落地

| token 组 | 设计 §1 | 实现位置 | 落地 |
|---|---|---|---|
| §1.1 颜色 14 槽（bg/panel/panel-2/surface/surface-2/line/line-2/ink/ink-2/mute/hi/hi-2/warn/danger） | 暗/亮两套 | `style.css:362-369`（亮默认）、`:370-380`（`prefers-color-scheme: dark`）、`:381-388`（`[data-theme=light]`）、`:389-396`（`[data-theme=dark]`） | ✅ 已落地（14/14；`--ui-warn` 定义了但 0 引用 → P2-6） |
| §1.2 几何（cut-sm/cut/cut-lg/hair/hair-2/bracket/sp-1..8/frame + `--cut-hex`/`--cut-bracket-tl`） | 8px 栅格 | `style.css:399-427`（另加 `--cut-hex-sm`/`--cut-hex-lg`/`--cut-one-sm` 三个派生多边形） | ✅ 已落地（12/12） |
| §1.3 字号阶（fs-micro..fs-6 / ui-track / ui-num） | 数据感小字阶 | `:405-407`（fs 阶 + track）；`--ui-num` **未定义**，改用 19 处直写 `font-variant-numeric:tabular-nums` | ⚠️ 部分：`--ui-num` 缺失（P2-6），效果等价 |
| §1.4 动效（t-0..t-5 / ease / ease-out / ease-in / hero-total / hero-stagger） | 时长与缓动 | `:409-411` | ⚠️ 部分：`t-0`/`t-5`/`hero-stagger` 0 引用（P2-6）；`hero-total` 仅被 JS 读、CSS 0 引用（**P1-2**） |
| §1.5 三技法（T-1 切角 / T-2 假框 / T-3 SVG 纹理）+ H-1 注释纪律 | 六禁的替代手段 | 切角：`--cut-hex*` 广泛使用；假框：`.ccard/.chip/.cat/.quick-a/.dash-cell/.hero-stat` 全是「`::before` 描边色 + `::after` 内缩 1px」成对出现；纹理：`--ui-grid`（`style.css:425`）+ `.hero-overlay`（`:579`） | ✅ 已落地；H-1 纪律执行到位（注释里没有任何 `box-shadow` / `linear-gradient` 字面量，用「投影类属性」「渐变函数」改写） |

### 3.2 R1 —— 设计 §2 九类组件落地表

| # | 组件 | 实现位置（`style.css`） | 判定 | 备注 |
|---|---|---|---|---|
| 2.1 | `.topbar` | `:437-449`（sticky + 青色 `scaleX` 生长线 `::before` + `.theme-toggle`） | ✅ 已落地 | 基线 `:17` 被追加段覆盖（P2-5） |
| 2.2 | `.sidenav` | `:451-463`（半透明底 + 三角形 `::before` 指示 + `.cur` 2px 青竖条） | ✅ 已落地 | **优于设计**：设计样例的 `details[open] > summary::before` 是裸选择器（会命中全站 details），实现收窄为 `.sidenav details[open] > summary::before`（`:457`） |
| 2.3 | `.crumbs` | `:466-471`；`tabular-nums` 追加 | ✅ 已落地 | 分隔符与 `<nav>` 类名未动；`.crumbs a:hover::after`（`:471`）在基线 `:213` 的 `::after` 之上合法覆盖 |
| 2.4 | `.prose` + `h2` 编号 | `:474-484`（`counter-reset:sec` + `::before` 编号 + `::after` 下划线 + `h1` 4px 底边） | ✅ 已落地 | 编号是**设计 U3 未决项**，实现已先做（见 §6.4） |
| 2.5 | 表格 | `:486-495`；`position:sticky` 段在 `:127`（同块替换）；`thead th::after`（`:492`）2px 青数据线；`tbody tr:hover` 衬底 | ✅ 已落地 | 表格未上 `clip-path` ✅（遵守 R-13）；字距按偏离③去掉（P2，需目视佐证） |
| 2.6 | 提示块 5 件（blockquote/dead-banner/missing-note/meta/cp-noscript） | `:498-510`（`.dead-banner` `:503`、`.missing-note` `:506`、`.meta` `:508`）、`.cp-noscript` `:334` | ✅ 已落地 | blockquote 左上 L 形角标用 `--cut-bracket-tl` |
| 2.7 | 卡片 `.ccard` 家族 | `:307-330`（`.cgrid`/`.citem[hidden]`/`.ccard` 双层假框/hover 位移/`:focus-visible`/`.cicon` 128px 上限/`.cicon-fb`/`.cname`/`.csub`/`.cstar`） | ✅ 已落地 | `.cicon{width:100%;max-width:128px}`（`:324`）守住 F14 的 128×128 清晰度线 ✅ |
| 2.8 | 角色面板（chips + 网格 + 计数） | `:279-306`（`.cp-*`/`.chip` 6px 切角假框/`aria-pressed` 三处状态/`.cp-count`）；`.cgrid --cell-min:132px` | ✅ 已落地 | 仅读 `aria-pressed`，**未改筛选 JS**（`character-panel.js` 原 68 行 0 删除，diff `+319 −0`）✅ |
| 2.9 | 首页仪表盘 `.dash` | `:533-560`（`.dash-cell` 单角切角 + 假框、`.quick-a` 切角、`.dash-item`/`.dash-empty`/`.dash-tag`） | ✅ 已落地 | `wiki/index.html` 零改动，`class="quick"`/`"quick-a"` 字面量不动 ✅（`[14] quick=True`） |

**R1 汇总：9/9 组件已落地，token 3.5/4 组完整。**

### 3.3 R2 —— 设计 §3 逐条对应

| 设计条目 | 实现 | 判定 |
|---|---|---|
| §3.1 状态机 `IDLE→ENTER(120ms)→HERO→NAVIGATE` | `character-panel.js:316`（入层）→ `:323-325`（120ms 后 `data-state=hero`）→ `:326`（`heroTotal()` 后 `location.assign`） | ✅ 时序一致 |
| `data-state` 五态（`idle/enter/hero/static/exit`） | 只写 `enter`/`hero`（`:211`、`:324`） | ⚠️ 2/5 态（P2-4，仅调试属性） |
| §3.2 时序表（0-120 背板/拉开、40-160 竖轴、120-360 主视觉、160-400 四角 +40、260-420 名字擦除、320-560 数据条 ×3、560-720 扫光、720-840 收束、840 跳转） | 逐帧对照 `style.css:639-654`：`heroBackIn`/`heroWipeIn` 0+120 ✅、`heroSpineIn` 40+120=160 ✅、`heroArtIn` 120+240=360 ✅、`heroFrameIn` 160+240=400 ✅、四角 160/200/240/280 各 +40 ✅、`heroNameIn` 260+160=420 ✅、`heroStatIn` 320/360/400+240=560/600/640 ✅、`heroSweepIn` 560+160=720 ✅、`heroSettleIn` 720+120=840 ✅ | ✅ **9/9 区间吻合**（但时长是硬编码，见 P1-2） |
| §3.2「总时长 CSS 唯一真相源，JS 读 `getComputedStyle`」 | JS 读 ✅（`:134-141`），CSS 该变量 0 引用 ❌ | ⚠️ **P1-2** |
| §3.3 DOM（overlay/stage/frame/spine/art-wrap/name/stats/sweep/hint/status） | `buildOverlay()` `:203-277` 全部建出；四角实际用 4 个 `.hero-br-*` 子元素（设计允「4 个伪/子元素」）✅ | ✅ 落地（`status` 位置修正见 §2.5） |
| §3.4 `sessionStorage` 键 `hsr-hero-v1` | `:91` `var STORE = "hsr-hero-v1"` | ✅ 一致 |
| §3.4 值 = JSON 字符串数组、元素为实体 id | `writeStore` `:123-131` `JSON.stringify([...ids])` | ✅ 一致 |
| §3.4 读失败 → 视为**存储不可用** → 不播 | `:98-121` `catch → null`；`:355` `if (seen === null) return`（原生跳转） | ✅ 一致 |
| §3.4 **在 `enter` 状态写入**（不是动画结束写） | `:320` 在 `startHero` 内、120ms 计时器之前 | ✅ 一致 |
| §3.4 长度 >300 重置、写入包 try/catch | `:126` `if (a.length > 300) a = []`；`:130` catch | ✅ 一致 |
| §3.4 reduced-motion 不写 storage | `:346-350` 提前 return | ✅ 一致 |
| §3.6 4 个无立绘角色（1511/1503/1513/1512）降级 | `:224-225` 判 `iconSrc` 为空 → `:242-245` 走 `.hero-art-sil`（`--ui-sil` data URI，**连请求都不发**） | ✅ 落地（比设计的「`<img>` 404 → error」更省，设计 §3.3 的 `hero-art-fb` 被 `hero-art-sil` 取代，功能等价） |
| §3.6 `character/*.png` 404 → 剪影 | 实现改为「回退已缓存 avatar」 | ⚠️ **P1-3 口径分歧** |
| §3.5 交互矩阵 10 行（首次/缺图/重复/换角色/动画中跳过/键盘 Enter/修饰键/bfcache/无 JS/reduced-motion） | 逐行对照 `onCardClick`（`:329-366`）、`onKeyDown`（`:368-374`）、`onPageShow`（`:376-382`） | ✅ **10/10 对应** |
| §3.5 唯一强制约束「`preventDefault` 只能在 overlay 插入成功之后」 | `:359-365`：`try{ startHero() }catch{ dropOverlay(); return }` 之后才 `:365 preventDefault()` | ✅ **严格执行**（这是我最在意的一条，实现没问题：任何异常路径都放行原生跳转） |
| §3.7 元数据读取顺序 | 实现优先读**卡片 DOM 的 `li[data-element]/[data-path]/[data-rarity]`**（`:252-258`），回退 `.csub` 按 `·` 切；设计只写了「`data-hero-*` → href 推导」 | ✅ 等价且更稳（未申报，见 §6.5） |
| 设计 §3.7「任一解析失败 → 数据条整体隐藏，动画与跳转不受影响」 | `:260-271` `if (shown) stage.appendChild(ul)` | ✅ 一致 |

---

## 4. 复算证据（命令 + 真实输出）

### 4.1 全站校验器（权威口径）

```bash
$ cd /g/HSR && python tools/verify_site.py
=== 静态站回归自检（W-4.6-67） ===
root: G:\HSR
pages: 6685 个生成页
[1] H1: 6685/6685 合规
[2] 面包屑: 6685/6685 合规
[3] titles.js: 6685 条, BOM=0, 井号标题=0, 元信息标题=0, 空分类=0
[4] 死链: report=0, 独立复算=0  (一致=True)
[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0
      说明: 已跳过 CI 构建期生成的图标 <img> 1692 个（src 含 assets/icons/，见工单 §1.2）
[6] 静态检查: esc=True combobox=True listbox=True
[7] 搜索链接编码: 含保留字符 path=4, 空格 path=23; app.js 已按段 encodeURIComponent = True
[8] 未收录链接: report=0, 独立复算=0 (一致=True)
[9] 表格结构: table=9168 thead=9168 紧跟thead=9168 (table==thead>0=True 紧跟==table=True)
[10] 首页可访问名称: aria-label=True label-for=False combobox=True aria-controls=True
[11] 小屏导航: theme.js matchMedia=True max-width:640px=True .sidenav details=True ; style.css 小屏.sidenav{max-height=True
[12] 打印样式: @media print=True 块内 display:none=True
[13] 剧情时间线: 单元=12(带日期=12 带锚点=12) 版本序单调=True | 节点=12 | 仅索引页=True 在prose前=True | timeline.js=True 外链=False
[14] 首页仪表盘: pages=6685(titles=6685 一致=True) latestVersion=4.7 版本数=4 | recent=30 倒序=True 字段齐=True | 容器齐=True quick=True home.js=True stats.js=True 无JS降级=True
[15] 角色直达面板: count=94 items=94 独立复算=94 字段齐=94 逐条比对错=0 url=0 citem=94 卡片href错=0 外链=False/False head-noscript=True 说明=True 缺图img=0 fallback=4 非图标img=0
RESULT: PASS
```

### 4.2 设计 §5 A2/A3 专项（`[5]` **不扫** `assets/*.js`，故手工补测）

```bash
$ python - <<'EOF'  # 把 [5] 同一套正则套到「新增 JS + style.css」
A2 shadow  : []
A2 gradient: []
A2 radius  : ['0','0','0','0','0','0','0','0','0','0']
A2 radius 违例: []
A2 逃逸 linearGradient: 0
A2 逃逸 radialGradient: 0
A2 逃逸 feDropShadow  : 0
A2 逃逸 <filter       : 0
A2 逃逸 filter=       : 0
A2 逃逸 <image        : 0
EOF
```
（10 个 `border-radius` 全在基线行 `:14,46,47,55,60,65,69,70,71,157`，值均为白名单 `0`。）

### 4.3 外链 / 依赖

```bash
$ grep -noE "https?://[^\"')]*" wiki/assets/style.css wiki/assets/character-panel.js | sort | uniq -c
      1 wiki/assets/style.css:425:http://www.w3.org/2000/svg
      1 wiki/assets/style.css:427:http://www.w3.org/2000/svg
$ grep -niE "(src|href)\s*=\s*[\"']https?://|@import|fonts\.googleapis|cdn\." <两文件>
(无输出)
$ grep -niE "XMLHttpRequest|fetch\(|import\(|navigator\.sendBeacon" <两文件>
(无输出)
```
该页实际子资源（未变）：`assets/style.css` ×1、`theme.js` ×1、`character-panel.js` ×1 —— **无新增请求**。

### 4.4 语法与体积

```bash
$ node --check wiki/assets/character-panel.js && echo OK
OK            # ES5 兼容：无 =>/const/let/模板串/可选链（grep 0 命中），零依赖

$ wiki/assets/style.css          旧=18133  新=42756  Δ=+24623  (+136%)
$ wiki/assets/character-panel.js 旧=2148   新=14022  Δ=+11874
```
> 口径说明：`gzip` 在宿主上不可用（`command not found`），**未测压缩后体积**，只报原始字节。

### 4.5 对比度复算（WCAG 2.x 相对亮度，脚本见下）

```
== LIGHT ==  ink/bg=16.79  ink/panel=18.65  ink/panel2=15.60
             ink2/bg=8.87  ink2/panel=9.85  ink2/panel2=8.24
             mute/bg=4.24 <4.5   mute/panel=4.71   mute/panel2=3.94 <4.5
             hi/bg=5.22    hi/panel=5.80    hi/panel2=4.85
             ccard hover 内层=#DDDFE4 ; mute/hover=3.53 <4.5
== DARK  ==  mute/bg=5.51    mute/panel=5.21  mute/panel2=4.84   （全部达标）
             panel(#0C1117)/bg(#06080C) = 1.06:1 ；line/bg = 1.41:1
候选修正：mute → #55606F ⇒ bg 5.75 / panel 6.39 / panel2 5.34 / hover 4.79（四对全 ≥4.5）
```
浅色 hover 内层推导：`rgba(10,13,19,.085)` 叠在 `#F1F3F7` 上 = `#DDDFE4`（`.ccard:hover::after` 用 `--ui-surface-2`）。

### 4.6 数据零改动 / 冻结面实测

```bash
$ for d in wiki/data zh_cn en_us zh_tw ja_jp ko_kr wiki/pages; do ...; done
0 改动: wiki/data
0 改动: zh_cn
0 改动: en_us
0 改动: zh_tw
0 改动: ja_jp
0 改动: ko_kr
0 改动: wiki/pages
$ git status --porcelain -- wiki/build_wiki.py wiki/index.html wiki/assets/
 M wiki/assets/character-panel.js
 M wiki/assets/style.css
$ grep -o 'class="citem"' 角色.html | wc -l                      → 94
$ grep -o '<a class="ccard" href="' 角色.html | wc -l           → 94
$ grep -o 'icon-fallback' 角色.html | wc -l                      → 4
$ grep -o 'class="cicon"' 角色.html | wc -l                      → 90
```

### 4.7 数据面回归（并行只读跑，均通过）

```bash
$ cd zh_cn && python ../scripts/verify_fields.py
异常合计: 0
已知待补充合计: 156        # 既有「待补充」状态，不计异常

$ python scripts/verify_links.py
（exit 0；输出仅为 docs/ 下示例文档里的 `[[wikilink]]` 占位符提示，与本次改动无关）
```

---

## 5. 6 处「相对设计的偏离」逐条判定

> 口径：**可接受 = 实现层修正，理由成立**；**需回改 = 偏离用户口径或破坏硬约束**。

| # | 偏离 | 设计原口径 | 我的裁定 | 依据 |
|---|---|---|---|---|
| ① | token **默认亮**而非暗（`style.css:362` 为亮，暗在 `prefers-color-scheme: dark` `:370`） | §1.1 表格「暗（默认 / 系统暗）」 | **可接受（且是必须做的修正）** | 仓库既有 token（`style.css:1-10`）本就是「亮默认 + `prefers-color-scheme: dark` 覆盖 + `data-theme` 三态」。若照设计把暗设为默认，用户首屏会在 JS 前闪一帧黑底（`theme.js` 是 `defer`），且与既有 20+ 处 `--bg/--ink` 规则的默认语义相反。实现对齐仓库约定 = 对；**设计 §1.1 的极性写错了**，建议 Architect 侧同步更正 |
| ② | 假框内层由半透明 `--ui-surface` 改**不透明** `--ui-panel` | §2.8 `.chip::after` / §2.9 `.quick-a::after` 用 `--ui-surface`（rgba .045/.085） | **可接受** | 内层是 `z-index:-1` 的底，若半透明则等于直接透出页面底色（浅色 `#F1F3F7`，与 `--ui-panel` 只差一点，chip 视觉上会「没有面」）；改不透明才有「描边 + 面板」的双层假框效果。设计 §1.5 T-2 的示例本身用的就是 `--ui-panel`，实现与 T-2 一致 |
| ③ | 去掉 `thead th` 的 `letter-spacing:.02em` | §2.5 `thead th{…letter-spacing:.02em}` | **可接受（理由需补实测）** | 代码注释（`:490`）给的理由是「窄列（属性/值两字列）会折行」。我**没有**复算折行（需浏览器量列宽），因此这条只算「理由合理但未取证」。建议 Tester 在 A12 目视环节顺手截图佐证；若实际不折行，则属于无谓偏离，应恢复 |
| ④ | `role=status` 播报节点挂到 **body**，而非 overlay 内 | §3.3 样例把 `<p class="hero-status sr-only" role="status">` 放在 `aria-hidden="true"` 的 overlay 里 | **可接受（修正了设计的真实缺陷）** | overlay 是 `aria-hidden="true"`（`:210`，设计自己也这么规定），**放进 overlay 的 live region 会被整棵子树屏蔽**，读屏收不到。实现把节点 append 到 `body`（`:289`），且顺序在 overlay 之后（`:316`）→ 兄弟节点，不被屏蔽（§2.5 已核）。设计 §3.3 需按此更正 |
| ⑤ | 网格纹理用**一套中性灰** SVG，而非亮/暗两套 | §1.5 T-3「亮色版把 `%23FFFFFF` 换 `%23000000`」 | **可接受** | `--ui-grid` 全站唯一引用处是 `.hero-overlay`（`:579`），底色恒为 `--ui-bg`；`#7C8798 @ .18` 在 `#F1F3F7` 与 `#06080C` 上都能读出细网格，没必要为此复制整套 token 块（少一份维护面）。六禁仍为 0（§2.1） |
| ⑥ | 扫光 `translateX(-110%)→310%` 且去掉 `mix-blend-mode:screen` | §3.2「-110% → 110%」；§3.3 `.hero-sweep{…mix-blend-mode:screen}` | **可接受** | ① 数学上 110% 不够：条宽 38%，`translateX(110%)` 时左缘=1.178、右缘=1.558…（按自身宽度百分比算）实际会停在**画面内**，收尾拖出一条残影；`310%` 才能彻底扫出，配合 `.hero-overlay{overflow:hidden;contain:layout paint}`（`:578-580`）裁住 ✅。② `screen` 在 `contain:paint` + 不透明底上会把亮色主题的青色洗白、暗色主题发灰，去掉后是可控的纯色窄条，与「不引渐变」的纪律一致 |

**6/6 全部判为「可接受」。无一项需要回改。**

---

## 6. 未申报的偏离（Coder 交付说明里没有、我审查发现的）

> 这节单列，因为「自述不算证据」：偏离要么写进交付说明，要么就由我写进评审。

| # | 偏离 | 位置 | 裁定 |
|---|---|---|---|
| 6.1 | `character/{id}.png` **404 → 回退已缓存 avatar**（而非设计规定的 SVG 剪影） | `character-panel.js:236-239` | ⚠️ **P1-3**：功能上是更优解（有真图优先），但直接与设计 §3.6 / A15 的断言冲突，**Tester 会据此判 FAIL**，必须先统一口径 |
| 6.2 | `.hero-sweep` 从 stage 内部**移到 overlay 层**（全视口高度竖条，不再被切角框裁住） | `character-panel.js:277` vs `style.css:621` | 可接受（横扫更「仪表」，且 `contain:paint` 已裁边）→ 记 P2-7，要求设计文档同步 |
| 6.3 | 元数据**优先读 `li[data-*]`**（`data-element`/`data-path`/`data-rarity`），`.csub` 只作回退 | `character-panel.js:252-258` | 可接受且**优于设计 §3.7**（DOM 里现成的结构化属性比字符串切分稳），建议 Architect 把它写回 §3.7 |
| 6.4 | `h2` 自动编号已实现（设计 **U3** 仍是未决项） | `style.css:474-479` | 需 Lead 追认：该改动会让 **6685 页**的正文小节标题多出 `00/01/…` 前缀（打印/PDF 也带）。若用户不接受，删 `.prose h2::before` 一条即回退（无其它耦合）——但请在合并前拍板 |
| 6.5 | `data-state` 只落地 2 态（设计 5 态） | `character-panel.js:211, 324` | P2-4 |

---

## 7. 未覆盖范围（本环节不做，交由 Tester / Lead）

| 项 | 为什么我没做 |
|---|---|
| 浏览器动态验收 A7 / A8 / A9 / A10 / A11 / A12 / A15 | 需真实 Chromium + reduced-motion 模拟 + `sessionStorage` 观测；且**任务说明 Tester 正在并行跑浏览器验收**，我不重复占用。本报告对可及性/降级的结论均为**静态代码级证据** |
| 600×900 横向溢出（A11） | 需实测 `scrollWidth`；我只能从 CSS 推断不溢出（`.hero-stage` 在小屏改为 `min-width:0;width:100%` + `box-sizing:border-box`，`:669-676`） |
| 真实渲染截图 / 视觉对齐度 | 无浏览器渲染，**不做「好不好看」的裁定**；设计 §2 各组件的视觉一致性只核到「声明是否存在、技法是否正确」 |
| 首屏性能（LCP / FCP） | 未跑 Lighthouse；只报了 CSS/JS 字节数（P2-12），且 `gzip` 不可用 |
| `build_wiki.py` 重建 | 任务明确禁止（会写 `wiki/pages`，与 Tester 冲突） |
| 4 个无立绘角色的真实观感 | 需断网/改文件实测（A15）；我核到「代码路径确实不发请求、走 `--ui-sil` data URI」为止 |

---

## 8. 给 Lead 的待裁定项（按紧急度）

| # | 事项 | 我的建议 |
|---|---|---|
| 1 | **P1-3 / 6.1**：`character/*.png` 404 时到底显示「已缓存 avatar」还是「SVG 剪影」？ | 接受实现（avatar），改设计 §3.6 + A15 口径；同步告知 Tester 别按旧断言判 FAIL |
| 2 | **6.4 / U3**：正文 `h2` 自动编号要不要？影响全部 6685 页可见文案 | 若要「数据感」就留；若在意打印/PDF，趁未合并删一条规则即可。**必须在合并前拍板** |
| 3 | **P1-2**：`--hero-total` 是真旋钮还是文档措辞？ | 优先改实现（把关键帧时长挂到变量），保留设计承诺；成本约 10 行 CSS |
| 4 | **P1-1**：浅色主题 `--ui-mute` 调深（`#55606F`）是否接受？ | 接受；同时把 `.ccard:hover::after` 换成不透明 `--ui-panel-2` |
| 5 | **P2-11**：工作区里那 3 个无关文件（`协作要求与行动准则.md` / `scripts/mimo_batch.py` / `docs/评测_*.md`） | 提交时只 `git add` 显式路径，别扫进去 |
| 6 | 设计文档需回写的 5 处（极性 §1.1、U5 已封住、§3.3 status 位置、§3.7 优先 `data-*`、§3.6 404 口径 + §3.2 旋钮措辞） | 交 Architect 一轮 `docs/designs/site-hero.md` 增补，不必重开阶段 |

---
---

# 第二轮复核（修复后验证）

> 本节为**追加**内容，上文（第一轮）一字未改。只审「本轮新增的修复」＋对上一轮 3 条 P1 逐条判定。

| 项 | 值 |
|---|---|
| 环节 | Reviewer 第二轮（只读） |
| 审查对象 | 修复后的工作区：`wiki/assets/style.css`（708 行 / 44,945 B）、`wiki/assets/character-panel.js`（394 行 / 14,402 B） |
| 对照 | 上一轮本报告 §1（P1-1/P1-2/P1-3）＋ `docs/designs/site-hero.md` §3.2 时序表、附录 R 裁定（R-1…R-9） |
| 复算环境 | `G:\HSR` @ `main` / HEAD `29b51331f`；`git diff --stat` = **2 文件 / +765 −37** |
| 写盘 | 仅本文件本节（追加）。**未改任何仓库文件、未跑 `build_wiki.py`** |
| 审查时间 | 2026-11-14 |

## R0 裁定

> **通过（Pass）** —— 上一轮 3 条 P1 全部「已修」，硬约束重新实测全绿；本轮新增 **0 条 P0 / 0 条 P1**，新增 **8 条 P2**（可排期，不阻塞合并）。

| 关注点 | 判定 | 一句话依据 |
|---|---|---|
| P1-1 浅色 `--ui-mute` 对比度 | **已修** | `style.css:368`/`:387` = `#55606F`；四组实测 **5.75 / 6.39 / 5.34 / 4.79**（全部 ≥4.5）；`:322` 的 `.ccard:hover::after` 已换成不透明 `--ui-panel-2` |
| P1-2 `--hero-total` 真旋钮 | **已修** | `:423` `--hero-stagger:calc(var(--hero-total)/21)`；`:658-674` 全部 16 个 duration/delay 均为 `calc(var(--hero-stagger)*k)`；默认 840ms 下逐格复算与设计 §3.2 **区间 100% 吻合**、末帧止于 840.0 |
| P1-3 图源降级口径 | **已按裁定** | `character-panel.js:243-246` 仍只是撤掉 256px 层露出已缓存 avatar；`:249-252` 剪影仅服务 4 个无图角色 —— 与附录 R-1（`designs:768`）一致 |
| 新问题 | **无 P0/P1** | 六禁 / 冻结面 / 数据零改动 / 零外链 全部重跑通过；新增问题 8 条均 P2 |
| 修复是否引入退步 | 有 3 处**需要记录的副作用** | 打印段对 `.cat/.quick-a/.dash-cell` 无效（P2-B′）、`.hero-hint` 前 700ms 不可见（P2-F）、JS 与 CSS 的 21/3 步长三处耦合（P2-D） |

## R1 上一轮 3 条 P1：逐条判定

| # | 上一轮要求 | 本轮实现（文件:行） | 判定 | 实测证据 |
|---|---|---|---|---|
| **P1-1** | 浅色 `--ui-mute` → `#55606F`（4 组 ≥4.5）；`.ccard:hover::after` 换不透明 `--ui-panel-2` | `style.css:368`（`:root` 亮）、`:387`（`[data-theme=light]`）= `#55606F`；`:322` `.ccard:hover::after{background:var(--ui-panel-2)}`（`#E7EBF2`，不透明） | **已修（含加固）** | WCAG 2.x 复算：`mute/bg #F1F3F7`=**5.75**、`mute/panel #FFFFFF`=**6.39**、`mute/panel-2 #E7EBF2`=**5.34**、`mute/surface-2 over bg #DDDFE4`=**4.79**、`mute/surface over bg #E7E9ED`=**5.25**。对照旧值 4.24 / 3.94 / 3.53 全部脱险。暗色 `#7C8798` 未动：5.51 / 5.21 / 4.84 ✅ |
| **P1-2** | `--hero-total` 成为真旋钮（关键帧 `calc(...)`，默认与旧字面量等价） | `style.css:423` `--hero-total:840ms; --hero-stagger:calc(var(--hero-total)/21)`；`:658-674` 16 条 `calc(var(--hero-stagger)*k)`；`:641-643` 注释写清 k 的来历 | **已修（且优于裁定措辞）** | 见下方 R1.1 时序复算表：`stagger=40.0000ms`，每格区间与设计 §3.2 逐行吻合，`max(delay+dur)=840.0`；把 `--hero-total` 改 630/500/1080ms 时末帧分别止于 630.0/500.0/1080.0（等比缩放 0.75×/0.595×/1.286×），JS `heroTotal()` 读到同一值 → **跳转时点与动画同时缩放**。Lead 裁定 R-7 写的是 `calc(var(--hero-total)*k)`，实现改用派生 `--hero-stagger` 再乘 k —— 数学等价、可读性更好，判「已修」不判「偏离」 |
| **P1-3** | 按 Lead 裁定 R-1：有 avatar 无立绘 → 上采样 avatar；4 个完全无图 → SVG 剪影 | `character-panel.js:233-248`（base=已缓存 avatar，top=256px 立绘，`onerror` 只移除 top 层）；`:249-252`（无 avatar 才 `silhouette()`） | **已按裁定** | 逐行核对与附录 R-1（`designs:768`）措辞一致：4 个无图角色 `imgs=0`、不发请求；有 avatar 无立绘 = 露出 128px 上采样图。**无需再改代码** |

### R1.1 时序等价复算（`stagger = 840/21 = 40.0000ms`）

| 元素 | 实现 `calc` 系数 (delay, dur) | 复算区间 | 设计 §3.2 期望 | 吻合 |
|---|---|---|---|---|
| `.hero-overlay` back / wipe | (0, 3) / (0, 3) | 0–120 / 0–120 | 0–120 背板 + 拉开 | ✅ |
| `.hero-spine` | (1, 3) | 40–160 | 40–160 | ✅ |
| `.hero-art-wrap` | (3, 6) | 120–360 | 120–360 | ✅ |
| `.hero-frame`（框） | (4, 6) | 160–400 | 160–400 | ✅ |
| `.hero-br-tl/tr/bl/br` | (4/5/6/7, 3) | 160–280 / 200–320 / 240–360 / **280–400** | 160–400，四角各 +1 步 | ✅（末角精确收于 400） |
| `.hero-name` | (6.5, 4) | 260–420 | 260–420 | ✅ |
| `.hero-stat` ×3 | (8/9/10, 6) | 320–560 / 360–600 / 400–640 | 320–560，逐个 +40ms | ✅ |
| `.hero-sweep` | (14, 4) | 560–720 | 560–720 | ✅ |
| `.hero-hint` | (17.5, 3) | 700–820 | **设计表无此行** | ⚠️ 新增，见 P2-F |
| `.hero-frame` settle | (18, 3) | 720–840 | 720–840 | ✅ |

> **等价性的口径说明（诚实标注局限）**：仓库内**没有第一轮快照**（`git stash list` 空、无 `.bak`/`.orig`、git 只到 `29b51331f`），因此无法做「旧 CSS vs 新 CSS」的逐字节 diff。本判定用的是「新实现 × 设计 §3.2 区间 × 上一轮报告里引用的旧字面量（delay 240/160/720/320/360/400、四角 160/200/240/280）」三方交叉：delay 序列完全一致、区间逐格一致，故判等价。唯一无法证明的是**四角 duration**（现为 3 步 = 120ms）；若上一轮是 6 步（240ms），则四角出现速度略快 —— 仍在设计区间内，判可接受，建议 Tester 目视确认「四角依次亮起」的观感未变糙。

### R1.2 本轮修复规模（测量值）

| 文件 | 上一轮记录 | 本轮 | 增量 | gzip-9（口径同 R-2） |
|---|---|---|---|---|
| `style.css` | 42,756 B | 44,945 B | **+2,189 B** | 12,595 B |
| `character-panel.js` | 14,022 B | 14,402 B | **+380 B** | 5,577 B |
| 合计 | 56,778 B | 59,347 B | +2,569 B | **gzip 增量 +11,635 B = 11.4 KiB**（R-2 预算 30 KiB ✅ 余量充足） |

## R2 本轮新增修复面清单（我如何在无快照下定位"增量"）

| # | 新增/改动点 | 位置 | 对应 |
|---|---|---|---|
| 1 | 浅色 `--ui-mute` 两处 → `#55606F` | `style.css:368`、`:387` | P1-1① |
| 2 | `.ccard:hover::after` → 不透明 `--ui-panel-2` | `:322` | P1-1② |
| 3 | `--hero-stagger` 改为 `calc(var(--hero-total)/21)` + 说明注释 | `:419-423` | P1-2 |
| 4 | 16 条 hero duration/delay 改为 `calc(var(--hero-stagger)*k)` | `:658-674` | P1-2 |
| 5 | `@media (prefers-reduced-motion: no-preference)` 包裹 9 组关键帧 + 全部动画声明 | `:644-675` | D-3 |
| 6 | `--ui-topbar-h` 算式推导 + `thead th{top:var(--ui-topbar-h)}` | `:404-410`、`:129` | D-1（P1-A） |
| 7 | 追加 `@media print` 段（`.topbar{display:none}`，顺序覆盖不用 `!important`） | `:699-708` | D-2（P2-B） |
| 8 | JS：`DEFAULT_MS`、`heroTotal()` 注释、新增 `heroEnterMs()=heroTotal()/7` | `character-panel.js:92`、`:133-149`、`:332` | P1-2 的 JS 侧 |
| 9 | （疑似本轮）`.hero-hint` 新增 700–820ms 淡入 | `style.css:674` | 见 P2-F |

## R3 新增修复逐项复核（含定级）

### P1-A `--ui-topbar-h` 用算式推导 —— 定级 **P2**（当前值正确，机制脆弱）

```css
/* style.css:404-410 */
--ui-topbar-h:calc(var(--sp-2) * 2 + 12px + var(--ui-hair) * 3 + var(--fs-1) * 1.6);
```

**先判「对不对」**：逐项还原 `.topbar` 的真实盒高 → `padding 8+8` + `border-bottom 1` + `.theme-toggle` `padding 6+6` + `border 1+1` + 行盒 `13×1.6=20.8` = **51.8px**，与算式一致 ✅；且全站 topbar 结构单一（`build_wiki.py:554` 与 `wiki/index.html:6` 同构，6685+1 页只有一个 `.theme-toggle`），不存在「首页多个按钮导致高度不同」的隐患。**故不是 P1。**

**问题在可维护性**：`12px`、`1.6`、`*3`（3 条发丝线）是**镜像字面量**，不是从 `.theme-toggle` 的声明里取来的。注释声称「上面任一 token 变动，让位高度自动跟随」——这只对 `--sp-2 / --fs-1 / --ui-hair` 成立。举例：把 `.theme-toggle{padding:6px 12px}` 改成 `4px 10px`，`--ui-topbar-h` 仍算 51.8，而真实高度变 47.8 → 表头吸附后**上沿被顶栏盖住 4px**，且没有任何测试会红。

**替代建议（按成本排序，任选其一）**：
- **① 最小改动 · 仍纯 CSS**：把剩余字面量 token 化并单点定义 —— `--ui-toggle-pad-y:6px; --ui-topbar-line:1.6; --ui-topbar-hair-n:3;`，然后 `.theme-toggle{padding:var(--ui-toggle-pad-y) 12px;line-height:var(--ui-topbar-line)}`，算式改用这三个 token。这样「改一处、两处同步」变成结构性保证。
- **② 真·单一真相源 · +1 行 JS**：`theme.js` 已在全站每页 `defer` 加载，加 `root.style.setProperty('--ui-topbar-h', topbar.offsetHeight + 'px')`（`load` + `resize`），CSS 的 `calc` 保留为无 JS 兜底。优点：对用户字号缩放、系统字体、以后给 topbar 加第二个控件全部自动正确。
- 另记一处**双口径**：同一概念（给 sticky 顶栏让位）现在有两个数 —— `:129` 用 `51.8`（变量），`:131` `[id]{scroll-margin-top:64px}` 仍是写死 `64`。64 > 51.8 不会裁内容，但建议下一轮统一成 `calc(var(--ui-topbar-h) + var(--sp-3))` 或注释说明「64 含 12px 余量」。

### P2-B 打印覆盖 —— 定级 **通过**，但发现**同一缺陷的残留分支**（P2-B′）

- **无 `!important`**：`grep -n "!important" wiki/assets/style.css character-panel.js` → 仅 `:81`、`:124` 两处**基线**（`prefers-reduced-motion: reduce` 的 `*` 兜底），本轮新增段 **0 处** ✅
- **顺序覆盖成立**：`.topbar` 的 `display` 声明共 4 处 —— `:17 flex`（基线）、`:143 none`（基线 print）、`:450 flex`（R1 屏幕段）、`:704 none`（本轮 print 段）。同特异度（`.topbar` 0,1,0）+ 本段位置最靠后 → 打印态 `none` 生效 ✅（`verify_site [12] @media print=True 块内 display:none=True` 也仍 PASS）
- **P2-B′（新）**：`:707` `.ccard,.chip,.cat,.quick-a,.dash-cell{background:transparent}` 对 **`.cat`/`.quick-a`/`.dash-cell` 无效** —— 这三个元素自身没有 `background`（`style.css:102`、`:561`、`:550`），它们的「面」全在 `::before`（`--ui-line`）与 `::after`（`--ui-panel`，暗色 `#0C1117` 不透明）。`:345` 的老打印段只清了 `.ccard`/`.chip` 的伪元素，没覆盖这三个。结果：**暗色主题 + 勾选"背景图形"打印首页**时，分类卡/快速访问/统计块仍是深色实心块 —— 正是 D-2 要治的那类缺陷，只是换了个组件。建议在 `:703-708` 补一行（与 `:345` 同构）：
  `.cat::before,.cat::after,.quick-a::before,.quick-a::after,.dash-cell::before,.dash-cell::after{background:transparent;clip-path:none}`
- 上一轮 P2-10（`.ccard` 打印退化为 1px 黑框）**仍开着**，属 P2 未处理，不算回归。

### P2-C `prefers-reduced-motion: no-preference` 包裹完整性 —— 定级 **通过**

脚本化核验（括号配对定位到块行区间）：

```
no-preference 块：#644..#675
hero @keyframes 9 个 → BackIn/645 WipeIn/646 SpineIn/647 ArtIn/648 FrameIn/650 NameIn/651 StatIn/652 SweepIn/654 SettleIn  全部 inBlock=True
hero animation 声明 14 条（658×2, 660, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674）                     全部 inBlock=True
块外 hero animation 声明：[]（0 条）
```

- ✅ **9/9 关键帧 + 14/14 动画声明全在块内，块外 0 残留**（上一轮 Tester D-3 报的正是这块缺陷，已闭合）。
- ✅ 仓库内已有 3 处同款写法（`:200`、`:205`、`:233`）→ 属**沿用既有约定**，不是新发明的机制。
- ⚠️ **副作用（P2，可接受）**：把关键帧一起搬进 `@media` 后，**不识别该媒体特性的老浏览器**（IE11 / Safari <10.1）会整块跳过 → 无关键帧、无动画声明；而 JS 的 `matchMedia('(prefers-reduced-motion: reduce)')` 在那里恒为 `false` → 仍插 overlay。降级结果是「静态 overlay 停 840ms 再跳转」，不空白、不报错（`.hero-overlay` 基础规则没有 `opacity:0`，`from{opacity:0}` 只由动画提供）。判接受，不必改；若要更稳，可把关键帧留在块外、只把 `animation` 声明放进块内。
- 另：`.hero-art-top{transition:opacity var(--t-2) linear}`（`:618`）在块外 —— reduce 下 overlay 根本不建（`character-panel.js:353-357` 提前 return），且 `:81`/`:124` 有 `*{transition:none!important}` 兜底，无实际影响。

### P2-D JS `heroEnterMs() = heroTotal()/7` 与 CSS 的 21 步自洽性 —— 定级 **P2（低风险静默漂移）**

- **当前自洽**：CSS `--hero-stagger = total/21`，`enter` 段 = 3 步 → `3/21 = 1/7`；默认 840ms 时 **CSS 3 步 = 120.0ms，JS `840/7` = 120.0ms**，完全对齐（复算见 R1.1）。
- **漂移风险**：`21`、`3`、`7` 三个数现在是**三处各自硬编码**（`:423` 注释、`:423` 的 `/21`、`:658-659` 的 `*3`、JS `:148` 的 `/7`）。谁把基准步数改成 24（例如加一步）而忘了 JS，`data-state` 的 `enter→hero` 切换点就悄悄错位。
- **风险被限制在"低"**：`data-state` 在 CSS 里**0 引用**（`grep -n "data-state" style.css` → 无输出，只有 JS 写它）→ 错位纯属调试属性偏差，无视觉后果。故 **P2**。
- **建议（一行级）**：在 `:root` 加 `--hero-enter:calc(var(--hero-stagger) * 3)`，JS 改为读 `--hero-enter`；这样「3 步」只存在一次，21→24 这类改动对 JS 透明。（顺带可让 JS 读 `--hero-stagger` × 3，效果相同。）
- **同族 P2-E**：`heroTotal()` 用 `parseFloat(getPropertyValue('--hero-total'))`，只认裸 `ms` 数字。若维护者写成 `0.84s` → `parseFloat` = 0.84 → `n>0` 通过 → **0.84ms 后立刻跳转**；若写成 `calc(840ms)` → `parseFloat` = `NaN` → 静默回落 840。建议 JS 加单位判断（`/ms$/` 直取，`/s$/` ×1000，否则回落默认）或在注释里写明「本变量必须是裸 `ms` 字面量」。

### P2-F `.hero-hint` 新增 700–820ms 淡入 —— 定级 **P2（可用性小退步 + 设计表未同步）**

`:674` `.hero-hint{animation:heroBackIn calc(var(--hero-stagger)*3) var(--ease) calc(var(--hero-stagger)*17.5) both}`，`both` 含 **backwards fill** → 0–700ms 期间按 `from{opacity:0}` 渲染。上一轮实现里「Esc / 点击 跳过」是 t=0 就可见的；现在**前 700ms 看不到跳过提示**（而 overlay 从 t=0 就可以点击/Esc）。设计 §3.2 时序表（`designs:436-448`）也**没有这一行**。

建议：把它提前到与名字同批（delay 3 步），或去掉 `both` 的前向填充改成 `forwards`，或干脆不动画。若保留现设计，需 Architect 在 §3.2 补一行并在 Tester A10（Esc 跳过）口径中注明「提示 700ms 后才可见」。

## R4 死 token 清单（P2）

脚本枚举 `style.css` 全部 67 个 `--x:` 定义并统计 `var(--x)` 引用（引用数 0 = 死）：

| token | 定义行 | 现状 | 备注 |
|---|---|---|---|
| `--ui-warn` | `:370`(亮)、`:379`(系统暗)、`:389`(`data-theme=light`)、`:397`(`data-theme=dark`) | 0 引用 | 设计 §1.1 规定的 14 槽之一，建议**保留并标「预留」**（不删） |
| `--sp-1` | `:411` | 0 引用 | 与上一轮清单相比**新变死**；但上一轮清单文字称「8 个」却只列 7 名，**不排除当时就漏列**，无法证明由本轮引入 |
| `--sp-7` | `:412` | 0 引用 | 预留 8px 栅格末段 |
| `--sp-8` | `:412` | 0 引用 | 同上 |
| `--fs-6` | `:414` | 0 引用 | 40px 字号阶未用 |
| `--t-0` | `:416` | 0 引用 | 0ms |
| `--t-1` | `:416` | **0 引用（本轮新增死）** | 与 Coder 自述一致：120ms 的最后一个消费者被 P1-2 的 `calc(stagger*3)` 取代 |
| `--t-5` | `:416` | 0 引用 | 700ms |

- **合计 8 个**（上一轮 7 个 → 本轮 `--hero-stagger` 转活、`--t-1` 转死，净持平）。
- 另：设计 §1.3 的 `--ui-num` **仍未定义**（`var(--ui-num)` 0 次），实现用 19 处直写 `font-variant-numeric:tabular-nums` —— 上一轮 P2-6 未处理，仍在。
- **处置建议**：时间/间距/字号阶属「刻度表」，建议**保留定义 + 行尾加 `/* 预留：暂无消费者 */`**（删了以后想用得重造）；`--t-1`/`--sp-1` 若确无规划则删（它们不属于「刻度必须连续」的语义）。`--ui-warn` 保留。
- 正向确认：`var()` 引用但从未定义的 token = **0 个**（不存在「用了没定义」的悬空引用）。

## R5 硬约束复查（本轮重新跑，不看历史）

| 项 | 命令 | 真实输出 | 判定 |
|---|---|---|---|
| 全站校验器 | `python tools/verify_site.py` | `[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0`；`RESULT: PASS` | ✅ |
| `[11]`/`[15]` 冻结面 | 同上 | `[11] … style.css 小屏.sidenav{max-height=True`；`[15] count=94 items=94 逐条比对错=0 url=0 citem=94 卡片href错=0 外链=False/False head-noscript=True 缺图img=0 fallback=4 非图标img=0` | ✅ |
| 冻结面字面量（直接 grep 生成页） | `cd wiki/pages/character && grep -o ... 角色.html \| wc -l` | `class="citem"`=**94**、`<a class="ccard" href="`=**94**、`icon-fallback`=**4**、`class="cicon"`=**90**（90+4=94）；`<noscript><style>.cp-filters{display:none}</style></noscript>`=**1** | ✅ 未动 |
| 小屏冻结串 | `grep -n "sidenav{max-height" style.css` | `140:@media (max-width:640px){ .sidenav{max-height:40vh;overflow:auto} }` | ✅ 未动（新增小屏段是 `:690 @media (max-width:640px){` 带空格、不含该串） |
| `zh_cn` 数据零改动 | `cd zh_cn && python ../scripts/verify_fields.py` | `异常合计: 0` / 已知待补充合计: 156（既有状态） | ✅ |
| 五语 + 生成物零改动 | `git status --porcelain -- <目录>` | `wiki/data` 0、`zh_cn/en_us/zh_tw/ja_jp/ko_kr` 各 0、`wiki/pages` 0、`wiki/index.html` 0、`wiki/build_wiki.py` 0、`wiki/assets/theme.js` 0 | ✅ |
| 死链 | `python scripts/verify_links.py` | exit 0（输出仅为 `docs/` 内示例文档的 `[[wikilink]]` 占位提示，与本工单无关） | ✅ |
| 六禁（源码全文，含注释） | `grep -niE "box-shadow\|linear-gradient\|repeating-linear\|radial-gradient\|conic-gradient" style.css character-panel.js` | **无输出** | ✅ |
| 变相绕过 | `grep -niE "linearGradient\|radialGradient\|feDropShadow\|<filter\|filter=\|drop-shadow\|backdrop-filter\|text-shadow\|<image"` | **无输出** | ✅ |
| 外链 | `grep -noE "https?://[^\"')]*"` | 仅 2 处：`style.css:438`、`:440` 的 `http://www.w3.org/2000/svg`（`data:` SVG 的 xmlns **字面量，不请求**，同上一轮结论） | ✅ |
| 网络 API | `grep -niE "XMLHttpRequest\|fetch\(\|import\(\|sendBeacon"` | **无输出** | ✅ |
| `border-radius` | `grep -n border-radius style.css` | 10 处，全在基线行（`:14,46,47,55,60,65,69,70,71,159`），值均 `0`；新增段 0 处 | ✅ |
| `!important` | 同上 | 仅 `:81`、`:124`（基线 reduce 兜底），本轮新增 0 处 | ✅ |
| JS 语法 | `node --check character-panel.js` | `OK`（ES5 语法，零依赖） | ✅ |
| CSS 结构 | 括号平衡复算 | `brace balance: 0` / `paren balance: 0` | ✅ |

## R6 本轮新发现的问题汇总（全 P2，共 8 条）

| # | 位置 | 问题 | 定级 | 建议 |
|---|---|---|---|---|
| R2-1 | `style.css:404-410`、`:129`、`:131` | `--ui-topbar-h` 算式正确但脆弱：`12px`/`1.6`/`*3` 是镜像字面量，注释承诺「任一 token 变动自动跟随」过度；与 `[id]{scroll-margin-top:64px}` 双口径 | P2 | 见 §P1-A 的 ①② 方案 |
| R2-2 | `style.css:707` | 打印段对 `.cat/.quick-a/.dash-cell` **无效**（三者自身无 background，面在伪元素上）→ 暗色 + 背景图形打印仍出深色块（D-2 残留分支） | P2 | 补一行伪元素 `background:transparent;clip-path:none` |
| R2-3 | `character-panel.js:148` vs `style.css:423/:659` | 步长 `21/3/7` 三处硬编码，改基准步数会静默漂移（仅影响 `data-state` 调试属性） | P2 | CSS 出 `--hero-enter:calc(var(--hero-stagger)*3)`，JS 读它 |
| R2-4 | `character-panel.js:134-142` | `parseFloat` 只认裸 `ms`；写成 `0.84s` 会立刻跳转，`calc()` 会静默回落 840 | P2 | 加单位分支 + 注释约束「必须是裸 ms 字面量」 |
| R2-5 | `style.css:674` | `.hero-hint` 700–820ms 淡入 + `both` 前向填充 → 前 700ms 看不到「Esc / 点击 跳过」；设计 §3.2 无此行 | P2 | 提前到 3 步，或改 `forwards`，或在设计表补一行 |
| R2-6 | `style.css:370/411/412/414/416` | 8 个死 token（含本轮转死的 `--t-1`）；设计 §1.3 的 `--ui-num` 仍未定义 | P2 | 保留刻度表 + 行尾标「预留」；`--t-1`/`--sp-1` 可删 |
| R2-7 | `designs/site-hero.md:685`（A15） | 附录 R-1（`:768`）已判 `character/*.png` 404 走 avatar，但 A15 正文**仍写「剪影显示」** —— 文档内部自相矛盾，Tester 若按 A15 字面测仍会误判 FAIL | P2（文档） | Architect 一行改写 A15 + `:148` `--hero-stagger` 由 `40ms` 改为「= total/21 派生」 |
| R2-8 | `style.css:594` | `.hero-overlay[hidden]{display:none}` 仍是死规则（JS 从不设 `hidden`） | P2 | 沿用上一轮 P2-3，删掉或改用 `hidden` |

## R7 未决（交 Lead 裁定）

| # | 事项 | 我的建议 |
|---|---|---|
| 1 | R2-1 的机制选择：纯 CSS 全量 token 化（①）还是 +1 行 JS 量测（②） | 建议 ①（不引入运行时依赖，代价 4 行 CSS）；若接受「JS 只读测量」则 ② 彻底解决 |
| 2 | R2-2 打印残留是否本轮就补（3 行 CSS，无风险） | 建议本轮补，与 D-2 同属打印口径收口 |
| 3 | R2-5 `.hero-hint` 时序：提前 vs 保持 vs 去掉动画 | 建议提前到 3 步（跳过提示应对齐"可点击"的时点） |
| 4 | R2-7 设计文档 A15 / `--hero-stagger` 两处措辞 | 交 Architect 一轮增补（一行一处），避免 Tester 按旧断言误判 |
| 5 | 上一轮 P2-1/P2-2/P2-8（播报节点泄漏、live region 首播、`nav` 幂等超时） | 仍在，本轮未动，建议排到下一个工单 |

## R8 本轮局限（诚实标注）

| 项 | 说明 |
|---|---|
| 无第一轮快照 | 仓库/git 均无 round-1 版本（`git stash` 空、无备份文件），「新增修复 diff」是**按当前源码 + 上一轮报告的引用值 + 设计附录 R** 三方交叉重建；四角 duration 的等价性无法逐字节证明（见 R1.1 口径说明） |
| 浏览器行为 | 未跑 Chromium（任务要求 Tester 并行跑）。以下仅静态判定、需 Tester 实测复核：① `animation` 简写里两个 `calc()` 时间值被正确分配为 `duration`/`delay`（尤其 Safari）；② 表头吸附位在 4 种主题 × 滚动态下不压字；③ `.hero-hint` 700ms 前的不可见性 |
| `gzip` | 宿主无 `gzip` 命令，用 Python `gzip.compresslevel=9` 复算（口径与 R-2 的 +10.2 KiB 一致，本轮 +11.4 KiB） |
| `build_wiki.py` | 按任务要求**未运行**（会写 `wiki/pages`，与 Tester 冲突） |
