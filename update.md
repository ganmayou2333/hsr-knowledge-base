# 更新日志（update）

> 本文件记录崩坏：星穹铁道资料库（Obsidian）的历次更新内容与时间。
> 最近更新：2026-10-04

## 2026-10-04 19:30

**W-4.6-87 收尾：Wiki 策展页同步（本轮补 W-4.6-87 + 页数口径澄清）**

- **`更新日志` 补本轮**：新增「首页改为仪表盘」条目，并写明**未动 URL / 分类 / 语言与版本切换**及其三项实测约束。
- **`Home` 补口径澄清（防误读）**：vault 表写 **6,668**、线上站点实际 **6,500** —— 因为 `*/quest/剧情文本/`（168 文件）按 D-020/D-025 **不入库**、链接优雅降级（D-044）。已加显式说明块，避免读者把两个页数当成笔误；并注明首页仪表盘的「收录 N 页」即**线上实际页数**。
- **`路线图与待补` 补工程项 3**：「信息架构对齐 nanoka.cc」—— 首页仪表盘**已完成**；剩余三项各带实测前置（`simulated` **414 个实体 ID 冲突**、本库 7 个类别在 nanoka 无对应、五语建站 **30,117 页**）。
- **同批更正**：`update.md` 的 W-4.6-87 条目原写「未 push」已失真 → 改为记录实际推送 `ec5aa93da..5e89b58ee` 与线上复测结论。
- **已 push**：主库 `5e89b58ee..1e63bcb79 main -> main`；Wiki 仓库 `23f4cf9..bf911d9 master -> master`。
- **Lead 独立验证（未采信执行方/自述）**：`git ls-remote` 两个仓库 → `refs/heads/main = 1e63bcb79…`、`refs/heads/master = bf911d9…`；`git show origin/master:<page>` 与 `tools/github-wiki/<page>` **归一化行尾后 8/8 一致**、`ls-tree` **恰好 8 页无多余**；GitHub 渲染页实际抓取命中：更新日志含 `首页改为仪表盘`/`30,117`/`414`/`最新收录`，Home 含 `6,500`/`不是笔误`/`优雅降级`，路线图含 `信息架构对齐`/`414 个实体 ID 冲突`；策展稿禁词与图片标签扫描 **0 命中**。

## 2026-10-04 17:05

**W-4.6-87：首页改成 nanoka.cc 式仪表盘（方案甲）—— Lead 实现与实测**

- **背景（用户要求）**：参考 nanoka.cc 的组织方式。Lead 用 `tools/render_fetch.py` 渲染取证实测其 HSR 站结构：**9 个顶层路由**（`/character` `/lightcone` `/relic` `/diff` `/achievement` `/item` `/monster` `/maze` `/currency`）+ **扁平两层详情 URL**（`/character/1511`）+ 顶栏语言/版本切换 + **首页仪表盘**（最新数据版本 / 快速访问 / 新增角色·光锥·遗器·敌对物种·物品分区）。对照我方：13 个顶层类别、**三层**详情 URL（`/character/丰饶/1105.html`）、无语言/版本切换、首页为 Hero+搜索+分类 bento。
- **用户拍板走「方案甲」**：只做**首页仪表盘 + 顶栏概览条**；**不动 URL、不动顶层分类、不加语言切换、不加假版本切换器**。
- **可行性核查（实测，推开三个硬约束 —— 这也是没做 A/B/D-2 的依据）**：
  1. **「数据版本切换」做不了**：库内是**单一快照**（`数据版本：4.5` 3,847 个 / `4.6` 2,494 个 / `3.6` 1 个，是同一快照内的来源差异），**无** `v4.5/`、`v4.6/` 版本化目录 → 硬做即**假切换器**，违反零编造。
  2. **URL 扁平化只能做一半**：`character` 93/93、`lightcone` 170/170、`relic` 62/62、`items` **3718/3718 唯一（0 冲突）**；但 `simulated` **1370 个带 ID 文件只有 956 唯一 → 414 个冲突**（ID 是 `1/3/17` 这类分类编号）→ 全局扁平化会互相覆盖（D-041 同类事故）。
  3. **语言切换 = 五语建站 = 30,117 页**（现 6,668），且四语镜像已确认存在「镜像未本地化」。
- **交付（`git status --porcelain` 实测，5 个文件）**：`wiki/build_wiki.py`（新增 `stats.js` 生成 + `DIR_LABEL` 分类显示名）、`wiki/index.html`（仪表盘结构）、`wiki/assets/home.js`（新增，只在首页引入）、`wiki/assets/style.css`（仪表盘样式）、`tools/verify_site.py`（新增 **[14] 首页仪表盘**）。
- **数据层**：`build_wiki.py` 解析每个文件的 `创建时间` / `更新时间` / `数据版本`（本就已在读 head，成本≈0），输出 `wiki/data/stats.js`（**不动 `titles.js`** → 搜索逻辑零风险）。解析失败则**不写文件 + WARN**，构建照常成功（延续 D-044 降级纪律）。
- **⚠️ 一处口径纠错（Lead 自查）**：初版用「**出现最多的版本**」当首页「数据版本」，算出 **4.5**（3,847）—— 与 README 的 **4.6** 基线口径**矛盾**。改为「**库内最高版本**（4.6）」+ **并列展示完整分布**（4.5×3,847 ｜ 4.6×2,494 ｜ 3.6×1）与覆盖率（带版本标记 6,342/6,668、带时间标记 **6,668/6,668**），单值不再造成误读。
- **一处视觉瑕疵修正**：最新收录的分类标签初版直接用了**目录名**（`items` / `stages` / `character`），与 `音乐` 不一致 → 改为从既有 `SIDENAV` 标签表派生显示名（`items→物品`、`stages→关卡`），**不新增手写映射**。
- **实测数据**：`创建时间` **100%**、`更新时间` **100%**、`数据版本` **95.1%**；更新日期分布 10-03 **17** / 10-02 **190** / 10-01 **244**；最新收录 Top1 = `行于命途2` @ 2026-10-03 23:22。
- **Lead 独立验收（全部亲跑；起本地 `http.server 8788` + 真实 Chrome）**：
  | 验收器 | 结果 |
  |---|---|
  | `tools/verify_site.py` | **RESULT: PASS**（[1]–[14]）；`[14] pages=6668(titles=6668 一致=True) latestVersion=4.6 版本数=3 recent=30 倒序=True 字段齐=True 容器齐=True quick=True home.js=True stats.js=True 无JS降级=True` |
  | `.tmp_build/verify_dashboard_live.py`（D1–D9） | **RESULT: PASS**：概览条三值与 `stats.js` 逐项一致（4.6 / 6,668 / 2026-10-03 23:22）；版本分布与覆盖率已填；最新收录 **12 条倒序**、首条日期==`updatedMax`；**首条真实点击跳到 `行于命途2` 页**；快速访问 4 链接全 **200**；390×844 `scrollWidth=390=innerWidth`；**禁用 JS 后降级文案可见 + 快速访问 4 + 分类 bento 13**（页面仍可用）；外链 **0**；**回归：搜索输入「真珠」仍返回 2 条** |
  | `.tmp_build/verify_timeline_live.py` / `verify_motion_live.py` | 回归 **T1–T9 / M1–M7 全 PASS**（首页改动未影响时间线与动效） |
  | 静态回归 | `build_wiki` 页 **6668** / 链接 **96564** / **死链 0** / 未收录 **0**；`verify_links` **exit 0**；`verify_fields` **异常 0 / 待补充 156**；五语言规模 **6668/5871/5867/5864/5847** 不变 |
  | 目视 | 全页截图（存**仓库外** `%TEMP%`，图片零入库）：概览条 / 版本分布 / 快速访问按钮 / 最新收录 12 行（中文分类标签 + 日期右对齐）/ 搜索 / 13 分类 bento —— Swiss 风格一致 |
- **明确未做（用户已确认排除）**：URL 扁平化、顶层分类重排、语言切换、**假版本切换器**。
- **已 push（用户放行）**：`ec5aa93da..5e89b58ee main -> main`；线上端到端复测 **仪表盘 D1–D9 / 时间线 T1–T9 / 动效 M1–M7 全 PASS**（线上页数 **6,500**，与纯净检出产物一致）。

## 2026-10-04 16:40

**W-4.6-86：两仓库「全部 push」完成 + 远端侧独立验证（Lead 亲验，不采信执行方自述）**

- **推送范围（两次主库 + 一次 Wiki 仓库）**：
  | 目标 | 推送 | 结果 |
  |---|---|---|
  | 主库 `origin/main` | `a712cf847..c8961cd8f` | 成功后 `HEAD == origin/main == c8961cd8f` |
  | Wiki `*.wiki.git` `master` | `a8aea6f..23f4cf9` | 成功后 `origin/master == 23f4cf90d`（默认分支是 **master**，非 main） |
- **推送途中的网络故障（如实记录）**：主库首次 push 报 `RPC failed; HTTP 408`、其后 `502`，**第 3 次重试成功**；`raw.githubusercontent.com` 连续 `502`/超时。→ **瞬时网络故障，不是仓库问题**；重试与换判据后全部取到。
- **策展稿同步前的纠错**：把公开 Wiki 稿补齐到实情时，我先写的镜像残留数字是 `ja 40 / ko 42 / zh_tw 2`（来自中间口径 C），**用定稿清单复算后改回 `ja 38 / ko 40 / zh_tw 1 = 79 文件`**（225 行 / 74 标记）—— 再次印证「数字不得手写，必须复算」。
- **Lead 独立验证（全部亲跑，未采信豆包自述）**：
  | 项 | 判据 | 结果 |
  |---|---|---|
  | 主库远端 | `git ls-remote` | `c8961cd8f2a919cba2a2988fa6a205d66d6ef790  refs/heads/main` ✅ |
  | Wiki 远端 | `git ls-remote` | `23f4cf90d9c41b1fb2fee1bdceb9dc1e64176cf4  refs/heads/master` ✅ |
  | Wiki 内容一致性 | `git show origin/master:<page>` vs `tools/github-wiki/<page>`（归一化行尾后） | **8/8 一致**、`ls-tree` 无缺失页、无多余页 ✅（首轮 DIFF 是 **CRLF 假警报**，已归一化排除） |
  | Wiki 渲染修订 | 抓 4 个页面 HTML 查关键词 | 「更新日志」含 `来源表达残留清零`/`剧情时间线`/`站点动效` + `225`/`74`/`90`；「Home」含 `6,668`/`5,871`/`5,864`/`5,847`/`30,117`；「路线图与待补」含 `派生镜像未本地化`；`_Sidebar` 可达 ✅ |
  | Pages | HTTP 探测 | 首页 **200**、`quest/索引` **200**（`timeline-root` 在、`tl-item=12`）✅ |
  | 工作区 | `git status` | 仅 2 个刻意不入库的用户文件（`docs/评测_MiMo…md`、`scripts/mimo_batch.py`）✅ |
- **执行方独立复核（旁证）**：豆包桌面版 job `W4686`（`started → 30% → 70% → done`），自述 8/8 通过、主库 HEAD `c8961cd`、Wiki 8 页齐、规模表 30,117、路线图第 8 条、剧情索引 12 条。**仅作旁证** —— 结论以本表 Lead 亲测为准。
- **口径登记**：Wiki 策展稿的单一真相仍在主库 `tools/github-wiki/`；Wiki 只放入口不放正文（5,000 文件软上限 + 扁平命名空间重名，见 `docs/github_wiki可行性评估.md`）。

## 2026-10-04 16:30

**W-4.6-85：剧情界面新增「版本轴时间线」+ 全站动效（6 项）—— Lead 实现与实测**

**一、剧情时间线（用户拍板：*在剧情界面做时间线功能，不重写 worldview/剧情时间线.md*）**

- **位置**：`wiki/pages/quest/索引.html`（侧边导航「剧情」的入口页），插在 `<div class="prose">` **之前**。
- **数据源唯一且已入库**：`zh_cn/quest/主线任务.md` —— 机械解析 12 个剧情单元的 `## 章节标题`、`### 章节名`、`### 版本`（含**官方日期区间**）、`### 子任务列表`；**零新增手写内容**，末尾「待补充」小节排除。该文件是**入库文件**（`.gitignore` 只忽略 `quest/剧情文本/`）→ GitHub Pages/CI 同样有数据（不重蹈 D-044 的坑）。
- **实测解析结果**：**12 单元 / 90 个子任务 / 大版本段 1.x–4.x / 版本序单调**。单元：序章 1.0、第一章 1.0~1.1、第二章 1.2~1.3、幕间一 1.4、幕间二 1.5、幕间三 1.6、第三章 2.0~2.3、幕间四 2.6、幕间五 2.7、第四章 3.0~3.7、终幕 3.8、第五章 4.0~。
- **一个真实发现**：文档里是**主题序**（幕间一 1.4 排在第二章 1.2~1.3 之前），时间线按**版本号排序**后才是官方发布顺序 —— 这正是时间线的价值；卡片上仍标注所属篇章。
- **静态优先的降级设计**：时间线本体、版本轴、子任务展开（原生 `<details>`）**全部由 Python 静态渲染** → **无 JS 也可读**；`assets/timeline.js` 只做静态做不到的一件事 —— **按 1.x/2.x/3.x/4.x 筛选**，且筛选条由 JS 动态插入，**无 JS 时不会留下点了没反应的死按钮**。
- **配套小改进**：`build_wiki.py` 的 `md_to_html` 现在给标题生成**锚点 id**（同页去重），时间线卡片因此能直接跳到 `主线任务` 页面对应章节小节。
- **解析缺陷（Lead 自查并修）**：① `4.0~（2026-02-13 ~ ）` 这种**开区间**未匹配 → 漏掉第五章；② `章节名` 用 ` / ` 分隔的多名称被当成单行 → 第四章只取到 1/8。两处修后单元数 11 → **12**。

**二、全站动效（用户选「推荐套」6 项，**纯 CSS**，未新增 JS 文件）**

| # | 效果 | 实现 |
|---|---|---|
| ① | 正文区块错峰入场（h1 → 时间线 → 正文 → 元信息，60ms 步进） | 模板加 `.mv` + `--i`，复用既有 `@keyframes riseIn` |
| ② | 时间线竖轴从 0 长到满高（`scaleY`，`transform-origin:top`） | `.timeline .tl::before` + `@keyframes axisGrow` |
| ③ | 链接 hover 下划线**从左展开** | `::after{transform:scaleX(0→1)}`，只给短链接（crumbs/pager/搜索/侧栏/时间线标题），避免正文长链接跨行错位 |
| ④ | 按钮按下 120ms 微反馈 | `:active{transform:translateY(1px)}` |
| ⑤ | 滚动揭示正文小节 | `@supports (animation-timeline: view())` + `@keyframes sectionIn`；不支持的浏览器**自动无动效** |
| ⑥ | 主题切换颜色 160ms 过渡 | `body/.sidenav/.meta/blockquote/th` 等少量元素 |

- **纪律**：全部只用 `transform/opacity/颜色` —— 不触碰 `verify_site [5]` 断言的 `border-radius / box-shadow / linear-gradient` 红线；无外链资源；所有动画包在 `prefers-reduced-motion: no-preference` 内。
- **动效修复 1 处（Lead 实测发现）**：⑥ 的通用规则**覆盖**了 ④ 给 `.theme-toggle` 设的 `transform` 过渡（按下仍位移但丢了 120ms 平滑）→ 已把按钮的 `transition` 显式并列声明，实测 `transition-property=transform, background-color, border-color, color`。

**三、防复发（`tools/verify_site.py` 新增 [13]）**
断言：`#timeline-root` **仅**剧情索引页存在 · 位于 `<div class="prose">` 之前 · 节点数 == 数据单元数（12）· 单元数 ≥2 且带日期 ≥2 · **版本 order 单调递增** · `assets/timeline.js` 已引入 · 无外部资源 —— 缺任一即 FAIL。

**四、Lead 独立验收（全部亲跑；起本地 `http.server 8788` + 真实 Chrome）**

| 验收器 | 结果 |
|---|---|
| `tools/verify_site.py` | **RESULT: PASS**（[1]–[13] 全过；`[13] 单元=12 带日期=12 带锚点=12 版本序单调=True 节点=12 仅索引页=True 在prose前=True 外链=False`） |
| `wiki/build_wiki.py` | 页 **6668** / 链接 **96564** / **死链 0** / 未收录 **0**；`时间线: 12 个单元` |
| `.tmp_build/verify_timeline_live.py`（T1–T9） | **RESULT: PASS** —— 容器 12 节点、筛选条 `['全部','1.x','2.x','3.x','4.x']` 且默认按下「全部」；**真实点击**：全部 12 → 1.x **6** → 4.x **1** → 回到全部 12；`<details>` 展开后 6 条子任务；**锚点跳转** `hash=序章-湛蓝星-黑塔空间站` 目标 `top=64`（`[id]{scroll-margin-top:64px}` 生效）；小屏 390×844 `scrollWidth=390=innerWidth` **无横向溢出**、改单列；**禁用脚本后仍 12 节点 / 7 个 `<details>`**（静态可读）；`prefers-reduced-motion:reduce` 下 `animation-name=none`；外链资源 **0** |
| `.tmp_build/verify_motion_live.py`（M1–M7） | **RESULT: PASS** —— ① `.mv` 四块 `delay=0s/0.06s/0.12s/0.18s` 且 `animation=riseIn`；② `axisGrow` 1.5s 后收敛为 `matrix(1,0,0,1,0,0)`（线宽 1px、色 `rgb(255,59,48)`）；③ 真实鼠标移入 `scaleX 0→1`；④ `:active` 实测 `matrix(1,0,0,1,0,1)`；⑤ `animation-timeline=view()` 生效；⑥ body 过渡 `0.16s`；⑦ **reduce 下 `.mv/.tl-item/.tl::before/.prose h2` 全为 `none`** |
| 回归 | `verify_links` **exit 0**；`verify_fields` **异常 0 / 待补充 156**；五语言规模 **6668 / 5871 / 5867 / 5864 / 5847**（与基线逐语言一致） |
| 目视 | 全页截图（存**仓库外** `%TEMP%`，遵守图片零入库）：版本轴红色方点、版本/日期两列、章节名与子任务展开、筛选按钮「全部」高亮 —— 与 Swiss 风格一致 |

- **已 push（用户放行，2026-10-04 16:16）**：`5427cedf7..29343e49b main -> main`；`origin/main` = `29343e49b`（领先/落后 **0/0**）。`wiki/pages/`、`wiki/data/` 为生成物不入库。
- **出库前按 D-044 纪律做纯净检出验收**（`git worktree` @ `29343e49b`，等价 CI 环境，无 `quest/剧情文本/`）：`build_wiki` **6500 页 / 94344 链接 / 死链 0**（34 处「未收录」= `quest/剧情文本` 未入库链接，属 D-044 预期）、时间线仍 **12 单元**、`verify_site` **RESULT: PASS**（含 [13]）。
- **线上端到端复测（真实 Chrome 直连 Pages，非本地）**：`verify_timeline_live.py` **T1–T9 全 PASS**、`verify_motion_live.py` **M1–M7 全 PASS**；首页与 `主线任务` 页均 **HTTP 200**。

## 2026-10-04 15:52

**W-4.6-83：清除 `quest/剧情文本` 的米游社来源表达残留（79 文件 / 225 行）—— Lead 亲写判定口径 + 独立差分验收**

- **问题（声明与内容自相矛盾）**：D-022/D-023 的「米游社源 91×5 原地表达清零」未做干净——`ja_jp` **38** / `ko_kr` **40** / `zh_tw` **1** 个文件的正文**仍是简体中文叙事**，而这些文件的 `> 状态：v0.2（结构完整；文字表达已按权利人声明撤下）` 已声称撤下。
- **⚠️ Lead 自我纠错（本轮最重要的发现）**：新会话接手稿与工单初稿用的判定规则是「不以特殊符号开头 + 长度 ≥ 40 字 + 含 CJK」，实测有**两个方向的错**：
  1. **误删**：`ja_jp` 有 **5 个文件 / 23 行日文正文**（`第二章_07`、`第二章_11`、`第二章_13`、`第五章_我如何遇到你的父亲`、`第五章_观光客的哲学`）含汉字且 ≥40 字，按字面规则会被**当成中文残留删掉** —— 那是日文本地化内容；
  2. **漏删**：`ja_jp` / `ko_kr` 各 **29 个文件 / 51 行** `<40` 字的简体中文叙事（如「通讯里神秘的协助者透露出两人似乎怀抱着某种目的。」）会被阈值放过，**处理后声明与内容依旧矛盾**。
  → 定稿口径改为：**改用 `zhconv` 机械简繁转换作判据**（`convert(s,'zh-hant') != s` ⇒ 含简体字）、阈值降到 **≥15 字**、加**假名/谚文豁免**、**排除 TAB 键值行**、**节范围限定**，并**豁免 `任務まとめ`/`임무 요약`/`任務總結` 类自撰摘要节**（那类节 `zh_cn` 本身就保留中文原文 → 属「镜像未本地化」另案，不是米游社「表达」残留）。判废条件自查：按原字面规则执行会**双向判废**。
- **判定口径与清单（Lead 落盘，执行方不得改规则）**：扫描器 `.tmp_build/w4683_final.py`；目标清单 `.tmp_doubao/W4683_targets.txt`（79 行）与 `.tmp_build/w4683_manifest.json`（逐文件 行号 / 节名 / 行文本 / 改动前 SHA256）。定稿范围 = `ja_jp` 38 / `ko_kr` 40 / `zh_tw` 1 = **79 文件 / 225 行**。
- **派单**：豆包桌面版（CDP，job `W4683`，`07:38:47 started → 07:51:56 done`，四段进度事件齐全）。处置规则 = **只删不加译**；仅当该节删完已无任何正文行才补一行标准标记（照抄 `zh_cn`）；若该节仍留日/韩文正文则**不补标记**。
- **Lead 独立验收（不采信执行方自述，全部亲跑）**：
  | 验收器 | 结果 |
  |---|---|
  | `.tmp_build/w4683_final.py` | `ja_jp 0 / ko_kr 0 / zh_tw 0`、`TOTAL residual files = 0`、**exit 0** |
  | `.tmp_build/w4683_verify.py`（8 项） | **RESULT: PASS**：备份 79/79 与基线 SHA256 全等；79/79 文件已改动；日/韩正文零丢失；节标题序列 0 变化；编号列表 0 变化；`> 更新时间：` 与 mtime 同一分钟 0 不一致 |
  | `.tmp_build/w4683_verify2.py`（逐行差分） | **RESULT: PASS**：删除行 **225** = 计划命中行（多重集合相等，零多删零少删）；新增行 **74** = **全部为标准标记行**（无非标记插入）；`> 来源：`/`> 状态：`/`> 创建时间：` 逐字不变；`zh_cn`/`en_us` 的 `quest/剧情文本` 今日改动文件数 **0**、全域 `.md` 改动 **0** |
  | `.tmp_build/w4683_check_leftover.py` | 删后仍保留日/韩文正文的命中节 **4 处**（`ja_jp`/`ko_kr` 各 2 处，含 `序章_02` 过场动画节 25/26 行日/韩对白）→ 均**未加标记**，符合工单 §2.3 |
- **回归**：规模 **6668 / 5871 / 5867 / 5864 / 5847**（与基线逐语言一致）；`verify_links` **exit 0**；`verify_site` **RESULT: PASS**（[9]–[12] 全 True）。
- **备份与回滚**：`.tmp_build/W4683_backup/`（79 文件，SHA256 与改动前全等）；回滚 = 直接覆盖回去。
- **注意（口径登记）**：`*/quest/剧情文本/` 被 `.gitignore:24` 忽略 → **`git diff`/`git status` 看不到本单改动**，故验收改用「备份 + SHA256 + 扫描器」；本单**数据改动不入库**（符合 D-020/D-025），入库的只有工单与本日志。已随 `29343e49b` **push**（用户 2026-10-04 16:16 放行）。

## 2026-10-04 14:40

**W-4.6-81 / W-4.6-82：GitHub Wiki 三页同步 + 打印样式（含一次纠错）—— Lead 逐项核对**

- **背景（Lead 实测）**：远端 Wiki 停在 `a8aea6f` @ **2026-10-03 15:24**（`git clone …wiki.git`，8 页；与本地 `tools/github-wiki/*.md` **逐文件零差异**）→ `Home` 规模表过期（`zh_cn` 6,665 → **6,668**、`en_us` 5,851 → **5,871**、`ja_jp` 5,845 → **5,864**、`ko_kr` 5,842 → **5,847**、合计 30,070 → **30,117**）、`更新日志` 缺 10-03 晚～10-04 全部内容、`路线图与待补` 有 3 项已完成却仍挂待办 + 1 项口径已作废。
- **交付（`git status --porcelain` 实测，6 个文件）**：`tools/github-wiki/{Home,更新日志,路线图与待补,数据来源}.md`、`wiki/assets/style.css`（新增 `@media print` 块）、`tools/verify_site.py`（新增 **[12] 打印样式**）。
- **Lead 复核中发现并打回纠正的 2 处（W-4.6-82）**：
  1. `Home.md` 的「详情文件」列被误填成「全部」数字 → 该表既有口径（Lead 用旧表 13 个 Δ 反推、**逐类吻合**）= `详情 = 全部 − 索引页`，索引页 = **文件名含「索引」** 或 **文件名 == 顶层分类目录名**；纠正后逐行复核：`items 3882/3829`、`quest 173/171`、`worldview 8/7`、`stages 4/4`、合计 `6668/6610` —— **13 行全部一致 ✅**。
  2. `路线图与待补.md` 第 6 条写了**未经实测**的「如 `行于命途3/4` 等仍有曲目缺中文名」→ Lead 扫描 `zh_cn/音乐/**` 全部 **620** 条曲目，仅 **5 条**不含中文（`长生梦短` #33 `Samudrartha (Instrumental)`、`Ripples of Past Reverie` #1/3/4/5），**无一条属于 行于命途3/4** → 已按实测改写。
- **Lead 独立验收**：`build_wiki` **6668 / 96564 / 死链 0 / 未收录 0**；`verify_site` **[12] @media print=True、块内 display:none=True、RESULT: PASS**（[9][10][11] 亦 True）；`verify_links` exit 0；`verify_fields` **异常 0 / 待补充 156**；Home 分类表 13 行核对全部一致；执行方遗留的根目录杂散文件 `verify_out_81.txt` 已删除。
- **未完成（需用户放行）**：**远端 Wiki 尚未推送**（本地稿已就绪；push 目标是独立仓库 `*.wiki.git`，不影响主库与 Pages）。

## 2026-10-04 13:55

**W-4.6-80：修线上 3 个缺陷（表格表头吸顶 / 小屏首屏被导航占满 / 搜索框无可访问名称）—— 由 Lead 线上实测复现并逐项核对**

| # | 缺陷 | 线上「修复前」实测证据（Lead 亲跑） | 修复 |
|---|---|---|---|
| A | **9,123 张表格全部没有 `<thead>`** → `table thead th{position:sticky}` 选择器永不命中，表头吸顶完全失效 | 生成页 `table=9123 / thead=0`；真实浏览器 `getComputedStyle(first th).position = static`，滚动 600px 后表头随之滚走 | `build_wiki.py` 表格分支改为 `<table><thead><tr><th>…</th></tr></thead><tbody>…</tbody></table>`（不动 `convert_inline`/`split_row`/单元格内容） |
| B | **小屏首屏被侧边导航占满** | 390×844 实测：`.sidenav` 高 **463px**、`main.top = 633px` → 正文首屏仅 **211px** | `theme.js` 新增「≤640px 时收起 `.sidenav details[open]`」；`style.css` 追加 `@media (max-width:640px){ .sidenav{max-height:40vh;overflow:auto} }` |
| C | **搜索框没有可访问名称**（只有 placeholder，屏幕阅读器读不出） | 本地与线上 `#search` 标签实测：无 `<label>`、无 `aria-label` | `index.html` 的 `#search` 加 `aria-label="搜索页面标题"`（保留原 placeholder 与 combobox/aria-controls） |

- **防复发**：`tools/verify_site.py` 新增 **[9] 表格结构**（table 数 == thead 数 且 >0、且每个 `<table>` 紧跟 `<thead>`）、**[10] 首页可访问名称**、**[11] 小屏导航**（theme.js 与 style.css 的静态断言）——三项均打印数字/True-False，缺字段即 FAIL。
- **Lead 独立验收（全部亲跑，不采信执行方自述）**：
  | 验收项 | 实测 |
  |---|---|
  | 静态 | `build_wiki` **6668 / 96564 / 死链 0 / 未收录 0**；`verify_site` **[9] table=9123 thead=9123 紧跟=9123、[10] True、[11] True、RESULT: PASS**；自算 `table=9123 thead=9123 tbody=9123`；`verify_links` exit 0；`verify_fields` **异常 0 / 待补充 156** |
  | **真实浏览器（本地构建产物 http://127.0.0.1:8787）** | `.tmp_build/verify_w4680_live.py` → **A/B/C 全 PASS**：含 thead=True、`position=sticky`、滚到表格顶后表头 top=0.92；390×844 下导航高 **86px**（原 463）、`main.top` **256px**（原 633）、`details[open]=False`；`aria-label='搜索页面标题'` 且 combobox/aria-controls 保留 |
  | 「修复前」基线（同一验收器，线上站） | A/B/C **全 FAIL**（thead=False / position=static；导航 463、main.top 633；aria-label=None）——证明缺陷确实存在、修复确实有效 |
- **执行通道事件（如实记录）**：本轮开工时**豆包桌面版未运行**（9222 ECONNREFUSED）。查 Windows 事件日志：**1074 @ 02:01:14（用户经开始菜单发起正常关机）+ 6006 @ 02:01:27（事件日志服务停止）+ 6005 @ 12:14:11（开机）** → 豆包随**正常关机**退出，非崩溃（Application 日志无 Doubao 错误）。Lead 用 `Start-Process E:\Doubao\app\Doubao.exe --remote-debugging-port=9222 --remote-allow-origins=*` 重启；用户切到「工作」模式后 CDP 派单成功。
- **工作区清理**：删除执行方遗留的根目录杂散文件 `verify_out.txt`（其内容已由 Lead 亲跑复现）。

## 2026-10-04 00:10

**W-4.6-77 批次 C-2：音乐镜像补「官方日文曲目名」14 张（ja_jp）—— 与 C-1 同口径，逐条机器复核通过**

- **交付（`git status --porcelain` 实测）**：`ja_jp/音乐/` 下**新增 14 个文件**（场景OST 13 张 + `PV专辑/行于命途6.md`）；**既有 `ja_jp` 行于命途1–5 仍为 33/22/21/22/23 未动**；未触碰其它目录。
- **数据来源 = Apple 官方**日区目录**（`lookup?id=<日区id>&country=jp&entity=song`）；派单附件 `docs/prompts/W-4.6-77_附件_官方日文曲目名.tsv`（**494 条 / 14 张**），SHA256 = `F621614A…C162FEB6`。Lead 逐张核对 **API 条数 == `zh_cn` 条数**（22/17/30/30/25/32/51/52/44/62/33/31/32/33）。
- **Lead 验收（亲跑）**：`.tmp_build/verify_w4677.py` → **19/19 PASS**（14 张逐条与附件精确一致；`収録曲数`、`発売日`、`データ来源` 为 jp 页、元信息 5 行、`## 基本情報`/`## 収録曲`/`## 説明` 结构全部合规；既有 5 张未被改）。
- **日区取数的一处关键纠错（Lead 自纠，已写进工单）**：`行于命途6` 的日区 id 实为 **`6795392477`**（`運命の道を歩んでVol.6`，2026-08-02，22 首），**不是** `1808347899`（那是 **Vol.4**）。此前按「曲目数吻合」误配过一次，靠核对返回的 `collectionName` 抓出。
- **未建项（如实登记 `docs/待补充清单.md`）**：`Ripples of Past Reverie` **日区未发行**（jp 检索 0 命中）→ 不建 `ja_jp` 文件；`ko_kr` 除 行于命途1–3（Naver Vibe）外**其余 12 张无官方韩文曲目名来源**；`ko_kr` 行于命途4/5 为「未取得 / 证据待复核」。
- **音乐镜像总账（本轮结束时实测，口径=各语言 `音乐/` 下详情文件数，不含主索引）**：`zh_cn` **20** → `en_us` **20/20**；`ja_jp` **19/20**（缺 Ripples，日区未发行）；`ko_kr` **5/20**（其中 **3 张**含官方韩文曲目名：行于命途1–3；4/5 为仅事实表＋证据待复核/未取得）；`zh_tw` **0/20**（繁体镜像未开工）。

## 2026-10-03 23:55

**W-4.6-76 批次 C-1：音乐镜像补「官方英文曲目名」15 张（en_us）—— 一次做成，全部可机器复核**

- **交付（`git status --porcelain` 实测）**：`en_us/音乐/` 下**新增 15 个文件** —— 场景OST 13 张（失控 / 星空剧场 1–3 / 洞穴寓言 上中下 / 神说要有笑 上下 / 长生梦短 / 雪融于烬 / 飞来波的圣状 上下）+ `PV专辑/行于命途6.md` + `角色与动画短片EP/Ripples of Past Reverie.md`；**既有 `en_us` 行于命途1–5 一字未动**；未触碰 `zh_cn/`、`ja_jp/`、`ko_kr/`、`zh_tw/`。
- **数据来源 = Apple 官方目录**（`lookup?id=<专辑id>&country=us&entity=song`）；派单附件 `docs/prompts/W-4.6-76_附件_官方英文曲目名.tsv`（**499 条 / 15 张**），SHA256 = `B915C7BD…F070963`。Lead 逐张核对：**API 条数 == `zh_cn` 同专辑曲目条数**（22/17/30/30/25/32/51/52/44/62/33/31/32/33/5）。
- **Lead 验收（亲跑）**：`.tmp_build/verify_w4676.py` → **20/20 PASS**（15 张逐条与附件精确一致；`Track Count`、`Release Date`、`Type`（Ripples 为 `Animated Short Single - EP`）、5 行元信息、`## Basic Info`/`## Tracks`/`## Notes` 结构全部合规；既有 5 张仍为 33/22/21/22/23 未被改）。
- **同日纠正一处 Lead 自身错误（重要）**：C-2 备料时我一度把 `行于命途6` 的**日区 id 误配为 `1808347899`**（那是 **Vol.4** 的日区页）。经核对返回的 `collectionName` 发现后，改用检索确认的正确 id **`6795392477`**（`運命の道を歩んでVol.6`，22 首，2026-08-02），并已写进 W-4.6-77 §1 的显式提醒。**教训：跨语言取数必须核对返回的专辑名，不能只看曲目数吻合。**

## 2026-10-03 23:30

**收口两个残留：`失控.md` 合计行修正（W-4.6-74）+ `行于命途2` 第 22 首官方中文名落盘（W-4.6-75）**

| # | 文件 | 改动 | 验收 |
|---|---|---|---|
| 1 | `zh_cn/音乐/场景OST/失控.md` | 「（共 19 首）」→「（共 17 首）」；`> 更新时间：` → 22:58（`git diff` 实测**仅 2 行变化**） | ✅ 通过 |
| 2 | `zh_cn/音乐/PV专辑/行于命途2.md` | 第 22 条 `Wanna Go Have Some Fun!` → **`一起出去玩嘛！（Wanna Go Have Some Fun!）`**；说明行改注官方来源「网易云音乐官方发行页 id=192740048」；`> 更新时间：` → 23:22（`git diff` 实测仅 3 行） | ✅ 通过 |

- **中文名取证与 Lead 独立复核**：执行方 W-4.6-73 取证单给出「一起出去玩嘛！」，Lead **亲自重跑官方发行页接口** `https://music.163.com/api/album/192740048` → `albumName=崩坏星穹铁道-行于命途2 Experience the Paths Vol.2`、`artist=HOYO-MiX`、**22 首**、`no=22 name='一起出去玩嘛！ Wanna Go Have Some Fun!'`；且第 1/21 首中文名与库内既有写法逐字一致 → **同一发行版，取证成立**（此后才落盘）。
- **Lead 验收（亲跑）**：`.tmp_build/verify_w4675.py` → **7/7 PASS**（22 条、第 22 条逐字、说明行含官方 URL、`曲目数=22` 未动、`## 关联条目` 与创建时间未动、其余 21 条未被重写）＋**新增回归项「全语言音乐文件：条目数 = 合计行 = 事实表，0 处不一致」**（该口径正是 W-4.6-72 我漏检的那一点）；`build_wiki` 6668/96564/死链 0/未收录 0、`verify_site` PASS、`verify_fields` 异常 0 / 待补充 156。
- **`行于命途5` 韩文曲目名：证据不足，**不落盘**（Lead 裁定）**：W-4.6-73 给出的 23 首韩文经 W-4.6-75 §2 复核，执行方**如实承认**其来源是 `general_search` 的**页面快照**、非可重跑抓取；Lead 用纯 HTTP 与 `tools/render_fetch.py` 访问同一 URL **均只得通用外壳（韩文曲目命中 0）** → 列「证据待复核」，已登记 `docs/待补充清单.md`（含 Vol.4 同批未取得）。
- **顺带发现（**未提交、待用户裁定**）**：工作区出现**非 Lead 创建**的未跟踪文件 `scripts/mimo_batch.py` —— 一个把 `zh_cn/**` 批量送 MiMo 翻译并可直接 `fetch --write` **写入 `en_us/ zh_tw/ ja_jp/ ko_kr/`** 的工具，与 **D-028（禁 LLM 机翻入库）** 及 D-017/D-021（交付须经 Lead 复核后入库）冲突。Lead **未运行、未提交**，等用户裁定。

## 2026-10-03 22:15

**W-4.6-72：音乐库两处口径修正（zh_cn 2 个文件）—— 按用户 2026-10-03 拍板**

| # | 文件 | 用户裁定 | 实际改动（`git diff` 实测） |
|---|---|---|---|
| 1 | `zh_cn/音乐/场景OST/失控.md` | **以 Apple 官方目录为准 → 17 首** | 删去官方目录中不存在的 2 行（`踏上旅途（Take the Journey）` 与其「（伴奏）」）；`曲目数` 19→**17**；说明行改为「中文曲名取自酷我音乐官方发行专辑页；曲目清单与曲目数（17 首）以 Apple 官方专辑页为准」；`> 更新时间：` → 22:03（= mtime 同分钟） |
| 2 | `zh_cn/音乐/角色与动画短片EP/Ripples of Past Reverie.md` | **按官方 EP 补全 5 首** | `> 数据来源：` 由**单曲页**改指官方 **EP 专辑页**（id `1850409281`）；曲目节补为 **5 条官方写法**（`English Ver.` / `昔涟（…Chinese Ver.）` / `Instrumental` / `English Harmonic Accompaniment` / `Chinese Harmonic Accompaniment`）；`曲目数` 1→**5**；说明行注明「中文名仅『昔涟』有官方来源，其余保留官方英文写法」 |

- **Lead 独立验收（全部亲跑）**：`.tmp_build/verify_w4672.py` → **11/11 PASS**（17 条与官方目录对位逐字一致、5 条与官方 EP 逐字一致、曲目数、说明行、数据来源 URL、`创建时间` 未动、**`## 关联条目` 节均保留**=D-042 未复发）；`verify_fields` → **异常 0 / 已知待补充 156**。
- **回归**：`build_wiki` 6668 页 / 96564 链接 / 死链 **0** / 未收录 **0**；`verify_links` exit 0；`verify_site` **RESULT: PASS**。
- **待补充清单**：上述两条由「待裁定」改为 **✅ 已解决**；仅余 `ko_kr/行于命途4–5` 韩文曲目名一项（韩方渠道无官方来源）。
- **执行方回执**：豆包本轮结束时同样未发出完整回执；裁定以**落盘文件 + Lead 亲跑验收器 + 回归**为准。

## 2026-10-03 22:05

**W-4.6-71 批次 B：音乐镜像补「官方韩文曲目名」（ko_kr 行于命途1–3）—— 韩区 Apple 接口不可用，改走 Naver Vibe 官方接口取证**

- **交付（`git status --porcelain` 实测）**：只改 3 个文件 —— `ko_kr/音乐/PV专辑/行于命途1–3.md`；**`行于命途4/5.md` 一字未动**（mtime 仍为 16:43）；未触碰 `zh_cn/`、`en_us/`、`ja_jp/` 及任何其它文件。
- **数据来源 = Naver Vibe 官方接口**（韩国官方音乐服务，专辑 `agencyName = miHoYo`）：`apis.naver.com/vibeWeb/musicapiweb/album/<id>/tracks`；专辑 id = **30117222 / 34561119 / 34561108**（曲目 33 / 22 / 21）；附件 `docs/prompts/W-4.6-71_附件_官方韩文曲目名.tsv`（76 条），实测 SHA256 = `742095660F3BC142041629EEA3B29FF9C923E9B86D998084CE62947050D44892`。
- **Lead 独立验收（全部亲跑）**：
  | 验收项 | 工具 | 实测 |
  |---|---|---|
  | 与附件逐条精确比对 | `.tmp_build/verify_w4671.py` | **PASS**：33/22/21 逐字一致；序号连续；条目数 == `수록곡 수`；说明行已按规定文案替换；创建时间未动；更新时间 = 21:50（= mtime 同分钟）；**4/5 两张未动**（无 `## 수록곡` 节、说明行原样） |
  | 与**官方接口实时查询**比对 | `.tmp_build/verify_w4671_api.py` | **3/3 一致，0 处不符**（直接重查 Naver Vibe，不经附件） |
  | 站点回归 | `build_wiki` / `verify_links` / `verify_site` / `verify_fields` | 6668 页 / 96564 链接 / 死链 **0** / 未收录 **0**；links exit 0；site **RESULT: PASS**；fields 异常 **0** / 已知待补充 **156** —— 与基线一致 |
- **关键取证结论（写入 `docs/待补充清单.md` 备注 8）**：① Apple **韩区目录接口恒不返回曲目**（`lookup?country=kr&entity=song` 仅 collection；韩区专辑页 headless 渲染后仍无曲目名，`render_fetch.py` 实测英文/日文曲名命中 **0**）；② **Naver Vibe 可用**，第二来源 **Bugs** 交叉核实一致（`설검(說劍)` = Vol.1 第 30 首 `On Swords`）；③ **Vibe 只覆盖 Vol.1–3** → **Vol.4/5 无官方韩文曲目名 ⇒ 不建节、登记待补充**（零编造，不拿日文/英文充数）。
- **执行方回执**：与批次 A 相同，豆包本轮结束时仍未发出完整回执；本裁定**以落盘文件 + 两项独立实测 + 回归**为准。

## 2026-10-03 21:45

**W-4.6-70 批次 A：音乐镜像补「官方曲目名」（en_us + ja_jp 各 5 张）—— 口径由「仅事实表」升级为含曲目清单（用户 2026-10-03 拍板推进 §4-6）**

- **范围与交付（`git status --porcelain` 实测）**：只改 10 个文件 —— `en_us/音乐/PV专辑/行于命途1–5.md`、`ja_jp/音乐/PV专辑/行于命途1–5.md`；`git diff --stat` = **10 files changed, 302 insertions(+), 20 deletions(-)**（每文件：新增曲目节 + 替换 1 行说明 + 改 1 行 `> 更新时间：`）。**未触碰 `zh_cn/`、`ko_kr/`、`zh_tw/` 及任何其它文件**。
- **数据来源 = Apple 官方目录接口**（`itunes.apple.com/lookup?id=<专辑id>&country=<地区>&entity=song`）；派单附件 `docs/prompts/W-4.6-70_附件_官方曲目名_en_ja.tsv`（121 条），实测 SHA256 = `62DF48AA7ACFF30238291BE1A2C4F25019AEB1009D11713C3BCD1DB42A7BFF11`（与派发副本逐字节一致）。
- **Lead 独立验收（全部亲跑，未采信执行方自述）**：
  | 验收项 | 命令 / 工具 | 实测结果 |
  |---|---|---|
  | 与附件逐条精确比对 | `.tmp_build/verify_w4670.py` | **10/10 PASS**：条目数 33/22/21/22/23 × 2 逐字一致；序号连续；条目数 == 事实表 `Track Count`/`収録曲数`；说明行已按规定文案替换；`> 创建时间：` 未动；`> 更新时间：` = 2026-10-03 21:40（= 文件 mtime 同分钟） |
  | 与**官方目录实时查询**比对 | `.tmp_build/verify_w4670_api.py` | **10/10 一致，0 处不符**（直接重查 Apple，不经附件） |
  | 站点回归 | `build_wiki` / `verify_links` / `verify_site` / `verify_fields` | 生成页 **6668** / 链接 **96564** / 死链 **0** / 未收录 **0**；verify_links **exit 0**；verify_site **[8]一致=True、RESULT: PASS**；verify_fields **异常 0 / 已知待补充 156** —— 与基线逐项一致 |
- **附带发现（Lead 实测，已登记 `docs/待补充清单.md`）**：音乐库全量曲目数审计（20 张专辑）→ **17 张一致**；**2 张真缺口**：`场景OST/失控.md` 文件 **19** 首 vs 官方目录 **17** 首（gb/us/de/th 四地区一致）、`角色与动画短片EP/Ripples of Past Reverie.md` 文件 **1** 首 vs 同 EP 官方 **5** 首；**1 张为地区参数假警报**：`星空剧场3` 用来源 URL 的 `ba` 地区查询得 0 首，改 gb/us/de 得 **25** 首（与文件一致）。**韩区（kr）接口恒返回 0 曲目** → 官方韩文曲名无法用该接口取证。
- **未做（如实登记）**：批次 B（`ko_kr` 5 张，需真实浏览器读韩区官方页）、批次 C（§4-7 `行于命途2` 第 22 首官方**中文**曲名）本轮**未派发**；执行方的完整回执在本轮结束时仍未发出，本裁定**以落盘文件与上述三项实测为准**。
- **遗留小项（不判废）**：10 个文件在末条曲目与说明节之间存在 **2 个空行**（工单未规定，10/10 一致）→ 日后如需统一为 1 个空行，另开小工单。

## 2026-10-03 19:00

**修「详情页链接点不动」（W-4.6-69）—— 定位方式：CDP 真实点击 + elementFromPoint**

- **用户报障**：「详情页内部的链接点不动」（线上、硬刷新无效）。
- **Lead 定位过程（全部实测，未靠猜）**：
  1. 线上 13 个分类卡 + 详情页 + 面包屑 + 正文链接 + 翻页链接：**逐条 HTTP 200**；
  2. 代码扫描：**无** `pointer-events`/`z-index`/`position:fixed`/`onclick` 等点击拦截；
  3. 新建 **最小 CDP 客户端** `.tmp_build/cdp_probe.py`（标准库手写 WebSocket，零依赖）→ 在**真实浏览器**里用
     `document.elementFromPoint(x,y)` 查「坐标上到底谁收点击」，再用 `Input.dispatchMouseEvent` **真实点击**：
     - 侧边导航 / 面包屑 / 正文链接 / 翻页链接 → **最上层都是 `<a>`，点击后 URL 确实变化** ✅ 均正常；
  4. 目标锁定「完整剧情文本」文字：线上 `pages/quest/主线任务.html` 该处最上层元素是
     **`<span class="missing">`，`isLink = False`，点击后 URL 不变** → **确认不可点**。
- **根因（Lead 自己引入的回归）**：W-4.6-59「死链优雅降级」把**无法解析的链接**渲染成 `<span class="missing">` 纯文本；
  公开站由 CI 构建，`zh_cn/quest/剧情文本/` 的 **168 个文件按合规决定不入库** → 其 **34 个链接**在公开站全成不可点文本。
  **更严重**：构建汇总只打印「总链接/死链」，降级数量**完全没输出**（日志显示「死链 0」，实际静默降级 34 处），
  且当时的 7 项自检对此**完全隐形**。
- **修复（W-4.6-69）**：
  | 文件 | 改动 |
  |---|---|
  | `build_wiki.py` | 降级输出改为 **`<span class="missing" title="本站未收录该页面">文本<span class="missing-note">（本站未收录）</span></span>`**；`link_report` 新增 **`missing` / `missing_list`**；汇总行**新增「未收录(降级为纯文本): N 处」** |
  | `assets/style.css` | 追加 `.missing` / `.missing-note`（**muted 灰 + 1px 细线**；**刻意不用强调红**，红是链接色，用了会让人更想点） |
  | `tools/verify_site.py` | 新增 **[8] 未收录链接**：读 `link_report.missing` + 生成页独立复算，二者必须一致；**字段缺失即 FAIL**（防止再次静默）；`missing > 0` 属预期不算 FAIL |
- **Lead 验收（亲自跑）**：`build_wiki` → 页 **6,668** / 链接 **96,564** / **死链 0** / **未收录 0 处（本地文件齐）**；`verify_site` → **[8] 一致=True、RESULT: PASS、exit 0**。
- **线上确认（CI 部署后实测）**：`pages/quest/主线任务.html` 现含 **32 处** `<span class="missing" title="本站未收录该页面">`，文字后带「（本站未收录）」标记；**截图复核**：该处为**灰色文本 + 方框标签**，与红色的真链接（如页内其它链接）**视觉上明确区分**，读者不会再误以为可点。
- **定位工具新增**：`.tmp_build/cdp_probe.py`（最小 CDP 客户端，标准库手写 WebSocket，零依赖）—— 可用 `elementFromPoint` 判定「坐标上谁收点击」并用 `Input.dispatchMouseEvent` **真实点击**；本次正是靠它把「链接点不动」从猜测变成证据。

## 2026-10-03 17:40

**W-4.6-67 前端质量加固（Codex 执行）+ 复核中新发现并修复 1 个线上 bug（W-4.6-68）**

- **Codex 交付（Lead 逐项实测复核，非采信自述）**：
  | 项 | 实测 |
  |---|---|
  | `tools/verify_site.py` | **新建 10,572 B**；我亲自跑 → `RESULT: PASS`、**exit 0**；6 项数字全部可读（[1] H1 6668/6668 · [2] 面包屑 6668/6668 · [3] titles.js 6668 条/BOM 0 · [4] 死链 report=0 独立复算=0 一致 · [5] 禁用项 6 项全 0 · [6] esc/combobox/listbox 全 True） |
  | 搜索体验 | `?q=`/`#q=` 深链、`history.replaceState`（**含 try/catch，`file://` 安全**）、`pageshow` 恢复、空态与「还有 N 条」**移出 listbox**（`#results` 直接子元素只剩 `role="option"`） |
  | 性能 | 索引惰性化（首次 `input` 才构建）+ `titles.js`/`app.js` 加 `defer`（`link_report.js` 保持同步，因内联死链横幅依赖它） |
  | 可读性 | `style.css` 仅追加 3 条（sticky 表头 / `[id]{scroll-margin-top}` / `forced-colors`） |
  | 边界 | `git diff --name-only -- zh_cn en_us zh_tw ja_jp ko_kr LICENSE` **为空** ✅ |
- **复核中新发现的真 bug（W-4.6-68，已修）**：`titles.js` 里 **4 条 path 含 `#`**（如 `simulated/事件/天才俱乐部#55余清涂.html`），而搜索结果此前用**未编码**的 `pages/${path}` → `#` 被当锚点**截断**。
  * **线上实测（修复前）**：编码后 **200** / 截断后 **404**（3 条样本全部如此）→ 用户搜到这类条目点进去就是 404。
  * **修复**：`app.js` 改为**按路径段编码** `'pages/' + h.t.path.split('/').map(encodeURIComponent).join('/')`。
  * **等价性证明**：对全部 **6,668** 条 path，新口径与生成器 `urlq()`（`quote(path, safe="/")`）**逐条一致（0 处不符）**；4 条含 `#` 的路径用新口径编码后线上**全部 200**。
  * **护栏**：`verify_site.py` 新增 **[7] 搜索链接编码**（统计含保留字符的 path 数 + 静态断言 `app.js` 必须按段 `encodeURIComponent`），我亲跑 **[7] 通过**。
- **回归**：`build_wiki` 页 **6,668** / 链接 **96,564** / **dead 0**；`verify_links` exit 0；`verify_fields` 异常 0；`verify_site` **PASS**。
- **Codex 主动申报的 3 处口径/降级**（Lead 认可）：① `[5]` 的 `<img>` 只统计**非图标**（图标 1,602 个由 CI 生成、工单已排除），并单独打印数量不隐藏；② `table thead th{sticky}` **当前不生效**——生成器输出 `<table><tr><th>` **无 `<thead>`**（实测 9,123 个表格、0 个含 `<thead>`），按最小改动未改 DOM；③ `verify_links.py` 打印的 57 条「死链」全部来自 `docs/` 与 `.tmp_*/` 里的**示例文本** `[[xxx]]` 等，与 wiki 数据无关（wiki 构建自身 dead 0）。

## 2026-10-03 17:25

**修复 4 个线上 bug（W-4.6-66）—— 全部由 Lead 在线上实测复现后定位**

| # | Bug | 严重度 | 实测证据（修复前） | 修复 |
|---|---|---|---|---|
| 1 | **全部生成页没有 `<h1>`** | 高 | 扫描 `wiki/pages`：**总页 6,668，含 `<h1` 的页 = 0**；CSS 里 `h1{...}` 永不生效，页面主标题在视觉上完全缺席 | `build_wiki.py` 模板 `<main>` 首个子元素插入 `<h1>{esc(title)}</h1>` |
| 2 | **面包屑 `首页` 与类别粘在一起** | 中 | `1503.html` 渲染为 `首页character / 欢愉 / 真珠_冰_五星` | `crumbs` 末尾补 ` / ` |
| 3 | **4 个活动页标题被 UTF-8 BOM 污染** | 中 | **线上** `data/titles.js` 有 4 条：`'\ufeff# 星际和平盛典：一镜到底'` 等；线上 `<title>` 实测 = `\ufeff# 「星际幻宠」乐园 — HSR Wiki`（浏览器标签真的显示 `#`） | 读文件后 `.lstrip("\ufeff")`；标题提取改为「首行必须是 `# `，否则退回文件名（去尾部 `_数字`）」 |
| 4 | **搜索结果标题未转义** | 中 | 线上有一条标题 `清唱剧<大守护者>首演盛况`，`app.js` 用未转义的 `innerHTML` → `<大守护者>` 被浏览器当未知标签吞掉 | 改用已有 `esc(h.t.title)` |

- **验收（Lead 亲自跑，5/5 通过）**：① 含 `<h1>` 的页 = **6,668 / 6,668**；② 抽样 h1 与 `<title>` **3/3 一致**；③ 面包屑含「首页 / 」= **6,668 / 6,668**；④ `titles.js` 中标题含 BOM 或开头 `# ` = **0**、标题是 `> ` 元信息行 = **0**；⑤ `app.js` 已用 `esc(h.t.title)` = **True**。
- **症状复查**：`1503.html` → `<h1>=真珠（冰·欢愉）`、面包屑 `首页 / character / 欢愉 / 真珠_冰_五星`；`星际幻宠乐园.html` → `<title>=「星际幻宠」乐园 — HSR Wiki`、`<h1>=「星际幻宠」乐园`。
- **回归**：`build_wiki` 页 **6,668** / 链接 **96,564** / **dead 0**；`verify_links` exit 0；`verify_fields` **异常 0 / 已知待补充 156**。
- **数据侧未动**：那 4 个 BOM 源文件**不改**（由生成器容错解决），遵守「数据与生成器分离」原则。

## 2026-10-03 17:00

**站点设计升级（W-4.6-65）：四个设计 skill 落地为本站可执行的版本**

- **加载并执行了 4 个 skill**：`gpt-taste`、`high-end-visual-design`、`ui-ux-pro-max`、`frontend-design`；并用 `ui-ux-pro-max` 的本地检索脚本取了权威结论。
- **关键依据**：`ui-ux-pro-max --design-system` 对「知识库/文档站」检索，**独立返回 `Minimalism & Swiss Style`** + 模式 **「FAQ/Documentation Landing」**（Hero with search bar → Popular categories）→ **与本库既有瑞士风方向一致**。
- **冲突裁决（重要，写进工单）**：
  | skill 建议 | 本库裁定 |
  |---|---|
  | 「Ethereal Glass · OLED 黑 + 毛玻璃」 | **采用 Swiss**（检索独立支持；阅读型站点不适合深黑毛玻璃） |
  | 禁 Helvetica / 推荐 Inter / 用 Google Fonts | **保留系统 Helvetica 栈**（离线+无 CDN 是硬红线；Helvetica 是瑞士风原教旨） |
  | 要求 GSAP + ScrollTrigger + 滚动钉住 | **仅 CSS 动效**（离线/无 CDN/6,668 页性能/许可相容） |
  | `picsum.photos` 图片、题内嵌图 | **一律不用图片**（图片零入库是既有红线） |
  | `rounded-[2rem]` 双壳 | **保持直角**，吸收「双壳嵌套」为**1px 细线外框 + 内层留白** |
  | 链接蓝 `#2563EB` | **保留瑞士红 `#E30613`** |
  | 无障碍要求 | **全部采纳**（焦点可见/对比/键盘/`prefers-reduced-motion`） |
- **落地（4 文件）**：
  * `index.html`：Hero（`h1` 宽容器 1 行）+ `#pagecount` **由 JS 填入**（不写死）+ 搜索框即主 CTA + **13 类 bento**（12×`span 3` = 3 行整 + 1×`span 12` = 1 行 → **4 行无空格**）+ 保留主题切换与页脚文案；
  * `assets/style.css`：`.cats`（`grid-auto-flow:dense`）、`.cat:hover` **700ms `cubic-bezier(.32,.72,0,1)`**、`@keyframes riseIn`（**只动 transform/opacity**）、**错峰** `animation-delay:calc(var(--i,0)*40ms)`、`.prose{max-width:72ch}`、当前类别**红色竖条**、`prefers-reduced-motion` 兜底；
  * `assets/app.js`：**无障碍完整实现** —— `role="combobox"/"listbox"/"option"`、`aria-expanded`/`aria-selected`/`aria-activedescendant`/`aria-live`、**空态给可操作建议**（而非「无结果」）、结果计数、`Esc` 焦点留在输入框、`prefers-reduced-motion` 时禁平滑滚动、HTML 转义防注入；
  * `build_wiki.py`：详情页套 `.prose`（72ch 行宽）。
- **实测验收**：`build_wiki` 页 **6,668** / 链接 **96,564** / **dead 0**；`verify_links` **exit 0**；`verify_fields` **异常 0**；**禁用项扫描全 0**（`picsum`/`googleapis`/`cdn.`/`gsap`/非零 `border-radius`/`box-shadow`/`linear-gradient`/第二种强调色）；详情页 `up` 前缀 `../../../` 正确、`cur` 高亮=角色。

## 2026-10-03 16:30

**新建两件 4.6 时装页（云边拾暖 / 月待花时）—— 4.6 残余缺口再关 2 条**

- **起因**：豆包查证 + Lead 逐字核实，确认 `云边拾暖`（**风堇**时装）与 `月待花时`（**绯英**时装）是 **4.6 官方内容**，此前被列为「查不到来源」的残余项。
- **建页**（W-4.6-62，执行方豆包，Lead 逐项实测）：
  | 文件 | 内容要点 |
  |---|---|
  | `zh_cn/items/Usable/PlayerOutfit/月待花时.md` | 适用角色=**绯英（欢愉·物理）**；限时价 **星琼 ×2680**（原价 3280）；特惠期 2026/09/28–2026/11/11 03:59；来源 `sr.mihoyo.com/news/166235` |
  | `zh_cn/items/Usable/PlayerOutfit/云边拾暖.md` | 适用角色=**风堇（记忆·风）**；限时价 **古老梦华 ×1350**（原价 1680）；同特惠期；同来源 |
  | `PlayerOutfit_索引.md` | 条目数量 **16 → 18**；新增 `- 无评级（2）` 与 `### 无评级` 分组（照 `Usable/Book` 先例） |
- **字段纪律**：SRR（4,073 / 4,017 条）**均未收录**这两件时装 → `实体ID` 写 **「无（官方未公开）」**、`评级` 写 **「待补充」**，**未编造**。
- **实测验收**：`build_wiki` → 页 **6,667**（+2）/ 链接 96,551 / **dead 0**；`verify_links` **exit 0**；`verify_fields` **异常 0 / 已知待补充 156**；两文件 **mtime 与 `> 创建时间` 同为 16:26**（口径一致）。

## 2026-10-03 16:25

**内容缺口查证交付 + 两项核验工具/方法建成**

- **豆包交付（W-4.6-61）**：
  | 产出 | 状态 | 内容 |
  |---|---|---|
  | `.tmp_doubao/v46_residuals.md` | ✅ 2,367 B | 3 条 4.6 残余条目结论 + 官方 URL |
  | `.tmp_doubao/music_official_names.tsv` | ✅ 13,466 B | **20 张专辑**的英/日/韩官方名、发行日期、来源 URL、备注（缺项一律写「**未取得**」，**无机翻** ✓） |
- **Lead 逐字核验（自述不算证据）**：
  1. **sr.mihoyo.com 是 Nuxt SPA**，纯 HTTP 抓取只有外壳 → 建 **`tools/render_fetch.py`**（本机 Chrome/Edge `--headless=new --dump-dom`，**真正执行 JS**）。渲染后官方原文证实：时装「月待花时」=**绯英**、限时**星琼 2680**（原价 3280）；「云边拾暖」=**风堇**、限时**古老梦华 1350**（原价 1680）；特惠期 **2026/09/28–2026/11/11 03:59**；异相仲裁官网页标题即「「异相仲裁」玩法说明」。存证 `.tmp_build/verify_dumps/`（各约 2.3 MB）。
  2. **Apple Music 网页版需登录/地区**，headless 渲染只出空壳（三个地区路径文本长度完全相同）→ 改用 **iTunes 公开查询 API**（`itunes.apple.com/lookup?id=<id>&country=<cc>`，JSON、免登录）。实测：失控 EN/JP/KR 三地区官方专辑名与 TSV **逐字一致**（`制御不能` / `통제 불능`）、**17 首**、**2023-03-24**；《长生梦短》韩区 **resultCount=0** → TSV 的「韩文名未取得」**属实**；《行于命途6》CA 区 **22 首** 一致。
- **额外发现（本库还缺）**：4.6「**协议商店**」上新内容（大黑塔•战略支援协议 / 战略合作协议 / 漫游补充协议 / 材料支持协议V2，含价格与限购次数）、礼包「黑塔•协议」限购刷新；「时尚单品」兑换价「**愿望星尘 180**」（可作既有页来源补强）。
- **新工具入仓**：`tools/render_fetch.py`（渲染抓取 / 关键词核验，零依赖）。
- **⚠️ 同一个坑本轮踩了三次（记教训）**：`.ps1` 若无 **UTF-8 BOM**，Windows PowerShell 5.1 按 ANSI 解码 → 中文注释变乱码并**破坏解析**（`commit_push.ps1`、`render-fetch.ps1`）。**处置**：工具类脚本**一律改用 Python**（本项目 Python 侧从未出编码问题）；确需 `.ps1` 时必须写 BOM（`[System.IO.File]::WriteAllText($p,$t,(New-Object System.Text.UTF8Encoding($true)))`）。

## 2026-10-03 15:40

**站点增强（W-4.6-60）：全站侧边导航 + 搜索升级 + 统计数字自动生成**

- **改动 4 个文件**（执行方=豆包，Lead 逐项实测）：
  | 文件 | 改动 |
  |---|---|
  | `wiki/build_wiki.py` | 每页注入**零 JS、可折叠**（`<details>`）的侧边导航：13 个类别 + **当前类别 `class="cur"` 高亮** + 「首页 / 搜索」；路径用现有 `up` 变量 |
  | `wiki/index.html` | 统计行改为 `<p class="stat" id="stat">` 由 JS **自动读取**（原先**写死 6664、已过期**，实为 6,665） |
  | `wiki/assets/app.js` | 搜索升级：**标题+路径**双匹配 · 小写与**全角空格**归一化 · 最多 50 条 + 「还有 N 条」 · **↑↓ / Enter / Esc** 键盘操作 · 结果显示所属类别 |
  | `wiki/assets/style.css` | 追加 `.sidenav` / `.sidenav li.cur` / `#results li.hl` —— 直角、细线、唯一瑞士红，**无圆角/阴影/渐变** |
- **实测验收**：`build_wiki` → 页 **6,665** / 链接 **96,523** / **dead 0**（链接数由 9,878 → 96,523，增量 = 每页新增 13 条导航，**口径自洽**）；`verify_links` **exit 0**；`verify_fields` **异常 0**。
- **`up` 前缀按层级正确**：`character/欢愉/1503.html` → `../../../pages/…`；`items/Virtual/Virtual/61.html` → `../../../../pages/…`。
- **高亮归属抽验全对**：角色页→`角色`、物品页→`物品`、音乐页→`音乐`、敌人页→`敌人`；首页 13 条分类链接**完好**。
- **Pages 实测：仍未上线**——`https://ganmayou2333.github.io/hsr-knowledge-base/` 带随机参数请求仍 **HTTP 404**；GitHub API 因**未认证限流（403）**无法查 `has_pages` 与 Actions 运行记录。本次 push 将再次触发 `pages.yml`，待观察。

## 2026-10-03 15:35

**仓库已转公开 + GitHub Wiki 8 页上线 + git 全历史安全扫描（干净）**

- **用户侧动作（Lead 实测核验，非采信自述）**：①仓库已 **Public**（未授权 API `private=False`、`has_wiki=True`）；②**Wiki 已创建**（`…hsr-knowledge-base.wiki.git` 可达），但 **`has_pages=False` → Pages 尚未开启**。
- **Wiki 8 页已批量推送并公开渲染**：远端 `refs/heads/master = a8aea6f7`；页面清单实测含 `Home.md` `_Sidebar.md` `项目简介.md` `许可与合规.md` `数据来源.md` `贡献指南.md` `更新日志.md` `路线图与待补.md`；公开页 `https://github.com/ganmayou2333/hsr-knowledge-base/wiki` **HTTP 200**，正文实测含「中文数据知识库」「30,070」「贡献指南」（侧边栏生效）。
- **推送踩坑（已解）**：首次 push 被拒 `push declined due to email privacy restrictions`——**全局** `user.email` 是私人邮箱，而主仓库用的是**本地** config 的 noreply 地址。处置：**只给 wiki 克隆**设 `186293913+ganmayou2333@users.noreply.github.com` 并 `--amend --reset-author`（**未改动全局配置**）→ 推送成功。
- **git 全历史安全扫描（Lead 亲自跑，脚本已入仓 `tools/git-history-scan.ps1`）**：
  | 项 | 结果 |
  |---|---|
  | 规模 | `.git` **73 MB**、提交 **110**、blob **89,130** |
  | 大文件（>1 MB） | **仅 1 个**：`.tmp_items_full.json`（1.31 MB），且**已不在 HEAD** |
  | 机密特征串（GitHub token / AWS key / sk- / 私钥 / Slack） | **全部无命中** ✅ |
  | 敏感路径（`.env`/`id_rsa`/`.pem`/`credential`/`.npmrc`） | **均未出现过** ✅ |
  | **历史作者邮箱** | **只有** `186293913+ganmayou2333@users.noreply.github.com` ✅ — **私人邮箱未入历史** |
- **结论**：公开历史**无泄密风险**；唯一待办是 **Pages 尚未开启**（Settings → Pages → Source = GitHub Actions）。

## 2026-10-03 15:20

**GitHub Wiki 可行性：实测结论「全库镜像不可行」+ 策展入口大纲**

- **官方依据（GitHub Docs）**：①Wiki **软上限 5,000 文件**，超出「部分页面**无法访问**」，文档**明确建议改用 GitHub Pages**；②**搜索引擎只索引 ≥500 star 的 wiki**，需被收录者**建议改用 Pages**；③Wiki **可见性随仓库**；④资格规则与 Pages **完全相同**（public+Free / private 需 Pro·Team·Enterprise）→ **无任何相对 Pages 的优势**；⑤链接语法 `[[页名\|显示文字]]` 可用，但**不支持**嵌入包含、定义列表、缩进、**目录（TOC）**。
- **本库实测（`.tmp_build/wiki_flat_test.py`）**：`zh_cn` **6,665** 页；扁平化重名——**按文件名口径**：唯一 5,969、重名 639 种、**被吞并 696 页**；**按 H1 标题口径**：唯一 5,726、重名 697 种、**被吞并 939 页**；应用前缀命名规则后可去重到 6,665 个唯一页名（12 个需序号兜底），**但页数不变 → 仍超上限 1,665 页（33.3%）**；页名最长 **43 字**。
- **结论**：**全库镜像不可行**（三个独立硬伤：5,000 上限 / 扁平重名 / 不被索引）；**可行用法 = 8 页策展入口**。
- **产出**：`docs/github_wiki可行性评估.md`（评估）、`docs/github_wiki策展大纲.md`（8 页大纲 + `_Sidebar` + 落地前置与维护纪律）。
- **口径纪律**：重名两个口径**并列报出**（文件名 vs H1 标题集合不同），单一口径不足以定论。
- **前置（需用户操作）**：要公开 Wiki 必须**仓库先 Public**（或升 Pro）；再 Settings → Features 勾选 **Wikis** 并创建 `Home`。

## 2026-10-03 15:05

**公开前必修两项完成：死链优雅降级 + 图标脚本编码兼容（W-4.6-59）**

- **触发**：为「GitHub Pages 公开」做**忠实本地 CI 模拟**（`git worktree` 取纯净检出，只给 CI 会给的东西）。**模拟立刻抓到 2 个真问题**——这正是本地完整库永远看不出来的：
  1. **纯净检出构建 = 6,497 页 / 34 条死链**（本地完整库是 6,665 页 / 0 死链）。根因：`zh_cn/quest/剧情文本/` 的 **168 个文件**按合规处置（D-020）**本就不入库**的（`.gitignore` 的 `*/quest/剧情文本/`），CI 里那 34 条「主线任务 → 剧情文本」链接全部指向不存在的页面。
  2. **`copy_icons.py` 在本机崩溃**：`UnicodeEncodeError: 'gbk' codec can't encode '\u2022'` → **exit 1**（CI 的 Ubuntu 是 UTF-8 不受影响，但 Windows 构建必挂，属可移植性 bug）。
- **用户拍板**：剧情文本**不入库**，改为**链接优雅降级**。（线上步骤维持「先不开」。）
- **处置与实测**：
  | 改动 | 内容 |
  |---|---|
  | `wiki/build_wiki.py` | `md_link` / `wikilink`：目标**不在 `PAGE_SET`** 时**不再输出 `<a class="dead">`**，改输出 **`<span class="missing">`** |
  | `wiki/assets/style.css` | 新增 `.missing{color:var(--muted)}`（克制的降级提示） |
  | `wiki/copy_icons.py` | 补 `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace")`，消除 GBK 控制台崩溃 |
- **验收（Lead 亲自跑，两个环境都验）**：
  - **纯净检出（=CI）**：`copy_icons` **exit 0**；`build_wiki` → **6,497 页 / 9,842 链接 / dead 0**（原 9,876 / 34）；`dead_list` 空；页内实测已是 `<span class="missing">完整剧情文本</span>`，**无 `class="dead"`**。
  - **本地完整库回归**：页 **6,665** / 链接 **9,878** / **dead 0**；`verify_links` **exit 0**；`verify_fields` **异常 0**。
- **纪律新增（D-044）**：**发布用构建必须在「纯净检出」里验收**——本地完整库含 gitignore 依赖，会**掩盖 CI 缺陷**。
- **决策记录补齐**：新登记 **D-043**（MediaWiki 演示实例 + `is_writable` 兼容层，此前只在 `update.md`/`Common.css` 引用、决策记录缺失，属 Lead 自我纠错）与 **D-044**（死链降级 + 纯净检出验收纪律）。

## 2026-10-03 14:46

**本批变更已分组提交并推送至远端**

- **5 组提交（每组显式路径，未用 `git add -A`）**，由豆包执行、Lead 实测复核：
  | 提交 | 内容 | 文件数 |
  |---|---|---|
  | `8186286b7` | `data(W-4.6)`：音乐库 20 专辑/618 曲目 + 敌人库(4) + 巡星之礼/潮玩礼券/愿望星尘/纪念奖章/孤狼墨镜 | 38 |
  | `3cc008902` | `i18n(W-4.6-31/32)`：`zh_tw` 镜像 22 个（events 7 + stages 3 + rules 5 + 货币战争 7） | 22 |
  | `ccc8de5e9` | `feat(wiki)`：瑞士风样式 + 三态主题切换 + 详情页 URL 改用实体ID + 首页导航修复 | 4 |
  | `9d4bddaab` | `tools`：MediaWiki 演示实例工具集（md2mw / dshImport / Common.css / 模板 / 启停脚本）+ `verify_fields` 纳入音乐·敌人类别 | 7 |
  | `355b6be80` | `docs(W-4.6)`：目标台账与结项、决策 D-039~D-043、音乐库规范 v1.15、MkDocs 迁移评估、仓库结构登记 | 9 |
- **推送核验（不采信自述）**：`git rev-parse HEAD` = `git rev-parse origin/main` = **`355b6be8090eb5962cfd62dbdd0f75536cebeb7d`**；`git ls-remote origin refs/heads/main` 返回**同一 SHA** → 远端确已更新。工作区**未提交 0**。
- **推送前回归（Lead 亲自跑）**：`build_wiki` → 页 6,665 / 链接 9,878 / **dead 0**；`verify_links` **exit 0**；`verify_fields` **异常 0 / 已知待补充 156**。
- **过程记录（1 个自己的坑）**：首版提交脚本 `commit_push.ps1` 是**无 BOM 的 UTF-8**，Windows PowerShell 5.1 按 ANSI 解码 → 中文路径变乱码（`zh_cn/音乐` → `闊充箰`）、`git add` 全部未命中；豆包**按纪律报错停手、未擅自改脚本**（处置正确）。修正方式：改**纯 ASCII 驱动脚本** + `git add --pathspec-from-file`（中文路径写 UTF-8 文件）+ `git commit -F`（提交信息写 UTF-8 文件），彻底绕开 shell 编码层。

## 2026-10-03 14:30

**MediaWiki 全量导入完成：正文页 6,668（zh_cn 全库）+ 瑞士风外观 + 一键启动脚本**

- **全量导入**（Lead 出转换器与导入脚本，**执行由豆包完成**）：`zh_cn` 全库 **6,665** 个 `.md` → MediaWiki 正文页 **6,668**；分类成员逐类归位：**物品 3880 / 模拟宇宙 2169 / 光锥 205 / 剧情 173 / 角色 119 / 遗器 65 / 音乐 21 / 世界观 8 / 活动 8 / 货币战争 7 / 规则 5 / 敌人 4 / 关卡 3**。
- **新增工具**：
  - `.tmp_mediawiki/seed/md2mw.py` —— vault `.md` → MediaWiki wikitext（模板参数 + 标题/表格/列表/双链转换 + **同名标题去重**）
  - `mediawiki-1.42.5/maintenance/dshImport.php` —— 单进程批量导入（走 PageUpdater API，6,665 页数分钟内完成；比逐页 `edit.php` 快两个数量级）
  - `.tmp_mediawiki/start-mediawiki.cmd` —— **一键启动/停止/查状态**（`start-mediawiki.cmd [stop|status]`），内含临时目录设置
  - `.tmp_mediawiki/seed/Common.css` → 已写入 `MediaWiki:Common.css`：**瑞士风**（Helvetica 栈 / 8px 栅格 / 全直角 / 细线 / 唯一瑞士红 `#E30613` / 禁阴影渐变）
- **收尾清理（豆包执行，Lead 实测复核）**：17 个含 `{ } # < >` 的**非法标题**已净化并补导 → **残留 0**；隔离测试页 `分类测试页` 与陈旧 `Category:分类` 已删除 → **均为 0**。
- **踩坑记录（供后续参考）**：① 1.42 已移除 `WikiPage::doEditContent()` 与 `PageUpdater::setSummary()`，需用 `setContent` + `saveRevision(CommentStoreComment)`；② `ContentHandler` 在该版本仍为全局类；③ PHP 双引号串里变量名后紧跟中文全角括号会被吞进变量名（需 `{$var}`）；④ `edit.php` 只读 stdin 且忽略无变化编辑。
- 站点：`http://127.0.0.1:8788/`（管理员 `Admin`）｜ **未提交、未推送**；`.tmp_mediawiki/` 约 800 MB，删除即可完全清理。

## 2026-10-03 14:20

**MediaWiki 批量导入：音乐库 21 页 + 模板自动归类**

- **新增转换器** `.tmp_mediawiki/seed/md2mw.py`（Lead 出稿，190 行）：把 vault 的 `zh_cn/*.md` 转成 MediaWiki wikitext —— 头部 `# 标题` → 页面标题；`> 数据来源/实体ID/数据版本/官方Wiki` → `{{实体}}` 参数（`> 创建时间/更新时间` 丢弃）；`## → ==`；markdown 表格 → MediaWiki 表格；列表/粗斜体/外链转换；`[[zh_cn/路径|显示]]` → `[[页面标题|显示]]`（未收录则降级为纯文本，避免满屏红链）。
- **模板升级**：`Template:实体` 增加**自动归类**——`分类` 参数优先，否则按 `类型` 精确匹配（角色/光锥/物品/遗器/音乐/活动/敌人/关卡）；同时启用 **TemplateData** 扩展（原 `<templatedata>` 未启用扩展时会被当纯文本输出，其描述里的 `[[Category:…]]` 还会**泄漏成真实分类**）。
- **导入结果（SQLite 权威口径）**：正文页 **25**（首页 + 音乐 20 专辑 + 音乐索引 + 真珠 + 潮玩礼券 + 1 隔离测试页）、模板 **1**；**`Category:音乐` 成员 = 21** ✓。
- **渲染实测**：抽验 `失控`/`行于命途6`/`真珠` 均 **HTTP 200 且模板渲染生效**，实体ID 单元格分别为 `无（官方未公开）`/`22`/`1503`；`分类：音乐` 链接已生成。
- **两处坑（已记录）**：① 模板改版后**已存在页面不会自动重建分类**，需重存或 `refreshLinks.php`；② `maintenance/edit.php` 对**内容无变化**的编辑会直接忽略（"no change was made"），故「重存同内容」不生效。
- **残留（本地演示无碍）**：隔离测试页 `分类测试页` 与 1 条陈旧 `Category:分类` 待清理（1.42 无 `deletePage.php`，可在网页端用 Admin 删除）。
- 站点：`http://127.0.0.1:8788/`；**未提交、未推送**。

## 2026-10-03 14:15

**本机 MediaWiki 实例已跑通（1.42.5 + PHP 8.3.35 + SQLite）＋ 建 `Template:实体` 通用信息框**

- **成果**：站点 `http://127.0.0.1:8788/`（HTTP 200，标题「HSR知识库」，MediaWiki **1.42.5**）；`Template:实体` 通用实体信息框已建（2,943 B wikitext），并导入 **3 个样本页**（真珠 / 潮玩礼券 / 失控）——**模板渲染全部生效**，实体ID 单元格实测分别为 `1503` / `61` / `无（官方未公开）`。
- **不装系统软件**：全部落在 `G:\HSR\.tmp_mediawiki\`（不入库）——PHP **8.3.35** 解压即用、MediaWiki **1.42.5 官方发行包**（含 `vendor/`）、数据库用 **SQLite**（PHP 自带 `pdo_sqlite`）、Web 用 `php -S`（无需 Apache/IIS）。
- **通道踩坑**：`php.net` / `mediawiki.org` / `releases.wikimedia.org` 在 PowerShell 下报 SSL 失败 → 实为 **schannel 吊销检查**，`curl --ssl-no-revoke` 即通；GitHub 镜像 tag 的包**不含 `vendor/`**，故改用官方发行包。
- **⚠️ 环境级缺陷与兼容层（重要）**：本机 PHP 的 **`is_writable()` 对任何路径恒返回 false**（连 PHP 自建目录、以及刚写入成功的文件都是 false），但真实写入完全正常。MediaWiki 多处依赖它 → 安装先后报「找不到可写临时目录 / 数据库只读 / 数据库文件不可写」。**处置**：新增 `dsh_compat.php`（`dsh_is_writable()` 用**真实写探测**），并在 MW 核心 **12 个文件 / 17 处**把 `is_writable(` 替换为 `dsh_is_writable(`；原件已备份至 `.tmp_mediawiki\compat_backup\`。**仅影响该演示实例，不动仓库数据。**
- **端口**：用户原选 `8080`，但该端口被 **steamwebhelper（Steam）** 占用 → 改用 **`8788`**，并同步改 `LocalSettings.php` 的 `$wgServer`。
- **建页工具坑**：`maintenance/edit.php` **只从 stdin 读正文**（多传文件参数会被忽略、存成空页）；改用 `cmd /c "... edit.php < file"` 输入重定向后正常。
- **登录**：管理员账号 `Admin`（口令 `HsrAdmin2026!`，仅本机演示用）。
- **未提交、未推送**；`.tmp_mediawiki\` 约 200 MB，删除即可完全清理（含一处对 MW 源码的本地补丁）。

## 2026-10-03 13:15

**① 主题切换升级为三态 ② wiki 详情页 URL 改用「实体ID」（用户拍板）**

- **① 三态主题**（`wiki/assets/theme.js` 整文件重写）：循环 **跟随系统 → 亮色 → 暗色 → 跟随系统**；`跟随系统` 时**移除 `data-theme`**（交给 `@media (prefers-color-scheme)`），`亮色/暗色` 时设 `data-theme` 覆盖系统；**按钮文字显示「当前」主题**并同步 `aria-label` / `title`；`localStorage` 记忆（`file://` 下 try/catch 兜底）。`index.html` 与 `build_wiki.py` 注入的按钮**静态初始文字**改为「跟随系统」（无 JS 兜底）。
- **② 详情页 URL 改用实体ID**（用户选定范围：**只改生成页 URL，`.md` 文件名一律不动**）。Lead 先实测前置条件：`zh_cn` 共 **6,665** 个 `.md`，其中**有数值实体ID 5,413**、非数值（无（官方未公开）等）**564**、无 ID 行 **688**；**同一目录内 ID 冲突 = 0**（跨类重复 446 个但分属不同目录，不冲突）→ 故「同目录内以 ID 替换文件名」安全。
  - 实现（`build_wiki.py`）：新增 `SRC2KEY`（源路径 → 页面键；有数值 ID 则键 = `目录/<ID>`，否则保持原相对路径），`PAGE_SET` 取其值集；`resolve()` 末尾追加 `t = SRC2KEY.get(t, t)`，并在键冲突时**退回原名并告警**。
  - **验收（Lead 亲自）**：`build_wiki` → 页 **6,665** / 链接 **9,878** / **dead 0**；`pages/character/欢愉/1503.html`（真珠）**已生成**、旧名 `真珠_冰_五星.html` **已消失**；`pages/items/Virtual/Virtual/61.html`（潮玩礼券）**已生成**；无 ID 的 `pages/音乐/场景OST/失控.html` **保留原名**；索引页链接已改指 `.../61.html`；首页 **13 条导航坏链 0**；`git status` 中**无任何 `zh_cn/` 改动**（只动生成器与生成物）。
- **本地入口**：`file:///G:/HSR/wiki/index.html`（右上角按钮在「跟随系统 / 亮色 / 暗色」间循环）
- **未提交、未推送**（按用户指示）。

## 2026-10-03 12:55

**① 暗色模式手动切换（全站生效） ② 「纪念奖章」建页（用户拍板）**

- **① 主题切换**：新增 `wiki/assets/theme.js`（原生 JS，约 22 行，零外部依赖）；`style.css` 增 `:root[data-theme="light"|"dark"]` 显式主题块（手动选择优先于系统偏好）+ `.topbar`/`.theme-toggle` 样式（直角、细线、无阴影、不用红色）；`index.html` 与 **`build_wiki.py` 注入的每个页面**均含 `.topbar` 按钮 + `{up}assets/theme.js`；选择写入 `localStorage`（`file://` 下包 try/catch 兜底），**跨页记住**。
- **Lead 实测捕获并修掉一个功能性缺陷**：首版按钮**没有任何点击绑定**（只定义了 `window.__toggleTheme` 却无人调用）→ 点了没反应。已把 `DOMContentLoaded` 回调改为**绑定 click 监听**（`wiki/assets/theme.js` L20-24），仅改这 1 个文件、未动 HTML 与生成器。
- **② 「纪念奖章」**（用户拍板：建页，实体ID 写「无（官方未公开）」）：`zh_cn/items/Material/Material/纪念奖章.md` 已建，评级**如实写「待补充」**（不编造星级）；并**照 `Usable/Book` 索引的「无评级」先例**登记进 `Material_索引.md`（条目数量 **66 → 67**、`- 无评级（1）`、新增 `### 无评级` 分组 + 条目行）。
- **回归（Lead 亲自）**：`build_wiki` → 页 **6,665**（+1＝纪念奖章）/ 链接 **9,878** / **dead 0**；`verify_fields` → **异常 0 / 已知待补充 156**；`style.css` 违规扫描（非零圆角 / 阴影 / 渐变 / em dash）**全部 0**；首页 **13 条**导航完整。
- **本地入口**：`file:///G:/HSR/wiki/index.html`（右上角「暗色 / 亮色」按钮可切;）
- **未提交、未推送**（按用户指示）。

## 2026-10-03 12:35

**wiki 样式重做：瑞士国际主义（Swiss / International Typographic Style）**

- **范围**：仅 `wiki/assets/style.css`（64 增 / 34 删）；`wiki/index.html` 仅排版微调，**13 条导航链接全部保留**（逐条实测）。
- **方法**：Lead 加载设计 skill（`design-taste-frontend`）并转成**可执行规范**下发给执行方（含 Design Read、三档 dials `VARIANCE 5 / MOTION 1 / DENSITY 5`、类契约、验收标准）。
- **落地要点**：单一无衬线栈 `"Helvetica Neue",Helvetica,Arial,"Noto Sans SC","PingFang SC"`；**左对齐右不齐**；**8px 间距栅格**；**固定字号阶梯** 40/26/19/16/14/13；**近单色 + 唯一强调色 瑞士红 `#E30613`**（暗色下 `#FF3B30`）；**全站直角（`border-radius:0`）**；表格细线 + `tabular-nums`；引用用 3px **黑**线（红只留给链接/标记）；`a:focus-visible` 2px 红框；`prefers-reduced-motion` 兜底；**暗色主题保留**。
- **验收（Lead 亲自实测）**：违规扫描 `border-radius:[1-9]` / `—`(em dash) / `box-shadow` / `gradient` / `backdrop-filter` / `text-align:justify` **全部 0 命中**；**16 项类/特性契约全部存在**；`python wiki/build_wiki.py` → 页 **6,664** / 链接 **9,877** / **dead 0**；首页 13 条导航逐条可达。
- **本地入口**：`file:///G:/HSR/wiki/index.html`
- **未动**：`wiki/build_wiki.py`（其中 `M` 为 Lead 早前 **D-041** 动态类别修复，非本次执行方改动）、任何 `.md`、`zh_cn/` 数据；**无新增图片/外部依赖（离线可用）**。

## 2026-10-03 12:20

**目标「4.6 补全 + 音乐专辑全量收集」收工（轮次 1–12，Lead 全程实测复核）**

> 用户目标：`将4.6版本补全并将所有音乐名字专辑也做收集`（goal `goal-0ae3122a…`）
> 台账：`docs/prompts/目标_4.6补全与音乐收集.md`（逐轮实测记录）

- **音乐库新建（规范 v1.15 §十八）**：`zh_cn/音乐/` 建成 **21 文件 = 20 张专辑 + 主索引**，分「场景OST 13 / PV专辑 6 / 角色与动画短片EP 1」。全部专辑**官方中文名经 Lead 独立复核**（百度百科 + 酷我/网易云/QQ音乐官方专辑页 + 官方新闻）；并**补入漏项**《神说要有笑（中篇）》（官方新闻 165244）。
- **曲目全量收集**：**618 首**，其中 **614 首**为「中文名（English Title）」双写；**1 首**（行于命途2 第 22 首）官方中文名未取得并**如实注明**；另 3 首为纯中文名或器乐版英文名（非缺失）。
- **曲名对账工具（新）**：`.tmp_build/verify_tracknames.py` —— 以 SRR `sub_type=MusicAlbum`（cn 272 / en 266，按 id 配对 266 条）做**零联网官方对账**；可校验 **232** 首 → **一致 232 / 不一致 0**。该工具**查出并修正 4 处真错误**（《神说要有笑（中篇）》「英雄集合」→ 官方「**英雄集结**」；《长生梦短》「蝉喓歌**：**…」3 处 → 官方「蝉喓歌**·**…」，脚本 `fix_tracknames.py`）。
- **4.6 补全**：① **`zh_cn/enemies/` 敌人库建成**（4 文件：主索引 + `首领/首领.md` + 「堕神之血•亚婆离」「狂兽的胚芽」，技能如实留「待补充」）；② **「巡星之礼」入 `events/`**（活动索引 5→6）；③ **道具 3 个**：「潮玩礼券」（ID 61）、「愿望星尘」（ID 284）、「孤狼墨镜」（ID 227017，`Usable/PlayerOutfit` → **确认无需新建「时装」类别**），均已登记进叶子索引；④ **4.6 对账**逐类完成（角色/光锥/遗器/活动/关卡/敌人/剧情），纠正执行方 3 处误报。
- **工具链修复（重要）**：`build_wiki.py` 顶层类别白名单**硬编码**导致新增类别后 **dead = 9** → 改为**动态推导**（**D-041**），修复后 **dead 0**；`verify_fields.py` 扩展纳入 `音乐`/`enemies` 类别（**D-041 遗留关闭**），并据此**两次捕获执行方「整文件重写丢节」回归**（**D-042**）。
- **最终校验（Lead 亲自）**：`verify_fields` **异常 0 / 已知待补充 156**；`build_wiki` 页 **6,664** / 链接 **9,877** / **dead 0**；`verify_links` exit 0；音乐时间戳不变式 **21/21**；图片 **0**。
- **仍未闭合（如实登记）**：① 「纪念奖章」SRR 无收录（4,073 条查无）→ 待用户定是否以「实体ID：无（官方未公开）」建页；② 音乐**四语言镜像**缺官方日/韩/繁专辑名（按 **D-028** 不建机翻）；③ 7 处 4.6 真缺口中的「云边拾暖」「月待花时」（SRR 未收录）、异相仲裁玩法页（官方未给机制）。
- **⚠️ 未提交、未推送**：工作区 **27 项**改动（`zh_cn/音乐/`、`zh_cn/enemies/`、4 个 `zh_tw` 目录、文档若干），等用户放行；**push 前必须**跑 `wiki/build_wiki.py` + `scripts/verify_links.py` + (`cd zh_cn`) `scripts/verify_fields.py`。
- **修复：`wiki/index.html` 首页导航全部坏链（Lead 实测发现）**：该文件是**静态手写**（不被 `build_wiki.py` 重生成），其 `href` 一律写成 `pages/zh_cn/<类>/…`，而生成器实际产出在 **`wiki/pages/<类>/…`（无 `zh_cn/` 前缀）** → **14 条导航链接自建立起全部打不开**。已改回 `pages/<类>/…`，并**补入新类别入口**（`音乐`、`敌人`、`规则`、`货币战争`、`世界观`），页数说明刷新为 **6664**；改后逐条 `Test-Path` 复核 **坏链接 0**。本地入口：`file:///G:/HSR/wiki/index.html`

## 2026-10-02 20:00

**W-4.6-24 结项：数据区文件时间戳落地（30,018 个 `.md`）+ 仓库回到可控状态**

- **用户口径（选项④）**：**只给数据文件加时间戳**——`zh_cn/` + `en_us/` `zh_tw/` `ja_jp/` `ko_kr/` 及各自 `quest/剧情文本/`；`docs/`、`wiki/`、根文档**一律不加**。
- **第 1 步（Lead）· 备份还原**：从 `.tmp_build/stamp_backup/`（**38,330 文件**，stamp 前全量快照，**保留原始文件系统时间**）robocopy `/COPY:DAT /E /MT:8 /R:0` 还原 5 个语言目录 → 五目录 **exit=1**（无失败），**12.5s**；同时把 `docs/`、`wiki/`、`compliance-assessment/` 与 10 个根 `.md`（共 64 个）`git restore` 回 HEAD。还原后 `git status --porcelain` = **2 行**（仅 2 个未跟踪的 `docs/prompts/00_*.md`）→ **证明备份与 HEAD 内容逐字节一致**。
- **第 3 步（豆包执行）· 盖时间戳**：新脚本 `.tmp_build/stamp_final.py`（`dry`/`stamp`/`touch`/`verify`，围栏感知、幂等、不认识的既有时间戳行保留不动）→ `stamp` **30,018/30,018**、0 error；`touch` 把线上 mtime 还原为真实值；`verify` **ok=30018 / bad=0**。
- **Lead 独立复核（自述不作证据）**：抽样 **25/25 一致**（正文时间戳 == `os.stat` == 备份时间）；幂等复跑 `stamped=0 / unchanged=30018`；`git diff --shortstat` = **29,182 files changed, 58,364 insertions(+), 0 deletions(-)**（纯 2 行/文件）；`LICENSE` 零改动；非数据区修改数 **0**；PNG **0**；`verify_links` exit **0**；`verify_fields` exit **0** 且仍为 **156**（命途 4 / 星级 3 / 获得途径 149）。
- **本轮暴露并闭环的 4 个缺陷**：①`scope_timestamps.py clean` 按行删除会**误删代码块示例行**（实证：上一轮 apply 把 `工单_4.6-24` §3.1 的示例改成实际时刻）→ 弃用，改 `git restore`（**D-032**）；②`stamp_times.py` 无围栏感知 → 新脚本已修；③此前「quest 836 个文件不在备份里」的说法**不成立**（实测备份含 168/167/167/167/167 = 836 个，**D-033** 更正）；④**沙箱 ACL 拒写**：数据目录对受限令牌拒写（robocopy `ERROR 5`），而 robocopy **未限重试**时按默认百万次静默重试 → 伪装成「卡死 20 分钟」；用 `diagnose-windows-sandbox-acl` 一次修复（`zh_cn` `writeOwner` false→true，`GRANTED=1`，回滚脚本在 `G:\dsh-acl-recovery-hsr\`）后恢复正常（**D-034**，并立纪律：批量文件操作一律显式 `/R:0 /W:0`）。
- **口径落盘**：`docs/仓库结构.md` 新增 §七「文件时间戳口径」——含**语义限制**（文件系统时间 ≠ 内容首发时间、≠ git 提交时间）与**维护纪律**（`stamp_final.py` 绑定本轮备份，**内容改动后不得直接重跑**）；决策记录新增 **D-031～D-034**。
- **⚠️ 仍未提交、未推送**：工作区 **29,184** 项改动（29,182 修改 + 2 未跟踪）全部待用户放行；**push 前必须补跑** `python wiki/build_wiki.py` + `python scripts/verify_links.py` + （`cd zh_cn`）`python ../scripts/verify_fields.py`。

## 2026-10-02 18:20

**W-4.6-23：仓库结构整理（清理 361 MB + 规范落盘）**

- **删除可再生成内容**：`temp/`（**284 MB** 一次性脚本 / 缓存 / TextMap 副本；`verify_links`、`verify_fields`、`build_wiki` 均不依赖）→ 已实测三项校验全部 exit 0；`.tmp_build/W4619_backup`（65 MB，内容已全部进入 git 提交）、三个校验副本 `g1lab` / `mtlab` / `pass2_lab`（11 MB）；误置于数据树内的空目录 `zh_cn/quest/剧情文本_备份_分支转换前/`。**合计释放 361 MB**（3,661 → 3,300 MB）。
- **`.gitignore` 重写**：分组注释（工作区临时 / SRR 克隆 / Wiki 生成物 / 敏感本机配置 / 来源受限内容），去除冗余与失效条目；逐条 `git check-ignore` 复验通过（`temp`、`.srr`、`.obsidian` 因目录已不存在而不报规则，属预期）。
- **新增 `docs/仓库结构.md`**：顶层结构权威表（作用 / 是否入库 / 体积）、根目录文档清单、**四条入库边界铁律**、提交纪律、定期清理规则、变更记录；README 结构表与口径说明已链接该文。
- **文档状态标注**：`docs/quest_pending_translation.md` 标注**已作废（存档）**——其中 LLM 补译计划已按 W-4.6-21 甲口径撤下，不得再作待办依据。
- **根目录 8 份文档保持原位**（如 `格式规范与要求.md` / `数据来源.md` / `待办清单.md` / `翻译办法.md`）：被 5–22 个文件引用，移动需批量改写相对链接；作为 vault 门面保留，新增文档默认放 `docs/`（已写入结构规范）。
- push：提交已推送至 `origin/main`。
- **⚠️ 清理误伤与修复（重要）**：`temp/win_certs.pem` 实为本机 git 用的 CA 包，删除后 push 报 `error setting certificate file`；改用 Windows 证书存储（`git config http.sslBackend schannel`，并移除 `http.sslCAInfo`）后恢复正常。已写入 `docs/仓库结构.md` §六「本机 git 配置」并立下纪律：**本机运行依赖的文件不得放在会被清理的目录**。

## 2026-10-02 15:25

**W-4.6-22：wiki 内链 URL 编码修复 + 统计口径刷新 + push**

- **D-030 修复**：`wiki/build_wiki.py` 新增 `urlq()`（`urllib.parse.quote(path, safe="/")`），Markdown 内链 / 双链 / 上一页 / 下一页 **4 处 href** 全部编码；死链统计改用 `unquote()` 还原后比对。库内含全角引号的文件名（`线索信息·“香味”.md`，55 处引用）不再破链；物理文件名保持不变。
- **构建与校验**：`python wiki/build_wiki.py` → **6,635 页**，`link_report.json` = `total 9842 / dead` **0**；`scripts/verify_links.py` 退出码 0（正式库死链 0）；`scripts/verify_fields.py`（在 `zh_cn/` 下运行）已知待补充 156（blessing 命途 4 / 星级 3 / items 缺获得途径 149），与既有记录一致。
- **统计口径刷新（实测 2026-10-02）**：`zh_cn` **6,635**（含索引）；镜像 `en_us` **5,851** / `zh_tw` **5,845** / `ja_jp` **5,845** / `ko_kr` **5,842**；`wiki/` **6,635 页**（=`zh_cn` 全量，每 `.md` 一页）。同步更新根 `README.md`（规模表 + 口径说明 + 校验工具链行）与四语言 `docs/README_{en,ja,ko,zh-Hant}.md` 镜像行。
- **索引口径统一**：`docs/multilang_index.md` 重写为实测表（character/lightcone/relic/items/simulated/quest/worldview 逐项，逐语言复算自洽）；`docs/multilang_coverage_report.md` 合计行补入 `quest`/`worldview` 并注明口径变更（旧表仅 5 类 → 5,669/5,670/5,670/5,667）。
- **push**：4 个 commit 已推送到 `origin/main`（最新 `2cb92f4ae`）→ **GitHub 上已不再跟踪**任何 `*/quest/剧情文本/` 文件（本地 168 个保留）。
- 落盘：`docs/prompts/工单_4.6-22_wiki链接编码.md`。

## 2026-10-02 15:05

**W-4.6-20/21：GitHub 撤下跟踪 + BWIKI 覆盖核对 + 机器翻译撤下**

- **GitHub 撤下跟踪（D-025）**：`git rm -r --cached` 五语言 `quest/剧情文本/`（836 个跟踪文件）→ `git ls-files '*/quest/剧情文本/*'` = **0**；本地 **168** 文件完好；`.gitignore` 增 `*/quest/剧情文本/`；提交 **`feede2962`**（850 文件）与 **`3994b56e6`**（文档）。**未 push**。
- **BWIKI 覆盖核对（D-026 / D-029）**：拉取 BWIKI 星铁站 `allpages` **7,888** 页，与 168 个任务文件规范化比对 → **全部有对应页**；唯一例外为本库自有索引 `支线任务索引.md`。`致黯淡星.md` 曾误判「0 命中」，实为页面标题带全角冒号「**致：黯淡星**」（Lead 更正并入文件头来源核验行）。
- **机器翻译撤下（D-028，甲口径）**：撤下 `en_us` + `zh_tw` 中**非官方本地化的 LLM 译文 / 未翻译中文残留** → 改动 **99** 文件（en 50 / zh_tw 49），占位符文件不动（239 skipped）；`ja_jp`/`ko_kr` 残留本为 0 未动；Lead 独立复核**残留非占位描述段 = 0**。执行前备份 `.tmp_build/W4621_backup/`（334 文件）。
- **Lead 自查修复**：镜像用**本地化标题**（`Quest Description`/`任務描述`），首版脚本按中文标题匹配 0 命中；且正则 `(?=\n##[ \t]|\s*$)` 的 `\s*$` 可匹配空 → 改为**逐行解析**后在副本验证通过再上线上。
- **附带发现（D-030）**：`wiki/build_wiki.py` **未做 URL 编码**，而库内有含全角引号的文件名 `线索信息·“香味”.md`（55 处引用）→ 浏览器请求该路径可能破链，待修。
- 落盘：`工单_4.6-20_Git撤下与BWIKI核对.md`、`工单_4.6-21_机器翻译撤下.md`；`决策记录.md` 新增 **D-025~D-030**；`docs/待补充清单.md` 更新。
- **仍未 push**：本地 3 个 commit 待用户放行。

## 2026-10-02 14:20

**W-4.6-19 阶段二执行完毕：米游社表达撤下 + BWIKI 样板清洗与 CC 标注（方案甲）**

- **用户放行**：按方案甲执行（原地清零 + BWIKI 清洗保留，不做整文件 `git rm`）。
- **G1 · 米游社来源表达撤下（454 文件 / 五语言）**：`quest/剧情文本/` 根目录米游社源文件 → 撤下任务描述与逐句对话正文，保留任务地区 / 类型 / 等级 / 奖励 / 章节结构等**事实性信息**；来源行改写为「官方公开数据（该站声明禁止转载，本库不再收录其文字表达）」；状态 `v1.0 → v0.2`。执行结果 `converted=440 / skipped=14`，**残留长描述段 0**（修复前 33）。
- **G2 · BWIKI 裸抓取文件清洗（370 文件 / 五语言）**：删除站点样板（站点简介、交流群号 1017604603、阅读数、编辑者、导航控件、面包屑）并写入**独立** `CC BY-NC-SA 4.0` 署名行；10 个源站空页按 `v0.1（源站为空页）` 标注。执行结果 **370/370**，样板串残留 **0**。
- **G4 · 声明与矛盾修正**：`NOTICE.md` 新增 §七「来源撤下与许可标注」（米游社限制 + BWIKI 三义务）、BWIKI 数据源行去重并写明 CC BY-NC-SA 4.0；`数据来源.md` 新增「来源撤下」与「三·二 B站 BWIKI」两节；`docs/數據來源.md`/`data-sources.md`/`データソース.md`/`데이터소스.md` 四语言同步；`README.md` 与 `NOTICE.md` 的「任何人均可再分发本项目内容」限缩为「仅代码、脚本与数据编排成果」。
- **验收（Lead 独立实测）**：BWIKI 署名 370/370；六类样板串命中 **0**；`g1.uncleared=[]`、`stillMiyoushe=[]`；入链 `zh_cn/quest/主线任务.md` **31** 目标、`en_us` **30** 目标，**0 缺失**；禁词扫描（反爬 / anti-crawl / 안티크롤링 / 规避反爬 / 防止 IP / 模仿得像正常人）**全部 0**；`LICENSE` 零改动。
- **Lead 自查修复的 3 个脚本缺陷**（均在本轮内闭环，副本回归后才上线上）：① G2 首版只切头部样板段 → 重写为统一幂等脚本；② G1 首版跳过 `## 任务描述` 段清理；③ 段落正则 `\s*$` 吞换行 + 幂等判断跨段误判 → 改为 `/^##[ \t]+(.+?)[ \t]*$/` 与段边界幂等。
- **安全网**：执行前全量备份至 `.tmp_build/W4619_backup/`（含剧情文本 168 个）；所有脚本与日志在 `.tmp_doubao/`（均被 `.gitignore` 覆盖，不入库）。
- **⚠️ 尚未提交**：改动只在工作区，**未 `git rm --cached`、未 commit、未 push**；仓库仍为 private。下一步需用户放行（见 D-024）。

## 2026-10-02 14:15

**W-4.6-19 阶段一评估通过 + 处置方案定稿（米游社撤下 / BWIKI 标注）**

- **自我更正（D-019）**：上一轮「全库 `CC BY-NC-SA` 0 命中」**不准确**。真实文本为 `CC　BY-NC-SA`（**全角空格 U+3000**），ASCII grep 漏检；宽匹配实测五语言 **各 74 个文件**（合计 370）含 BWiki 站点样板。但该文本是**抓取残留**、非有意署名，文档层（NOTICE/数据来源/README）仍为 0 处 → 「合规标注缺失」结论仍成立。
- **双来源定性（D-020）**：`zh_cn/quest/剧情文本/` 根 94 文件（93 有来源行，其中 **91 个标「米游社Wiki」**，含完整对话表达）；`冒险任务/`(48)+`同行任务/`(26)=**74 个为 BWIKI 页面裸抓取**（站点样板、交流群号 1017604603、阅读数、导航控件；74/74 命中）。
- **通道裁定（D-021）**：豆包桌面版**确实具备真实 PowerShell / Write / Grep 与「完全访问」**，能读写本机文件（独立写出 389B 队列文件、跑完 publish→claim→complete；独立产出 448 行评估），**但仍无 MCP 连接器**。→ 豆包可用作**文件级执行方**，交付以「落盘文件 + Lead 独立复核」为准。
- **阶段一评估**：`G:\HSR\.tmp_doubao\W-4.6-19-阶段一评估.md`（448 行 / 29.5 KB，豆包产出）。Lead 独立复核 4 项数字 **168 / 91 / 74 / 370 全部复现**；两处「不一致」确认为**口径差异**：①`Get-Content|Measure -Line`=603（非空行）vs `ReadAllLines`=664（总行数）②引用 `剧情文本/` 的文件 16 个（旧口径 14 已排除 `docs/`）。
- **关键入链事实**：`主线任务.md` 引用 `剧情文本` 72 次 / `剧情文本/` 32 次，**唯一目标 31 个、0 缺失**，且**全部指向根目录**（不指向冒险/同行）→ 整文件删除会断链，故采纳「原地表达清零」。
- **方案定稿（D-022）**：G1 = 91×5 米游社源**表达清零 + 事实留注**；G2 = 74×5 BWIKI 裸抓取**清洗样板 + 补独立 CC BY-NC-SA 4.0 署名**；G4 = `NOTICE`/`数据来源`/`README`（含四语言）加声明并修「任何人均可再分发本项目」矛盾表述。**默认不做整文件 `git rm`**。
- **落盘**：`docs/prompts/工单_4.6-19_米游社撤下与BWIKI标注.md`（阶段一）、`docs/prompts/工单_4.6-19_阶段二_执行.md`（阶段二，待在用户拍板后放行）；`决策记录.md` 新增 **D-021 / D-022**，**D-023** 为待拍板三选一。
- **工作区产出约定**：所有豆包/评估产出统一放 `G:\HSR\.tmp_doubao\`（已被 `.gitignore` 的 `.tmp_*` 覆盖，不入库）。

## 2026-10-01 22:25

**Lead 复核：合规评估报告对账 + 豆包通道裁定（含 3 项新发现缺口）**

- **通道裁定（D-016）**：豆包桌面版**不支持第三方 MCP server**（`%APPDATA%\Doubao` 全域 0 命中；连接器目录无 `clients.json`、8790 端口未监听）；CDP 实测其真实工具清单无 `task_claim`/`task_complete`，豆包自答「未执行过 task_claim」→ 会话 `38445143454447618` 中「已回报」为**虚构**，不得作为交付证据。**可用通道 = CDP 消息通道**（`127.0.0.1:9222`，下发 + 读回双向已实测）。
- **合规报告对账（报告 = 豆包 16:10 产出，22KB，git 已跟踪）**：6 条整改中 3 条已落地并复核——① 版权标识（`© 米哈游版权所有` 6 文件命中）② 反爬表述（已清除）③ 数据源合规表（已补 BWIKI / 米游社「禁止转载」标注）。
- **新发现缺口 1（红线）**：**BWIKI 的 CC BY-NC-SA 4.0 义务全库零标注**（`grep 'CC BY-NC-SA'` → **0 命中**），而 `数据来源.md` L74 载明 BWIKI 源事件文本已回填 **320/384** 条 → 署名 / 相同方式共享义务未履行（D-019）。
- **新发现缺口 2**：授权表述与限缩条款**自相矛盾**——`README.md:44`「任何人均可免费使用、复制、修改、再分发本项目」↔ 同节「AGPL 仅覆盖代码 / 脚本 / 编排」；`NOTICE.md:45/64` 同病 → 落 `工单_4.6-18` C-2。
- **新发现缺口 3**：`NOTICE.md:28-29` BWIKI 行**重复且口径不一** → 落 `工单_4.6-18` C-3。
- **落盘**：新增 `docs/prompts/工单_4.6-18_许可分层与BWIKI标注.md`（红线 / 5 项执行内容 / 验收标准 / 交付格式）；`决策记录.md` 新增 **D-018**（许可分层口径草案，待拍板）、**D-019**（BWIKI 标注缺口认定为红线）。
- **环境下修复**：工作区被 Windows 文件权限阻塞（`SetNamedSecurityInfoW failed (Win32 5)`）→ 权限诊断脚本一次修复（`G:\HSR` 增补当前用户完全控制，`WRITE_OWNER: false→true`，`GRANTED=1 REFUSED=0`），报告留于 `%TEMP%\dsh-acl-recovery-hsr\`。
- **时间戳说明**：本文件原 17:20 条日志实际落盘于提交 `3ded6bf3c`（17:13:49）之后约 6 分钟，属既有不一致，此处留痕、不回改历史条目。

## 2026-10-01 17:20

**MCP 工具层更名与精简：`obsidian-kb-mcp` → `markdown-kb-mcp`**

- 独立项目更名为 **`markdown-kb-mcp`**（原 `obsidian-kb-mcp`，GitHub 旧地址自动重定向）；包名 `obsidian_kb_mcp` → `markdown_kb_mcp`，版本 **v1.2.0**。
- **精简**：HSR 专属配置移出核心目录 → `examples/profiles/hsr.json`（示例）；`profiles/` 只保留通用 `generic.json`；profile 查找同时支持两处，`--profile hsr` 行为不变。
- 清理无关内容：移除 `__pycache__`、工具描述去掉品牌表述、README 去掉与具体知识库绑定的叙述。
- 回归验证：Python 冒烟测试 20/20、Node 冒烟测试 19/19 全绿；知识库侧 `README.md` / `格式规范与要求.md` §十七 / `60_模块_MCP.md` 引用已同步更新。

## 2026-10-01 17:10

**合规整改（P0 · 依合规评估报告）**

- **删除「规避反爬」类表述**（11 处 / 5 文件，含英、韩镜像）：统一改为「遵守来源站点 robots.txt 与服务条款、控制请求频率」；`协作要求与行动准则.md` 移除「模仿得像正常人」「防止 IP 被封」。
- **补标准版权标识**：`README.md`（正文 + 版权声明节）、`NOTICE.md`、四语言 README、wiki 站点页脚，统一加「© 米哈游版权所有 + 素材权利声明 + 非官方无关联」。
- **限缩 AGPL 授权范围**：README「使用与许可」与 NOTICE §一 明确 AGPL **仅覆盖代码 / 脚本 / 数据编排**；游戏素材不在授权范围、**不得据本仓库许可再分发**；并注明 AGPL 系上游 StarRailRes 的强制要求。
- **数据源合规表补全**：NOTICE §二 增补 B站 BWIKI（仅作参考与交叉核对）；米游社官方 Wiki 标注其词条「禁止转载」→ **仅提取事实性字段**。
- **新增「本库的原创性贡献」小节**：四级索引 / 双链 / 格式规范 / 多语言对齐 / 剧情结构官方化 / 校验工具链，正面回应「纯搬运」边界质疑。
- **MCP 工具层抽出为独立项目** [`obsidian-kb-mcp`](https://github.com/ganmayou2333/obsidian-kb-mcp)（MIT · profile 驱动 · 10 工具 · 自带冒烟测试 20/20）；本库移除 `mcp/` 并更新全部引用。

## 2026-10-01 15:30

**严谨性专项修正（Lead 直接执行）+ 合规应急**

- **合规应急**：远端 `main` 删除两份私人会话记录（`docs/对话记录.xml`、`StarRailRes_data/对话记录_20260827.xml`），提交 `b9a4bfa2`、`308b700e`。⚠️ **历史中仍有留痕，须 `git filter-repo` 彻底清除**（见 W-4.6-17）。
- **格式规范 v1.13 → v1.14**：§一 目录树补 `wiki/`、`mcp/`；新增 **§十七「工程目录 wiki / mcp」**（入库 / 不入库边界表 + 3 条约束）；更新日期改 2026-10-01。
- **根 README 修正**：格式规范版本号 `v1.9` → **v1.13**（落后 4 个版本）；内容结构表补 `wiki/`、`mcp/`、`docs/`、`scripts/` 四行；文档索引表补 `NOTICE.md`、`wiki/README.md`、`mcp/README.md`、`docs/prompts/README.md`；规模数字统一千分位（`3,823` / `1,793`）。
- **数据来源 5 语言同步**：更新日期 `2026-09-30` → **`2026-10-01`**；SRR 双克隆口径由「不一致时以 `StarRailRes_repo/` 为准」改为**按用途分工**（多语言 JSON → `StarRailRes-master/index_new/`；图包与可更新副本 → `StarRailRes_repo/`）。
- **`SRR图包来源.md` 格式修复**：还原被备注从中间截断的元信息表格。
- **提示词系统同步**：`docs/豆包提示词_4.6版本建库.md` 格式规范版本 `v1.12` → `v1.14`、必读章节补 `§十六 ~ §十七`。
- **`docs/SRR_ID对照报告.md`**：加装「数字已过时」警示横幅（物品 1,594 → 现况 3,823，待重跑）。

## 2026-10-01 10:30

**W-4.6-14 SRR 图片实施（方案 B · 图片不入库）+ 真珠页链接修正**

- **新建 `wiki/copy_icons.py`**：零依赖，按 KB 实体ID 从 StarRailRes 复制用到的图标到 `wiki/assets/icons/`（1,602 个 / 43.9 MB，生成物已 gitignore）。
- **build_wiki.py 新增 `inject_icon()`**：角色页注入头像（avatar/96px）+ 立绘（character/200×280），光锥/遗器/物品/奇物注入对应小图标；无图标走 CSS 占位降级。
- **真珠页 2 条错误链接修正**：`TracePath/思绪末屑` → `CommonMonsterDrop/`，`EchoOfWar/海妖残鳍` → `AvatarRank/`。
- **pages.yml 更新**：CI 浅克隆 SRR（`.srr/`）→ copy_icons.py → build_wiki.py。
- **.gitignore 补**：`.srr/`、`wiki/assets/icons/`（图片零入库）。

## 2026-10-01 10:00

**W-4.6-13 SRR 素材接入方案（含覆盖率矩阵）**

- 新增 `wiki/IMAGERY_PLAN.md`：素材盘点（4,311 图标 / ~86 MB）、ID 映射表、三方案对比（A 入库子集 / B CI 拉取 / C 外链）、HTML/CSS 模板、版权风险评估。
- 覆盖率矩阵实测：角色立绘 ~82%、光锥 ~80%、遗器套装 ~92%、物品 ~42%。
- 用户拍板：方案 B（CI 拉取）+ 公开接受图标 + 含立绘。

## 2026-10-01 09:30

**W-4.6-12 静态 Wiki 上线（6,693 页）+ 双链归零**

- 新建零依赖静态站：`wiki/build_wiki.py` + `index.html` + `assets/`（浅/深色随系统、响应式、标题搜索）。
- 两遍扫描修复：表格 `\|` 转义、相对路径 Markdown 链接解析、空目标 `[[|...]]` 降级、Markdown 链接 `.md`→`.html` 转换。
- 死链从 5,337 → 0（wiki 自统计）；正式库 `zh_cn/` 经 verify_links.py 复核 0 死链。
- `.github/workflows/pages.yml`：push main 自动构建部署 GitHub Pages。

## 2026-10-01 09:00

**W-4.6-11 剧情完整性/正确性检查 + GitHub 上传准备**

- 完整性检查：4.6 系列子任务矩阵、索引挂接、全库抽检头部元信息。
- 正确性检查：术语抽验（兽蜕/虚照/路易斯•弗莱明）、占位残留、双链、状态真实性。
- git 预检：256 文件改动 + 未跟踪目录清单；无 `_tmp_*` 残留；C2/C3 待 Lead 放行。

## 2026-09-30 23:15

**W-4.6-09 规范扩展三类库（events/enemies/stages）+ 4.6 首批条目**

- **规范升级**：`格式规范与要求.md` v1.12 → **v1.13**，新增 §十六「活动 / 敌人 / 关卡库结构」（三类边界、三级索引、三种模板）；§一 目录树补 events/enemies/stages；§三 元信息补「无官方 ID 类别」例外条款。
- **新建目录**：`zh_cn/events/版本活动/`、`zh_cn/stages/侵蚀隧洞/`（enemies/ 暂不建——两个新敌人中文名在 TextMap 与官方中文更新说明中均未取到，登记待补充）。
- **新建索引**：`events/活动.md`（主索引）、`events/版本活动/版本活动.md`（类型索引）、`stages/关卡.md`（主索引）、`stages/侵蚀隧洞/侵蚀隧洞.md`（类型索引）。
- **新建详情（2 个）**：
  - `events/版本活动/爱，幽灵与机器人.md`（版本活动 demo，中文名据官方 4.6 更新日志）
  - `stages/侵蚀隧洞/密伶之径.md`（关卡 demo，对应遗器 133/134，中文名据库内遗器获取途径字段）
- **待补充登记**：敌人「Blood of the Fallen God: Yabuli」「Frenzied Beast's Seed Germ」中文名未取到，已登记 `docs/待补充清单.md`，不建占位。
- **镜像登记**：三类库（events/enemies/stages）四语言镜像待建，已登记 `docs/multilang_index.md`。

## 2026-09-30 21:31

**W-4.6-02 剧情文件 v0.1 质检整改（4 项最小编辑）**

- **P0-1a（摘要冒充原文摘录·第三节）**：`第五章_月升之前与兽共舞.md` 第三节「三月七的小本本」原为本助手压缩改写的 bullet 列表，与节标题「原文摘录」声明不符。已按 TextMap 原文（hash 10017765357679671623 / 3430321620919673614）逐字回填，去 `<color>/<b>/<size>/<i>/<unbreak>/<icon>` 标签，行尾加 `<!-- 原文含排版标签，已去标签 -->`。
- **P0-1b（摘要冒充原文摘录·第六节第1条）**：hash 225961152287437221（狸狸通信内幕）原为压缩摘要，已按原文逐字回填，去 `<color>/<icon>` 标签并加注释。
- **P0-1c（节标题说明）**：行39「官方简体中文原文摘录」改为「官方 TextMap 文本片段」，明确标注第三节与第六节第一条为逐字原文、其余为摘要，消除混排歧义。
- **P0-2（间隔号）**：`路易斯·弗莱明`（U+00B7）改为 `路易斯•弗莱明`（U+2022），与 hash 4839230631150652937 原文逐字一致。全文检索确认本轮文件无 `·`/`•` 混用。
- **P1-3（角色名误写）**：`主线任务.md:830`「早已揭开真实身份的『虚无』」改为「虚照」（官方原文 hash 4839230631150652937：「虚照向你坦白她的真实身份」）。全文检索 `「虚无」` 仅剩第三章存量文件中黄泉=虚无令使的正确用法。
- **P2-4（时间戳）**：上一条日志原标 `21:30`，写入时实际报告时刻为 21:19，已改为 `21:19`。
- **改动范围**：仅限上述 4 处（2 个数据文件 + 本日志）；未补写台词、未调整片段顺序、未增删 hash 条目。

---

## 2026-09-30 21:19

**4.6 剧情文件 v0.1 扩充：官方 TextMap 主题片段回填**

- **文件**：`zh_cn/quest/剧情文本/第五章_月升之前与兽共舞.md`（v0.1 → v0.1 扩充）。
- **依据**：`30_模块_剧情获取.md` G.2/G.3/G.5——TextMap 仅用于措辞校验与片段提取，**不还原对话顺序**；拿不到有序来源时保持 v0.1，只交主题片段清单（每条带 hash）。
- **回填内容**（均来自本地 `temp/textmap/TextMapCHS.json`，按主题归类）：
  - 前情·归寂之死与兽蜕苏醒（5 条 hash）
  - 姬子托付与列车启程（4 条 hash，含真珠留守与二相乐园共存亡）
  - 千星城七人部长会议派系（三月七小本本：奥斯瓦尔多/亚婆离/塔拉梵/钻石/扎扎德/阎世罗/疤眼夫人/在田）
  - 在田关键一票与幻月游戏重启（4 条 hash）
  - 阿哈身份揭露与反毁灭同盟领袖之议（4 条 hash）
  - 紧急避难通知与舆论战（3 条 hash）
  - 兽蜕追击与星核猎手会合（3 条 hash）
  - 灯塔 BOSS（2 条 hash）
- **术语修正**：官方原文为「**兽蜕**」（非此前误写的「贪饬受退」），已全文统一。
- **状态**：v0.1。正文逐句对话顺序待米游社 WIKI / B 站 Wiki 有序对话页回填；本地无任务脚本（已全库扫描确认）。
- **数据来源.md**：版本基线 4.5→4.6，真珠描述从「前瞻」改为「正式纳入」。

---

## 2026-09-30 20:30

**4.6 版本「月升之前，与兽共舞」新增内容建库（简中详情收尾 + en_us 试点镜像 + 索引同步）**

- **背景**：4.6 版本新增内容全量建库，按用户方案 C 执行——本轮聚焦简中详情核验修正、索引同步与自检日志；zh_tw/ja_jp/ko_kr 三语言镜像（除已写 en_us 4 个外）延后为后续单独大项。
- **数据源**：官方英文更新说明 https://hsr.hoyoverse.com/en-us/news/166468 ；新增关卡 https://sr.mihoyo.com/news/166478 ；商店上新 https://sr.mihoyo.com/news/166235 ；米游社真珠词条 https://bbs.mihoyo.com/sr/wiki/content/7935/detail ；Beebom Pearl Kit（beta）。
- **简中详情（核验修正，非新建骨架）**：
  - `zh_cn/character/欢愉/真珠_冰_五星.md`（1503，欢愉·冰 5★）：回填官方 Lv.80 属性（HP1203/ATK465/DEF727/SPD99/能量180）；晋阶材料由错误「思绪末屑」系列修正为童真蜡笔/造梦蘸钢/梦现管锥（CommonMonsterDrop）+ 海妖残鳍（AvatarRank）；补 A6 行迹、总属性加成（防御 22.5%）、星魂 E1–E6、技能材料说明。
  - `zh_cn/lightcone/欢愉/献给明日的色彩.md`（23055，欢愉 5★）：晋阶材料改摘要式 + 《绒绒号》系列命途材料双链，移除误入的「童真蜡笔×20」。
  - `zh_cn/relic/隧洞遗器/贪噬禁果的异端.md`（134）：2 件套核验为官方正式值「暴击伤害+16%」（非泄露的 ATK+12%）。
  - `zh_cn/relic/隧洞遗器/戏梦点星的伶人.md`（133）。
- **en_us 镜像（4 个新增，试点格式已确认）**：`en_us/relic/隧洞遗器/Dreamlit Actor.md`、`The Edacious Heretic.md`、`en_us/lightcone/欢愉/Colors for Tomorrow.md`、`en_us/character/欢愉/Pearl_冰_五星.md`。真珠官方英文 Introduction 已回填。
- **索引同步（阶段 C）**：角色总索引 欢愉 6→7 / 合计 92→93 / 版本 4.5→4.6；光锥总索引 欢愉 12→13 / 合计 169→170 / 版本 4.5→4.6，欢愉五星索引 6→7 补入「献给明日的色彩」；遗器总索引 版本 4.5→4.6（62 遗器 = 34 隧洞 + 28 位面）；README 数量统计同步。
- **待官方最终核验的数值分歧（文件内已标注，不武断覆盖）**：真珠战技治疗量（简中 6% DEF+120 vs Beebom 12% DEF+240）、天赋减伤（15% vs 30%）、终结技强化普攻额外欢愉伤害（30% vs 60%）；光锥叠影 1 敌方受伤（Prydwen 现值 +22% vs Honey Hunter beta「+10%/每名欢愉额外+4%」）。
- **自检**：`scripts/verify_links.py` 因存量日文特殊文件名在 Windows `open()` 报错（Errno 22）未能全库跑通（非本轮引入）；本轮涉及双链目标已逐一 Glob/Test-Path 核验存在（信用点、童真蜡笔/造梦蘸钢/梦现管锥、海妖残鳍、《绒绒号》三件、两件新遗器、真珠、光锥）。
- **遗留待办**：① `en_us/character/欢愉/_冰_五星.md` 空角色名前瞻占位与 Pearl_冰_五星.md 重复，未删除（铁律不动存量），待用户定夺；② 真珠/光锥技能官方正式数值待版本上线后复核；③ zh_tw/ja_jp/ko_kr 三语言镜像正文待后续大项铺开。

---

## 2026-09-30 21:05

**4.6 新增剧情（开拓任务「月升之前，与兽共舞」）骨架建库 + 索引挂接**

- **新增文件**：`zh_cn/quest/剧情文本/第五章_月升之前与兽共舞.md`（4.6 开拓任务，第五章·二相乐园）。
  - 内容：头部元信息 + 任务描述 + 任务过程节点大纲 + 关联条目；**正文逐句对话留空待回填**（零编造铁律：不写未核实台词）。
  - 依据：格式规范与要求.md §一（quest/剧情文本/）；基准文件 `第四章_英雄啊归以凡身向侵晨.md`。
- **剧情大纲来源**：官方版本更新说明 + 公开剧情实况视频（抖音合集）。核心节点：真珠交托二相乐园存续重任→列车组赴千星城出席反毁灭同盟会议→欲借公司七人董事会引来琥珀王注视以存护之力压制即将苏醒的「兽蜕」→「虚无」（阿哈）身份揭露同行→灯塔/生研院守御事件。
- **索引挂接**：
  - `zh_cn/quest/主线任务.md`：第五章子任务列表补入 4.5「千星城·挥掷千星的筹码」（官方公告 165896，2026-08-26，开拓等级≥21）与 4.6「月升之前，与兽共舞」（双链至新建文件）；新增两个节点详细剧情段；关键角色补入真珠与阿哈。
  - 任务类型说明：4.6 任务属第五章·二相乐园（非第四章翁法罗斯），命名 `第五章_<任务名>.md`，与同章既有文件命名一致。
- **待补充**：①正文逐句台词（建议从本地 `temp/textmap/TextMapCHS.json` 按任务 ID 提取，或游戏内实机录入）；②官方任务描述原文（sr.mihoyo.com 4.6 更新说明「开拓任务」段）；③4.6 冒险任务（如「变形记」，生研院接取）是否纳入——待用户确认范围。

---

## 2026-08-31 10:48

**en_us character 参数注释机械批提交 + quest 试点检查与重跑**

- **背景**：多语言工程收尾（翻译办法.md §四/§六）；en_us 残留中文行清理。
- **改动**：
  - 参数注释机械替换（`fix_param_notes.py`，92 文件 1793 行：表头 `参数N`→`Param N`、占位符说明、参数标签 `#N[i]`）提交，commit `d877bb19`；951 个上下文片段待 subagent 翻译后回填（temp/param_ctx_en_us.json）。
  - `翻译办法.md` 纳入版本管理（此前未跟踪）。
- **quest 试点检查**：3 试点文件（我曾在阿卡迪亚 135 / 铸剑为犁 596 / 主线任务 552 中文行）处于 P2 生成基线（TextMap 台词已映射，wiki 叙述/结构/选项残留中文，铸剑为犁含约 30+ 行 B站噪音）；此前中断的试点 subagent 零落盘（git 无改动）。
- **进行中**：按翻译办法 §六 重跑试点——1 个后台 subagent 处理 3 文件（每文件即存、删噪音、术语表统一）。
- **待办**：试点完成后验证剩余中文行数并评估质量/token；确认后铺开 quest 4 批（每批约 42 文件）。

---

### 四、阶段四 P2（剧情任务多语言）完成【2026-08-31 晚】
- **数据源**：官方游戏文本 TextMap（DimbreathBot/TurnBasedGameData，46.6万条 hash→文本，CHS/EN/JP/KR/CHT 五语言，经 curl 下载至 temp/textmap/）。
- **quest 剧情文本 167 文件 × 4 语言**：台词/任务名/列表/引用用 TextMap 官方映射翻译。
- **quest 台词补译至 100%**：EN 612 句、zh_tw 620 行、ja_jp 616 句、ko_kr 2329 句（wiki 转写差异文本 LLM/zhconv 补译，subagent 并行）。
- **worldview 8 文件 × 4 语言**：LLM 并行翻译（subagent），行数逐一对应、官方专名、双链保留。
- **提交**：`47d55f0d`~`ad50efdc` 共 7 个 commit。

---

### 一、多语言数据查找（阶段一~三完成：探查 / P0 基础迁移 / P1 物品与模拟宇宙）

- **目标**：为 zh-TW / en-US / ja-JP / ko-KR 四语言生成多语言数据（待办清单.md 第六节）。
- **数据源**：本地 StarRailRes-master/index_new 官方 JSON（cn/cht/en/jp/kr 五语言同量）。
- **阶段一（数据探查与规划）**：
  - 输出 `docs/multilang_coverage_report.md`（各语言 JSON 覆盖度 + md 数据库 ID 对照分析）。
  - 输出 `docs/multilang_id_map.json`（名称 → ID 集合对照表）。
  - 探查结论：P0/P1 目录官方 JSON 100% 同量覆盖；奇物/祝福按「名称→ID 集合」匹配（多 ID 同名合并）。
- **阶段二（P0 基础数据迁移，4 语言）**：
  - character 93 详情 × 4 = 372 文件：名称/命途/属性/技能（名称/类型/简述/效果模板/满级效果）/星魂全量官方文本。覆盖 98.9%（缺 真珠 7935，五语言 JSON 均未收录）。
  - lightcone 169 × 4 = 676 文件：名称/命途/背景故事/叠影效果。100% 覆盖。
  - relic 60 × 4 = 240 文件：名称/套装效果（2件套/4件套）。96.8%（缺 133/134 贪噬禁果的异端/戏梦点星的伶人）。
- **阶段三（P1 物品与模拟宇宙，4 语言）**：
  - items 3823 详情 × 4 ≈ 14000 文件：名称/获得途径。100% 覆盖（按 ID 校验；英文等语言存在多名同译，文件数略少于 ID 数）。
  - simulated 祝福 906 + 事件 384 + 奇物 84 + 加权奇物 fallback 66，× 4 语言：名称/效果官方文本。100% 覆盖。
  - 未生成：乐园漫记/惊世奇迹 150 项（米游社 WIKI 手工数据，无官方 JSON）；差分宇宙/祝福/奇物/事件 302 个索引分组文件（索引不翻译）。
- **目录结构**：`en_us/` `zh_tw/` `ja_jp/` `ko_kr/`，镜像 cn 目录结构，文件名用目标语言名称。
- **生成脚本**：`temp/multilang_gen_p0.py`（角色/光锥/遗器）、`temp/multilang_gen_p1.py`（物品/模拟宇宙）、`temp/multilang_probe.py`（探查）。
- **索引**：`docs/multilang_index.md`（4 语言文件统计与导航）。
- **待后续（阶段四/五）**：quest/worldview 剧情多语言（P2）、角色介绍 desc 回填、角色故事/遗器部位描述长文本补全（翻译工具辅助）、最终覆盖率报告更新。

---

## 2026-08-30（周日）

### 一、剧情文本全量上传（48个）
- 从米游社 WIKI 经浏览器操作获取完整交互对话，生成并推送 48 个剧情文本文件至 GitHub（`quest/剧情文本/`）。
- 覆盖章节：
  - 第五章「二相乐园」30个：第一部分（断界残章·离别之痛）7个 / 第二部分（若梦浮生·相见之欢）5个 / 第三部分（白厄与黑天鹅·真相之痛）5个 / 后续任务13个
  - 第四章「翁法罗斯」5个：我曾在阿卡迪亚 / 悬锋啊，请涤去你的血锈•下 / 银辇啊，迅赴那黑色大地 / 英雄啊，归以凡身向侵晨 / 纸页啊，镌留记忆的涟漪
  - 第三章「仙舟罗浮」13个：一、安灵布奠，天清路远 至 十三、罗浮往事
- 每个文件含：任务描述 / 任务过程 / 分场景完整对话（角色名+台词）/ 任务总结（关键信息 / 角色关系 / 伏笔）。
- GitHub 推送：11 次 commit（update.md 1次 + 剧情文本10批），最新 commit `2a999d6`。

### 二、items 目录重构（按 SRR type/sub_type 分类）
- 原 items/ 目录按自定义分类（任务道具/阅读物/配方/礼物/素材/宝箱等21个子目录）重构为按 StarRailRes 的 `type` / `sub_type` 字段分类。
- 新目录结构：6大 type（Material / Mission / Usable / Virtual / Display / Pet），共 26 个 sub_type。
- 原目录备份至 `items_backup_20260830/`，旧版分类索引暂存于 `items/_indexes/`。

### 三、items 全量补全（覆盖率 34.3% → 95.2%）
- SRR items.json 对照发现本地物品覆盖率仅 1377/4017（34.3%），缺失 2640 条。
- 分批次补全全部有效缺失物品，新增 **2446** 个物品详情文件：
  - Mission（任务道具）+90（过滤15个空名称/`{TEXTJOIN#61}`占位）
  - Material/Material（普通材料）+35
  - 27个小类别 +420（礼物38/食物17/虚拟物品42/以太技能32/以太灵19/骰子战斗角色36/骰子战斗骰子25/博物馆藏品33/博物馆展品21/角色衣装15/手机主题14/聊天气泡12/头像框5/宠物5/帕姆皮肤5/模拟宇宙勋章10/个人名片6/精灵餐厅物品18/希莉儿服装17/斗技场技能12/遗器稀有度展示4/直播物品4/三消V2物品1/PixAir材料1/平台绑定礼物1/手机壳2/强制可选礼物25）
  - Usable/Book（书籍）+838
  - Usable/MusicAlbum（音乐专辑）+266
  - Usable/TravelBrochurePaster（旅行手册贴纸）+252
  - Display/RelicSetShowOnly（遗器套装展示）+240
  - Material/PlanetFesItem（星球节庆物品）+128
  - Material/Eidolon（星魂）+97
  - Usable/ChessRogueDiceSurface（差分宇宙骰子面）+80
- 最终本地物品详情文件 **3823** 个，覆盖率 **3823/4017 = 95.2%**。
- 剩余194个未补全为空名称/`{TEXTJOIN#61}`占位物品，无实际意义。
- 所有新生成物品使用统一模板：基本信息表（名称/用途/评级/类型）+ 说明 + 获得途径，数据源标注为 StarRailRes items.json。

### 四、items 索引文件全量重建
- 重建全部索引文件以包含补全后的3823个物品：
  - 1个主索引（物品总索引.md，含覆盖率标注）
  - 7个 type 索引（Material / Mission / Usable / Virtual / Display / Pet）
  - 全部 sub_type 索引（含按评级分组的物品列表 + ID标注）
- 索引使用 Obsidian 双链格式 `[[zh_cn/items/type/sub_type/文件名|显示名]]`。

### 五、待办清单更新
- 同步更新 `待办清单.md`，记录剧情文本上传、items重构与补全、索引重建等完成项。
- 收尾约定中 update.md 更新与 GitHub 推送标记为已完成。

---

## 2026-08-29（周六）

### 一、世界观剧情库建立（worldview/）
- 新增世界观剧情库 `worldview/`，含索引.md / 世界观总览.md / 星神与命途.md（13+命途）/ 势力与组织.md（7大势力）/ 星球与地点.md（5大星球+其他）。
- 新增 `worldview/剧情时间线.md`，覆盖 1.0~4.2 共 33 个版本，含版本名 / 日期 / 主线任务名 / 剧情概要 / 新角色 / 新场景 / 新玩法 + 版本总览表。
- 新增 `worldview/术语词典.md`，9 大类（核心概念 / 角色种族 / 战斗机制 / 势力 / 地点 / 物品 / 玩法 / 其他 / 待补充），共 80+ 词条，含交叉引用链接。
- 新增 `worldview/人物关系.md`，8 大势力/星球分组（列车组 / 星核猎手 / 雅利洛 / 仙舟 / 匹诺康尼 / 翁法罗斯 / 二相乐园）+ 5 条跨势力关键关系链（罗浮旧怨 / 匹诺康尼情感 / 雅利洛恋人 / 星核猎手起源 / 天才俱乐部）。

### 二、任务剧情库建立（quest/）
- 新增任务剧情库 `quest/`，含索引.md / 主线任务.md（序章~第五章，6大星球主线+5幕间剧情概要）/ 同行任务.md（按角色分组，8大类角色同行任务列表与概要）。
- 新增 `quest/剧情文本/` 目录，按章节存放完整剧情对话文本。

### 三、序章剧情文本全量完成（6个）
- 从米游社 WIKI 经浏览器操作获取完整交互对话，生成 6 个序章剧情文本文件：
  - 序章_01_今天是昨天的明天.md
  - 序章_02_今天的你是昨天的我.md
  - 序章_03_那是在春天开始之前.md
  - 序章_04_只是个数字.md
  - 序章_05_我曾有过的美梦.md
  - 序章_06_昨日之花.md
- 每个文件含：任务描述 / 任务过程 / 完整交互对话 / 任务总结（关键信息 / 角色关系 / 伏笔）。

### 四、第一章剧情文本全量完成（24个）
- 从米游社 WIKI 经浏览器操作获取完整交互对话，生成 24 个第一章「雅利洛-VI」剧情文本文件：
  - 第一部分：12个（01~12）
  - 第二部分：7个（13~19）
  - 第三部分：5个（20~24）
- 覆盖完整主线：从抵达贝洛伯格到击败可可利亚，含所有分支对话、可选择调查对象、过场动画描述。

### 五、第二章剧情文本全量完成（14个）
- 从米游社 WIKI 经浏览器操作获取完整交互对话，生成 14 个第二章「仙舟罗浮」剧情文本文件：
  - 第一部分「乘槎驭风仙窟游」：11个（01~11）
  - 第二部分「云树百丈蔽重楼」：2个（12~13）
  - 第三部分「劫波渡尽战云收」：1个（14）
- 覆盖完整主线：从抵达仙舟到击败幻胧、建木重生，含丹恒视角任务、饮月君变身、镜流/罗刹/刃的真实目的揭示。
- 剧情文本总计：44个完整文件（序章6 + 第一章24 + 第二章14）。

### 六、规则库完善（rules/）
- 通用战斗逻辑 v0.2 补充速度·行动条 / 效果命中 / 能量恢复三章 + 防御常数 / 击破公式。
- 状态优先级 v0.2 补充控制分类表 / DoT叠层规则 / 回合流程判定A·B。
- 规则.md 索引同步 v0.2。

### 七、异常特例库完善
- 新增第5~9条特例（追加攻击机制 / 减抗下限-100% / 减防上限100% / 弱点植入银狼 / 超击破与击破特攻），完善第1~4条来源标注，共9条已知特例。

### 八、差分宇宙祝福补全
- SRR_ID 对照发现祝福覆盖率仅 805/1219（66%），缺失 414 个全部为差分宇宙祝颂（ID 段 634xxx/661xxx/668xxx/671-678xxx）。
- 从 StarRailRes-master 提取，跳过 1 个 name="0" 无效占位条目（634000），有效 413 实体按名称合并为 403 个文件（2 组同名合并：三月七 2ID、{NICKNAME} 10ID）。
- 字段标注「无（差分宇宙）」，主索引新增「差分宇宙祝颂（无星级，403）」分组。
- 覆盖率 805/1219 → 1218/1219（99.9%）；verify_fields 异常 0、verify_links 无新增死链。

### 九、README.md 多语言优化
- 主 README.md 优化多语言版本展示，避免主界面语言版本过多。
- 增加繁体中文、日文、韩文、英文版本。
- 按 RFC 4646 标准标注语言代码（zh-Hans / zh-Hant / ja / ko / en）。

### 十、其他优化
- 数据来源文档名称修改，按对应语言文字标注。
- py 文件整理，部分脚本优化。
- 模拟宇宙子文件夹按星级分文件夹优化。
- 子索引优化：只有一两个条目的索引直接分到上级索引。
- 角色行迹详细描述增加，含每个等级对应信息表（3.x和4.x角色注意）。
- 角色故事安排在最底下，{NICKNAME}占位符填充。
- 货币战争 6 项缺漏补全。
- C盘清理程序编写。

---

## 2026-08-28（周五）

### 一、模拟宇宙区域建立（simulated/）
- 新增模拟宇宙数据区域 `simulated/`，数据源为开源仓库 StarRailRes（github.com/Mar-7th/StarRailRes，v4.5，本地克隆于 StarRailRes_repo/）。
- 生成四个分类：祝福 907 个文件、奇物 84 个文件、事件 384 个文件、区块 15 个文件，均含详情 + 分类索引 + 主索引「模拟宇宙.md」。
- 祝福 / 奇物 / 事件存在大量同名实体（不同难度 / 版本 / 选项），已按规范合并为单一文件，正文聚合全部实体ID（如「分裂咕咕钟」12 个 ID）。

### 二、祝福命途回填（ID 段推断 + 米游社 WIKI）
- 发现祝福 ID 段命途规律：6120-6128（经典模拟宇宙）、6150-6158（黄金与机械）两套段位精确对应 9 大命途，已自动推断。
- 从米游社 WIKI 767（模拟宇宙·祝福一览）抓取经典模拟宇宙 216 条祝福的精确命途（含「存护&虚无」等双命途交错），浏览器操作获取。
- 命途覆盖：418 / 907 个祝福。

### 三、祝福星级回填（米游社 WIKI 7483 / 4993）
- 从米游社 WIKI 7483（差分宇宙·乐园漫记）与 4993（差分宇宙·千面英雄）抓取祝福星级。
- 两版本祝福完全重合（144 条：三星 24 / 二星 56 / 一星 64），含新命途「同谐」。
- 星级覆盖：144 / 907 个祝福；祝福索引新增「按星级」分组。

### 四、事件文本回填（米游社 WIKI 7483 / 4993）
- 从米游社 WIKI 7483（122 事件）与 4993（117 事件）抓取差分宇宙事件简表，含「选项 → 结果」完整文本。
- 事件文本覆盖：126 / 384 个事件，详情页新增「事件文本」选项表格。
- 事件图片共用情况已在详情标注（59 组共用图，491 条事件复用）。

### 五、数据来源与规范同步
- 「数据来源」文档新增 StarRailRes（模拟宇宙数据源）与米游社 WIKI 767 / 7483 / 4993 三条来源登记。
- 「格式规范与要求」同步模拟宇宙目录结构与字段规范（祝福 / 奇物 / 事件 / 区块）。

### 六、GitHub 保存
- 模拟宇宙区域及配套脚本 / 数据提交并推送至 GitHub（ganmayou2333/HSR，master）。
- 第三方图库克隆 StarRailRes_repo/ 加入 .gitignore 排除（体积大、含版权素材，不入库）。
- 待补充：经典模拟宇宙（612x / 615x 段）祝福星级与经典事件文本，米游社 WIKI 无结构化数据源，需逐篇攻略提取。

### 七、格式规范纳入模拟宇宙（v1.7）
- 「格式规范与要求」升级至 v1.7：
  - 目录结构规范目录树加入 `simulated/`（模拟宇宙库：祝福 / 奇物 / 事件 / 区块，祝福含四级评级索引）。
  - 新增「八、模拟宇宙文件内容结构」章节（通用结构模板、数据源为 StarRailRes JSON、同名合并、事件文本、待补充字段规则）。
  - 后续章节重编号：八 → 九（双链规范）、九 → 十（数据维护）、十 → 十一（扩展规划）、十一 → 十二（行动前要求）、十二 → 十三（物品说明）、十三 → 十四（光锥说明）、十四 → 十五（遗器说明）。
- 「待办清单」新增「〇、模拟宇宙区域待办」与「四、规范扩展规划」「五、收尾约定」章节。

### 八、祝福评级索引建立
- 按规范生成 3 个独立评级索引文件：`simulated/祝福/祝福_三星.md`（24 条）、`祝福_二星.md`（56 条）、`祝福_一星.md`（64 条），格式同角色评级索引（所属 / 评级 / 数量 / 返回分类索引 / ★级链接列表）。
- `祝福.md` 的「按星级」分组改为链接三个评级索引；「待补充（763）」列表完整保留（修复一次误删后从 git 恢复重做）。
- 评级索引链接有效性校验：0 失效。

### 九、模拟宇宙索引结构核查
- 奇物 / 事件 / 区块 三个分类索引均含「返回主索引」链接，三级结构合规（主索引 → 分类索引 → 详情）。
- 事件文本覆盖率复核：385 个事件详情文件中 364 个非空（其中 165 个含「选项 → 结果」表格），21 个待补充；口径较此前 126 更精确。
- 待办清单数据同步更新。

### 十、全库双链校验
- 编写 `verify_links.py` 双链校验脚本（处理表格内 `\|` 转义与文件名含 `#` 的 Obsidian 锚点歧义）。
- 扫描 3279 个 md 文件、9959 条 wikilink：**知识库真实死链 0**。
- 残留 15 条均为占位示例（格式规范 / SRR 图包来源的 `[[xxx]]` 演示）或 StarRailRes_data 工作文档中的数值误识别，非知识库内容。

### 十一、奇物星级全量回填
- 从米游社 WIKI 7483（乐园漫记）、4993（千面英雄）差分宇宙页面经浏览器模拟点击提取奇物星级分组（3星 / 2星 / 1星）。
- 回填 72 个奇物星级（三星 5 / 二星 23 / 一星 44），其中 4 个（万识囊、塔拉毒火焰、粉红冲撞、虫网）由游戏8差分宇宙图鉴补充确认。
- 经典模拟宇宙独有奇物 12 个（存护/丰饶火漆、中规中矩/乱七八糟代码、混沌云芝/特效灵药、黑洞之阱、无效文字打印机、《鸡窝头侦探》等）确认**无星级机制**（星级为差分宇宙引入概念，816 经典奇物一览无星级列），文件标注「无（经典模拟宇宙）」。
- 奇物索引 `simulated/奇物/奇物.md` 重建为按星级分组（三星 / 二星 / 一星 / 无星级），84 条 0 失效链接。
- 模拟宇宙.md 主索引同步更新奇物星级说明。
- 待办清单「奇物星级」勾选完成。

---

## 2026-08-27（周四）

### 一、目录结构整理（14:20）
- 角色文件按命途拆分到子文件夹，共 8 类：丰饶、同谐、存护、巡猎、智识、毁灭、虚无。
- 角色文件名规范由「角色名_命途_属性_星级」调整为「角色名_属性_星级」，命途由文件夹层级体现，避免冗余。
- 全库双链校验通过，物品与光锥引用保持有效。

### 二、光锥资料全量补全（14:25）
- 完成全部光锥收录，共 169 个文件（五星 71 个、四星 73 个、三星 25 个）。
- 四星与三星光锥从索引文件升级为完整文件，补齐以下字段：
  - 基本信息（名称、命途、评级）
  - 背景故事
  - 基础属性（Lv.80 生命 / 攻击 / 防御）
  - 叠影效果（技能名 + 效果说明）
  - 晋阶材料（等级、信用点、材料数量）
- 修复此前因页面渲染问题反复获取失败的光锥条目（共 3 个）。

### 三、角色资料（14:30）
- 全部四星角色整理完成，四星与五星角色合计 28 个。
- 角色文件包含：基本信息、配音演员、基础属性、晋阶材料、技能材料、战技、附加能力、总属性加成、星魂、推荐遗器。
- 推荐配装部分仅保留推荐遗器（主词条、副词条、4 件套、2 件套），不含光锥推荐。
- 文件内已建立与对应物品资料的关联。

### 四、物品资料（14:35）
- 按页面 item 标签全量收录物品，共 1429 个文件。
- 按用途与来源分类存放，分类包括：宝箱、怪物掉落、光锥经验材料、合成素材、角色晋阶材料、角色经验材料、礼物、配方、任务道具、世界货币、通用货币、素材、消耗品、行迹材料、行迹材料_光锥晋阶材料、行迹材料_角色晋阶材料、行迹素材、遗器经验材料、阅读物等。

### 五、规范性文件（14:40）
- 根目录创建「格式规范与要求」，固化文件命名、目录结构与格式要求。
- 根目录维护「光锥总索引」「物品总索引」两个索引文件，便于检索。

### 六、目录归档与索引重构（14:50）
- 角色按命途归档：28 个角色拆入 character/ 下 7 个命途子文件夹，文件名改为「角色名_属性_星级」，命途由文件夹体现。
- 光锥按命途归档：169 个光锥拆入 lightcone/ 下 9 个命途子文件夹。
- 光锥索引改为三级结构：
  - 主索引 `lightcone/光锥.md`（由根目录「光锥总索引」改名迁入）索引各命途；
  - 各命途索引 `lightcone/<命途>/<命途>.md`（9 个）索引该命途下全部光锥；
  - 具体光锥详情 `lightcone/<命途>/<光锥名>.md`。
- 四星/三星光锥已从索引升级为完整文件，与五星同规格。
- 全库双链校验通过（2010 条，仅格式规范示例 1 条误报）。

### 七、角色与物品索引同步（14:55）
- 角色建立三级索引：主索引 `character/角色.md` + 7 个命途索引 `character/<命途>/<命途>.md`，索引全部 28 个角色。
- 物品建立三级索引：主索引 `items/物品.md`（由根目录「物品总索引」改名迁入）+ 19 个分类索引 `items/<分类>/<分类>.md`，索引全部 1428 个物品文件。
- 角色/光锥/物品三大库统一采用「主索引 → 二级索引 → 详情」三级结构，各二级索引含返回主索引链接。
- 全库双链校验通过（2090 条，仅格式规范示例 1 条误报）。

### 八、四级评级索引（15:10）
- 在角色/光锥/物品三大库的二级索引（命途/分类索引）下新增评级索引层，形成四级结构：主索引 → 命途/分类索引 → 评级索引 → 详情。
- 评级索引文件按星级命名（五星.md、四星.md、三星.md…），二级索引改为链接各评级索引。
- 共生成评级索引：角色 12 个、光锥 27 个、物品 51 个（合计 90 个）。
- 全库双链校验通过（2253 条，仅格式规范示例 1 条误报）。

### 九、角色资料全量补全（五星）（15:20）
- 通过角色列表页数据补齐此前缺失的全部 64 名五星角色，角色库由 28 个扩充至 92 个。
- 补全范围包含：各版本五星角色、联动角色（Saber、Archer、远坂凛、吉尔伽美什 等）、开拓者其余形态（存护火、同谐虚数、记忆冰、欢愉雷）、以及记忆与欢愉命途角色。
- 新增命途子文件夹「记忆」（7 个）与「欢愉」（6 个），命途目录由 7 类扩展至 9 类。
- 新增角色文件与既有角色同规格：基本信息、配音演员、基础属性（Lv.80）、晋阶材料、技能材料、战技、附加能力、总属性加成、星魂、推荐遗器（仅遗器，不含光锥推荐）。
- 技能材料数据修正：依据各角色技能树（skill_trees）数据确定材料种类（光锥晋阶材料、角色晋阶材料、周本 Boss 材料、命运的足迹），与页面渲染数量对应生成，并建立物品双链。
- 索引同步更新：角色主索引、9 个命途索引、五星 / 四星评级索引全部重建。
- 全库双链校验通过：新增 64 个角色文件共 896 条物品引用，0 断链。

### 十、旧角色材料数据修正（15:35）
- 对既有 28 个角色文件的晋阶材料与技能材料进行重算修正，材料种类改为依据各角色技能树数据（skill_trees）确定，取代此前的命途 / 属性经验映射。
- 修正内容示例：
  - 佩拉（冰·虚无）行迹角色材料由「古代零件 / 古代转轴 / 古代引擎」修正为「熄灭原核 / 微光原核 / 蠢动原核」；
  - 周本 Boss 材料按各角色实际数据归位（如佩拉修正为「守护者的悲愿」）。
- 全部 92 个角色文件链接格式统一为「单竖线」引用，移除历史遗留的转义反斜杠。
- 声优等其余字段保持原有手动数据，未受影响。
- 全库双链校验通过（3236 条，仅格式规范示例 1 条误报）；92 个角色文件材料区块完整性校验 0 问题。

### 十一、Obsidian 表格管道符转义修复（15:45）
- 修复 Obsidian 表格内 wikilink 的管道符未转义导致的表格串行（多格子）问题。
- 背景：Obsidian 中表格内的双链管道符必须转义为竖线前加反斜杠，否则会被误判为表格列分隔符，导致材料表列错位。
- 对全库 92 个角色文件的晋阶材料、技能材料、推荐队伍等所有表格内 wikilink 统一转义处理。
- items 与 lightcone 库经扫描无同类问题，未改动。
- 风堇文件试跑官方百科合并样例，验证转义规则后并入。

### 十二、官方 Wiki 角色百科全量合并（方案B）（16:50）
- 从米游社官方 Wiki 抓取 93 个角色的官方百科数据，按方案 B 并入现有 character 角色库。
- 增量内容：数据来源（官方Wiki）、阵营/城邦/神权/定位、总属性加成补充、推荐光锥、推荐队伍。
- 抓取节奏：每 2 个请求间隔 10 秒，后按用户要求调整为随机 5-10 秒、三线并行（多标签页）抓取。
- 92 个已有角色文件合并完成；真珠（4.6 前瞻角色，欢愉·冰·五星）为官方 Wiki 新收录，新建基础文件并加入欢愉命途索引与五星评级索引。
- 砂金·戏浪、真珠等新角色官方词条数据不全（仅阵营/定位/角色故事/配音），其余字段待正式版本上线后补充。
- 修复全库 37 个角色文件「总属性加成」表格重复行（官方补充与原有字段名差异导致），保留原有行。
- 全库校验：总属性加成无重复、表格内 wikilink 转义正确（0 未转义）、推荐队伍/推荐遗器表格列数正常。

### 十三、空评级索引清理（17:10）
- 按用户要求：索引所在目录下只有一个评级有数据时，只保留有数据的评级索引。
- 删除 11 个空评级索引：全部命途的空「三星」索引（9 个，游戏无三星角色）+ 欢愉 / 记忆 的空「四星」索引（2 个）。
- 欢愉、记忆 仅保留「五星」索引；其余命途保留「五星 + 四星」索引。
- 删除前确认 0 个文件引用这些空索引，无悬空链接；全库双链校验通过（4702 条）。

### 十四、遗器库建立（17:50）
- 按用户要求将遗器加入资料库，隧洞遗器与位面饰品分开存放。
- 从 hsr.nanoka.cc/relic 抓取全部 62 个遗器：隧洞遗器 34 个（实体 ID 101-134）、位面饰品 28 个（实体 ID 301-328）。
- 建立 relic/ 目录：主索引 遗器.md + 隧洞遗器/ 与 位面饰品/ 两个子目录，各含类型索引与 62 个遗器详情文件。
- 每个遗器文件包含：数据来源、基本信息（名称/类型/实体ID）、套装效果（2 件套 / 4 件套）、部位（隧洞 4 部位 / 位面 2 部位）。
- 抓取方式按用户要求采用网页模拟点击，随机 8-12 秒间隔控制请求频率。
- 遗器规则.md 的遗器双链更新指向 relic/遗器.md（含隧洞 / 位面两个类型索引）。
- 为 92 个角色文件「推荐遗器」章节的遗器套装名添加 relic 库双链（4 件套/2 件套表格，表格内管道符转义），共新增 548 条。
- 全库双链校验通过（5318 条，0 死链）。

### 十五、子索引文件改名（18:16）
- 按用户要求将评级子索引文件统一改名为「文件夹名_星级.md」。
- 全库 94 个评级索引重命名：角色 17 个、光锥 27 个、物品 51 个。
- 示例：character/丰饶/五星.md → character/丰饶/丰饶_五星.md；items/通用货币/三星.md → items/通用货币/通用货币_三星.md。
- 同步更新全库 94 处指向这些索引的 wikilink 引用，显示名保持不变。
- 全库双链校验通过（5318 条，0 死链）。

### 十六、格式规范更新与数据来源文档（18:24）
- 「格式规范与要求」更新至 v1.6：
  - 目录结构规范加入 relic/ 遗器库（主索引 + 隧洞遗器/位面饰品 类型索引 + 详情）。
  - 四级评级索引命名规范改为「文件夹名_星级.md」（如 丰饶_五星.md）。
  - 新增空评级索引规则（仅一个评级有数据时只保留有数据的索引）。
  - 新增「遗器文件内容结构」章节与「遗器全量收录说明」。
  - 双链规范补充遗器双链示例；章节编号整体重排（一~十四）。
- 新建根目录「数据来源」文档：汇总 hsr.nanoka.cc、米游社官方 Wiki、官网三个数据来源的用途 / 覆盖 / 抓取方式 / 版权声明。

### 十七、与官方 Wiki 数据校验（18:30）
- 校验对象：角色 / 光锥 / 遗器（数据源：米游社官方 Wiki 图鉴 channel/map/17/18、channel/map/17/30）。
- **角色**：本地 93 个与官方完全一致，无缺失。官方角色区 98 个，多出的 5 个为开拓者男女形态分开词条（欢愉 7047/7046、记忆、同谐、存护、毁灭），本地已合并为单文件，属合理差异。
- **光锥**：本地 169 个覆盖官方全部 168 个，无缺失。官方图鉴未列出「向浪花掷下盛夏」（4.5 新欢愉五星，id 23064），官方 Wiki 更新滞后，本地更全。
- **遗器**：本地 62 个覆盖官方全部 60 个，无缺失。官方图鉴未收录最新 2 个 4.5 隧洞遗器「戏梦点星的伶人」（133）、「贪噬禁果的异端」（134），本地更全。
- **套装效果抽查**：「坠星启航地」官方图鉴文本与本地位面饰品文件完全一致。
- 结论：本地库数据完整，无缺失；官方 Wiki 图鉴在 4.5 最新内容上有更新滞后（缺 1 光锥 + 2 遗器）。

### 十八、遗器补充官方来历与获取途径（18:52）
- 从官方 Wiki 抓取 60 个遗器词条（content cid），补充各部位「描述 + 来历（背景故事）」与「获取途径」至本地遗器文件。
- 60 个遗器文件按新结构重建：头部元信息追加「官方Wiki」来源，新增「获取途径」章节，部位展开为「部位标签：名称 + 描述 + 来历」。
- 部位标签：隧洞遗器（头部/手部/躯干/脚部）、位面饰品（位面球/连结绳）。
- 2 个官方 Wiki 未收录的 4.5 新遗器（贪噬禁果的异端、戏梦点星的伶人）标注「官方Wiki暂无词条」。
- 抓取方式：官方 Wiki 逐词条访问，随机 6-9 秒间隔，共 7 批。
- 「格式规范与要求」遗器文件结构章节同步更新（新增获取途径、部位描述/来历规范）。
- 全库双链校验通过（5320 条，0 死链）。
### 十九、全库内容检查与污染清理（19:08）
- 执行全库无关文本扫描，清除官方 Wiki 抓取混入的页脚与页面导航文本。
- **遗器文件**：60 个遗器文件「来历」末尾混入的官方 Wiki 页脚（词条贡献者、编辑团队、欢迎语、全部评论等）已全部截断清理；62 个遗器文件结构检查通过（基本信息/获取途径/套装效果/部位/描述/来历，无重复章节、无数量异常）。
- **角色文件**：6 个角色文件（丹恒•腾荒、爻光、开拓者、椒丘、昔涟、长夜月）的「推荐队伍」被官方页面文本污染为畸形表格，已整段重建为「官方 Wiki 配队推荐角色列表」（角色去重、带本地双链）；「推荐光锥」章节按字段级重建，清除末尾渗入的配队/导航文本。
  - 修复细节：椒丘「推荐光锥」开头的空标题块与错误技能/效果行已删除；丹恒•腾荒第 4 块「任意高攻光锥」改为准确光锥链接（比阳光更明亮的），并修正推荐度星级。
  - 其余 87 个角色文件复查无污染。
- 全库无关词复扫：仅剩合法内容（光锥名「欢迎来到银河城」、背景故事台词等），无污染残留。
- 全库双链校验通过（5089 条，0 死链；1 条为格式规范文档中的占位示例）。


### 二十、物品文件夹（items）数据质量修复（19:19）
- 全库扫描 items（1500 个 md），发现并修复以下问题（修复前已整体备份至 .tmp_build/items_backup_20260827）：
- **文件名规范化**：96 个物品文件名被误加「 行迹材料」后缀。
  - 其中 51 个为重复冗余文件（与「行迹材料_角色晋阶材料」「行迹材料_光锥晋阶材料」目录中的同名文件实体 ID 完全一致），已删除；
  - 其余 44 个（怪物掉落 13、行迹素材 31）重命名去掉后缀（如「勇气撕裂胸膛 行迹材料」→「勇气撕裂胸膛」）。
- **引用同步更新**：43 个文件共 368 处 wikilink 同步更新；怪物掉落_一星 / 行迹素材_一星 索引重建（仅含本目录物品、显示名去后缀）；怪物掉落.md / 行迹素材.md / 物品.md 总索引数量标注更新（怪物掉落 34→13，行迹素材 61→31，物品合计 1428→1377）。
- **空文件清理**：删除 0 字节空文件「items/任务道具/{TEXTJOIN.md」（{TEXTJOIN#61} 的残留）。
- 全库双链校验通过（5038 条，0 死链；1 条为格式规范文档占位示例）。
- **待办（需从数据源抓取，量大且有 IP 风险，待用户确认）**：约 1202 个详情文件缺「说明」、1310 个缺「获得途径」；约 1199 个详情文件「类型」字段误标为「索引」（正确应为「Material / 具体类型」）。


### 二十一、模拟宇宙·差分宇宙归档（simulated/差分宇宙）
- 新建 `simulated/差分宇宙/` 版本归档结构：人间喜剧（方程 56）/ 千面英雄（金血祝颂 85 + 方程 104 + 加权奇物）/ 乐园漫记（面具 + 惊世奇迹 + 方程 72）/ 角色专属（87）。
- **迁移**：从 `simulated/祝福/` 迁出 404 个非祝福数据 —— 63xx 金血祝颂（85，米游社 4993 金血祝颂表确认）→ 千面英雄/金血祝颂；66xx 角色专属（87）→ 角色专属；67xx 方程（人间喜剧 56 / 千面英雄 104 / 乐园漫记 72，分别由米游社 3164 / 4993 / 7483 方程表确认）→ 各版本方程目录。
- **分类字段修正**：404 个迁移文件「特殊类型」改为 金血祝颂 / 角色专属 / 方程，「命途」标注「无（按所属角色 / 按角色 / 按达成条件）」；方程补「达成条件」字段（如 一首美丽的诗＝6记忆+4繁育、不沉巨舰＝存护*3毁灭*2）。
- **临界方程命途回填**：61xx 16 个临界方程祝福（神迹系列 + 可爱黑洞 / 睡前故事 / 最后的子弹 / 无限非概率 / 幻造物 / 参考文献 / 极乐舞会 / 界外天魔主）命途由效果文本「命途『XX』产生临界回响」回填（记忆 / 虚无 / 巡猎 / 毁灭 / 欢愉 / 繁育 / 智识 / 同谐）。
- **索引重建**：祝福.md（按星级分组，待补充 359）+ 祝福_三星（24）/ 祝福_二星（56）/ 祝福_一星（64）重建；新建 差分宇宙.md 主索引 + 各版本/分类索引；模拟宇宙.md 分类与说明更新。
- **现状**：祝福/ 剩余 503 实体（命途待补充 69 ＝ 61xx【高光时刻】/未命名 2 + 67xx 新赛季机制祝福 67，7483 / 4993 / 3164 均未收录）；67xx 67 个新机制祝福（【蛀洞】【逆会心】【发牌员】等）暂留祝福/ 待最新版本数据源。
- 全库双链校验通过（simulated/ 区域 1410 文件，0 死链）。


---

### 二十二、模拟宇宙·差分宇宙空分类填充（面具 / 惊世奇迹 / 加权奇物）
- 从米游社 WIKI 7483（差分宇宙·乐园漫记）提取并生成三个空分类数据：
  - **面具**（9 个，乐园漫记 4.1 机制）：斗士 / 镜头 / 机铠 / 马之 / 财猫 / 囧之 / 敷衍 / 战车 /「两张」面具，含 面具简介 / 愿力获取 / 面具效果 / 背景故事。
  - **惊世奇迹**（149 个，乐园漫记 4.1 机制）：局部战争 / 失去日 / 三人成行 等，含 效果 / 适用面具。
  - **加权奇物**（196 个，差分宇宙通用机制）：故事的现在时 / 给你鼓励 / 自动化体验 等，含 奇物效果 / 奇物故事。
- 索引更新：乐园漫记 / 千面英雄 版本索引与分类索引重建；差分宇宙总数 404 → 758（人间喜剧 56 / 千面英雄 385 / 乐园漫记 230 / 角色专属 87）。
- 全库双链校验通过（simulated/ 区域 1764 文件，0 死链）。



---

### 二十三、模拟宇宙·货币战争（simulated/货币战争）
- 新建 `simulated/货币战争/` 知识库：货币战争.md（主索引）/ 玩法机制.md / 角色图鉴.md / 羁绊图鉴.md / 赛季更新.md，共 5 个文件。
- **玩法机制**：米游社 WIKI 6564 玩法说明 —— 对局流程 / 站位（前台/后台）/ 角色赋能 / 羁绊 / 星级 / 角色招募 / 金币·等级·商店 / 装备（简易→进阶）/ 投资环境与投资策略 / 优势布局 / 标准博弈·超频博弈 / 奖励说明。
- **角色图鉴**：按 1-5 费分组汇总（费用 / 属性 / 站位 / 羁绊 / 赋能要点），含 V4.0（大丽花·爻光·火花）、V4.2（不死途·银狼LV.999·绯英·开拓者欢愉）、V4.4（千冶•刃·姬子•启行·远坂凛·吉尔伽美什）新增角色与 3.7 基础角色。
- **羁绊图鉴**：阵营羁绊 22 种（仙舟 / 狼狩 / 追击 / 燃血 / 战技点 / 银河学者 / 星核猎手 / 夜之半神 / 贝洛伯格 / 星间旅人 / 击破 / 持续伤害 / 能量 / 减益 / 公司 / 量子同频 / 群攻 / 巡海游侠 / 列车同行 等）+ 流派羁绊（欢愉 V4.2 / 命运圣杯 V4.4）+ 独立羁绊（领航员 / 头号玩家）+ 专家顾问列表。
- **赛季更新**：零和博弈（3.7）→ V4.0 / V4.2 / V4.4 三次扩充记录（新增角色 / 新增羁绊 / 职级与晋升等级 / 竞争对手阵营 / 装备战利品 / 投资环境策略数量）。
- 模拟宇宙.md 分类新增「货币战争（5）」并更新数据来源说明。
- 数据来源：米游社 WIKI 6564 + 官方赛季扩充说明 V4.0（news/162649）/ V4.2（news/163610）/ V4.4（news/165186）+ 游侠/九游攻略。

### 二十三补、货币战争补全（V3.8 调整 + 装备图鉴）
- 从官方「货币战争•零和博弈」调整说明 V3.8（2025/12/17，miyoushe 71454150）补全：角色图鉴新增 V3.8 角色调整要点（貊泽/飞霄/灵砂/托帕&账账/黑塔/翡翠/银枝/那刻夏/景元/丹恒•饮月/Archer/乱破/波提欧/彦卿/流萤等）；羁绊图鉴新增 V3.8 羁绊调整（狼狩/追击/银河学者/群攻/战技点/减益/击破/巡海游侠/星核猎手/燃血）；赛季更新新增 V3.8 记录。
- 新建 `simulated/货币战争/装备图鉴.md`：装备体系（简易→进阶合成规则）、已知基础/进阶装备（轮滑鞋/光能电池/幸运星/垃圾袋/电光履/火力风暴潮/永动机/光能盾牌等）、星徽列表（治疗/护盾/量子同频/列车同行/欢愉/命运圣杯/追击/持续伤害/银河学者），来源含攻略「一篇看懂货币战争所有装备，合成配方大全」（70299740）。
- 货币战争知识库 5 → 6 文件；模拟宇宙.md 计数同步；主索引目录新增装备图鉴。
- 双链校验通过（simulated/ 1770 文件，0 死链）。
- 待办：装备完整合成配方为图片（装备合成一图流 70300443），仅文字部分可提取；3.7 基础角色费用/站位仍待游戏内图鉴补充。

### 二十四、货币战争目录迁移（独立玩法重构）
- 用户纠正：货币战争为**独立玩法**，不属于模拟宇宙。将 `simulated/货币战争/` 整体迁移至仓库顶层 `货币战争/`（git mv，保留历史）。
- **链接修正**：货币战争 6 个文件内部链接前缀 `[[zh_cn/simulated/货币战争/` → `[[货币战争/`；货币战争.md 移除「返回 [[simulated/模拟宇宙|模拟宇宙主索引]]」与「模拟宇宙系列自走棋玩法」描述，改为独立常驻自走棋玩法。
- **模拟宇宙.md**：分类移除「货币战争」条目；说明中移除货币战争数据来源描述。
- **待办清单.md**：货币战争待办从「〇、模拟宇宙区域待办」移出，改为独立小节「〇•货币战争知识库待办（独立玩法，非模拟宇宙子玩法）」，并补充迁移完成项。
- **README.md**：结构表新增 `货币战争/`（6）；`simulated/` 规模更新为 1764。
- 校验：simulated/ 1764 文件 0 死链；货币战争/ 6 文件 0 死链。

### 二十五、遗器官方源核对——尾部重复文本清理（待办三）
- 扫描发现 62 个遗器详情文件中有 60 个在「## 部位」结构化章节后残留官方 Wiki 抓取产生的整段重复裸文本（遗器名 + 部位名 + 来历重复出现）。
- 对待办三清单的 59 个遗器 + 1 个清单外新增遗器（恶海逐波的船长，同源问题）共 60 个文件执行清理，删除重复文本合计约 3429 行。
- 清理逻辑：以「## 部位」后首个「遗器名裸行」（或部位名裸行，含向前回溯 1 行的遗器名变体，如「无主的荒星茨冈尼亚」「筑城者的贝罗伯格」）为起点，截断至尾部 `---`，保留结构化部位块与文件生成时间。
- 处理前整体备份至 `.tmp_build/relic_backup_20260828/`（60 个文件）。
- 验证：62 个遗器详情文件全部通过（无重复段落、结构完整）；全库双链校验 6835 条，0 真实死链（仅格式规范文档示例 1 条误报）。
- 备注：「戏梦点星的伶人」「贪噬禁果的异端」为官方 Wiki 未收录的 4.5 新遗器，无重复问题，未改动。

### 二十六、待办清单数据库复核更新
- 全面扫描 vault 实际状态，修正待办清单中过时 / 口径错误的记录：
  - **物品补全（一）**：实际缺字段详情文件 947 个（途径 946 / 说明 5 / 类型 3），修正原「1259 项 / 途径 1017 / 说明 76 / 类型 71」记录。修正点：此前将 51 个「分类_X星」评级索引误计为缺字段详情。明细按当前实际重建：任务道具 574 / 阅读物 261 / 配方 95 / 礼物 14 / 素材 2 / 宝箱 1。
  - **角色（二）**：配音演员为空 44 个（待办二 90 项中 42 个 + 清单外 2 个：知更鸟•晴歌、风堇），已在清单标注。
  - **事件文本**：384 事件中已回填 126（含「选项 → 结果」表格）、待补充 258，修正原「21 待补充」口径误差（明细存 temp/event_todo_list.txt）。
  - **祝福星级 / 命途**：复核确认仍为星级缺 359、命途缺 69（与清单一致）。
  - **空评级索引**：三星 24 / 二星 56 / 一星 64 均有数据，无空索引，已勾选完成。
  - **校验脚本**：标注双链校验已落地（verify_links.py，0 死链），字段级校验待落地。
- 复核过程使用的统计脚本存于 temp/（scan_todo_status.py、recheck*.py、final_items_check.py 等）。

### 二十七、物品补全——获得途径 / 说明 / 类型（待办一）
- **类型补全（3/3）**：《星间启航》绘本、监控影像 → Mission / 任务道具；生物波勘探仪 → Usable / 消耗品。
- **获得途径补全（618/946）**：
  - **米游社 WIKI 官方增量（592）**：发现免登录静态接口 `act-api-takumi-static.mihoyo.com/common/blackboard/sr_wiki/v1/content/info?app_sn=sr_wiki&content_id={cid}`，批量抓取 732 个缺途径物品详情（0 错误），592 个含官方「来源」字段。覆盖：任务道具 485 / 配方 93 / 礼物 10 / 阅读物 3 / 素材 1。
  - **BWIKI 补漏（26）**：`wiki.biligame.com/sr/api.php?action=ask` 抓取 7 分类 1581 条，本地匹配后独有可补 26 个（任务道具 24 / 配方 2），已清洗 `[[链接]]`。
  - 按既有格式写入 `## 获得途径` + 无序列表；格式校验 0 异常，未误写任何索引文件。
- **说明补全（5/5）**：万敌获得了徽记 / 任务道具 ★ / 冥灯开路指引 / 觅宝券 / 世界货币 ★★★ 5 个文件补「## 说明」章节，标注「暂无官方描述数据（数据源未收录）」。
- **剩余无源（328）**：阅读物 258 / 任务道具 65 / 礼物 4 / 素材 1 —— 在米游社 WIKI（140 个 content 词条为空壳）、BWIKI（书籍 627 条无途径）、hsr.nanoka.cc、StarRailRes 四大数据源均无「获得途径」记录，保持缺字段待后续版本数据源。
- **数据源探索记录**：hsr.nanoka.cc 主源（英文库 item_comefrom 为空）与米游社旧黑板 API（需签名）为死路；BWIKI 书籍分类无途径字段；米游社 WIKI 分类图鉴（channel/map/17/{catId}）+ content 静态接口为主要增量来源。
- 中间数据与脚本存于 temp/（write_plan.json、mihoyo_detail.json、bwiki_items_all.json 等）。

### 二十八、阅读物获得途径补充——米游社 proceed + 攻略源（待办一·续）
- **米游社 WIKI 阅读物「获得方式」字段（138）**：阅读物词条 material 采用 `partKey=read`，其 `proceed` 字段即官方「获得方式」（此前仅解析 partKey=main 遗漏）。补齐缺途径阅读物 136 + 任务道具 2 的官方途径（如《地底百科：动物》→ 雅利洛-VI-行政区与莉拉对话获得）。
- **17173 黑塔阅读物攻略（14）**：解析「阅读物：X / 位置：Y」+ 舱段分组，补齐科员们的留言便条 6、黑塔的手稿 4、黑塔情诗 3、黑塔研究图鉴 1（如科员们的留言便条其一 → 空间站「黑塔」-主控舱段，地图右上方长方形桌子上）。
- **雅利洛/仙舟攻略确认（17）**：《贝洛伯格的音乐家》卷一~六+真结局（磐岩镇-娜塔莎诊所内）、帕斯卡的日志（世界任务「难得有情·其二」）、贝洛伯格大事年表·寒潮之前（「当生意来敲门」）、旅行篇/工作篇/天舶司金刚椟/形虎拳馆/将军的日记其三（仙舟罗浮）等。
- **药王秘传/旧报纸批（10）**：千手慈怀药王救世品、药方·龙蟠虬跃、药王秘传·证物集册（仙舟罗浮主线获得）；冰原狼出没、大守护者塔提维娜、兄弟对簿公堂（边缘通路旧报纸）；梅登矿道要塌了、矿工每周报 158/192 期、写给闯入者的便条。
- **本轮合计新增 169 个获得途径**（全库有途径 1049 → 1218）。
- **剩余 149 个无数据源**：任务道具 63（剧情/任务专属）、星神/派系图鉴类 42（「丰饶」药师等游戏内图鉴解锁，无逐条途径）、其他阅读物 39（教育部难题、科员档案、数据记录、梁沐系列等，文本攻略未收录明确位置）、礼物 4、素材 1。明细存 temp/remaining_final.json。
- **数据源**：米游社 content/info 静态接口 proceed 字段、17173 黑塔阅读物全收集、九游/3DM 仙舟书籍收集、米游社雅利洛书籍索引与 1.0 全收集、米游社「书籍收集」合集 26 篇版本攻略（post API 离线抓取）。

---

### 二十九、角色配音演员全量回填（待办二）
- 复核全库 93 个详情角色配音状态：原 65 个角色配音为占位（21 个老角色 `…` + 44 个 3.x/4.x 新角色 `-`），此前待办清单仅记录 44 个（漏计 21 个老角色占位）。
- **数据源**：BWIKI 星铁 wiki（wiki.biligame.com/sr）MediaWiki API `action=parse&prop=wikitext`，角色图鉴模板含 `中文CV/日文CV/韩文CV/英文CV` 字段；65/65 命中。
- **回填 66 个角色**：65 个占位角色四语 CV + 真珠（4.6 前瞻，补全四语）。例：花火 中文赵爽/日文上田麗奈/韩文성예원/英文Lizzie Freeman；银枝 英文 Talon Warburton（已清理 `{{#info:}}` 模板注释）。
- **开拓者处理**：同谐/存护/欢愉/记忆 4 形态按 BWIKI「开拓者•XX」页填男女双组（穹/星，中文秦且歌/陈婷婷、日文榎木淳弥/石川由依等）；毁灭开拓者顺带修正英文（Shaun Mendum → Caleb Yen/Rachael Chau）并补女组。
- **仙舟三月七**：BWIKI「三月七」页 NO-CV，改用「三月七•巡猎」页（中文诺亚/日文小倉唯/韩文정혜원/英文Skyler Davenport）。
- **Fate 联动**：Saber/Archer/远坂凛/吉尔伽美什 英文配音官方暂无，标注「暂无」。
- 回填后全库校验：93 个详情角色配音 0 占位；修改前已整体备份至 temp/voice_backup_20260828/。
- 待办清单二标记完成。

---

### 三十、模拟宇宙数据补全（祝福星级/命途 + 事件文本 + 评级索引）
- **数据源**：BWIKI 星铁 wiki（wiki.biligame.com/sr）MediaWiki API（`action=query&prop=revisions&rvprop=content&rvslots=main` 多页面批量，每批 ≤45，间隔 1.5s，Edge UA + Referer 规避 567 限流）。
- **祝福星级 356/359**：612x/615x 经典段 + 67xx 新机制祝福，从祝福词条 `稀有度` 字段回填（1星→一星等）。剩 3 个 BWIKI 无词条：【高光时刻】/未命名/密室收藏家。
- **祝福命途 65/69**：67xx 新赛季机制祝福用「差分宇宙方程」模板 `命途1/命途2` 字段（双命途以 `&` 连接，如 欢愉&记忆）；回响交错 3 个（重叠象眼/附着菌毯=繁育、肃肃置罗=巡猎）。剩 4 个：高光时刻/未命名/密室收藏家 + 混沌医师（BWIKI 无命途字段）。
- **页面名映射**：BWIKI 用 `•` 无空格（《冠军晚餐•猫的摇篮》等 25 个）、「罝→置」、派系类「（方程）」页；特殊字符事件（判定无机/认知拓宽/完美大挑战）用 `*斜体*` 写法。
- **事件文本 194/258**：解析「模拟宇宙事件」（85）+「模拟宇宙剧情」（105）模板，还原开场剧情 +「选项→结果」表格 + 各选项剧情 + 结尾，说话人标注（宇宙·起源宇宙：…）；虚构史学家合并其一/其二；4 个特殊字符事件单行 `{{剧情选项}}` 已处理。格式遵循规范「选项→结果」表格。
- **评级索引重建**：三星 150 / 二星 158 / 一星 167，新建 `祝福_四星.md`（25，临界方程/神迹/派系类，BWIKI 稀有度 4 星）；主索引 `祝福.md` 待补充列表 359→3。
- 剩余：祝福 3 星级 + 4 命途、事件 64 个（星神遭遇/方程/商店类）待米游社 WIKI 或游戏攻略源。备份：temp/bless_backup_20260828/、temp/event_backup_20260828/、temp/index_backup_20260828/。

---

### 三十一、货币战争 6 项缺漏补全（2026-08-28）
- **装备合成配方**：新增 10 种基础装备（8 常规 + 红钻/蓝钻）+ 36 种进阶装备完整合成表（8 系，3DM 322682 转「装备合成一图流」图片 OCR 全量）+ 红钻阵营星徽 8 / 蓝钻流派星徽 8 + 财富宝钻；`装备图鉴.md` 重写。
- **3.7 基础角色费用**：61 位完整费用表（1费14/2费13/3费13/4费12/5费9，源：游戏内「数据银行·角色图鉴」截图，米游社 70655171「锐评货币战争全部角色」），含站位（三月七/姬子后台、银狼前后台、瓦尔特前台等）与赋能要点；`角色图鉴.md` 新增章节。
- **投资环境/投资策略完整清单**：新建 `投资环境与投资策略.md`（83 环境 + 334 策略）。环境按 3.7基础61/4.0 12/4.2 7/4.4 3 分组；策略按白银77/黄金135/棱彩122 分组，3.7 基础 261 附完整效果（米游社 70474667），版本新增 73 标注（4.0/4.2/4.4 图鉴 73319229/74981853/76936594），含特殊触发条件与刷取建议（标准博弈限定 9 策略 2 环境、位面限定、三佩佩）。
- **基础赛季竞争对手**：13 个基础阵营名单收录（凛冬经贸联合体/冷锋兵器工业/纷争前线军团/深穹智械科技/灰手生命科技/猎星资本/铁盾安保集团/增熵能源集团/巨鹿生物制药/造梦兄弟影业/火线动力机甲/银甲武装公司/造梦互动娱乐），首领待游戏内确认；`赛季更新.md` 更新。
- **独立羁绊**：补 魔术师（Archer）、大守护者（布洛妮娅）、命运卜者（黑天鹅）入 `羁绊图鉴.md` 独立羁绊表。
- **欢愉/命运圣杯成员核对**：欢愉 5 人（爻光1费/绯英2费/银狼LV.999 3费/火花4费/开拓者4费）、命运圣杯 4 人（远坂凛1费/吉尔伽美什2费/Saber 3费/Archer 5费），与角色图鉴交叉验证通过。
- 数据整理脚本：temp/strategy_data_part1.py、part2.py、gen_invest.py（可再生文档）。
- 剩余：基础赛季竞争对手首领名、部分投资环境完整效果待游戏内「数据银行」确认。

---

### 三十二、本地可完成待办收尾核对（2026-08-28）
- **祝福命途索引评估（待办〇-2）**：评估结论**不建立**命途索引。理由：①格式规范 v1.7 定义祝福/ 结构为「分类索引 + 评级索引 + 详情」，未含命途索引层级；②祝福存在大量双命途交错（60 种组合，如 繁育&存护、记忆&毁灭 等），单命途归类会产生重复交叉引用；③主索引已有星级四级结构（三星 150 / 二星 158 / 一星 167 / 四星 25）足以导航。命途覆盖 499/503（99%）。
- **事件「属性」字段与区块目录核对（待办〇-4）**：384/384 事件均有「属性」字段（无缺失）。属性取值为 SRR 原始事件分类（事件 160 / 秘闻 151 / 方程 26 / 事件·虫群 9 / 虫群 5 / 交易 5 / 事件·交易 3 / 事件·遭遇 2 / 铸造 2 / 星神命途各 1 / 天才俱乐部成员各 1）；区块目录为地图节点类型（simulated_blocks.json 15 个：事件/事件·异常/事件·虫群/交易/休整/冒险/奖励/战斗/战斗·虫群/精英/首领/首领·虫群/自我认知/空白/未命名）。两体系不同源；星神与天才俱乐部成员事件的属性 = 关联星神命途 / 成员编号，地图上归类为「事件」节点。核对结论：字段完整、取值与数据源一致，无需改动。
- **「天国」遗器命名核对（待办三）**：官方 Wiki 词条 6271 标题与 3.7 版本公告（sr.mihoyo.com/news/160674）均使用「天国@直播间」为正式名，本地文件名即官方实际显示名，**无需改名**。
- 待办清单同步勾选三项完成；无文件改动（纯核对类），仅更新 update.md 与待办清单。

---

### 三十三、规范扩展规划落地（规则库 + 字段级校验）（2026-08-28）
- **校验脚本（verify_fields.py）**：新建字段级校验脚本，按分类检查详情文件（含实体ID 元信息者）——元信息（数据来源/数据版本/实体ID）、基本信息必备字段、必备章节、可选章节、实体ID 重复（按分类聚合，避免跨库伪重复）。全库 3619 文件 / 3092 详情：**异常 0、重复 ID 无**；已知待补充 160 项（祝福命途 4 / 星级 3、真珠 2、物品获得途径 149、4.5 新遗器获取途径 2）单独归类。
- **祝福 / 奇物模板统一**：发现 274 祝福 + 66 奇物详情文件（同名合并结构）用「## 说明」而非规范模板「## 效果」，已统一改为「## 效果」（340 个文件，标题级改动，内容不变；索引文件跳过）。
- **verify_links.py**：skip_dirs 加入 StarRailRes_data（工作文档数值误识别），知识库内容双链 0 死链（剩余 5 条均为文档占位示例 [[xxx]]）。
- **规则库建立（rules/）**：新建 `rules/` 规则库（v0.1 初始框架）：
  - `规则.md`（主索引，含使用约定：特例优先、公式入库、可信度标注）
  - `通用战斗逻辑.md`（伤害总公式 / 持续伤害 / 击破伤害 / 暴击 / 属性抗性 / 韧性·击破 / 防御与等级，数值标可信度）
  - `状态优先级.md`（增益减益 / 控制 / DoT / 叠加驱散 / 回合机制）
  - `计量单位规范.md`（百分比 / 回合 / 倍率 / 层数书写全局约定）
  - `异常特例库.md`（登记规范 + 4 条初始特例：击破伤害、DoT 暴击、非弱点削韧、控制免疫 Boss，增量登记制）
- **格式规范 v1.7 → v1.8**：目录结构树新增 `rules/`；「十一、后续扩展规划」勾选规则库 / 异常特例库 / 校验脚本（世界观剧情库保留待确认范围）。
- 待办清单「四、规范扩展规划」同步勾选；update.md 记录。

---

### 三十四、差分宇宙祝福补全（413 实体 / 403 文件）（2026-08-29）
- **背景**：SRR_ID 对照发现模拟宇宙·祝福覆盖率仅 805/1219（66%），缺失 414 个实体全部为差分宇宙祝颂（ID 段 634xxx/661xxx/668xxx/671-678xxx），SRR 数据无星级/命途/类型字段。
- **补全内容**：
  - 从 `StarRailRes-master/index_new/cn/simulated_blessings.json` 提取缺失的 414 个实体
  - 跳过 1 个无效条目（634000，name="0" 占位）
  - 有效 413 个实体，按名称合并为 **403 个文件**（2 组同名合并：三月七 2ID、{NICKNAME} 10ID）
  - 字段标注：类型=祝福（差分宇宙）、命途=无（差分宇宙）、星级=无（差分宇宙）、特殊类型=差分宇宙祝颂
  - 单实体文件用纯文本效果；同名合并文件用实体ID-效果表格
- **索引更新**：`simulated/祝福/祝福.md` 主索引新增「差分宇宙祝颂（无星级，403）」分组
- **校验结果**：
  - verify_fields.py：异常 0、重复 ID 无（差分宇宙祝福"无（差分宇宙）"不计入待补充）
  - verify_links.py：无新增死链（剩余 6 条均为文档占位示例）
  - 祝福覆盖率：805/1219 → **1218/1219（99.9%）**，仅差 1 个 name="0" 无效占位条目
- 待办清单、update.md 同步更新；SRR_ID对照报告保留为参考文档。

---

## 2026-08-29 02:30

**角色技能等级数值表与行迹解锁材料全量补全**

- **背景**：此前 92 个角色文件的「战技」章节仅含技能名称 + 满级效果文本，无逐等级数值表；「附加能力（行迹）」表格仅含名称 + 效果，无解锁条件与解锁材料。
- **数据源**：StarRailRes master（本地 `StarRailRes-master/`），`character_skills.json`（技能 params 数值数组 + desc 效果模板）、`character_skill_trees.json`（行迹 anchor + levels[0].promotion + materials）、`items.json`（材料名称映射）。
- **技能章节重构（92 个角色）**：
  - 每个技能（普攻/战技/终结技/天赋/秘技）新增：类型、简述、最大等级、效果模板（含 `#N[i]` 占位符）、**完整等级数值表**（普攻 1-6 级 / 其他 1-10 或 1-15 级，参数列用泛称「参数1(%)/参数2」避免自动推断错误）、**参数说明**（每个 `#N[i]` 占位符的上下文解释）、满级效果（占位符替换为实际数值）。
  - 星魂升级后变体（ID 前缀 1，技能/行迹重复）自动去重，只保留基础形态。
- **行迹表格增强（92 个角色）**：
  - 附加能力表格新增「解锁条件」（晋阶等级，如 晋阶2/4/6）与「解锁材料」（材料名×数量，如 猎人的直觉×4）两列。
  - 开拓者·记忆（8007）保留知识库已有的第 4 行迹「未完的尾声」（SRR 仅含 3 个基础附加能力，额外行迹从知识库原有数据保留）。
- **跳过角色**：真珠（7935，4.6 前瞻，SRR master 无数据），保持原有格式不变。
- **3.x/4.x 角色验证**：黄泉（1308）、火花（1501）等 3.x/4.x 角色 SRR 数据完整，技能/行迹结构与旧角色一致，批量脚本统一处理无异常。
- **生成脚本**：`batch_gen_char_detail.py`（可复跑，参数名泛称策略，开拓者记忆额外行迹保留逻辑）。
- **提交**：commit `f113074`，92 files changed，+12477 / -3193。
- **待办**：真珠详细数据待 SRR 更新或手动补充；参数名当前为泛称，后续可根据官方 Wiki 逐角色人工标注具体参数名（如「护盾倍率」「持续回合」等）。

---

## 2026-08-29 12:39

**角色故事全量补全**

- **背景**：此前 93 个角色文件仅有简短「角色介绍」，无完整角色故事/传记。
- **数据源**：米游社 Wiki 静态接口 `act-api-takumi-static.mihoyo.com/common/blackboard/sr_wiki/v1/content/info`，从角色词条的 `rpg_new_tmp_content.modules` 中提取 `character_story` 组件数据。
- **补全内容（93 个角色）**：
  - 每个角色文件「基本信息」之后新增「## 角色故事」章节，包含：角色简介（detail）+ 角色故事·其一~其四（标准角色 4 章）。
  - 开拓者 5 个形态使用「你的「故事」•一~五」格式（5 章，含开拓任务解锁条件）。
  - 三月七等特殊角色 5 章。
  - 真珠（4.6 前瞻）、砂金•戏浪（4.6 前瞻）章节较少，数据不全属正常。
- **特殊处理**：
  - 椒丘（cid=3058）使用旧版模板（`tmp_type: RpgTemplateTypeDefault`），角色故事在 `contents` 列表的 HTML 字段中，单独解析 `<details><summary>` 结构。
  - 其余 92 个角色使用新版 RPG 模板，从 `character_story` 组件的 JSON data 字段提取。
  - HTML 标签清理（`<i>`、`<br>`、`<strong>` 等），保留纯文本。
- **抓取脚本**：`scripts/fetch_char_stories.py`（支持断点续传，请求间隔 1.5-3 秒，进度存 `.tmp_build/story_progress.json`）。
- **提交**：commit `7572d38`，93 files changed，+8813。
- **覆盖率**：93/93 角色均有角色故事章节（85 个标准 4 章 + 开拓者 5 章 + 三月七 5 章 + 前瞻角色少章）。

---

## 2026-08-30 00:46

**第三章/第四章/第五章剧情文本全量完成（新增32个，剧情文本总数92个）**

- **背景**：此前剧情文本库已完成序章（6个）、第一章（24个）、第二章（14个），共44个。第三章「仙舟罗浮」后续、第四章「匹诺康尼」、第五章「二相乐园」及支线任务剧情文本缺失。
- **数据源**：米游社 WIKI（bbs.mihoyo.com/sr/wiki），经浏览器操作（computer_use_tool）逐任务页面获取完整交互对话，包括任务描述、任务过程、完整对话、分支选项。
- **第三章剧情文本（13个）**：
  - 第一部分「乘槎驭风仙窟游」后续、第二部分「云树百丈蔽重楼」、第三部分「劫波渡尽战云收」及同行任务。
  - 覆盖：丹恒饮月君变身、镜流/罗刹/刃真实目的揭示、建木重生、幻胧击败等完整主线。
- **第四章剧情文本（5个）**：
  - 匹诺康尼主线关键任务，覆盖：家族与梦主、太一之梦、星期日篡夺齐响诗班、黄泉黑天鹅唤醒人们等。
- **第五章「二相乐园」剧情文本（27个）**：
  - **第一部分「欢迎来到二相乐园」（7个）**：幻月是慈悲的女王、机械复制时代的艺术作品、幻造艺术的基本原理、杀手们没有假期、象征交换与侦探、每个人都能成名十五分钟、主播女孩的审慎魅力。
  - **第二部分「献给破晓的失控」（4个）**：一位中年艺术家的肖像、一个正义罪人的忏悔、浪子与六翼天使一般神圣、多么神圣的笑声。
  - **第三部分「如是，众生欢笑不已」（7个）**：观光客的哲学（幻月开口！胜者成为永久欢愉星神）、如果我们的语言是笑声（火花调查满愿·十五年前血涂游戏）、嚎叫白噪音或个人的体验（满愿幸福语法真相·假面愚者把痛苦酿成美酒）、鸣的锣响的钹（列车紧急会议·二十万受术者·取胜概率71%）、我们赖以生存的隐喻（二十万人病变为丰饶之民·全域扩散）、血清素恐惧症（银狼回忆加入星核猎手原因·模因污染）、液态现代性的生成语法（满愿电视台舆论攻势·姬子十五年前击败告死魔）。
  - **后续核心任务（8个）**：误以为结束的错觉（幻月时讯新闻·满愿变成怪物·20万人受影响·86亿损失）、昨日的世界（姬子父亲隆介疑点·绝灭大君归寂·绘世一族风化诅咒·52%概率被归寂利用）、我如何遇到你的父亲（前情提要·刃跃入贪饕熔炼倏忽·隆介从头到尾是归寂假扮·归寂多个位置同时现身）、不存在的国度（归寂现身揭露绘世是毁灭子嗣·千年前哈托彼亚废墟女婴）、你逃我也逃（二维市空间扭曲·骰子脸怪物宣告·星期日乌鸦叫大家撤离泊地站）、错误的喜剧（归寂把姬子关进画里·三处空白三个秘密·完成名为姬子的画作）、瞬息全乐园（姬子留下线索·引力波频率求救·列车引擎空间曲率密钥·引力探针接收信号）、谜与恐怖的乐园（黄金教师讲贪饕故事·未抵用笑声填满贪饕嘴巴被啃稀巴烂·大卫戴立志成为贪饕行者）。
- **支线任务（4个）**：
  - 匹诺康尼支线：树上的灾兆（流萤花火接头·康士坦丝梦主阴谋·寰宇蝗灾·银枝纯美骑士团）、世间的每一个清晨（大丽花流萤·太一之梦·黄泉黑天鹅唤醒人们）。
  - 翁法罗斯支线：烈阳啊为迷途照明前路（丹恒赞达尔·三月七过去黑暗·忆庭窃贼·铁墓记忆）、故事啊完篇于初遇之时（迷迷在命运重渊苏醒·记忆回音黑潮雅努萨波利斯·获得光锥飞向粉色的明天）。
- **每个剧情文本文件结构**：任务描述 / 任务过程 / 完整交互对话（分章节）/ 任务总结（关键信息 / 角色关系 / 伏笔）。
- **第五章剧情完整脉络**：开局进入二相乐园 → 幻造艺术学习 → 调查十五年前血涂游戏真相 → 满愿揭面幸福语法 → 列车紧急会议 → 二十万人病变 → 银狼回忆 → 舆论攻势 → 满愿变成怪物 → 隆介疑点 → 刃牺牲熔炼倏忽 → 归寂现身揭露真相 → 隆介是归寂假扮 → 姬子被关进画里 → 引力波求救信号 → 准备反击。
- **剧情文本统计**：序章6 + 第一章24 + 第二章14 + 第三章13 + 第四章5 + 第五章27 + 支线4 = **93个**（含此前已有的部分第三章/第四章文件，本次新增32个）。
- **抓取方式**：浏览器自动化操作，每任务页面等待5秒加载，滚动触发懒加载，正则提取交互对话区域，批量处理（每批3-4个任务）。
- **待补充**：第五章部分支线任务（鼹鼠之歌、银辇啊挽别那人间史诗等）、部分任务后续对话内容（页面截断）、角色语音与过场动画描述。

---

## 说明
- 数据版本基线：4.5（真珠为 4.6 前瞻角色，单独标注）。
- 数据来源为粉丝制作数据库站点，游戏图像与资产版权归 HoYoverse 所有。
- 本文件不包含任何链接（双链 / 网址），仅作纯文本更新记录。
