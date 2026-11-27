# 知识库规模真值表（`docs/metrics.md`）

> **本文件由 `scripts/gen_metrics.py` 自动生成，请勿手工编辑。**
> 生成时间：`2026-11-28 02:09:01`
> 重新生成：`python scripts/gen_metrics.py`（幂等：除上一行时间外，两次运行输出逐字节相同）
> 校验：`python tools/verify_site.py` 的 `[16]` 项解析本文末尾的**机器可读真值**，
> 与 `README.md` · `docs/README_{en,ja,ko,zh-Hant}.md` · `docs/仓库结构.md` 出现的规模数字逐项比对。

---

## 一、口径（读数字前必看）

| 指标 | 口径 | 实测命令 |
|---|---|---|
| **入库数** | `git ls-tree` 口径：生成时 `HEAD` 提交中的文件。CI 与线上内容取决于各自检出和部署的提交。 | `git ls-tree -r --name-only HEAD -- <lang> \| grep -c '\.md$'` |
| **工作区数** | 本地磁盘实际文件数，**含实际存在的 gitignore 文件，例如 `*/quest/剧情文本/`**（D-020/D-025 合规撤下、不入库）。 | `find <lang> -name '*.md' \| wc -l` |
| **详情文件** | 含 `> 实体ID：` 元信息，且排除「文件名 == 上级目录名」的索引 / 分组文件与类别主索引（D-048 / D-061 / D-067）。 | `cd zh_cn && python ../scripts/verify_fields.py` |
| **页面数** | `zh_cn/` 每个 `.md` 一页；构建产物反映构建时工作区，不一定是生成统计时的工作区。 | `python wiki/build_wiki.py` |

> **对外报数一律用「入库数」**（D-068）：文档若写工作区数，必须在括注中写明口径与差值来源，
> 否则会出现「文档比线上多 167 个文件」的失真。

---

## 二、总览

| 指标 | 值 | 说明 |
|---|---|---|
| `zh_cn` 页面数（静态站） | **6,679** | `wiki/data/stats.js` 的 `pages`（构建时快照）；统计时工作区 `.md` 数 6,679 |
| `zh_cn` 入库 `.md` | **6,679** | 工作区 6,679，与 HEAD 数量差 0；原因需逐项核对 |
| `zh_cn` 详情文件数 | **6,141** | 详情口径合计（各分类之和见 §四） |
| 库内最高数据版本 | **4.7** | `stats.js` 的 `latestVersion` |
| `verify_fields` 异常 | **0** | 要求 0 |
| `verify_fields` 已知待补充 | **156** | 已知状态，不计异常 |
| 站点死链 | **0** | `link_report.json` 的 `dead`，要求 0 |

---

## 三、五语规模（入库 / 工作区）

| 语言目录 | 入库 `.md` | 工作区 `.md` | 数量差（工作区 − HEAD） |
|---|---|---|---|
| `zh_cn/` | 6,679 | 6,679 | 0 |
| `en_us/` | 5,722 | 5,722 | 0 |
| `zh_tw/` | 5,715 | 5,715 | 0 |
| `ja_jp/` | 5,717 | 5,717 | 0 |
| `ko_kr/` | 5,700 | 5,700 | 0 |

> 数量差是两个计数之差，并非未入库文件数；忽略或未跟踪文件、工作区删除等均可能影响差值。`*/quest/剧情文本/` 的处理见 D-020、D-025。
> 镜像四语入库均值 5,713.5，十位取整 **各约 5,710**（README 括注口径）。

---

## 四、各类详情文件数（`zh_cn`，详情口径）

| 类别 | 详情数 | 目录 |
|---|---|---|
| 角色库 | **94** | `character/` |
| 光锥库 | **172** | `lightcone/` |
| 物品库 | **3,829** | `items/` |
| 遗器库 | **64** | `relic/` |
| 模拟宇宙库 | **1,793** | `simulated/` |
| 活动库 | **12** | `events/` |
| 敌人库 | **155** | `enemies/` |
| 关卡库 | **2** | `stages/` |
| 音乐库 | **20** | `音乐/` |
| **合计** | **6,141** | 各分类之和 |

**`simulated/` 1,793 的构成**（`verify_fields` 分类口径）：

| 子类 | 数量 |
|---|---|
| 祝福 `blessing` | 906 |
| 奇物 `curio` | 84 |
| 事件 `simu_event` | 384 |
| 区块 `block` | 15 |
| 差分宇宙 `diff` | 404 |

**`relic/` 64 的构成**：隧洞遗器 **34** + 位面饰品 **30**。

**文档型目录**（不含 `> 实体ID：`，详情口径计 **0**）的实际 `.md` 数：

| 目录 | 实际 `.md` |
|---|---|
| `quest/` | 5 |
| `worldview/` | 17 |
| `货币战争/` | 7 |
| `rules/` | 5 |

---

## 五、链接与死链

| 指标 | 值 | 来源 |
|---|---|---|
| 站点页内链接总数 | 97,336 | `wiki/data/link_report.json` 的 `total`（`build_wiki.py` 产物） |
| 站点死链数 | **0** | 同上 `dead`（要求 0） |
| 站点未收录（优雅降级为纯文本） | 30 | 同上 `missing`（合规未入库内容，属预期，不算死链） |
| 全库双链 `[[…]]` 总数 | 23,464 | `scripts/verify_links.py`（扫描 29,684 个 `.md`） |
| 全库双链死链数 | 53 | 同上（含文档里的示例行，故非 0） |
| **数据区**（五语目录）双链死链数 | **0** | 同上；**判据（要求 0）**：非 0 时 `verify_links.py` 退出码为 1 |

> 文档区（`docs/`、`update.md`、`格式规范与要求.md` 等）的死链多为**语法示例**（`[[xxx]]`、`[[页面\|示例]]`），
> 按 D-072 与 `verify_links.py` 口径**不计入**数据区判据。

---

## 六、版本分布（`zh_cn`，`stats.js` 口径）

| 数据版本 | 页面数 |
|---|---|
| 4.7 | 172 |
| 4.6 | 2,488 |
| 4.5 | 3,847 |
| 3.6 | 1 |
| **带版本页合计** | **6,508** |
| 带日期页合计 | 6,679 |

> `stats.js` 生成时刻：`2026-11-28 02:09`。版本分布 ≠ 最新版本：库内绝大多数页面的 `> 数据版本：` 仍是收录时的版本。

---

## 七、校验状态

| 校验器 | 命令 | 结果 |
|---|---|---|
| `verify_fields` | `cd zh_cn && python ../scripts/verify_fields.py`（**必须在 `zh_cn` 下运行**） | 扫描 6,679 个 `.md`；详情 6,141；异常 **0**；已知待补充 **156** |
| `verify_links` | `python scripts/verify_links.py`（仓库根） | 双链 23,464；死链 53（其中数据区 **0**） |
| `verify_site` | `python tools/verify_site.py`（仓库根） | `[1]`–`[16]` 全 PASS；`[16]` 即比对本文真值 |

---

## 八、机器可读真值（`tools/verify_site.py` 的 `[16]` 解析本节）

> 格式固定：每行 `| \`<key>\` | <值> |`。改动本节会使 `[16]` 失配 —— 请改 `gen_metrics.py` 重新生成。

| key | value |
|---|---|
| `pages` | 6,679 |
| `md_commit_zh_cn` | 6,679 |
| `md_worktree_zh_cn` | 6,679 |
| `md_commit_en_us` | 5,722 |
| `md_worktree_en_us` | 5,722 |
| `md_commit_zh_tw` | 5,715 |
| `md_worktree_zh_tw` | 5,715 |
| `md_commit_ja_jp` | 5,717 |
| `md_worktree_ja_jp` | 5,717 |
| `md_commit_ko_kr` | 5,700 |
| `md_worktree_ko_kr` | 5,700 |
| `detail_total` | 6,141 |
| `detail_character` | 94 |
| `detail_lightcone` | 172 |
| `detail_items` | 3,829 |
| `detail_relic` | 64 |
| `detail_simulated` | 1,793 |
| `detail_events` | 12 |
| `detail_enemies` | 155 |
| `detail_stages` | 2 |
| `detail_music` | 20 |
| `relic_cavern` | 34 |
| `relic_planar` | 30 |
| `doctype_quest` | 5 |
| `doctype_worldview` | 17 |
| `doctype_货币战争` | 7 |
| `doctype_rules` | 5 |
| `link_total` | 97,336 |
| `link_dead` | 0 |
| `link_missing` | 30 |
| `wikilink_total` | 23,464 |
| `wikilink_dead` | 53 |
| `wikilink_dead_data` | 0 |
| `wikilink_files` | 29,684 |
| `vf_issue` | 0 |
| `vf_known` | 156 |
| `mirror_commit_avg_round10` | 5,710 |
| `mirror_gap` | 0 |
| `versioned_pages` | 6,508 |
| `dated_pages` | 6,679 |
| `labeled_nonofficial_en_us` | 5,689 |
| `labeled_nonofficial_zh_tw` | 5,711 |
| `labeled_nonofficial_ja_jp` | 5,678 |
| `labeled_nonofficial_ko_kr` | 5,675 |
| `version_4.7` | 172 |
| `version_4.6` | 2,488 |
| `version_4.5` | 3,847 |
| `version_3.6` | 1 |

*本文件由 `scripts/gen_metrics.py` 生成；口径争议以 `docs/prompts/决策记录.md` 的 D-048 / D-062 / D-068 为准。*
