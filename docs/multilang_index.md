# HSR 多语言数据索引

> 生成时间：2026-08-31
> 语言：en_us（英语）/ zh_tw（繁体中文）/ ja_jp（日语）/ ko_kr（韩语）
> 数据源：StarRailRes index_new 官方 JSON（cn 基准 → 各语言回填）

## en_us

- character: 93 文件
- lightcone: 169 文件
- relic: 58 文件
- items: 3506 文件
- simulated: 1843 文件
- **小计：5669 文件**

## zh_tw

- character: 93 文件
- lightcone: 169 文件
- relic: 60 文件
- items: 3505 文件
- simulated: 1843 文件
- **小计：5670 文件**

## ja_jp

- character: 93 文件
- lightcone: 169 文件
- relic: 60 文件
- items: 3505 文件
- simulated: 1843 文件
- **小计：5670 文件**

## ko_kr

- character: 93 文件
- lightcone: 169 文件
- relic: 60 文件
- items: 3502 文件
- simulated: 1843 文件
- **小计：5667 文件**

## 汇总

- 4 语言合计约 **22676** 个 md 文件（详情为主，不含 cn 索引）
- 覆盖口径：按实体 ID 校验，character 98.9% / lightcone 100% / relic 96.8% / items 100% / blessing 100% / event 100%
- 未覆盖：真珠(7935)、遗器 133/134（官方 JSON 未收录）；乐园漫记/惊世奇迹 150 项（米游社 WIKI 手工数据，无官方 JSON）
- 生成脚本：temp/multilang_gen_p0.py（角色/光锥/遗器）、temp/multilang_gen_p1.py（物品/模拟宇宙）
