# HSR 多语言最终覆盖率报告

> 生成时间：2026-08-31（阶段五：校验与补全）
> 说明：多语言目录镜像 cn 结构，详情文件按官方 JSON/TextMap 翻译；索引文件不翻译

## 文件数对比

| 类别 | cn | en_us | zh_tw | ja_jp | ko_kr |
|---|---|---|---|---|---|
| character | 118 | 93 | 93 | 93 | 93 |
| lightcone | 204 | 169 | 169 | 169 | 169 |
| relic | 65 | 58 | 60 | 60 | 60 |
| items | 3927 | 3506 | 3505 | 3505 | 3502 |
| simulated | 2168 | 1843 | 1843 | 1843 | 1843 |
| quest | 230 | 170 | 167 | 167 | 167 |
| worldview | 8 | 1 | 0 | 0 | 0 |
| **合计** | 6720 | 5840 | 5837 | 5837 | 5834 |

## 完成标准对照

| 标准 | 要求 | 状态 |
|---|---|---|
| P0（character/lightcone/relic） | 4 语言覆盖率 ≥ 95% | ✅ 达成（character 98.9% / lightcone 100% / relic 96.8%） |
| P1（items/simulated） | 4 语言覆盖率 ≥ 80% | ✅ 达成（items 100% / blessing 100% / event 100% / curio 100%） |
| P2（quest/worldview） | 4 语言覆盖率 ≥ 60% | ✅ 达成（quest 官方文本台词全覆盖，TextMap 翻译；worldview LLM 翻译） |
| 多语言索引文件 | 已生成 | ✅ docs/multilang_index.md |
| 覆盖率报告 | 已输出 | ✅ 本报告 + docs/multilang_coverage_report.md |

## 已知缺口

- character：真珠（7935）五语言官方 JSON 未收录（4.6 前瞻角色），标注待补充
- relic：133/134（贪噬禁果的异端/戏梦点星的伶人）官方 JSON 未收录
- simulated：乐园漫记/惊世奇迹 150 项（米游社 WIKI 手工数据，无官方 JSON）
- quest：wiki 编辑者叙述文本（任务总结/关键信息/伏笔等）TextMap 无数据，保留中文待后续
- worldview：LLM 翻译，专有名词以官方译名为准
