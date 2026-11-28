# HSR 静态 Wiki

零依赖静态站，`file://` 可直接打开 `index.html`。

## 本地预览

直接双击 `wiki/index.html`，或：

```powershell
# 重新生成
python wiki/build_wiki.py
```

## 目录

- `index.html` 首页（搜索 + 导航）
- `assets/` 样式与脚本
- `build_wiki.py` 生成器（扫描 `data/zh_cn/` 全量 md）
- `pages/`（生成物，已 gitignore）
- `data/titles.js`、`data/link_report.js`（生成物，已 gitignore）

## GitHub Pages

- 站点：https://ganmayou2333.github.io/hsr-knowledge-base/
- `.github/workflows/pages.yml` 在 push 到 `main` 时先运行质量检查，通过后浅克隆 SRR → copy_icons.py → build_wiki.py 并发布。PR 也运行相同的质量检查；是否阻止合并取决于仓库的保护规则。
- 首次需在仓库 Settings → Pages 选 GitHub Actions 来源。
- 图标当前在构建时从 StarRailRes 拉取，**不随仓库分发**。StarRailRes 的目标用途为**核验**图标引用；该变更尚未落到 `copy_icons.py` 与 `pages.yml`。

## 搜索与检查

- 搜索索引由构建脚本生成，包含标题、路径和每篇正文开头最多 240 字的可读摘要；摘要之外的正文不会命中。无需网络，支持 `file://`；禁用 JavaScript 时仍可浏览分类和正文。
- 2026-11-20 本地完整数据集生成的 `titles.js` 为 2,096,808 字节；文件大小随收录内容变化，干净检出可能不同。
- 以下命令在仓库根目录执行；`check_quality.py` 对已记录的数据区失效链接使用精确基线，新增失效链接或字段异常会失败。修复基线中的链接后，应同时更新基线。

```powershell
python wiki/build_wiki.py
python tools/check_quality.py
python tools/verify_site.py
python tools/verify_docs.py
python -m unittest tools.test_wiki_search tools.test_quality_gate tools.test_preview_review tools.test_preview_review_server tools.test_preview_artifact tools.test_package_preview tools.test_preview_bundle tools.test_stage_preview tools.test_trusted_quality tools.test_preview_catalog tools.test_reconcile_previews tools.test_preview_release tools.test_verify_preview_publication -v
node --check wiki/assets/app.js
node --check wiki/assets/home.js
node --check preview_shell/shell.js
node --check preview_shell/frame.js
$env:WIKI_BROWSER = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
node tools/test_preview_browser.mjs
node tools/test_preview_browser.mjs --external
node tools/test_preview_browser.mjs --transient-object
node tools/test_preview_browser.mjs --service
node tools/test_preview_browser.mjs --service --service-initial-failure
node tools/test_preview_wiki.mjs
node tools/test_wiki_browser.mjs
```

浏览器检查需要 Node.js 22 或更新版本与 Chrome/Edge，路径按本机安装位置调整。它使用 `file://` 检查 1280×800、600×900 和 390×900 视口、正文摘要检索、键盘打开、减少动态效果及禁用 JavaScript 后的浏览。
真实 Wiki 预览检查需要先生成站点并复制图标；PR 自动检查会准备这些素材。

`preview_shell/` 和 `tools/preview_bundle.py` 是隔离预览的实验性组件，尚无可信发布流程，不应直接部署为公开预览。浏览器测试覆盖隔离、主动跳转、基本导航和过期隐藏；外层内容安全策略限制框架跳转，已在 Chromium 内核浏览器验证。正式发布前仍需验证目标浏览器兼容性并完成发布流程与安全审查。

`python -m tools.stage_preview OWNER/REPO PR编号 构建运行编号 输出目录 --trusted-run 独立检查运行编号` 可将指定 PR 的检查产物转换成仅含 JSON 的新本地目录。必须从独立可信的检出运行；它要求独立数据检查与当前 PR 版本匹配，该检查已在 GitHub 默认分支启用，但尚未接入最终发布；外部 fork 的运行关联仍需解决。转换后的目录不会自动发布，也不能代替实时状态校验、清理和外部 PR 的完整安全审查。

`python -I /可信检出/tools/trusted_quality.py /只读PR检出` 使用可信检出的数据检查脚本和基线检查 PR 数据。应在无发布凭据、资源受限的环境运行，且检查期间 PR 检出不可被修改；该检查器尚未接入可信发布流程，不能单独作为预览发布授权。

`python -m tools.preview_catalog OWNER/REPO 预览输入目录 可信页面目录 输出目录` 能将多个已暂存预览组装到新的本地目录；已关闭或过期的 PR 不会出现在新目录中。输入按 PR 编号分目录，输出目录必须不存在。它只组装，不执行部署或定期清理；上线仍需要可信发布、状态刷新与清理触发机制。

组装时会尝试从可信环境生成审核快照。静态页面只有在快照未满 15 分钟、提交一致且 GitHub 当前审核记录与快照一致时才显示「已有人工批准（快照，可能延迟）」；请求失败、快照过期或记录变化时显示未经人工审查。审核者权限变化可能在快照到期前滞后；15 分钟是有效期上限，不保证刷新频率。自动发布尚未部署，因此不能认为审核状态同步已完成。

`python -m tools.preview_review_server OWNER/REPO --site 已组装目录` 提供实验性的预览页面和只读审核接口，默认仅监听本机。上线需要同源 HTTPS 反向代理及限流；服务只使用可查询审核者权限的只读 GitHub 凭据，不得持有发布凭据。此服务尚未部署，GitHub Pages 本身不能运行它。

独立数据检查与公开预览的剩余接入条件见 [预览运行说明](../docs/preview-operations.md)。

---

## 素材范围与署名

- 本站**仅发布 `icon/**` 图标**（头像 / 立绘 / 光锥 / 遗器 / 物品 / 奇物），**不发布**游戏字体与 `image/**` 高清大图。
- 图标当前在构建时从 [StarRailRes](https://github.com/Mar-7th/StarRailRes)（AGPL-3.0）拉取，**不随仓库分发**。StarRailRes 的目标用途为**核验**图标引用；该变更尚未落到 `copy_icons.py` 与 `pages.yml`。
- 页脚须保留：`© 米哈游版权所有 · 非官方非商业同人整理 · AGPL-3.0（仅覆盖代码与编排）· 图标来自 StarRailRes`。
