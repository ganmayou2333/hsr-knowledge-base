# 测试报告 · 站点视觉重构（R1）+ 角色 hero 动画（R2）

| 项 | 值 |
|---|---|
| 环节 | Tester（真实浏览器验收） |
| slug | `site-hero` |
| 被测改动 | `wiki/assets/style.css`（306→684 行，18133→42756 B）、`wiki/assets/character-panel.js`（68→387 行，2148→14022 B） |
| 上游 | issue **#13**、设计 `docs/designs/site-hero.md`、Coder 探针（`.tmp_build/hero_probe.html`、`css_probe.html`、`table_ab.html`） |
| 写盘范围 | 本文件 + `.tmp_build/` 下的探针与截图；**未修改任何产品文件**（`git status wiki/assets wiki/build_wiki.py` 无新增改动） |
| 运行环境 | Windows，Python 3.14.9，Chromium 内核 **Edge 157.0.4341.60**（headless=new，CDP 控制，非 jsdom）；站点由 `python -m http.server 8899 --bind 127.0.0.1` 从仓库根提供同源页面 |
| 探针 | `.tmp_build/t_tester_probe.py`（零依赖 CDP 客户端，复用 `cdp_probe.py` 的 WS 实现）、`.tmp_build/t_a2_js_scan.py`（A2 静态扫描） |
| 判定基线 | 设计 §5 + 本次任务的 A1–A18（任务口径优先） |

**结论：17 项判 PASS、0 项硬 FAIL、2 条缺陷（1×P1、1×P2）、1 项口径待 Lead 裁定（A16 传输计量单位）。**
用户点名重点 **A12（顶部标题不被裁切）实测不可复现**——见 A12 小节，Coder 截图里的「裁切」实际是 hero 名字 `heroNameIn` 擦除动画的进行中帧。

---

## 1. 汇总表（A1–A18）

| # | 断言 | 结果 | 关键证据（实测） |
|---|---|---|---|
| A1 | `verify_site.py` PASS，`[5]` 六项全 0 | **PASS** | `[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0`；`RESULT: PASS`；exit 0 |
| A2 | JS 静态扫描无禁用字面量 | **PASS** | `box-shadow`/`linear-gradient`/`repeating-`/`http(s)://`/`<img` 各 `hits=0`；`border-radius` 0 处 |
| A3 | 构建 6685 页 / 死链 0 / 未收录 0 | **PASS** | `生成页面: 6685`、`总链接: 96883, 死链: 0`、`未收录: 0 处`；`git status wiki/pages wiki/data` 空（产物可重生成、与工作区一致） |
| A4 | `verify_fields` 异常 0 / 待补 156 | **PASS** | `扫描 6685 / 详情 5992 / 异常合计: 0 / 已知待补充合计: 156`（命途 4 + 星级 3 + items 获得途径 149） |
| A5 | `verify_links` exit 0 | **PASS**（证据偏弱，见备注） | exit 0；`死链数: 56` 全部位于 `docs/`、`update.md`、`.tmp_*` 的**文档示例/正则片段**，数据区（`zh_cn/ en_us/ ja_jp/ ko_kr/ zh_tw/ wiki/`）死链 **0** |
| A6 | hero 首点：拦截成功 + overlay + 记账 + 840ms 跳转 | **PASS** | `dispatchEvent 返回=False`；`overlay={state:enter→hero, ariaHidden:true}`；`storage=["1014"]`；`--hero-total=840ms`，`beforeunload` 记时 **842 ms**；t≈1150ms 已到 `1014.html` |
| A7 | 二次点击 `intercepted=false`、无 overlay、不重播 | **PASS** | 同会话再点 1014：`dispatchEvent=True`（未被 preventDefault）、`overlay=None`、`storage` 仍 `["1014"]`、原生跳转 `1014.html` |
| A8 | reduced-motion：不播 / 直接跳 / 不记账 | **PASS** | `matchMedia(reduce)=True`；`intercepted=False`、`overlay=None`、`storage=None`、t≈600ms 已到 `1014.html` |
| A9 | Tab+Enter 与鼠标一致；overlay 期间 Esc 可跳过 | **PASS** | 真实 Tab（聚焦末位 chip 后逐次 Tab、命中即停）活动元素=`A.ccard Saber`；Enter → `overlay={state:hero}`+`storage=["1014"]`+跳 `1014.html`；Esc 后 **+312 ms** 跳到 `1404.html` |
| A10 | 无 JS：卡片仍是 `<a>`、href 正确、可进详情 | **PASS** | `Emulation.setScriptExecutionDisabled(true)`：94 张卡全是 `A.ccard`、`href=../../pages/character/毁灭/1014.html`、`overlay=false`、`.cp-filters display=none`（head noscript 生效）；**真实鼠标点击** → `1014.html` |
| A11 | 600×900 无横向溢出、`cgrid` 列数 ≥4 | **PASS** | `innerWidth=600 docScrollWidth=600 bodyScrollWidth=600 无溢出=True cgrid列数=5`；越界元素 0 个 |
| A12 | **顶部 h1 不被裁切** | **PASS** | 角色页 scrollY=0：`h1.top=662.86`（1280×900）/`253.78`（600×900），`top>=0`、完整可见、`h1.top ≥ topbar.bottom`、9 个采样点无遮挡、祖先无裁剪容器；另加 3 页×3 宽度共 9 组合全部 PASS |
| A13 | 主题四组合：`--ui-hi`、`::before` clip-path、对比度 | **PASS** | 4 组合 `--ui-hi` = `#0A6E8C`（亮）/`#6FE3FF`（暗）；卡片 `::before clip-path=polygon(8px 0px, 100% 0px, …)`；卡片文字/底对比 **15.83–18.65**、正文对比 **16.79–16.87**（≥4.5）；另测「跟随系统」两态同样正确 |
| A14 | `thead th` sticky 生效且不遮挡首行 | **PASS**（字面）**但缺陷 D-1** | `position=sticky z-index=1`，无破坏 sticky 的祖先；scrollY=0 时 `th.bottom=1376.5` == 首行 `top=1376.5`（不重叠）。**吸附状态下表头被 sticky topbar 压住 51.8/65.8px** → 见 D-1 |
| A15 | `@media print` 下 hero overlay 与侧栏隐藏 | **PASS**（含缺陷 D-2） | print 媒体下：overlay `display:none`（含手工注入的 `.hero-overlay` 节点）、`.sidenav` none、`.crumbs` none、`.theme-toggle` none、`.hero-sweep` none、body 白底 |
| A16 | 单页新增传输 ≤30 KB；首屏 JS ≤50 ms | **⚠ 待裁定** | 增量 raw **+36497 B（35.6 KiB）> 30 KB**；gzip(-9) **+10399 B（10.2 KiB）< 30 KB**。首屏 JS 执行：面板页 **+1.2 ms**、首页 **+9.5 ms**（≤50 ms ✓），无 >50 ms 长任务 |
| A17 | 4 个无立绘角色 `img`=0、无 404 | **PASS** | 1511/1503/1513/1512 全部：`overlay.imgs=0`、`剪影=True`、数据条 3 行、`坏请求=[]`、跳转正常 |
| A18 | 面板页与首页 `console.error`=0 | **PASS** | 面板页 0 条（含点卡片播完一轮 hero）、首页 0 条；无 JS 异常。首次加载另有 `/favicon.ico` 404（Log 级，仓库 HEAD 无 favicon，与本次改动无关，见 D-5） |
| A19 | *额外*：修饰键不劫持 / storage 不可用降级 | **PASS** | `Ctrl+点击`：`intercepted=False overlay=False storage=None`；`Storage` 抛异常：不播、原生跳 `1014.html` |

材料：无 `.tmp_build/` 之外的新增文件；截图 25 张（见 §5 清单）。

---

## 2. 逐条证据

### A1 · `verify_site.py`

```
$ python tools/verify_site.py
pages: 6685 个生成页
[4] 死链: report=0, 独立复算=0  (一致=True)
[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0
      说明: 已跳过 CI 构建期生成的图标 <img> 1692 个
[8] 未收录链接: report=0, 独立复算=0 (一致=True)
RESULT: PASS
VERIFY_EXIT=0
```
日志：`.tmp_build/t_a1_verify.log`

### A2 · JS 静态扫描（`[5]` 不扫 `assets/*.js`，需补测）

```
$ python .tmp_build/t_a2_js_scan.py
A2 box-shadow       hits=0 []
A2 linear-gradient  hits=0 []
A2 repeating-       hits=0 []
A2 http(s)://       hits=0 []
A2 <img             hits=0 []
A2 border-radius      hits=0 values=[]
A2 行数=388 字节=14022
```
`<img>` 节点由 `el("img", …)`（DOM API）创建，属 A2 允许的形式。日志：`.tmp_build/t_a2_scan.log`

### A3 · 构建

```
$ PYTHONUTF8=1 python wiki/build_wiki.py
角色面板: 94 个角色 | 命途 9 | 属性 7 | 无图 4
生成页面: 6685
总链接: 96883, 死链: 0
未收录(降级为纯文本): 0 处
BUILD_EXIT=0
$ git status --porcelain wiki/pages wiki/data     # 空输出
```
日志：`.tmp_build/t_a3_build_utf8.log`（首次跑的同参数日志 `t_a3_build.log` 因控制台代码页乱码不可读，结论一致）

### A4 · 字段校验

正确口径是 **在 `zh_cn/` 下运行**（仓库根运行会把五语数据一起扫，得 `异常合计: 64291`，与文档基线不可比）：

```
$ cd zh_cn && python ../scripts/verify_fields.py
扫描 md 文件数: 6685
详情文件数: 5992
异常合计: 0
已知待补充合计: 156        # [blessing]命途4 + [blessing]星级3 + [items]获得途径149
EXIT=0
```
日志：`.tmp_build/t_a4_fields_zhcn.log`（仓库根口径：`.tmp_build/t_a4_fields.log`）

### A5 · 双链校验

```
$ python scripts/verify_links.py
扫描文件数: 30673
链接总数: 23140
死链数: 56
LINKS_EXIT=0
```
- 56 条死链的源文件全部是 `docs/**`、`update.md`、`格式规范与要求.md`、`翻译办法.md`、`.tmp_*`；**数据区 0 条**（逐条核对 `-> [[` 明细）。
- ⚠ 口径备注：`scripts/verify_links.py` 结束时**没有设置非零退出码**（脚本尾部无 `sys.exit`/`raise`），因此「exit 0」不具判别力；本报告以「数据区死链 0」作为实质证据。
日志：`.tmp_build/t_a5_links.log`（GBK 编码）

### A6 / A6b / A6c / A6d · hero 首次点击

```
A6   首点 1014 dispatchEvent 返回=False intercepted=True
A6   t≈60ms overlay={'state':'enter','ariaHidden':'true','imgs':2,'sil':False,
                     'stats':['属性风','命途毁灭','星级五星']} storage=["1014"]
A6   t≈310ms overlay.state='hero'
A6   t≈1150ms url=1014.html overlay=False
A6b  t≈720ms 定格帧：name='Saber' clip=inset(0px 0% 0px 0px) rect=[588,526,105,41] scrollW=105 clientW=105
A6b    stage=[430,226,420,447] art=[512,258,256,256] 立绘已就位=True hint=True
A6d  intercepted=True --hero-total=840ms → 点击到开始导航实测=842 ms
A6c  跳转到 1014.html 的实测时点 ≈ 1008 ms（含导航提交，见 A6d 的 842ms）
A6   console/network 错误=['log:Failed to load resource: the server responded with a status of 404 (File not found)']
     坏请求=['404 http://127.0.0.1:8899/favicon.ico']      ← 唯一的错误项，见 D-5
```
`A6d` 用 `beforeunload` + `performance.now()` 在文档内记时，避免 CDP 轮询误差。截图：`shot_a6_hero_1280.png`（t≈310ms，进行中）、`shot_a6_hero_settle_1280.png`（t≈720ms，定格）、`shot_a6_hero_stage_zoom.png`。
日志：`.tmp_build/t_probe_a6a7a8.log`、`.tmp_build/t_probe_b5.log`

### A7 · 二次点击不重播

```
A7   新载入 storage=["1014"]
A7   二次点 1014 返回=True intercepted=False overlay=None
A7   t≈500ms url=1014.html overlay=False storage=["1014"]
```

### A8 · reduced-motion

```
A8   matchMedia reduce = True
A8   点 1014 返回=True intercepted=False overlay=None storage=None 卡片类=-
A8   t≈600ms url=1014.html overlay=False storage=None
```
`Emulation.setEmulatedMedia features=[{prefers-reduced-motion: reduce}]`（真实媒体模拟，非打补丁）。

### A9 · 键盘

```
A9   焦点起点 chip=重置
A9   Tab 后活动元素={'tag':'A','cls':'ccard','txt':'Saber风·毁灭★★★',
                    'href':'../../pages/character/%E6%AF%81%E7%81%AD/1014.html'}
A9   Enter 后 t≈220ms overlay={'state':'hero',...} storage=["1014"]
A9   t≈1150ms url=1014.html
A9   Esc 前 overlay=True；Esc 后 +312ms url=1404.html overlay=False
```
Tab 用 `Input.dispatchKeyEvent` 真实按键（非 `focus()` 直设），Enter/Esc 同为真实按键。

### A10 · 无 JS

```
A10  关 JS 方式=scriptDisabled；页面内 eval 是否可用=object
A10  卡片={'n':94,'tag':'A','cls':'ccard','href':'../../pages/character/毁灭/1014.html',
           'overlay':False,'filtersDisplay':'none','noscriptStyle':True}
A10  真实点击后 url=1014.html（期望进入详情页）
```
`Emulation.setScriptExecutionDisabled(true)` 是真·关 JS（`head noscript style` 因此生效，`.cp-filters` 被隐藏），随后用 `Input.dispatchMouseEvent` 真实点击。

### A11 · 600×900

```
A11  viewport=600 docScrollWidth=600 bodyScrollWidth=600 无溢出=True cgrid列数=5
A11  越界元素(前5)=[]
```
截图：`shot_a11_600x900.png`（5 列卡片、导航已折叠、无横向滚动条）

### A12 · 顶部标题不被裁切（用户点名重点）

主测（任务要求的那一条）：

```
A12  1280x900 scrollY=0 h1 rect top=662.86 bottom=728.86 h=66 | top>=0=True | 完整可见=True
A12    h1.top >= topbar.bottom？True (h1.top=662.86 topbar.bottom=99.8) margin-top=0px opacity=1 transform=matrix(1,0,0,1,0,0)
A12    遮住 h1 的采样点 0 个 []；祖先裁剪=[]
A12  600x900 scrollY=0 h1 rect top=253.78 bottom=308.28 h=54.5 | top>=0=True | 完整可见=True
```

扩展（3 页面 × 3 宽度 = 9 组合，全部不裁）：

```
A12b  角色总索引 1280x900 h1 top=662.9 h=66 被裁=False 被遮=[] 文本='角色总索引'
A12b  角色总索引 1440x900 h1 top=662.9 h=66 被裁=False 被遮=[] 文本='角色总索引'
A12b  角色总索引 600x900  h1 top=253.8 h=54.5 被裁=False 被遮=[] 文本='角色总索引'
A12b  角色详情 1014 1280x900/1440x900/600x900 全部 被裁=False 被遮=[] 文本='Saber（风·毁灭）'
A12b  首页 1280x900 top=123.8 / 1440x900 top=123.8 / 600x900 top=91.8 全部 被裁=False
```

截图：`shot_a12_title_1280x900.png`、`shot_a12_title_600x900.png`（截图为页面顶部 200px：`.topbar` 上方的空白是 `body{padding:48px 32px 64px}` 的既有留白，不是裁切）。

**Coder 那张「疑似被裁」的截图如何解释**：`shot_a6_hero_1280.png`（t≈310ms）里 hero 名字显示为 **「Sa」**、数据条与提示行尚未出现——这不是标题被裁，而是 `@keyframes heroNameIn{from{clip-path:inset(0 100% 0 0)}…}`（`style.css:632`，260ms 起、160ms）擦除动画的**进行中帧**。定格帧（A6b，t≈720ms）实测 `name='Saber' clip=inset(0px 0% 0px 0px)`、`scrollWidth=clientWidth=105`，无裁切残留。

### A13 · 主题四组合

```
A13  系统=light data-theme=light → --ui-hi=#0A6E8C clip-path=polygon(8px 0px,100% 0px,100% calc…
                                   卡片文字/底对比=18.65 正文对比=16.79 border=0px radius=0px
A13  系统=light data-theme=dark  → --ui-hi=#6FE3FF clip-path=polygon(…) 对比=15.83 / 16.87
A13  系统=dark  data-theme=light → --ui-hi=#0A6E8C clip-path=polygon(…) 对比=18.49 / 16.79
A13  系统=dark  data-theme=dark  → --ui-hi=#6FE3FF clip-path=polygon(…) 对比=15.96 / 16.87
A13b 系统=light 无 data-theme（跟随系统）→ --ui-hi=#0A6E8C bodyBg=rgb(241,243,247) 对比=18.65/16.79
A13b 系统=dark  无 data-theme（跟随系统）→ --ui-hi=#6FE3FF bodyBg=rgb(6,8,12)     对比=15.96/16.87
```
四组合截图：`shot_a13_light_light.png`、`shot_a13_light_dark.png`、`shot_a13_dark_light.png`、`shot_a13_dark_dark.png`；卡片切角实拍：`shot_a13c_cards_{light,light}.png` 等 4 张（亮色下左上/右下切角与 1px 描边肉眼可辨）。

### A14 · 表格 sticky

```
A14  thead th position=sticky z-index=1 高=65.8
A14  scrollY=0 时 th.bottom=1376.5 首行 top=1376.5 重叠=False
A14  破坏 sticky 的祖先=[]
A14c scrollY=1570；th=0..65.8，topbar=0..51.8(z=20, th z=1)
A14c 视口 y=10 处最上层=DIV.topbar；y=60 处=TH.；topbar 背景=rgb(6,8,12)
A14c 表头可见高度=14px / 表头总高=65.8px
```
→ 断言字面成立（sticky 生效、静止态不压首行），但吸附态下表头被新增的 sticky topbar 盖住 **51.8 px**，只剩 14 px 可见 —— 记缺陷 **D-1**。截图：`shot_a14_table_sticky.png`、`shot_a14c_top.png`、`shot_a14c_full.png`。

### A15 · 打印

```
A15  打印前 overlay=True
A15  print 媒体下：overlay=none sidenav=none topbar=flex sweep=none topbar::before=none bodyBg=rgb(255,255,255)
A15b print：注入 overlay display=none visibility=visible；sidenav=none crumbs=none toggle=none
A15b print：.topbar display=flex 背景=rgb(6,8,12) 边框=1px rgb(35,43,56) 高度=17 矩形=[0,17,17]
A15b print+系统暗：topbar 背景=rgb(6,8,12)（body=rgb(255,255,255)）
```
断言两要素（overlay、侧栏）均隐藏 ✓；但 `.topbar` 在打印态仍是 `display:flex` 且带深色背景 → 纸面出现 17px 深色条（**D-2**，截图 `shot_a15b_print_dark.png` 顶部可见）。

### A16 · 性能预算

体积（`git show HEAD:` 取基线，`gzip.compress(…,9)`）：

| 文件 | HEAD | 现在 | Δ raw | Δ gzip |
|---|---|---|---|---|
| `wiki/assets/style.css` | 18133 B | 42756 B | **+24623 B** | +6080 B |
| `wiki/assets/character-panel.js` | 2148 B | 14022 B | **+11874 B** | +4319 B |
| 合计（面板页新增） | — | — | **+36497 B = 35.6 KiB** | **+10399 B = 10.2 KiB** |

首屏 JS 执行（`Performance.getMetrics` 的 `ScriptDuration` 差值，about:blank 为基线）：

```
A16  角色面板页 ScriptDuration Δ=+1.2 ms | TaskDuration Δ=+112.9 ms | Layout Δ=+62.7 ms | 样式 Δ=+9.4 ms
A16   角色面板页 buffered 长任务(>50ms) ms=[]
A16  首页 ScriptDuration Δ=+9.5 ms | TaskDuration Δ=+78.0 ms | Layout Δ=+21.2 ms | 样式 Δ=+16.2 ms
A16  首页 buffered 长任务(>50ms) ms=[]
A16  面板页资源：style.css encoded=42756 / theme.js 1581 / character-panel.js 14022（本机 http.server 不压缩）
```
→ **JS 预算 PASS（1.2 / 9.5 ms ≪ 50 ms）**；**传输预算按口径分歧**：未压缩 35.6 KiB 超预算，gzip 后 10.2 KiB 达标（静态托管 GitHub Pages 实际走压缩）。见「未决 U1」。日志：`.tmp_build/t_a16_sizes.log`、`.tmp_build/t_probe_b3.log`。

### A17 · 无立绘 4 角色

```
A17  1511 intercepted=True overlay.imgs=0 剪影=True 数据条=['属性量子','命途欢愉','星级五星'] 坏请求=[]
A17  1503 intercepted=True overlay.imgs=0 剪影=True 数据条=['属性冰','命途欢愉','星级五星']   坏请求=[]
A17  1513 intercepted=True overlay.imgs=0 剪影=True 数据条=['属性量子','命途欢愉','星级五星'] 坏请求=[]
A17  1512 intercepted=True overlay.imgs=0 剪影=True 数据条=['属性风','命途记忆','星级五星']   坏请求=[]
A17  → 四者跳转后 url 分别为 1511/1503/1513/1512.html
```
截图：`shot_a17_1511_silhouette.png`（剪影 + 名字「星神★阿哈」+ 数据条，无坏图图标）。

### A18 · 控制台

```
A18  角色面板页 console.error/异常=0 []
A18  首页 console.error/异常=0 []
```
采集面：`Runtime.consoleAPICalled(type=error)` + `Runtime.exceptionThrown` + `Log.entryAdded(level=error)`，期间含一轮完整 hero 播放。
另见 **D-5**：首次加载会出现一条 `Failed to load resource … 404`（`/favicon.ico`，见 A6 小节实测行 `坏请求=['404 …/favicon.ico']`）。仓库 HEAD 无任何 favicon 资产、HTML 也无 `<link rel="icon">`，属既有现象，不是本次引入。

---

## 3. 缺陷清单

### D-1（P1，本轮引入）滚动时 sticky 表头被 sticky `.topbar` 压住，表头文字不可见

- **现象**：滚动到「表头应吸附」的位置后，`thead th` 确实吸附在 `top:0`，但新增的 `.topbar` 也 `top:0` 且 `z-index:20 > 表头 z-index:1`、背景不透明，把表头盖住 51.8/65.8 px，只剩 14 px 可见；`document.elementFromPoint(640,10)` 返回 `DIV.topbar`。
- **文件:行**：`wiki/assets/style.css:437-439`（本次新增 `.topbar{position:sticky;top:0;z-index:20;…background:var(--ui-bg);border-bottom:…}`）与 `wiki/assets/style.css:127`（`table thead th{position:sticky;top:0;z-index:1;background:var(--ui-panel-2)}`）冲突。
- **回归依据**：`git show HEAD:wiki/assets/style.css:17` 为 `.topbar{display:flex;justify-content:flex-end;margin:0 0 24px}` —— 改动前 topbar 不是 sticky，不存在该冲突。
- **复现步骤**：
  1. `cd G:\HSR && python -m http.server 8899 --bind 127.0.0.1`
  2. 打开 `http://127.0.0.1:8899/wiki/pages/character/%E6%AF%81%E7%81%AD/1014.html`
  3. 向下滚动约 1570px（第一张「稀有度/阵营/角色介绍…」表格吸附时）
  4. 观察：表头行的文字被顶部「跟随系统」条遮住，只露出底边 14px
  5. 探针复跑：`python .tmp_build/t_tester_probe.py a14c`
- **期望**：表头吸附位置让开 topbar（如 `thead th{top: <topbar 高度>}` 或用 `--ui-topbar-h` 变量），或让 topbar 不 sticky。
- **影响**：详情页/索引页所有 `<table>` 的表头在滚动中不可读；视觉重构的「数据感」卖点在该场景失效。

### D-2（P2，本轮引入）打印时页首出现 17px 深色条

- **现象**：`@media print` 下 `.topbar` 计算值 `display:flex`（不是 `none`），背景 `rgb(6,8,12)`、下边框 1px，实测矩形 `[0,17,17]`；暗色主题打印会在纸面顶部打出一条深色带（截图 `shot_a15b_print_dark.png` 顶部可见）。
- **文件:行**：`wiki/assets/style.css:141`（print 里 `.topbar,…{display:none}`）被 `wiki/assets/style.css:437-439`（后出现的 `.topbar{display:flex;…background:var(--ui-bg);border-bottom:…}`，同特异度、位置更后）覆盖；HEAD 的 `.topbar` 无背景/边框，所以旧版打印无可见条。
- **复现步骤**：
  1. `python -m http.server 8899 --bind 127.0.0.1` → 打开角色总索引页
  2. DevTools → Rendering → Emulate CSS media type = `print`（且系统偏好为暗色）
  3. 观察页首 17px 深色条
  4. 探针复跑：`python .tmp_build/t_tester_probe.py a15b`
- **期望**：打印里 `.topbar{display:none}` 真正生效（提高选择器特异度或把该规则移到新段之后）。

### D-3（P2，健壮性观察，不阻断）hero 关键帧缺「第二道保险」

- `wiki/assets/style.css:639-653` 的 `.hero-overlay/.hero-frame/.hero-br-*/.hero-name/.hero-stat/.hero-sweep` 动画规则**没有**包在 `@media (prefers-reduced-motion: no-preference)` 内（设计 F9/§3.6 要求两道保险，`style.css:198/203/231` 的老动效都是这么写的）。
- 实际行为不回归：JS 在 reduce 下根本不建 overlay（A8 实测不播、不记账），且 `style.css:124` 的 `@media(prefers-reduced-motion:reduce){*{animation:none!important}}` 兜底。
- 建议：与既有动效段保持一致，仍包一层，避免将来 JS 分支调整后漏掉。

### D-4（info）设计文档引入 3 条假死链

`docs/designs/site-hero.md` 里写了 `[[:space:]]` 这类正则示例，被 `scripts/verify_links.py` 当成 wikilink，贡献 3 条「死链」（只在 `docs/`，数据区 0）。若要求 `verify_links` 输出全零，需在文档里转义或写在代码块之外。

### D-5（info，既有）`/favicon.ico` 404

仓库与 HTML 均无 favicon 声明，浏览器自动请求 `/favicon.ico` → 本地/线上 404（`Log` 级错误一条）。HEAD 同样如此，与本次改动无关；若 A18 要求「零 Log 错误」，需单独补 favicon（属新决策）。

---

## 4. 未决（需 Lead 裁定）

| # | 问题 | 我的实测数据 | 建议 |
|---|---|---|---|
| U1 | A16「新增传输 ≤30 KB」按哪种口径 | 未压缩 **+36497 B（35.6 KiB）**；gzip -9 **+10399 B（10.2 KiB）** | 若按静态托管实际传输（gzip/brotli）→ PASS；若按仓库字节 → FAIL，需要 Coder 再压 ~5.7 KB。请裁定口径 |
| U2 | A14 如何判定 | 字面断言（sticky 生效 + 静止态不压首行）PASS；但 D-1 让表头在滚动中不可读 | 建议按 **P1 打回**（同一处改动引入），修完只重跑 `a14/a14b/a14c` |
| U3 | D-2（打印深色条）是否本轮修 | 17px 深色条，仅打印路径可见 | 影响面小但属本轮引入，建议顺手修（一行特异度/顺序问题） |
| U4 | A5 判据是否改成「数据区死链 0 + 脚本退出码可用」 | `verify_links` 永不返回非零，`exit 0` 无判别力 | 建议给脚本补 `sys.exit(1 if dead else 0)`，或把 A5 写成数据区口径 |

---

## 5. 可复跑清单

```bash
# 0) 起站（后台）
cd /g/HSR && python -m http.server 8899 --bind 127.0.0.1

# 1) 静态断言
python tools/verify_site.py                       # A1
python .tmp_build/t_a2_js_scan.py                 # A2
PYTHONUTF8=1 python wiki/build_wiki.py            # A3
cd zh_cn && python ../scripts/verify_fields.py    # A4（注意口径）
cd .. && python scripts/verify_links.py           # A5
python - <<'EOF'  # A16 体积
# 见 .tmp_build/t_a16_sizes.log 里的同款脚本
EOF

# 2) 浏览器断言（一个进程跑完，避免抢占 9345 端口）
python .tmp_build/t_tester_probe.py a6 a6b a6c a6d a8 a9 a10 a11 a12 a12b \
       a13 a13b a13c a14 a14b a14c a15 a15b a16 a17 a18 a19
```

日志与截图（均在 `.tmp_build/`）：

| 断言 | 日志 | 截图 |
|---|---|---|
| A1 / A2 / A3 / A4 / A5 | `t_a1_verify.log`、`t_a2_scan.log`、`t_a3_build_utf8.log`、`t_a4_fields_zhcn.log`、`t_a5_links.log` | — |
| A6 / A7 / A8 | `t_probe_a6a7a8.log`、`t_probe_b5.log` | `shot_a6_hero_1280.png`、`shot_a6_hero_settle_1280.png`、`shot_a6_hero_stage_zoom.png` |
| A9 / A10 / A11 | `t_probe_b1.log` | `shot_a11_600x900.png` |
| A12 | `t_probe_b2.log` 的 a12b 段 | `shot_a12_title_1280x900.png`、`shot_a12_title_600x900.png` |
| A13 | `t_probe_b2.log`、`t_probe_b4.log`、`t_probe_a13c.log` | `shot_a13_{light,dark}_{light,dark}.png`、`shot_a13c_cards_*.png` |
| A14 | `t_probe_b2.log`、`t_probe_b3.log`、`t_probe_a14c.log` | `shot_a14_table_sticky.png`、`shot_a14c_top.png`、`shot_a14c_full.png` |
| A15 | `t_probe_b2.log`、`t_probe_b3.log` | `shot_a15_print.png`、`shot_a15b_print_layout.png`、`shot_a15b_print_dark.png` |
| A16 | `t_a16_sizes.log`、`t_probe_b3.log` | — |
| A17 / A18 | `t_probe_b3.log` | `shot_a17_1511_silhouette.png` |

---

## 6. 边界声明

- 未修改 `wiki/assets/*`、`wiki/build_wiki.py`、`wiki/data/*`、`zh_cn/*` 等任何产品/数据文件；本环节唯一产品级写盘是 `docs/test-reports/site-hero.md`，其余全部在 `.tmp_build/`。
- 浏览器为 Chromium 内核（Edge 157）headless，通过 CDP `Input.dispatchMouseEvent` / `Input.dispatchKeyEvent` / `Emulation.setEmulatedMedia` / `Emulation.setScriptExecutionDisabled` 驱动，无 jsdom、无 DOM 桩。
- 未覆盖：真 iOS Safari 的 `clip-path` 前缀行为、真实打印纸面（用媒体模拟代替）、bfcache 返回路径（`pageshow` 清理）、多标签并发。

---

## 第二轮复测（修复后）

| 项 | 值 |
|---|---|
| 环节 | Tester（第二轮 · 回归复测，只读） |
| slug | `site-hero` |
| 被测状态 | 工作区修复后（`wiki/assets/style.css` 44945 B、`wiki/assets/character-panel.js` 14402 B，`git status` 同上轮两文件 M，无其它产品改动） |
| 本轮修复项 | D-1 表头让开 sticky 顶栏、D-2 打印深色条、D-3 hero 关键帧 reduced-motion 保险、P1-1 浅色对比度、P1-2 `--hero-total` 真旋钮 |
| 上游 | issue #13、`docs/designs/site-hero.md`、本文件第一轮缺陷清单 §3 |
| 探针 | `.tmp_build/t_tester_probe.py`（上一轮遗留，`a*`）、`.tmp_build/f_issue13_probe.py`（Coder 本轮，`f1..f5`）、**本轮新增** `.tmp_build/t2_b8_dark.py`（B8 深色三页扫描 + B3 相位分离扫描）、`.tmp_build/t2_b3_shots.py`（B3 视口截图） |
| 运行环境 | Windows；Python 3.14.9；Edge（Chromium）157 headless=new，CDP 真实事件；站点 `python -m http.server 8899 --bind 127.0.0.1`（同源） |
| 写盘范围 | 只写本文件 + `.tmp_build/`；**未改任何产品文件**（复测前后 `git status` 集合一致） |

**结论：B1–B10 全部 PASS，0 条 FAIL；5 项修复均实测生效（D-1/D-2/D-3/P1-1/P1-2）。另留 2 条 P2 观察（表体滚出相重叠、`--ui-surface-2` 合成衬底理论值 3.81）与 1 条既有 info（D-5 favicon），均不阻断。**

### B1–B10 汇总

| # | 断言 | 结果 | 关键证据（实测，口径见下） |
|---|---|---|---|
| B1 | `verify_site.py` PASS、`[5]` 六项全 0 | **PASS** | `[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0`；`RESULT: PASS`；exit 0 |
| B2 | 构建 6685 页 / 死链 0 / 未收录 0 | **PASS** | `生成页面: 6685`、`总链接: 96883, 死链: 0`、`未收录(降级为纯文本): 0 处`；构建后 `git status wiki/pages wiki/data zh_cn en_us ja_jp ko_kr zh_tw` 为空（产物与工作区一致） |
| B3 | 滚动中 `th` 与 `.topbar` 重叠 = 0，1280 与 600 两档 | **PASS** | 吸附相：`th=51.8..117.58 topbar=0..51.8 重叠=0px`；1280/600 各 14 个滚动位置**全部 0px**；`--ui-topbar-h` 解析值 51.8 == 渲染高度 51.8（差 0.0）；9 点命中全为 `TH`；表头可见高度 65.8/65.8px |
| B4 | 打印 `.topbar` `display:none`、矩形高 0 | **PASS** | `print(系统暗=True)：.topbar display=none 矩形[top,h]=[0,0]`（1024，两轮 print 模拟均系统暗）；`sidenav=none overlay=none sweep=none bodyBg=rgb(255,255,255)` |
| B5 | 首点播 / 二点不播 / reduce 不播且不写 storage | **PASS** | 首点 `intercepted=True overlay=enter→hero storage=["1014"]` t≈1150 ms 到 `1014.html`；二点 `intercepted=False overlay=None storage=["1014"]`；reduce `intercepted=False overlay=None storage=None` |
| B6 | 改 `--hero-total:1200ms` 后 delay 按比例变化，误差 ≤1 ms | **PASS** | 首帧 delay `0.16s → 0.228571s`，理论 `1200×160/840=228.571`，**误差 0.000 ms**；`hero-sweep dur 0.16→0.228571 / delay 0.56→0.8`、`hero-name delay 0.24→0.371429`、`hero-stat3 delay 0.4→0.571429`；默认值仍读 840ms |
| B7 | reduce 下 hero 各元素 `animation-name` 全 `none`；no-pref 非 none | **PASS** | no-pref：`frame:heroFrameIn,heroSettleIn name:heroNameIn sweep:heroSweepIn overlay:heroBackIn,heroWipeIn stat1:heroStatIn`；reduce：`frame/name/sweep/overlay/spine/stat1/hint` 全 `none`；CSSOM 里 10 个关键帧 + 17 条 hero 规则确实在 `@media (prefers-reduced-motion: no-preference)` 块内 |
| B8 | 深色 `--ui-mute` 对 4 组衬底 ≥4.5 | **PASS** | `①5.513 ②5.212 ③4.843 ④4.843`（hover 实测衬底）；三页 23 类真实 mute 文字最差 5.13，0 类不达标。⚠ 理论合成口径见 P2-A |
| B9 | A11 600×900 无横向溢出、A17 四个无立绘无坏图、A18 `console.error=0` | **PASS** | `viewport=600 docScrollWidth=600 bodyScrollWidth=600 无溢出=True cgrid列数=5`；1511/1503/1513/1512 全 `overlay.imgs=0 剪影=True 坏请求=[]`；面板页/首页 `console.error=0` |
| B10 | gzip-9 增量 ≤30 KB | **PASS** | gzip Δ **+11635 B = 11.36 KiB**（raw Δ +39066 B = 38.15 KiB） |

### 逐条证据

#### B1 · `verify_site.py`

```bash
$ PYTHONUTF8=1 python tools/verify_site.py ; echo exit=$?      # 日志 .tmp_build/r2_b1_verify.log
[1] H1: 6685/6685 合规        [2] 面包屑: 6685/6685 合规
[3] titles.js: 6685 条, BOM=0 井号标题=0 元信息标题=0 空分类=0
[4] 死链: report=0, 独立复算=0 (一致=True)
[5] 禁用项: radius=0 shadow=0 gradient=0 img=0 外链脚本=0 外链样式=0
[6] 静态检查: esc=True combobox=True listbox=True
[15] 角色直达面板: count=94 items=94 独立复算=94 字段齐=94 url=0 citem=94 卡片href错=0 缺图img=0 fallback=4
RESULT: PASS
exit=0
```
→ **PASS**：`[5]` 六项全 0（新增 hero/chip/ccard 段未引入 radius/shadow/gradient）。

#### B2 · `build_wiki.py`

```bash
$ PYTHONUTF8=1 python wiki/build_wiki.py ; echo exit=$?         # 日志 .tmp_build/r2_b2_build.log
角色面板: 94 个角色 | 命途 9 | 属性 7 | 无图 4
首页统计: 页 6685 | 库内最高版本 4.7 | 版本分布 {'4.5': 3847, '4.6': 2489, '4.7': 22, '3.6': 1}
生成页面: 6685
总链接: 96883, 死链: 0
未收录(降级为纯文本): 0 处
$ git status --porcelain wiki/pages wiki/data zh_cn en_us ja_jp ko_kr zh_tw
(空)
```
→ **PASS**：6685 页 / 死链 0 / 未收录 0，且构建幂等（生成产物与工作区无差异）。

#### B3 · 表头吸附（`a14` / `a14b` / `a14c` + `f1` + 相位扫描）

```bash
$ python .tmp_build/t_tester_probe.py a14 a14b a14c    # .tmp_build/r2_tprobe_a14a15.log
A14    thead th position=sticky z-index=1 高=65.8
A14    scrollY=0 时 th.bottom=1376.5 首行 top=1376.5 重叠=False
A14    破坏 sticky 的祖先=[]
A14b   滚动后 th.top=51.8 th.bottom=117.6 (z=1) topbar 占 0..51.8 (z=20) 重叠高度=0px
A14b   th 背景=rgb(18, 25, 38)
A14c   scrollY=1570；th=51.8..117.6，topbar=0..51.8
A14c   视口 y=10 处最上层=DIV.topbar；y=60 处=TH.
A14c   表头可见高度=65.8px / 表头总高=65.8px        ← 上一轮为 14px/65.8px

$ python .tmp_build/f_issue13_probe.py f1              # .tmp_build/r2_fprobe.log
f1a    视口=1280x900 scrollY=1570 表头文字='属性'
f1a    .topbar 高度(渲染)=51.8  --ui-topbar-h(表头 top 解析值)=51.8  一致=True (<0.6px)
f1a    吸附态 th=51.8..117.58 (h=65.78)  topbar=0..51.8 → 重叠=0px 不重叠=True 表头完整可见=True 已吸附=True
f1a    吸附区域 9 点命中=['TH'×9]      P1-A 判定=PASS
f1b    视口=600x900 scrollY=1150 → 重叠=0px 9 点全 TH  P1-A 判定=PASS

$ python .tmp_build/t2_b8_dark.py sticky                 # .tmp_build/r2_b8_run.log
B3s    1280x900 采样：吸附相 14 / 表体滚出相 3 / 未吸附相 7
B3s    1280x900 吸附相最大重叠 = 0px，重叠位置 0 个 → PASS(重叠=0)
B3s    1280x900 吸附态定点 th=51.8..117.58 topbar 高=51.8 表头 top 解析值=51.8(差 0.0) 9 点全 TH → PASS
B3s    600x900  吸附相最大重叠 = 0px，重叠位置 0 个 → PASS(重叠=0)
```
→ **PASS（D-1 已修）**。判据落在「表头已吸附且表体仍在视口内」的 14 个滚动位置上，两档全 0 重叠；`--ui-topbar-h` 是从 token 算出来的（`calc(--sp-2*2 + 12px + --ui-hair*3 + --fs-1*1.6)` = 51.8），解析值与 `.topbar` 渲染高度差 0.0px，不是写死像素。
截图（视口实拍，`python .tmp_build/t2_b3_shots.py`）：`.tmp_build/shot_b3v_stuck_1280.png`、`shot_b3v_stuck_600.png` —— 表头「属性 | 值」整行在顶栏之下，蓝色下划线完好；对比上一轮 `shot_a14c_top.png`（表头被压到 14px）。

#### B4 · 打印（`a15` / `a15b` + `f2`）

```bash
A15    打印前 overlay=True
A15    print 媒体下：overlay=none sidenav=none topbar=none sweep=none topbar::before=none bodyBg=rgb(255, 255, 255)
A15b   print：注入 overlay display=none；sidenav=none crumbs=none toggle=none
A15b   print：.topbar display=none 背景=rgb(6, 8, 12) 边框=1px rgb(35, 43, 56) 高度=0 矩形=[0, 0, 0]
A15b   print+系统暗：topbar 背景=rgb(6, 8, 12)（body=rgb(255, 255, 255)）
f2a    print(系统暗=True)：.topbar display=none 矩形[top,h]=[0, 0] body底=rgb(255,255,255) → P2-B 判定=PASS
f2b    print(系统暗=True)：同上 → P2-B 判定=PASS
```
→ **PASS（D-2 已修）**：`display` 计算值 `none`、矩形高 0（上一轮 `display=flex`、矩形 `[0,17,17]`）。截图 `shot_a15b_print_dark.png` 顶部为纯白，上一轮同位置的 17px 深色条消失。

#### B5 · hero 主路径（`a6` / `a7` / `a8`）

```bash
A6     首点 1014 dispatchEvent 返回=False intercepted=True
A6     t≈60ms  overlay={'state': 'enter', 'ariaHidden': 'true', 'imgs': 2, 'sil': False,
                        'stats': ['属性风', '命途毁灭', '星级五星']} storage=["1014"]
A6     t≈310ms overlay.state={'state': 'hero', ...}    → 跳过阶段正常
A6     t≈1150ms url=1014.html overlay=False
A7     新载入 storage=["1014"]；二次点 1014 返回=True intercepted=False overlay=None
A7     t≈500ms url=1014.html storage=["1014"]          ← 不重播、不改写
A8     matchMedia reduce = True
A8     点 1014 返回=True intercepted=False overlay=None storage=None
A8     t≈600ms url=1014.html overlay=False storage=None ← 不播、不写 sessionStorage
```
→ **PASS**：三条路径与设计一致（首点播报+记账+840ms 级跳转；二点直跳；reduce 直跳不记账）。
A6 的 `坏请求=['404 http://127.0.0.1:8899/favicon.ico']` 属既有 D-5（仓库无 favicon），与修复无关。

#### B6 · 单旋钮（`f4`）

```bash
f4     默认：--hero-total=840ms  --hero-stagger=calc(840ms / 21)
f4       默认 .hero-frame   name=heroFrameIn, heroSettleIn dur=0.24s, 0.12s delay=0.16s, 0.72s
f4       默认 .hero-sweep   dur=0.16s delay=0.56s
f4     改成 --hero-total=1200ms 后：
f4       .hero-frame  delay=0.228571s, 1.02857s
f4       .hero-sweep  dur=0.228571s delay=0.8s
f4       .hero-name   delay=0.371429s     .hero-br-br delay=0.4s
f4       .hero-stat1/2/3 delay=0.457143s, 0.514286s, 0.571429s
f4     首帧 delay 160.0 → 228.571（理论 228.571 = 1200×160/840，误差 0.000ms）
f4     P1-E 判定=PASS
```
→ **PASS**：只改一个自定义属性，整套 21 步节奏等比缩放；误差 0.000 ms（判据 ≤1 ms）。默认值仍等于旧的 840ms 字面量，未改变既有观感。

#### B7 · reduced-motion 保险（`f5`）

```bash
f5     CSSOM：@media(prefers-reduced-motion:no-preference) 内含关键帧 10 个 =
       ['axisGrow','heroBackIn','heroWipeIn','heroSpineIn','heroArtIn','heroFrameIn',
        'heroNameIn','heroStatIn','heroSweepIn','heroSettleIn']
f5     CSSOM：同块内含 hero 规则 17 条 = ['.mv','.timeline .tl','.timeline .tl::before',
       '.hero-overlay','.hero-frame','.hero-br-tl','.hero-br-tr','.hero-br-bl','.hero-br-br',
       '.hero-spine','.hero-art-wrap','.hero-name','.hero-stat:nth-child(1..3)','.hero-sweep','.hero-hint']
f5     no-preference：frame:heroFrameIn, heroSettleIn name:heroNameIn sweep:heroSweepIn overlay:heroBackIn, heroWipeIn stat1:heroStatIn
f5     reduce：frame:none name:none sweep:none overlay:none spine:none stat1:none hint:none
f5     P2-C 判定=PASS
```
→ **PASS（D-3 已修）**：hero 段 17 条规则 + 10 个关键帧已整体包进 `@media (prefers-reduced-motion: no-preference)`（`style.css:644`），与既有动效段同构；reduce 下 9 组元素 `animation-name` 全 `none`，no-preference 下全部非 `none`。

#### B8 · 深色主题对比度（本轮补测）

探针 `.tmp_build/t2_b8_dark.py`（新增，零依赖 CDP）：系统暗 + `data-theme=dark` 双确认，token 用「临时元素吃 `var()` 再读 computed」的方式取真值（不是抄源码字面量），半透明衬底按 alpha 合成后计算，公式用 WCAG 相对亮度。

```bash
$ python .tmp_build/t2_b8_dark.py dark darkall hover   # 日志 .tmp_build/r2_b8_run.log
B8  主题：data-theme=dark 系统暗=True；body 底=rgb(6, 8, 12)
B8  token：--ui-mute=rgb(124, 135, 152)  --ui-bg=rgb(6, 8, 12)  --ui-panel=rgb(12, 17, 23)
        --ui-panel-2=rgb(18, 25, 38)  --ui-surface=rgba(255,255,255,0.043)
        --ui-surface-2=rgba(255,255,255,0.086)
B8  ① --ui-mute / --ui-bg       = #7C8798 on #06080C → 5.513:1 PASS
B8  ② --ui-mute / --ui-panel    = #7C8798 on #0C1117 → 5.212:1 PASS
B8  ③ --ui-mute / --ui-panel-2  = #7C8798 on #121926 → 4.843:1 PASS
B8  ④ --ui-mute / hover 衬底(实测 a.ccard::hover::after) → 4.843:1 PASS
B8h 强制 :hover（matches(':hover')=True）卡片 ::after 衬底 = rgb(18, 25, 38)，描边 ::before=rgb(111, 227, 255)
B8h hover 态：.csub(--ui-mute) 对 ::after 衬底 #121926 → 4.843:1 PASS
```

四组数值（B8 必测口径）：

| 衬底 | token | 实测 RGB | 对比度 | 判 |
|---|---|---|---|---|
| `--ui-bg` | `#06080C` | `rgb(6, 8, 12)` | **5.513:1** | PASS |
| `--ui-panel` | `#0C1117` | `rgb(12, 17, 23)` | **5.212:1** | PASS |
| `--ui-panel-2` | `#121926` | `rgb(18, 25, 38)` | **4.843:1** | PASS |
| hover 衬底（真 `:hover` 的 `.ccard::after`） | `--ui-panel-2` | `rgb(18, 25, 38)` | **4.843:1** | PASS |

补充：把「全站真实 `--ui-mute` 文字」按其**祖先背景链**合成后逐类算对比度（面板页 / 详情页 / 首页三页，共 23 类）：

```
面板页 角色.html：9 类，最差 B.（5.13:1），不达标 0
  DIV.meta / 底=#111316 → 5.13   .csub ×94 / 伪元素衬底 #0C1117 → 5.21
  NAV.crumbs . P.cp-meta . SPAN.cp-count . footer → 5.51   SPAN.cp-label(11px) → 5.51
角色详情 1014.html：5 类，最差 5.13:1，不达标 0
首页 index.html：9 类，最差 SPAN.c|#0C1117（5.21:1），不达标 0
```
→ **PASS**：四组全部 ≥4.5，且没有一类真实 `--ui-mute` 文字落在不达标衬底上。浅色侧（P1-1 修复）同时复测：`mute #55606F` 对 bg/panel/panel-2/hover = **5.75 / 6.39 / 5.34 / 5.34**（`f_issue13_probe.py f3` 判定 PASS）；对照 `docs/reviews/site-hero.md` 记录的旧值 `#6B7484`（4.24 / 3.94 / 3.53）全部脱险，我的独立复算与其数字一致（暗色 5.51/5.21/4.84 vs 我 5.513/5.212/4.843）。

#### B9 · 回归不倒退（`a11` / `a17` / `a18`）

```bash
A11    viewport=600 docScrollWidth=600 bodyScrollWidth=600 无溢出=True cgrid列数=5
A11    越界元素(前5)=[]
A17    1511 intercepted=True overlay.imgs=0 剪影=True 数据条=['属性量子','命途欢愉','星级五星'] 坏请求=[] → url=1511.html
A17    1503 … imgs=0 剪影=True 坏请求=[] → 1503.html
A17    1513 … imgs=0 剪影=True 坏请求=[] → 1513.html
A17    1512 … imgs=0 剪影=True 坏请求=[] → 1512.html
A18    角色面板页 console.error/异常=0 []
A18    首页 console.error/异常=0 []
```
→ **PASS**：600×900 仍无横向溢出（`cgrid` 5 列）；四个无立绘角色仍是剪影降级、0 张 `<img>`、0 坏请求；控制台 0 error（favicon 404 仍是既有 Log 级 D-5）。

#### B10 · 体积（gzip-9，基线取 `git show HEAD:`）

```bash
$ python - <<'EOF'   # 口径：gzip.compress(data, 9) 字节数差
file                                HEAD raw   now raw     d_raw  HEAD gz   now gz     d_gz
wiki/assets/style.css                  18133     44945    +26812     5465    12595    +7130
wiki/assets/character-panel.js          2148     14402    +12254     1072     5577    +4505
wiki/assets/theme.js                    1581      1581        +0      831      831       +0
wiki/assets/app.js                      5932      5932        +0     2783     2783       +0
TOTAL                                                     +39066                     +11635
d_gz KB=11.36  d_raw KB=38.15
```
→ **PASS**：gzip 增量 **11.36 KiB ≤ 30 KB**；raw 增量 38.15 KiB（记录备查，静态托管实际走压缩，口径同上一轮 U1）。

### 本轮新发现（均 P2，不阻断）

**P2-A（口径风险）`--ui-mute` 若压在 `--ui-surface-2` 叠层上只有 3.81:1。**
`--ui-surface-2`（`rgba(255,255,255,.086)`）合成到 `--ui-panel-2` = `#262D39`，`#7C8798` 对其为 **3.814:1（<4.5）**；合成到 `--ui-panel` = **4.217:1（<4.5）**。
现实可达性：`--ui-surface-2` 只用于 `.sidenav li.cur a` 与 `code`（`style.css:121/523`），两者正文用 `--ui-ink`，**当前没有任何 `--ui-mute` 文字落在 surface-2 上**（三页 23 类扫描可证），故 B8 判 PASS。
风险：将来若把 `--ui-mute` 文字（如 `.csub`/`.cp-label`）放进 surface-2 叠层，会直接跌破 4.5。若 Lead 的「hover 衬底」口径取「token 理论合成」而非「实测可达衬底」，则 B8 第 ④ 组 = 3.81，本轮改判 **1 条 FAIL**，需 Coder 把 mute 提到约 `#8B96A8` 或把叠层降到 α≤.05。**请裁定口径。**

**P2-B（固有行为，非 D-1）表体滚出视口时表头会被顶栏盖住。**
步长 40px 遍历第一张表：吸附相 14 个位置重叠全 0；当**表底升到视口内 60px 以内**（整表离场）时，`th` 被容器底推走，重叠峰值 51.8px（1280：scrollY≈1889，`th=-5.8..59.9`；600：scrollY≈1469，`th=-6.4..59.4`）。
判读：此时表头随自己的表格一起离场、下方已无该表内容可标注，属 sticky 到容器底的固有行为，不影响可读性；但上一轮 HEAD 的 `.topbar` 非 sticky，所以「离场瞬间被顶栏压住」确实是本次视觉重构带来的新观感。截图：`shot_b3v_exit_1280.png`、`shot_b3v_exit_600.png`。若要彻底消除，可让 `.topbar` 在表格离场时不遮挡（如 `thead th` 与 `.topbar` 同 z 序时改用 `background-clip` 或给 topbar 加透明间隙），建议下一轮再评估。

### 未决（需 Lead 裁定）

| # | 问题 | 我的实测 | 建议 |
|---|---|---|---|
| V1 | B8「hover 衬底」按实测可达衬底（4.84 PASS）还是按 token 理论合成（3.81 FAIL） | 两种都给了数值；实际无 mute 文字落在 surface-2 | 建议取「实测可达」→ 本轮全 PASS；把 P2-A 记成下一轮的 token 约束 |
| V2 | 续表 P2-B 是否要修 | 离场瞬间峰值 51.8px，仅表底 60px 内出现 | 建议记为 P2 观察，不退回 |
| V3 | 上一轮 U1（A16 体积口径：raw 38.15 KiB / gzip 11.36 KiB） | 本轮 gzip 增量 11.36 KiB | 建议按 gzip 判 PASS，与 A16 口径统一 |

### 第二轮可复跑清单

```bash
cd /g/HSR && python -m http.server 8899 --bind 127.0.0.1      # 起站（后台）
PYTHONUTF8=1 python tools/verify_site.py                        # B1
PYTHONUTF8=1 python wiki/build_wiki.py                          # B2
python .tmp_build/t_tester_probe.py a14 a14b a14c a15 a15b      # B3/B4（旧探针）
python .tmp_build/t_tester_probe.py a6 a7 a8 a11 a17 a18        # B5/B9
python .tmp_build/f_issue13_probe.py f1 f2 f4 f5                # B3/B4/B6/B7（Coder 探针，独立复核）
python .tmp_build/f_issue13_probe.py f3                         # P1-1 浅色对比度
python .tmp_build/t2_b8_dark.py dark darkall hover sticky        # B8 + B3 相位扫描
python .tmp_build/t2_b3_shots.py                                # B3 视口截图
```

| 产物 | 路径 |
|---|---|
| 日志 | `.tmp_build/r2_b1_verify.log`、`r2_b2_build.log`、`r2_fprobe.log`、`r2_tprobe_a14a15.log`、`r2_tprobe_b5b9.log`、`r2_b8_run.log`、`r2_b3_shots.log` |
| 截图 | `shot_b3v_stuck_1280.png`、`shot_b3v_stuck_600.png`、`shot_b3v_exit_1280.png`、`shot_b3v_exit_600.png`、`shot_b8_dark_panel.png`、`shot_b8_dark_hover.png`、`shot_b8_dark_角色.png`、`shot_b8_dark_首页.png`、`shot_a15b_print_dark.png` |
| 探针 | `.tmp_build/t2_b8_dark.py`、`.tmp_build/t2_b3_shots.py`（本轮新增，均只读） |

### 边界声明（第二轮）

- 未修改 `wiki/assets/*`、生成器、数据；复测前后 `git status --porcelain` 集合一致（仍只有 Coder 的 `style.css` / `character-panel.js` 两个 M 与 docs 未跟踪项）。唯一产品级写盘仍是本文件。
- 浏览器为 Chromium 内核 Edge 157 headless，通过 CDP `Emulation.setDeviceMetricsOverride` / `setEmulatedMedia` / `CSS.forcePseudoState` 驱动；无 jsdom、无桩。
- 未覆盖：真实打印纸面（用 `Emulation.setEmulatedMedia(print)` 代替）、真 iOS Safari 的 `clip-path` 行为、`prefers-contrast: more` / `forced-colors` 实机。
