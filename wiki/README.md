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
- `build_wiki.py` 生成器（扫描 `zh_cn/` 全量 md）
- `pages/`（生成物，已 gitignore）
- `data/titles.js`、`data/link_report.js`（生成物，已 gitignore）

## GitHub Pages

- 站点：https://ganmayou2333.github.io/hsr-knowledge-base/
- `.github/workflows/pages.yml` 在 push 到 `main` 时自动浅克隆 SRR → copy_icons.py → build_wiki.py 并发布。
- 首次需在仓库 Settings → Pages 选 GitHub Actions 来源。
- 图标为构建时从 StarRailRes 拉取，**不随仓库分发**。

## 后续扩展

- 全文搜索（目前仅标题/路径模糊匹配）
- 深色/浅色手动切换（目前跟随系统）
- 侧栏目录

---

## 素材范围与署名

- 本站**仅发布 `icon/**` 图标**（头像 / 立绘 / 光锥 / 遗器 / 物品 / 奇物），**不发布**游戏字体与 `image/**` 高清大图。
- 图标在构建时从 [StarRailRes](https://github.com/Mar-7th/StarRailRes)（AGPL-3.0）拉取，**不随仓库分发**。
- 页脚须保留：`© 米哈游版权所有 · 非官方非商业同人整理 · AGPL-3.0（仅覆盖代码与编排）· 图标来自 StarRailRes`。
