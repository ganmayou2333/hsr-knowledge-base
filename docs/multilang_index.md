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

## 待建镜像（4.6 新增三类库，2026-09-30）

以下三类为 `格式规范与要求.md v1.13` 新增目录，**仅 zh_cn/ 有详情，四语言镜像全部待建**：

- `events/`（活动库）：zh_cn 已有 1 条（爱，幽灵与机器人），en_us/zh_tw/ja_jp/ko_kr 待建
- `enemies/`（敌人库）：zh_cn 暂无详情（新敌人中文名待补充），镜像待建
- `stages/`（关卡库）：zh_cn 已有 1 条（密伶之径），en_us/zh_tw/ja_jp/ko_kr 待建

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-10-02 | 全量复核为实测值；合计口径自洽；W-4.6-19 剧情文本表达撤下后各语言 quest 计数不变（文件保留、内容改写） |
