# Data Sources

> **Languages:** [简体中文](../数据来源.md) · [繁體中文](數據來源.md) · [English](data-sources.md) · [日本語](データソース.md) · [한국어](데이터소스.md)

> Overview of all data sources in the Honkai: Star Rail Data Knowledge Base (Obsidian)
> Updated: 2026-10-01
> Data version baseline: 4.6

---

## I. Source Overview

| Source | Use | Coverage | Acquisition method |
|---|---|---|---|
| hsr.nanoka.cc | Full data for characters / Light Cones / items / Relics | 93 characters, 169 Light Cones, 3823 items, 62 Relics | Browser simulation click + random interval |
| bbs.mihoyo.com/sr/wiki (Official Wiki) | Official character increments, Relic attribute rules, SU Blessing Paths | Official data for 93 characters, Relic main/sub-stat rules, classic SU Blessing Paths | Simulated click + 10 s interval every 2 requests |
| sr.mihoyo.com (Honkai: Star Rail official site) | Version update notes (reference) | Announcements for 4.2 and later | Web browsing |
| github.com/Mar-7th/StarRailRes (SRR) | Full SU data: Blessings / Curios / Events / Occurrences | 1219 Blessings, 239 Curios, 524 Events, 16 Occurrences | Git repository clone, index_new/cn JSON |

> **Two clones, two purposes**: multilingual JSON data comes from `StarRailRes-master/index_new/` (13 languages, ZIP snapshot pinned at v4.5); the **icon pack** comes from `StarRailRes_repo/` (git clone, pullable, icon/image/font, cn data only). Within one purpose, the newer version wins (both are v4.5 as of now).

---

## II. hsr.nanoka.cc (Primary data source)

Fan-made database site; Chinese data comes directly from rendered page text.

| Path | Data | Count | Entity ID range |
|---|---|---|---|
| /character | Characters (list + details) | 93 | character/<id> |
| /lightcone | Light Cones (list + details) | 169 | lightcone/<id> |
| /item | Items (list + details) | 3823 | item/<id> |
| /relic | Relics (list + details) | 62 (34 Cavern + 28 Planar) | relic/101-134, 301-328 |
| /monster | Monsters | Not collected | - |

- **Data version**: 4.5 (page version comparison includes 4.5.51, etc.).
- **Fetching rules**: pages are read sequentially in a browser at a random 8–12 s interval, and at a lower rate when three workers run in parallel; we honour each source's robots.txt and terms of service and use the data for personal, non-commercial compilation only.
- **Limitations**: Details for new characters follow official publication. Pearl (1503) has been fully added as of 4.6 (Base Stats / Skills / Eidolons), but some values such as skill multipliers are not officially published and are marked "values pending verification" in the pages.
- **Library size (rechecked 2026-09-30)**: 3823 item detail files under `/item` (previously recorded as 1429); the increase comes mainly from categories supplemented via StarRailRes `items.json`.

---

## III. miHoYo Community Wiki (Official increments)

miHoYo's official community Wiki, maintained by the Trailblazer Notes editing team, with official platform support.

| Content | URL form | Use |
|---|---|---|
| Character encyclopedia | bbs.mihoyo.com/sr/wiki/content/<id>/detail | Official character data increments: faction / city-state / god power / role / recommended Light Cone / recommended team / voice actor / character story |
| Relic encyclopedia | bbs.mihoyo.com/sr/wiki/content/relic/list | Relic main/sub-stat rules (reference) |
| SU Blessing overview | bbs.mihoyo.com/sr/wiki/content/767/detail | Classic SU Blessings: precise Path (incl. dual-Path interleave), pre/post-enhanced effects |

- **Fetching rules**: sequential browser reading; 10 s interval every 2 requests (frequency controlled per user request).
- **Merge method**: Plan B — official data is increment-merged into existing nanoka character files without replacing original data; SU Blessing Paths merged into SRR Blessing files (Wiki takes priority over ID-segment inference).
- **⚠️ Source withdrawal (2026-10-02 · W-4.6-19)**: that wiki's entries declare "no reproduction" (禁止轉載), which binds its **wording**. The library has therefore **withdrawn** the task descriptions and verbatim dialogue copied from it, keeping only factual fields (region / type / level / rewards / chapter structure).

---

## III-ter. Bilibili BWIKI (CC BY-NC-SA 4.0)

- **License**: the site states its content is provided under **CC BY-NC-SA 4.0**. Use fulfils three obligations: **Attribution (BY)** — source and licence noted in each file header; **NonCommercial (NC)** — this library is free and non-commercial; **ShareAlike (SA)** — derivatives of its original expression must be shared under the same licence.
- **Boilerplate cleanup (2026-10-02 · W-4.6-19)**: site boilerplate carried in by scraping (site intro, chat-group id, view counts, navigation widgets) has been **fully removed** and is never used as attribution.

---

## III-bis. StarRailRes (Simulated Universe data source)

github.com/Mar-7th/StarRailRes (SRR) is the primary data source for the Simulated Universe region, cloned locally to `G:\HSR\StarRailRes_repo`.

| File | Data | Count | Notes |
|---|---|---|---|
| index_new/cn/simulated_blessings.json | Blessings | 1219 | Effects / enhanced effects; Paths supplemented from miHoYo Wiki 767 and ID-segment inference |
| index_new/cn/simulated_curios.json | Curios | 239 | Effects / lore |
| index_new/cn/simulated_events.json | Events | 524 | Name / type / image; event texts backfilled 320/384 (BWIKI source) |
| index_new/cn/simulated_blocks.json | Occurrences | 16 | Name / description |

- **Same-name merge**: entities with the same name across difficulty / version / option are merged into a single file, aggregating all entity IDs in the body.
- **Path inference**: ID segments 6120-6128 (classic SU) and 6150-6158 (Gold and Gears) correspond to the 9 Paths; miHoYo Wiki 767 provides precise Paths for 216 classic SU Blessings (incl. dual-Path interleave such as "Preservation & Nihility").
- **Data completion (2026-08-28)**: Blessing rarities 356/359, Curio rarities 84/84, event texts 320/384 (source: BWIKI HSR wiki); remaining 3 Blessing rarities and 64 events (Aeon encounters / equations / shop types) pending miHoYo Wiki or game guide sources.
- **Images**: 524 events reuse 59 shared image groups, de-duplicated and annotated.

---

## IV. Copyright & Disclaimer

- Data sources are the fan-made database site (hsr.nanoka.cc), the official community Wiki (miHoYo) and the open-source repository (StarRailRes). The game name, characters, art resources, and text are copyrighted by **HoYoverse (miHoYo)**.
- This knowledge base is for **non-commercial personal use** only, following each region's official fan/derivative creation guidelines (see README copyright notice):
  - **Mainland China**: Honkai: Star Rail Fan Works Creation Guide V3.0 (current as of 2025-07-15)
  - **Japan**: Honkai: Star Rail fan creation guidelines (miHoYo / COGNOSPHERE)
  - **Other regions (outside Mainland China & Japan)**: Honkai: Star Rail Fan Creations Guide v2.0 (current as of 2024-08-23)
- Official Wiki article content is original work of the Trailblazer Notes editing team; redistribution is prohibited.
- StarRailRes is a third-party open-source data repository (AGPL-3.0); its data copyright belongs to the repository author; attribution must be retained.

---

*Data version baseline: 4.6 (Pearl is now officially included in 4.6; 4.6 additions: Pearl 1503 / Light Cone &quot;Colors for Tomorrow&quot; 23055 / Relics 133 &amp; 134 (official English names pending) / Trailblaze mission 月升之前，与兽共舞 (official English name pending))*
