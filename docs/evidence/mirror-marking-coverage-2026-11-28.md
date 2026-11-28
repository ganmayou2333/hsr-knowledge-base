# 四语镜像标记与阅读提示覆盖统计（2026-11-28）

> **用途**：issue #35 验收所需的「标记规则 / 覆盖统计」补充。现有 `scripts/audit_mirror_provenance.py` 统计全库已跟踪镜像的 `本地化来源：非官方` 标记，`tests/test_mirror_reader_notices.py` 直接断言页首阅读提示存在，但没有一份同时按「类别 × 语言」列出**页首提示、非官方标记、部分收录、实体 ID 行**的可复核统计。本文件补上该表。
>
> **基线**：`G:\HSR`，分支 `main`，HEAD `d7e0daf79414e4c080851fdfe3c8c9c230514eb1`。读取 Git 跟踪路径的当前工作区内容；执行时 `git status --porcelain` 另有与本统计无关的 `.gitignore` 修改与未跟踪目录，未提交改动可能影响结果。
>
> **边界**：标记或提示存在只说明页面有可见文字；**不证明**官方原文、字段完整、译文质量或与中文基准同步。未标非官方也不等于官方。

## 一、复核命令

```text
python -X utf8 scripts/audit_mirror_marking_coverage.py
```

脚本为只读：`git ls-files` 取四语 `character` / `lightcone` / `relic` / `events` 的跟踪 `.md`，读取工作区内容。口径：

- **非官方标记**：文件前 8192 字节内含 `本地化来源：非官方`（与 `scripts/gen_metrics.py`、`scripts/audit_mirror_provenance.py` 的标记与字节窗口相同）。
- **页首阅读提示**：首个 `\n---` 之前含本语言提示。角色/光锥/遗器与活动使用两套措辞：英文 `> Reader note:` / `> Reading note:`，韩文 `> 읽기 안내:` / `> 열람 안내:`；繁中、日文两类同字。此两套措辞与 `tests/test_mirror_reader_notices.py` 的断言一致。
- **部分收录**：含 `> 状态：部分收录`。
- **含实体ID行**：含 `> 实体ID：` 行（含「未核实」等非数字写法），用于区分详情与索引。
- 只覆盖上述四类；不包含 `quest`、`worldview`、`items`、`simulated` 等目录，因此数字不能与 `docs/metrics.md` 的 `labeled_nonofficial_*` 或 `audit_mirror_provenance.py` 的 `all` 行直接比较。

## 二、统计结果

| 语言 | 类别 | 已跟踪文件 | 含实体ID行 | 非官方标记 | 页首阅读提示 | 部分收录 | 非官方标记但无页首提示 |
|---|---|---:|---:|---:|---:|---:|---:|
| en_us | character | 94 | 94 | 93 | 94 | 0 | 0 |
| en_us | lightcone | 172 | 172 | 170 | 172 | 0 | 0 |
| en_us | relic | 64 | 64 | 60 | 64 | 2 | 0 |
| en_us | events | 12 | 12 | 6 | 12 | 6 | 0 |
| en_us | 四类合计 | 342 | 342 | 329 | 342 | 8 | 0 |
| zh_tw | character | 94 | 94 | 94 | 94 | 0 | 0 |
| zh_tw | lightcone | 172 | 172 | 171 | 172 | 1 | 0 |
| zh_tw | relic | 64 | 64 | 62 | 64 | 2 | 0 |
| zh_tw | events | 14 | 12 | 13 | 14 | 1 | 0 |
| zh_tw | 四类合计 | 344 | 342 | 340 | 344 | 4 | 0 |
| ja_jp | character | 94 | 94 | 93 | 94 | 0 | 0 |
| ja_jp | lightcone | 172 | 172 | 169 | 172 | 1 | 0 |
| ja_jp | relic | 64 | 64 | 60 | 64 | 2 | 0 |
| ja_jp | events | 12 | 12 | 0 | 12 | 6 | 0 |
| ja_jp | 四类合计 | 342 | 342 | 322 | 342 | 9 | 0 |
| ko_kr | character | 94 | 94 | 93 | 94 | 0 | 0 |
| ko_kr | lightcone | 172 | 172 | 169 | 172 | 1 | 0 |
| ko_kr | relic | 64 | 64 | 60 | 64 | 2 | 0 |
| ko_kr | events | 12 | 12 | 0 | 12 | 6 | 0 |
| ko_kr | 四类合计 | 342 | 342 | 322 | 342 | 9 | 0 |

## 三、读数

- **页首提示**：四语四类共 1,370 个跟踪文件全部命中本语言提示（en 342/342、zh_tw 344/344、ja 342/342、ko 342/342）；「非官方标记但无页首提示」为 **0**。繁中活动行 14 个文件包含 2 个索引，故总数比其余语言多 2。
- **非官方标记**：四类合计 en 329、zh_tw 340、ja 322、ko 322。与 2026-11-28 `docs/mirror-provenance.md` 更新表的对应类别行一致（角色 93/94/93/93，光锥 170/171/169/169，遗器 60/62/60/60，活动 6/13/0/0）。
- **部分收录**：en 8（遗器 2 + 活动 6）、zh_tw 4（光锥 1 + 遗器 2 + 活动 1）、ja 9（光锥 1 + 遗器 2 + 活动 6）、ko 9（同 ja）。部分收录只表示「页面自述只覆盖公告所列字段」，不表示其余页面完整。
- **未标非官方**：仍有页面既未标非官方、也未标部分收录（如 ja_jp / ko_kr 的 4.7 活动六页，提示中写明活动名/介绍/时间/等级已对照官方更新说明、其他内容未核）。未标非官方不能推断为官方原文或已同步。

## 四、与既有口径的关系

| 统计 | 范围 | 标记 | 字节窗口 | 可否与本表互换 |
|---|---|---|---|---|
| 本表 `audit_mirror_marking_coverage.py` | 四语四类跟踪 `.md` | 非官方标记 + 页首提示 + 部分收录 + 实体 ID 行 | 8192 | 本表 |
| `audit_mirror_provenance.py` | 四语全部跟踪 `.md`（类别细分仅四类） | 仅非官方标记 | 8192 | 不可；范围与列不同 |
| `docs/metrics.md` 的 `labeled_nonofficial_*` | 四语工作区全部 `.md`（含可能被忽略的文件） | 仅非官方标记 | 8192 | 不可；文件集合与测量时间不同 |

本表可复核的方式：记录 `git rev-parse HEAD`、`git status --porcelain` 后重跑上述命令；工作区新增或改动会改变结果。活动对应与逐页来源范围见 [mirror-activity-ledger-2026-11-28.md](mirror-activity-ledger-2026-11-28.md)；数字 ID 对账见 [../mirror-provenance.md](../mirror-provenance.md)。
