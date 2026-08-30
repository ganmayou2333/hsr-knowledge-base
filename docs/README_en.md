# Honkai: Star Rail · Data Knowledge Base (HSR)

> **Languages:** [简体中文](../README.md) · [繁體中文](README_zh-Hant.md) · [English](README_en.md) · [日本語](README_ja.md) · [한국어](README_ko.md)

An **Obsidian**-based data knowledge base for *Honkai: Star Rail*, systematically organizing game data and materials such as characters, Light Cones, items, Relics, the Simulated Universe, quest texts, and world-building. Pages are linked via wikilinks, supporting structured search and quick navigation. In addition to Simplified Chinese, multilingual mirrors are provided in English / Traditional Chinese / Japanese / Korean.

> Data version baseline: 4.6 (Jade is a 4.6 preview character, noted separately)

---

## Content Structure

| Directory | Content | Size (detail files) |
|---|---|---|
| `character/` | Character library (archived by 9 Paths, 4-level index) | 93 |
| `lightcone/` | Light Cone library (archived by Path, 4-level index) | 169 |
| `items/` | Item library (categorized by use, 4-level index) | 3823 |
| `relic/` | Relic library (Cavern Relics / Planar Ornaments) | 60 |
| `simulated/` | Simulated Universe library (Blessings / Curios / Events / Occurrences / Divergent Universe) | 1793 |
| `quest/` | Quest text library (Trailblaze / Companion / Adventure missions) | 167 |
| `worldview/` | World-building library (Aeons / Factions / Locations / Glossary / Relationships) | 8 |
| `货币战争/` | Currency War library (standalone auto-chess mode: gameplay / characters / bonds / equipment / seasons) | 7 |
| `rules/` | Rules library (combat mechanics / status priority / exceptions) | 5 |
| `en_us/` `zh_tw/` `ja_jp/` `ko_kr/` | Multilingual mirrors (English / Traditional Chinese / Japanese / Korean, mirroring all data above) | ~5,840 each |

> The index hierarchy is unified as: Main Index → Category / Path Index → Rating Index (rarity) → Details. Size counts detail files only (index and group files excluded).

---

## Data Sources

See [Data Sources](data-sources.md) for details:

- **hsr.nanoka.cc**: Base data and details for characters / Light Cones / items / Relics
- **miHoYo Community Wiki** (bbs.mihoyo.com/sr/wiki): Character encyclopedia, Relic origins & acquisition, Simulated Universe Paths / rarity / event texts
- **Official website**: Official materials
- **StarRailRes open-source repository** (github.com/Mar-7th/StarRailRes): Full Simulated Universe data (Blessings / Curios / Events / Occurrences JSON)

---

## Usage

1. Open this directory as a vault in **Obsidian**.
2. Enter from each library's main index, then browse along "Category / Path → Rating → Details".
3. Material / Relic / Light Cone references inside character files are wikilinks and can be clicked directly.
4. Search can directly look up character / item / Light Cone names.

---

## Standards & Documents

| Document | Description |
|---|---|
| [格式规范与要求.md](../格式规范与要求.md) | Format standards master (directory / naming / fields / wikilinks / version v1.9, Simplified Chinese) |
| [协作要求与行动准则.md](../协作要求与行动准则.md) | Project collaboration requirements & code of conduct |
| [数据来源.md](../数据来源.md) | Data sources, coverage & copyright notes |
| [遗器规则.md](../遗器规则.md) | Relic rules |
| [SRR图包来源.md](../SRR图包来源.md) | SRR full image pack source notes |
| [update.md](../update.md) | Update changelog |
| [待办清单.md](../待办清单.md) | Data completion & extension backlog |
| [multilang_index.md](multilang_index.md) | Multilingual data index (4-language file statistics) |
| [multilang_final_report.md](multilang_final_report.md) | Multilingual final coverage report |

---

## Copyright Notice

- The game name, characters, art resources, and text are copyrighted by **HoYoverse (miHoYo)**. This repository is for **non-commercial personal use** only, following the official fan/derivative creation guidelines of each region.
- **Applicable regions & guideline versions**:

| Region | Official guideline | Version & release date |
|---|---|---|
| Mainland China | Honkai: Star Rail Fan Works Creation Guide | V1.0 (2023-04-17) → V2.0 (2024-08-23) → **V3.0 (2025-07-15, current)**[1] |
| Japan | Honkai: Star Rail fan creation guidelines (miHoYo / COGNOSPHERE) | Current version (verified 2026-02-21)[2] |
| Other regions (outside Mainland China & Japan) | Honkai: Star Rail Fan Creations Guide | V1.0 (2023-04-22) → **V2.0 (2024-08-23, current; officially stated not applicable to Mainland China and Japan)**[3] |

- Simulated Universe data is derived from **StarRailRes** (github.com/Mar-7th/StarRailRes, **AGPL-3.0**)[4]; this repository accordingly adopts **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [LICENSE](../LICENSE).
- Other data sources are listed in [Data Sources](data-sources.md).
- Third-party image packs (StarRailRes_repo/) are not included in version control.

> [1] https://www.miyoushe.com/ys/article/66426966
> [2] https://www.niji-guidelines.com/guidelines/honkai-star-rail
> [3] https://hsr.hoyoverse.com/en-us/news/125457
> [4] https://github.com/Mar-7th/StarRailRes/blob/master/LICENSE
