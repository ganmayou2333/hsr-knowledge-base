# HSR 多语言数据索引

> 生成时间：2026-08-31 ｜ **最近复核：2026-10-02（Lead 实测，含 4.6 三类库与剧情文本口径）**
> 语言：en_us（英语）/ zh_tw（繁体中文）/ ja_jp（日语）/ ko_kr（韩语）
> 数据源：StarRailRes index_new 官方 JSON（cn 基准 → 各语言回填）

## en_us（合计 **5,851**）

| 分类 | 文件数 |
|---|---|
| character | 94 |
| lightcone | 170 |
| relic | 60 |
| items | 3506 |
| simulated | 1843 |
| quest | 170 |
| worldview | 8 |
| **合计** | **5,851** |

## zh_tw（合计 **5,845**）

| 分类 | 文件数 |
|---|---|
| character | 93 |
| lightcone | 169 |
| relic | 60 |
| items | 3505 |
| simulated | 1843 |
| quest | 167 |
| worldview | 8 |
| **合计** | **5,845** |

## ja_jp（合计 **5,845**）

| 分类 | 文件数 |
|---|---|
| character | 93 |
| lightcone | 169 |
| relic | 60 |
| items | 3505 |
| simulated | 1843 |
| quest | 167 |
| worldview | 8 |
| **合计** | **5,845** |

## ko_kr（合计 **5,842**）

| 分类 | 文件数 |
|---|---|
| character | 93 |
| lightcone | 169 |
| relic | 60 |
| items | 3502 |
| simulated | 1843 |
| quest | 167 |
| worldview | 8 |
| **合计** | **5,842** |

## 汇总

- 4 语言合计 **23,383** 个 `.md`（实测 2026-10-02；口径 = 各语言目录下全部 `.md`，与 README 镜像行一致）
- **口径说明**：合计 = `character + lightcone + relic + items + simulated + quest + worldview`，经逐语言复算**完全自洽**（2026-10-02 复核）
- 覆盖口径：按实体 ID 校验，character 98.9% / lightcone 100% / relic 96.8% / items 100% / blessing 100% / event 100%
- 未覆盖：真珠(7935)、遗器 133/134（官方 JSON 未收录）；乐园漫记/惊世奇迹 150 项（米游社 WIKI 手工数据，无官方 JSON）
- 生成脚本：temp/multilang_gen_p0.py（角色/光锥/遗器）、temp/multilang_gen_p1.py（物品/模拟宇宙）

## 待建镜像（4.6 新增类别，**实测刷新 2026-10-02**）

以下类别为 `格式规范与要求.md v1.13` 新增，**仅 zh_cn/ 有详情，四语言镜像全部待建**（口径 = 逐语言目录递归 `.md` 计数，实测命令见 `.tmp_build/lang_coverage.py`）：

| 类别 | zh_cn | en_us | zh_tw | ja_jp | ko_kr | 备注 |
|---|---|---|---|---|---|---|
| `events/` | **7** | 0 | 0 | 0 | 0 | 活动库 |
| `stages/` | **3** | 0 | 0 | 0 | 0 | 关卡库（含索引） |
| `rules/` | **5** | 0 | 0 | 0 | 0 | 规则库 |
| `货币战争/` | **7** | 0 | 0 | 0 | 0 | 玩法库 |
| `enemies/` | **0（目录不存在）** | — | — | — | — | 敌人库**从未建立**（2026-10-02 实测） |
| **合计待建** | **22** | **22** | **22** | **22** | **22** | 共需 **88** 个镜像文件 |

> 另：主类目的部分缺失（character 118→94/93、items 3876→3506/3505/3502、lightcone 205→170/169、quest 173→170/167、relic 65→60、simulated 2168→1843）属**既有设计**——4.6 新实体在 SRR `index_new`（停在 v4.5）中无官方本地化名，故未建；口径见 `multilang_coverage_report.md`。

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-10-02 | **实测刷新本节**：原写「events 1 条 / stages 1 条」为过时值，实测 **events 7 / stages 3 / rules 5 / 货币战争 7 = 22 个 zh_cn 文件待建镜像（88 个镜像文件）**；补记 `enemies/` 目录不存在；来源 = `.tmp_build/lang_coverage.py` 实测 |
| 2026-10-02 | 全量复核为实测值；合计口径自洽；W-4.6-19 剧情文本表达撤下后各语言 quest 计数不变（文件保留、内容改写） |
