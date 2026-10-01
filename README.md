# 崩坏：星穹铁道 · 数据知识库（HSR）

> **语言 / Languages：** [简体中文 (zh-Hans)](README.md) · [繁體中文 (zh-Hant)](docs/README_zh-Hant.md) · [English (en)](docs/README_en.md) · [日本語 (ja)](docs/README_ja.md) · [한국어 (ko)](docs/README_ko.md)

基于 **Obsidian** 的《崩坏：星穹铁道》数据知识库，系统整理角色、光锥、物品、遗器、模拟宇宙、剧情文本、世界观等游戏数据与资料，页面间通过双链（wikilink）关联，支持结构化检索与快速跳转。除简体中文外，另提供英文 / 繁体中文 / 日文 / 韩文多语言镜像。

> 数据版本基线：4.6（4.6 内容收录：2026-09-28；文档口径统一：2026-09-30；含新角色真珠、新光锥献给明日的色彩、新遗器戏梦点星的伶人 / 贪噬禁果的异端）

---

## 内容结构

| 目录 | 内容 | 规模（详情文件） |
|---|---|---|
| `zh_cn/` | **简体中文基准库**（角色/光锥/物品/遗器/模拟宇宙/剧情/世界观/规则/货币战争/活动/关卡） | ≈6,693 |
| `character/` | 角色库（按 9 大命途归档，四级索引） | 93 |
| `lightcone/` | 光锥库（按命途归档，四级索引） | 170 |
| `items/` | 物品库（按用途分类，四级索引） | 3,823 |
| `relic/` | 遗器库（隧洞遗器 / 位面饰品） | 62 |
| `simulated/` | 模拟宇宙库（祝福 / 奇物 / 事件 / 区块 / 差分宇宙） | 1,793 |
| `quest/` | 剧情文本库（主线 / 同行 / 冒险任务） | 167 |
| `worldview/` | 世界观库（星神 / 势力 / 地点 / 术语 / 人物关系） | 8 |
| `货币战争/` | 货币战争库（独立自走棋玩法：玩法 / 角色 / 羁绊 / 装备 / 赛季） | 7 |
| `rules/` | 规则库（通用战斗逻辑 / 状态优先级 / 异常特例） | 5 |
| `events/` | 活动库（版本活动 / 常驻活动 / 复刻活动，v1.13 新增） | 5 |
| `enemies/` | 敌人库（普通 / 精英 / 首领 / 周本BOSS，v1.13 新增，暂无详情） | 0 |
| `stages/` | 关卡库（侵蚀隧洞 / 历战余响 / 凝滞虚影 / 材料关卡，v1.13 新增） | 1 |
| `en_us/` `zh_tw/` `ja_jp/` `ko_kr/` | 多语言镜像（英文 / 繁体中文 / 日文 / 韩文，镜像 zh_cn 数据） | 各约 5,840 |
| `wiki/` | **静态 Wiki 站点**（模板 + 生成器；`pages/`、`data/`、`assets/icons/` 为生成物，不入库） | 6,693 页 |
| `mcp/`（已迁出） | MCP 只读工具层**已抽出为独立项目**：[obsidian-kb-mcp](https://github.com/ganmayou2333/obsidian-kb-mcp)（profile 驱动、零依赖） | — |
| `docs/` | 文档（多语言 README / 数据来源 / 报告 / 提示词系统 / 待补充清单） | — |
| `scripts/` | 校验与生成脚本（`verify_fields` / `verify_links` / `compare_srr_ids` 等） | — |

> 以上 `character/`~`stages/` 均位于 `zh_cn/` 下（`zh_cn/character/` 等）；`wiki/`、`mcp/`、`docs/`、`scripts/`、`temp/` 位于仓库根。索引层级统一为：主索引 → 分类 / 命途索引 → 评级索引（星级） → 详情。规模为详情文件数（不含索引与分组文件）。
> **口径说明**：`zh_cn/` 合计行为 `zh_cn/` 下全部 `.md` 文件数（含索引，实测 2026-10-01 = 6,693）；各分类行为详情文件数（不含索引），故两者不直接相加。

---

## 使用与许可

- 本项目**免费、非商业**，任何人都可自由使用、复制、修改、再分发。
- 许可：**AGPL-3.0**（因派生自 AGPL-3.0 的 StarRailRes，衍生作品须同许可）。
- 游戏素材与文本版权归 **HoYoverse**，依官方同人指引使用；图标不随仓库分发。
- 第三方来源与许可详情见 [NOTICE.md](NOTICE.md)。

---

## 在线 Wiki

- 站点：https://ganmayou2333.github.io/hsr-knowledge-base/ （GitHub Pages 自动构建，push main 即更新）
- 本地预览：`python wiki/build_wiki.py` 后打开 `wiki/index.html`
- 说明：图标在 CI 构建时从 StarRailRes 拉取，**不随仓库分发**；无图标实体显示占位符。

---

## 数据来源

详见 [数据来源.md](数据来源.md)：

- **hsr.nanoka.cc**：角色 / 光锥 / 物品 / 遗器基础数据与详情
- **米游社官方 Wiki**（bbs.mihoyo.com/sr/wiki）：角色百科、遗器来历与获取途径、模拟宇宙命途 / 星级 / 事件文本
- **官网**：官方资料
- **StarRailRes 开源仓库**（github.com/Mar-7th/StarRailRes）：模拟宇宙全量数据（祝福 / 奇物 / 事件 / 区块 JSON）

---

## 使用方式

1. 使用 **Obsidian** 打开本目录作为 vault。
2. 从各库主索引进入，沿「分类 / 命途 → 评级 → 详情」逐级浏览。
3. 角色文件内的材料 / 遗器 / 光锥引用均为双链，可直接点击跳转。
4. 搜索可直接检索角色名 / 物品名 / 光锥名。

---

## 规范与文档

| 文档 | 说明 |
|---|---|
| [格式规范与要求.md](格式规范与要求.md) | 全库格式总纲（目录 / 命名 / 字段 / 双链 / 版本 v1.13） |
| [协作要求与行动准则.md](协作要求与行动准则.md) | 项目协作核心要求与行动准则 |
| [数据来源.md](数据来源.md) | 数据来源、覆盖范围与版权说明 |
| [遗器规则.md](遗器规则.md) | 遗器规则说明 |
| [SRR图包来源.md](SRR图包来源.md) | SRR 全量图包来源说明 |
| [update.md](update.md) | 历次更新日志 |
| [待办清单.md](待办清单.md) | 数据补全与扩展待办 |
| [NOTICE.md](NOTICE.md) | **第三方来源与许可声明**（AGPL-3.0 与各数据源许可状态） |
| [wiki/README.md](wiki/README.md) | 静态 Wiki：本地预览与 GitHub Pages 启用 |
| [obsidian-kb-mcp](https://github.com/ganmayou2333/obsidian-kb-mcp) | **MCP 只读工具层**（已独立成仓：profile 驱动、零依赖、自带冒烟测试） |
| [docs/prompts/README.md](docs/prompts/README.md) | 提示词系统管理总纲 |
| [docs/multilang_index.md](docs/multilang_index.md) | 多语言数据索引（4 语言文件统计） |
| [docs/multilang_final_report.md](docs/multilang_final_report.md) | 多语言最终覆盖率报告 |

---

## 版权声明

- 游戏名称、角色、美术资源及文本版权归 **HoYoverse（米哈游）** 所有，本仓库仅用于**非商业个人用途**，遵循各地区的官方同人/粉丝创作指引。
- **适用地区与指引版本（简体中文标注）**：

| 地区 | 官方指引 | 版本与发布日期 |
|---|---|---|
| 中国大陆 | 《崩坏：星穹铁道》同人衍生作品创作指引 | V1.0（2023-04-17）→ V2.0（2024-08-23）→ **V3.0（2025-07-15，现行）**<sup>[1]</sup> |
| 日本 | 《崩坏：星穹铁道》二次创作指南（miHoYo / COGNOSPHERE） | 现行版（2026-02-21 核验）<sup>[2]</sup> |
| 其他地区（中国大陆与日本以外） | 《Honkai: Star Rail Fan Creations Guide》 | V1.0（2023-04-22）→ **V2.0（2024-08-23，现行；官方明示不适用于中国大陆与日本）**<sup>[3]</sup> |

- 模拟宇宙数据派生自 **StarRailRes**（github.com/Mar-7th/StarRailRes，**AGPL-3.0**）<sup>[4]</sup>，本仓库依此采用 **GNU Affero General Public License v3.0（AGPL-3.0）**，详见 [LICENSE](LICENSE)。
- 其余数据来源见 [数据来源.md](数据来源.md)。
- 第三方图库（StarRailRes_repo/）不纳入版本管理。

> [1] https://www.miyoushe.com/ys/article/66426966
> [2] https://www.niji-guidelines.com/guidelines/honkai-star-rail
> [3] https://hsr.hoyoverse.com/en-us/news/125457
> [4] https://github.com/Mar-7th/StarRailRes/blob/master/LICENSE
