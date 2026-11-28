# 仙舟 9 艘 + 3 名将军/元帅：页面与双链只读核查（2026-11-28）

> 用途：issue #4「仙舟 9 艘与将军/元帅页面」的现状核查记录。
> 性质：**只读检查**——脚本读取 Markdown 与目录，未写数据区（本记录本身除外）。检查对象为工作区 `G:\HSR`（`main`，当时 HEAD `d7e0daf79`）。

## 一、页面存在性（12 项）

| 实体 | 期望页面 | 存在 |
|---|---|---|
| 曜青 | `zh_cn/worldview/仙舟曜青.md` | 是 |
| 朱明 | `zh_cn/worldview/仙舟朱明.md` | 是 |
| 玉阙 | `zh_cn/worldview/仙舟玉阙.md` | 是 |
| 方壶 | `zh_cn/worldview/仙舟方壶.md` | 是 |
| 虚陵 | `zh_cn/worldview/仙舟虚陵.md` | 是 |
| 罗浮 | `zh_cn/worldview/仙舟罗浮.md` | 是 |
| 岱舆 | `zh_cn/worldview/仙舟岱舆.md` | 是 |
| 圆峤 | `zh_cn/worldview/仙舟圆峤.md` | 是 |
| 苍城 | `zh_cn/worldview/仙舟苍城.md` | 是 |
| 怀炎（烛渊将军·朱明） | `zh_cn/character/人物/怀炎.md` | 是 |
| 玄全（伏波将军·方壶） | `zh_cn/character/人物/玄全.md` | 是 |
| 有无（尘冥将军·虚陵） | `zh_cn/character/人物/有无.md` | 是 |
| 华（云骑元帅） | —— | **否，按裁定不建页**（来源为第三方转写，不满足官方来源） |

## 二、`zh_cn/worldview/势力与组织.md` 仙舟表双链

- 表格位置：`### 仙舟` 节；表头 1 行 + 数据行 9 行（4 列：仙舟 / 将军 / 龙尊 / 状态）。
- 9 艘仙舟**全部**以 `[[zh_cn/worldview/仙舟<名>|…]]` 双链指向对应页面。
- 将军列中怀炎、玄全、有无均以 `[[zh_cn/character/人物/<名>|…]]` 双链；另有飞霄（曜青）、爻光（玉阙）、景元（罗浮）为既有双链。
- 岱舆行将军列写「青竹（领袖）」为纯文本：官方原文（`zh_cn/relic/位面饰品/折断的龙骨.md`）称青竹为岱舆**领袖**而非将军，且岱舆殉爆早于帝弓与七天将建制，故不建人物页、不加双链。
- 圆峤 / 苍城 / 虚陵行将军列为空或待核，未编造。

## 三、全库 worldview 双链完整性（本地只读）

```
扫描目录：zh_cn/worldview（17 个 .md）
双链总数：75
死链数：0
```

口径：正则 `\[\[([^\]\|\\]+?)(?:\|[^\]]*)?\]\]`，对去掉代码块后的正文逐条取目标，按「仓库根相对路径 + `.md`」判存在。这是**本库内部**链接检查，不涉及站点构建（站点构建与 `verify_site` / `verify_docs` 由 Lead 统一执行）。

## 四、未解决（写入 `docs/待补充清单.md`）

1. 华：仍只有第三方转写（旧委托署名「华，云骑元帅」，TextMap 哈希 `11981578411064480828`）与三测录像旁证，**不满足官方来源**，不建页。
2. 虚陵现状、圆峤失踪后的情况、方壶与玉阙的状态仍待核（既有条目不因本次检查而改变）。
3. 苍城覆灭的精确年份仍待核。

## 五、复现

```python
import re
from pathlib import Path
ROOT = Path('.').resolve()
LINK = re.compile(r'\[\[([^\]\|\\]+?)(?:\|[^\]]*)?\]\]')
files = sorted((ROOT / 'zh_cn/worldview').rglob('*.md'))
tot = 0; miss = []
for p in files:
    t = p.read_text(encoding='utf-8')
    for m in LINK.finditer(t):
        raw = m.group(1).strip()
        if raw.endswith('.md'):
            raw = raw[:-3]
        tot += 1
        if not (ROOT / (raw + '.md')).is_file():
            miss.append((p.name, raw))
print('files', len(files), 'links', tot, 'dead', len(miss), miss)
```
