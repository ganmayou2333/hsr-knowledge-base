# 崩坏：星穹铁道 · 数据知识库（HSR）

> **语言 / Languages：** [简体中文](README.md) · [繁體中文](docs/README_zh-Hant.md) · [English](docs/README_en.md) · [日本語](docs/README_ja.md) · [한국어](docs/README_ko.md)

基于 **Obsidian** 的《崩坏：星穹铁道》数据知识库，系统整理角色、光锥、物品、遗器、模拟宇宙等游戏数据与资料，页面间通过双链（wikilink）关联，支持结构化检索与快速跳转。

> 数据版本基线：4.5（真珠为 4.6 前瞻角色，单独标注）

---

## 内容结构

| 目录 | 内容 | 规模 |
|---|---|---|
| `character/` | 角色库（按 9 大命途归档，四级索引） | 93 |
| `lightcone/` | 光锥库（按命途归档，四级索引） | 169 |
| `items/` | 物品库（按用途分类，四级索引） | 1428+ |
| `relic/` | 遗器库（隧洞遗器 / 位面饰品） | 62 |
| `simulated/` | 模拟宇宙库（祝福 / 奇物 / 事件 / 区块 / 差分宇宙） | 1765 |
| `货币战争/` | 货币战争库（独立自走棋玩法：玩法 / 角色 / 羁绊 / 装备 / 赛季） | 7 |

> 索引层级统一为：主索引 → 分类 / 命途索引 → 评级索引（星级） → 详情。

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
| [格式规范与要求.md](格式规范与要求.md) | 全库格式总纲（目录 / 命名 / 字段 / 双链 / 版本 v1.7） |
| [协作要求与行动准则.md](协作要求与行动准则.md) | 项目协作核心要求与行动准则 |
| [数据来源.md](数据来源.md) | 数据来源、覆盖范围与版权说明 |
| [遗器规则.md](遗器规则.md) | 遗器规则说明 |
| [SRR图包来源.md](SRR图包来源.md) | SRR 全量图包来源说明 |
| [update.md](update.md) | 历次更新日志 |
| [待办清单.md](待办清单.md) | 数据补全与扩展待办 |

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
