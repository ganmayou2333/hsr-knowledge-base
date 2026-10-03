# GitHub Wiki 可行性评估（Lead）

> 建立：2026-10-03 ｜ 触发：用户问「githubWiki 可行性」｜ 结论速览：**作为全库镜像不可行；仅适合做「几十页的策展入口」**

## 一、结论

| 用途 | 可行性 | 理由 |
|---|---|---|
| **全库镜像**（把 `zh_cn` 6,665 页搬进 Wiki） | **不可行** ❌ | 三个独立硬伤：**5,000 文件软上限**、**扁平命名空间重名**、**不被搜索引擎索引** |
| **策展入口**（项目说明 / 许可与合规 / 数据来源 / 贡献指南 / 路线图，几十页） | **可行** ✅ | 页数远低于上限、无重名风险；正文外链到 Pages 主站 |
| 与 **GitHub Pages** 的关系 | Pages 更合适 ✅ | 官方文档在「超出 5,000 文件」与「需要被搜索引擎索引」两种情形下**都明确建议改用 GitHub Pages** |

## 二、官方文档依据（GitHub Docs）

| # | 原文要点 | 出处 |
|---|---|---|
| 1 | 「For performance reasons, wikis have a **soft limit of 5,000 total files**, regardless of file type. If you exceed this limit, **some pages may be inaccessible** to users. If you need a larger wiki, **we recommend using GitHub Pages**.」 | [About wikis](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis) |
| 2 | 「Search engines will only index wikis with **500 or more stars** that you configure to prevent public editing… **If you need search engines to index your content, you can use GitHub Pages in a public repository.**」 | 同上 |
| 3 | 「If you create a wiki in a **public** repository, the wiki is available to the public. If you create a wiki in a **private** repository, only people with access to the repository can access the wiki.」→ **可见性随仓库** | 同上 |
| 4 | 资格规则：**public 仓库 Free 可用；private 仓库需 Pro / Team / Enterprise** → **与 Pages 完全同一规则，无隐私优势** | [About wikis](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis)、[What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) |
| 5 | 链接语法：Markdown 模式用 `[文字](wiki 页完整 URL)`；**MediaWiki 模式**用 `[[页名\|显示文字]]` | [编辑 wiki 内容](https://docs.github.com/zh/communities/documenting-your-project-with-wikis/editing-wiki-content) |
| 6 | MediaWiki 语法**不支持**：**嵌入包含（transclusion）、定义列表、缩进、目录（TOC）** | 同上 |

## 三、本库实测对照

| 项 | 实测 | 对 Wiki 的含义 |
|---|---|---|
| `zh_cn` `.md` | **6,665** | **超 5,000 软上限 33%** → 部分页面**无法访问** |
| 五语言 `.md` 合计 | **30,070**（zh_cn 6,665 / en_us 5,851 / zh_tw 5,867 / ja_jp 5,845 / ko_kr 5,842） | 更不可能 |
| **重名·口径 A（按文件名）** | 唯一 **5,969**；重名 **639 种** → **被吞并 696 页** | Wiki 是**扁平命名空间，无子目录** |
| **重名·口径 B（按 H1 标题）** | 唯一 **5,726**；重名 **697 种** → **被吞并 939 页** | 同上（同页不同文件名/标题也会撞） |
| 应用前缀命名规则后 | 可去重到 **6,665** 个唯一页名（其中 **12** 个需加序号兜底） | **但页数不变 → 仍超上限 1,665 页** |
| 页名长度（前缀规则后） | 中位 **7** 字、最大 **43** 字（个别页名是一整句话） | 超长页名在 Wiki 中不可用/难维护 |
| 现有 Wiki 仓库 | `git ls-remote …/hsr-knowledge-base.wiki.git` → **Repository not found** | 该 wiki **尚未创建/启用** |
| Pages 侧现状 | 纯净检出构建 **6,497 页 / dead 0**、体积 **63.3 MB** | Pages 已有可行方案（D-044） |

> 实测脚本：`.tmp_build/wiki_flat_test.py`（不入库）。**两个口径都列出**，因「文件名」与「H1 标题」重名集合不同，任一口径都足以否决全库镜像。
>
> **计数口径更正（Lead 自我纠错）**：本文件初版写「五语言合计 **89,339**」属**错误**——那是用 `Get-ChildItem -Recurse` 全仓扫描，把 **`.tmp_build\stamp_backup\`（38,330 文件全量快照）** 与 **`.tmp_ci\`（纯净检出）** 里的副本**重复计数**所致。排除副本后的**正确值 = 30,070**（逐目录实测：6,665 + 5,851 + 5,867 + 5,845 + 5,842）。**纪律**：统计语言/类别规模时**必须排除 `.tmp_*` 工作副本**。

## 四、如果仍要用 Wiki（仅策展入口）的注意点

1. **无目录（TOC）**：官方明确不支持，得手写导航（`_Sidebar.md`）。
2. **无模板嵌入**：不能用 transclusion 复用信息框，重复内容只能抄。
3. **重名**：扁平命名空间下页面名必须唯一 → 需加前缀（如 `物品-潮玩礼券`）。
4. **可见性**：想让 Wiki 公开，**仓库必须先公开**（与 Pages 同一个前置条件）。
5. **批量写入**：Wiki 是**独立 git 仓库**，可本地克隆后批量推送（本次探测因 wiki 未创建而未取到远端）。

## 五、建议

**走 GitHub Pages 作为主站**（工作流已就绪、纯净检出 dead 0、体积合规），**Wiki 留空或只放 5–20 页的策展入口**（项目简介 / 许可与合规 / 数据来源 / 如何贡献 / 更新日志），正文链接到 Pages。
