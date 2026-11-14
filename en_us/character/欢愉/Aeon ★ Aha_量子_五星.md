# Aeon ★ Aha (Quantum · Elation)

> 数据来源：[https://hsr.nanoka.cc/character/1511](https://hsr.nanoka.cc/character/1511) (English name / attribute / skills / traces / Eidolons from nanoka 4.7.51 `en/character/1511.json`); [Version 4.7 "Now, Lay Laughter to All Stars" Update Details](https://hsr.hoyoverse.com/en-us/news/167246) (official English name, Path and rarity)
> 数据版本：4.7
> 实体ID：1511
> 创建时间：2026-11-14 17:50
> 更新时间：2026-11-14 17:50

---

## Basic Info

| Attribute | Value |
|---|---|
| Character Name | Aeon ★ Aha |
| Path | Elation |
| Attribute | Quantum |
| Rarity | ★★★★★ |
| Faction | Pending |
| Limited | Yes |
| Introduction | Cries and comedy intertwine, and the deathly still cosmos awakens to daybreak in a farce.<br>Stepping back onto the stage of the Path, I tear off the god's mask. Who is Aha? I am Aha!<br>To play, to trick, to hunt... Please bear witness to an improv tour where humans and gods dance as one! |
| Role | Elation-system core damage dealer and team buffer: claims enemy Max HP through "Elation Debt" with the Aeonic Authority "The True Story of Aha," stars as the lead in the "Aha Instant," and ascends the Path of Elation (Punchline / "Certified Banger" → Bliss / "Party Trick") |

> Faction / Limited note: nanoka 4.7.51 `chara_info.camp` is `null` and the Version 4.7 Update Details publish no faction → recorded as Pending, not inferred. "Limited" is recorded as Yes per the work order's convention (a new 5★ added in Version 4.7 and released with the version warp; the official notice uses the word "Limited" only for their "Limited Collection Outfit").
>
> Introduction is the official English in-game text (nanoka `en` `desc`, line breaks restored).

### Voice Actors

| Language | VA |
|---|---|
| Chinese | Pending |
| Japanese | Pending |
| Korean | Pending |
| English | Pending |

> Voice actors: all four `chara_info.va` fields (chinese / japanese / korean / english) are `null` in nanoka 4.7.51, and the Version 4.7 Update Details credit no voice actor → Pending, not inferred.

---

## Base Stats (Lv.80)

| Attribute | Value |
|---|---|
| Base HP | 1,047 |
| Base ATK | 679 |
| Base DEF | 509 |
| Base SPD | 94 |
| Taunt | 100 |
| Max Energy | Pending (this character does not use Energy; the Ultimate is activated with "Wishpower") |

> Recomputation: nanoka `stats.6` (6th ascension segment) `base + add × (80 − 1)`, then truncated — HP 484.704 + 7.128×79 = 1,047.82 → 1,047; ATK 314.16 + 4.62×79 = 679.14 → 679; DEF 235.62 + 3.465×79 = 509.36 → 509. The same formula reproduces the Lv.80 values already published in the library for the two neighbouring 4.5/4.6 characters. SPD / Taunt are the nanoka values (94 / 100). Values are identical to the zh_cn source file.

## Ascension Materials (Lv.1 → Lv.80)

| Level | Materials | Qty |
|---|---|---|
| Pre-20 | [[zh_cn/items/Material/CommonMonsterDrop/童真蜡笔\|Whimsy Wax]] | 5 |
| 20→30 | [[zh_cn/items/Material/CommonMonsterDrop/童真蜡笔\|Whimsy Wax]] | 10 |
| 30→40 | [[zh_cn/items/Material/CommonMonsterDrop/造梦蘸钢\|Dreamweave Steel]] | 6 |
| 40→50 | [[zh_cn/items/Material/CommonMonsterDrop/造梦蘸钢\|Dreamweave Steel]] | 9 |
| 50→60 | [[zh_cn/items/Material/CommonMonsterDrop/梦现管锥\|Lucid Awl]] | 6 |
| 60→70 | [[zh_cn/items/Material/CommonMonsterDrop/梦现管锥\|Lucid Awl]] | 9 |
| Each stage | [[zh_cn/items/Virtual/Virtual/信用点\|Credit]] | 4,000 / 8,000 / 16,000 / 40,000 / 80,000 / 160,000 (total 308,000) |
| From 30→40 | [[zh_cn/items/Material/AvatarRank/嗤笑丑面\|Sneering Harlequin]] | 3 / 7 / 20 / 35 (total 65) |

> Source: nanoka 4.7.51 `stats.*.cost` (six ascension stages; entity IDs 2 = Credit / 116001 = Whimsy Wax / 116002 = Dreamweave Steel / 116003 = Lucid Awl / 110443 = Sneering Harlequin). Material names are aligned to the library's item entries by entity ID.

## Skill Materials

Skill level cap: Basic ATK 1→6 / Skill 1→10 / Ultimate 1→10 / Talent 1→10 / Elation Skill 1→10 (base caps, nanoka `skill_trees.max_level`); Eidolon E3 (Ultimate +2, Basic ATK +1, Elation Skill +1) and E5 (Skill +2, Talent +2, Elation Skill +1) raise these further, so the reachable maximums are Basic ATK 7 / Skill 12 / Ultimate 12 / Talent 12 / Elation Skill 12 (in-game level text states "up to a maximum of Lv. 15").

| Materials | Qty |
|---|---|
| [[zh_cn/items/Virtual/Virtual/信用点\|Credit]] | 1,740,000 |
| [[zh_cn/items/Material/WeeklyMonsterDrop/命运的足迹\|Tracks of Destiny]] | 6 |
| [[zh_cn/items/Material/TracePath/《绒绒号》手绘分镜稿\|The Fluffy Hand-drawn Storyboards]] | 11 |
| [[zh_cn/items/Material/TracePath/《绒绒号》连载纪念刊\|The Fluffy Serialization Memorial Issue]] | 41 |
| [[zh_cn/items/Material/TracePath/《绒绒号》典藏版合集\|The Fluffy Collector's Edition]] | 80 |
| [[zh_cn/items/Material/WeeklyMonsterDrop/伪觉者的期许\|High Hopes of the Falsely Enlightened]] | 9 |
| [[zh_cn/items/Material/CommonMonsterDrop/童真蜡笔\|Whimsy Wax]] | 26 |
| [[zh_cn/items/Material/CommonMonsterDrop/造梦蘸钢\|Dreamweave Steel]] | 38 |
| [[zh_cn/items/Material/CommonMonsterDrop/梦现管锥\|Lucid Awl]] | 22 |

> Method: cost of raising Basic ATK / Skill / Ultimate / Talent to their base caps (6 / 10 / 10 / 10), accumulated level-by-level from nanoka `skill_trees.point01`–`point04` `material_list`.
>
> Additional totals: Elation Skill 1→10 requires Credit 520,000 · The Fluffy Hand-drawn Storyboards 3 · The Fluffy Serialization Memorial Issue 12 · The Fluffy Collector's Edition 24 · Whimsy Wax 7 · Dreamweave Steel 11 · Lucid Awl 14; unlocking all Traces (including the three bonus Traces) requires Credit 740,000 · Tracks of Destiny 2 · The Fluffy Hand-drawn Storyboards 4 · The Fluffy Serialization Memorial Issue 16 · The Fluffy Collector's Edition 35 · High Hopes of the Falsely Enlightened 3 · Whimsy Wax 8 · Dreamweave Steel 7 · Lucid Awl 22 (same-source per-level accumulation).

---

## Skills

> Effect text below is taken from nanoka 4.7.51 English skill descriptions (placeholders resolved with the level parameters, ratio parameters rendered ×100%); italic/colour markup is stripped and the official capitalisation is kept.

### Basic ATK: Starfrost, Showtime!

- **Type**：Basic ATK · Single Target
- **Summary**：Deals Quantum Elation DMG to one enemy.
- **Max Level**：7
- **Level Table**：

  | Level | DMG multiplier (%) |
  |---|---|
  | Lv.1 | 25% |
  | Lv.2 | 30% |
  | Lv.3 | 35% |
  | Lv.4 | 40% |
  | Lv.5 | 45% |
  | Lv.6 | 50% |
  | Lv.7 | 55% |

- **Max Effect (Lv.7)**：Deals 55% Quantum Elation DMG to one designated enemy target.

### Skill: This Emanator Was Certified by Aha™

- **Type**：Skill · Support / Follow-Up ATK
- **Summary**：Enables one designated ally character (excluding this unit) to gain the "Emanator of Elation" state, then immediately launches a Follow-Up ATK dealing Quantum Elation DMG to all enemies. The target holding "Emanator of Elation" has their Elation stat increased, and enables Aeon ★ Aha to gain "Wishpower" at the start of their turn.
- **Max Level**：12
- **Level Table**：

  | Level | "Emanator of Elation" Elation increase (%) | Follow-Up ATK multiplier (%) | "Wishpower" gained at target's turn start |
  |---|---|---|---|
  | Lv.1 | 10% | 25% | 1 |
  | Lv.2 | 11% | 27.5% | 1 |
  | Lv.3 | 12% | 30% | 1 |
  | Lv.4 | 13% | 32.5% | 1 |
  | Lv.5 | 14% | 35% | 1 |
  | Lv.6 | 15% | 37.5% | 1 |
  | Lv.7 | 16.25% | 40.625% | 1 |
  | Lv.8 | 17.5% | 43.75% | 1 |
  | Lv.9 | 18.75% | 46.875% | 1 |
  | Lv.10 | 20% | 50% | 1 |
  | Lv.11 | 21% | 52.5% | 1 |
  | Lv.12 | 22% | 55% | 1 |

- **Max Effect (Lv.12)**：Enables one designated ally character (excluding this unit) to gain the "Emanator of Elation" state, then immediately launches Follow-Up ATK, dealing 55% Quantum Elation DMG to all enemies. The "Emanator of Elation" state lasts for the entire battle until it switches to the next target. The target with the "Emanator of Elation" state has their Elation stat increased by 22% and, at the start of their turn, enables Aeon ★ Aha to gain 1 point of "Wishpower."

### Ultimate: Aha! Let There Be Laughter

- **Type**：Ultimate · AoE / Bounce
- **Summary**：Advances Aha's action and grants Aeon ★ Aha the "Faces of Elation" state. Deals heavy Quantum Elation DMG to all enemies, then deals 5 instances of Quantum Elation DMG to random enemy targets.
- **Max Level**：12
- **Level Table**：

  | Level | AoE DMG multiplier (%) | DMG instances | Per-instance multiplier (%) | Aha's action advance (%) | "Faces of Elation" duration (turn) |
  |---|---|---|---|---|---|
  | Lv.1 | 120% | 5 | 36% | 20% | 3 |
  | Lv.2 | 128% | 5 | 38.4% | 20% | 3 |
  | Lv.3 | 136% | 5 | 40.8% | 20% | 3 |
  | Lv.4 | 144% | 5 | 43.2% | 20% | 3 |
  | Lv.5 | 152% | 5 | 45.6% | 20% | 3 |
  | Lv.6 | 160% | 5 | 48% | 20% | 3 |
  | Lv.7 | 170% | 5 | 51% | 20% | 3 |
  | Lv.8 | 180% | 5 | 54% | 20% | 3 |
  | Lv.9 | 190% | 5 | 57% | 20% | 3 |
  | Lv.10 | 200% | 5 | 60% | 20% | 3 |
  | Lv.11 | 208% | 5 | 62.4% | 20% | 3 |
  | Lv.12 | 216% | 5 | 64.8% | 20% | 3 |

- **Max Effect (Lv.12)**：Aha's action advances by 20%. Aeon ★ Aha gains the "Faces of Elation" state, lasting for 3 turn(s). This duration decreases by 1 at the start of Aeon ★ Aha's every turn. Deals 216% Quantum Elation DMG to all enemies. Then, deals 5 instance(s) of DMG, with each instance dealing 64.8% Quantum Elation DMG to one random enemy.

### Talent: Work Wonders with THEM

- **Type**：Talent · Enhancement
- **Summary**：Can activate the Ultimate after "Wishpower" reaches 8, and Wishpower can overflow up to 10 after reaching its upper limit. Aeon ★ Aha gains "Wishpower" after using Basic ATK, Skill, or Elation Skill. After allies' Punchline reaches a set value for the first time, Aeon ★ Aha immediately gains "Wishpower" and increases all allies' CRIT DMG; this can trigger again after Aha's turn ends.
- **Max Level**：12
- **Level Table**：

  | Level | "Wishpower" needed to activate Ultimate | "Wishpower" overflow cap | "Wishpower" gained per ability used | Punchline trigger threshold | "Wishpower" gained immediately | All allies' CRIT DMG increase (%) | CRIT DMG duration (turn) |
  |---|---|---|---|---|---|---|---|
  | Lv.1 | 8 | 10 | 1 | 40 | 1 | 20% | 3 |
  | Lv.2 | 8 | 10 | 1 | 40 | 1 | 22% | 3 |
  | Lv.3 | 8 | 10 | 1 | 40 | 1 | 24% | 3 |
  | Lv.4 | 8 | 10 | 1 | 40 | 1 | 26% | 3 |
  | Lv.5 | 8 | 10 | 1 | 40 | 1 | 28% | 3 |
  | Lv.6 | 8 | 10 | 1 | 40 | 1 | 30% | 3 |
  | Lv.7 | 8 | 10 | 1 | 40 | 1 | 32.5% | 3 |
  | Lv.8 | 8 | 10 | 1 | 40 | 1 | 35% | 3 |
  | Lv.9 | 8 | 10 | 1 | 40 | 1 | 37.5% | 3 |
  | Lv.10 | 8 | 10 | 1 | 40 | 1 | 40% | 3 |
  | Lv.11 | 8 | 10 | 1 | 40 | 1 | 42% | 3 |
  | Lv.12 | 8 | 10 | 1 | 40 | 1 | 44% | 3 |

- **Max Effect (Lv.12)**：Can activate Ultimate after "Wishpower" reaches 8. After reaching its upper limit, Wishpower can still overflow up to 10. After using Basic ATK, Skill, or Elation Skill, Aeon ★ Aha gains 1 "Wishpower." After allies' Punchline reaches 40 for the first time, Aeon ★ Aha will immediately gain 1 "Wishpower" and then increase all allies' CRIT DMG by 44%, lasting for 3 turn(s). This can trigger again after Aha's turn ends.

### Technique: ABRACADABRA!

- **Type**：Technique · Field
- **Summary**：After using the Technique, creates a Special Dimension around this unit. Enemies within it get inflicted with "Optical Illusion" and cannot detect ally targets. After entering combat, Aha immediately gains 1 extra turn where a fixed amount of Punchline is taken into account; this turn does not consume Punchline.
- **Max Level**：1
- **Level Table**：

  | Level | Fixed Punchline taken into account | Dimension duration (sec) |
  |---|---|---|
  | Lv.1 | 20 | 20 |

- **Max Effect (Lv.1)**：After using Technique, creates a Special Dimension around this unit, lasting for 20 second(s). Enemies within this Special Dimension get inflicted with "Optical Illusion." Once inflicted with "Optical Illusion," they cannot detect ally targets. After entering combat, Aha immediately gains 1 extra turn where a fixed amount of 20 Punchline is taken into account. This turn does not consume Punchline. Only 1 dimension effect created by allies can exist at the same time.

- **Extra: Field attack** (nanoka 151106 "Attack", MazeNormal type): Attacks an enemy; after entering combat, reduces the corresponding Type Toughness of the enemy target. This is the regular overworld attack outside the Technique and has no level parameters.

### Elation Skill: Yes Aha At Full Moon

- **Type**：Elation Skill · AoE / True DMG
- **Summary**：Always gets used at the end of Aha Instant regardless of Participant ID. Deals Quantum Elation DMG to all enemies, and deals True DMG based on the total non-True DMG dealt by ally targets during this Aha Instant, distributed evenly among all enemies.
- **Max Level**：12
- **Level Table**：

  | Level | AoE Elation DMG multiplier (%) | True DMG conversion ratio (%) |
  |---|---|---|
  | Lv.1 | 30% | 20% |
  | Lv.2 | 33% | 20% |
  | Lv.3 | 36% | 20% |
  | Lv.4 | 39% | 20% |
  | Lv.5 | 42% | 20% |
  | Lv.6 | 45% | 20% |
  | Lv.7 | 48.75% | 20% |
  | Lv.8 | 52.5% | 20% |
  | Lv.9 | 56.25% | 20% |
  | Lv.10 | 60% | 20% |
  | Lv.11 | 63% | 20% |
  | Lv.12 | 66% | 20% |

- **Max Effect (Lv.12)**：Always gets used at the end of Aha Instant regardless of Participant ID. Deals 66% Quantum Elation DMG to all enemies, and deals True DMG based on 20% of total non-True DMG dealt by ally targets during this Aha Instant, distributed evenly among all enemies.

### Innate Trace: Faces of Elation ★ Ex Nihilo

- **Type**：Innate Trace · Enhancement (Lv.2 unlocked by Eidolon E2)
- **Summary**：While holding the "Faces of Elation" state, enables allies' Path of Elation to ascend, enhancing Punchline and "Certified Banger" into Bliss and "Party Trick." Bliss recovers part of its consumed amount when Aha Instant ends. During "Faces of Elation," Aeon ★ Aha's CRIT Rate increases and the DMG dealt ignores part of the enemy target's DEF.
- **Max Level**：2
- **Level Table**：

  | Level | Bliss recovery ratio (%) | DEF ignore (%) | CRIT Rate increase (%) |
  |---|---|---|---|
  | Lv.1 | 10% | 30% | 12% |
  | Lv.2 | 10% | 60% | 20% |

- **Max Effect (Lv.2)**：While holding the "Faces of Elation" state, Aeon ★ Aha enables allies' Path of Elation to ascend, and enhances Punchline and "Certified Banger" into Bliss and "Party Trick," respectively. Bliss recovers 10% of its consumed amount when Aha Instant ends. During "Faces of Elation," Aeon ★ Aha's CRIT Rate increases by 20%, and the DMG dealt ignores 60% of the enemy target's DEF.

### Aeonic Authority: The True Story of Aha

- **Type**：Aeonic Authority · Suppression
- **Summary**：When Aeon ★ Aha or a teammate deals DMG, additionally applies the "Elation Debt" effect onto the enemy target; "Elation Debt" persists through the enemy target's phase transition.
- **Max Level**：1
- **Level Table**：

  | Level | "Elation Debt" as % of HP lost | "Elation Debt" cap (% of target's Max HP) |
  |---|---|---|
  | Lv.1 | 25% | 10% |

- **Max Effect (Lv.1)**：When Aeon ★ Aha or a teammate deals DMG, additionally applies the "Elation Debt" effect onto the enemy target, equal to 25% of their HP loss. "Elation Debt" persists through the enemy target's phase transition, capped at 10% of the target's Max HP.

### States & Terms (mechanics new in 4.7; nanoka glossary verbatim)

| Term | Entry |
|---|---|
| "Elation" Path Ascension | While Aeon ★ Aha holds the "Faces of Elation" state, "Punchline" and "Certified Banger" get enhanced to "Bliss" and "Party Trick" respectively, and ally characters on the Path of Elation will activate their "Innate Trace" effects. |
| Elation Debt | Elation Debt will claim part of Max HP. Any current HP within the claimed portion is lost immediately. |
| Aha | When taking action, triggers an Aha Instant and causes units capable of using Elation Skills to each use their Elation Skill 1 time. If there are no units capable of using Elation Skills when Aha takes action, Aha will use "Let There Be Laughter." The Aha Instant lasts until the final Elation Skill finishes this time. When the Aha Instant ends, participating characters gain the "Certified Banger" state for the Punchline points taken into account this time, lasting for 2 turns. After Aha takes action, all Punchlines will be consumed. |
| Punchline | Punchline is shared by the whole team. When dealing Elation DMG, the more Punchline taken into account, the higher the Elation DMG. |
| Certified Banger | Characters participating in the Aha Instant gain the "Certified Banger" state. And the Punchline points from the current Aha Instant are taken into account for this state, lasting for 2 turns. Ability effects and Elation DMG produced by the "Certified Banger" state are calculated based on the Punchline points taken into account. Punchline points taken into account for multiple "Certified Banger" states are combined for the calculation. The duration of each "Certified Banger" state is tracked independently. |
| Elation DMG | The more Punchline taken into account, and the higher the Elation and Character Level, the greater the Elation DMG dealt. Elation DMG is not affected by DMG Boost effects. |
| True DMG | Non-Type DMG that is not affected by any effects. This DMG is not considered as launching 1 attack. |
| Action Advance | Reduces the target's waiting interval before the next action. |
| Follow-Up ATK | Unleashes an extra attack on the target. This effect is triggered automatically when requirements are met. |

## Trace Bonuses

| No. | Name | Unlock | Effect | Unlock Materials |
|---|---|---|---|---|
| A2 | A Prank on Aeons | Ascension 2 | Skill's Follow-Up ATK additionally deals 20% Elation DMG of the same Type as the target who holds the "Emanator of Elation" state, and recovers 1 Skill Point(s). This additionally dealt Elation DMG is not considered as an instance of attack. | [[zh_cn/items/Virtual/Virtual/信用点\|Credit]]×5,000 · [[zh_cn/items/Material/TracePath/《绒绒号》手绘分镜稿\|The Fluffy Hand-drawn Storyboards]]×2 · [[zh_cn/items/Material/WeeklyMonsterDrop/伪觉者的期许\|High Hopes of the Falsely Enlightened]]×1 |
| A4 | A Carnival in Whimsy | Ascension 4 | When receiving healing or a Shield provided by a teammate, gains 1 "Wishpower." This can be triggered up to 1 time(s). The trigger count resets after the Ultimate is used. | [[zh_cn/items/Virtual/Virtual/信用点\|Credit]]×20,000 · [[zh_cn/items/Material/TracePath/《绒绒号》连载纪念刊\|The Fluffy Serialization Memorial Issue]]×4 · [[zh_cn/items/Material/WeeklyMonsterDrop/命运的足迹\|Tracks of Destiny]]×1 · [[zh_cn/items/Material/WeeklyMonsterDrop/伪觉者的期许\|High Hopes of the Falsely Enlightened]]×1 |
| A6 | A Box of Everything | Ascension 6 | When Aeon ★ Aha's SPD reaches 125/150 or higher, the Elation stat increases by 120%/150%, respectively. When combat starts, own action advances by 30%. | [[zh_cn/items/Virtual/Virtual/信用点\|Credit]]×140,000 · [[zh_cn/items/Material/TracePath/《绒绒号》典藏版合集\|The Fluffy Collector's Edition]]×8 · [[zh_cn/items/Material/WeeklyMonsterDrop/命运的足迹\|Tracks of Destiny]]×1 · [[zh_cn/items/Material/WeeklyMonsterDrop/伪觉者的期许\|High Hopes of the Falsely Enlightened]]×1 |

> Stat nodes (10 in total) are summed in "Stat Bonuses"; the material column lists the single-node cost from nanoka `material_list`.

> Trace A6 values: nanoka `point08` `param_list` = [125, 150, 1.2, 1.5, 0.3], converted under the library's ratio convention (ratio parameters ×100%) → Elation +120%/+150% at SPD ≥125/150 and 30% action advance when combat starts. Values at this tier are unusually large; if the official site later publishes its own English wording, the official text takes precedence.

## Stat Bonuses

| Attribute | Bonus |
|---|---|
| CRIT DMG | 37.3% |
| CRIT Rate | 12.0% |
| SPD | +5 |

> Summed over all stat nodes in nanoka `skill_trees` `status_add_list`: CRIT DMG 5.3%+5.3%+8%+8%+10.7% = 37.3%, CRIT Rate 2.7%+4%+5.3% = 12%, SPD +2+3 = +5.

## Eidolons

| Eidolon | Name | Effect |
|---|---|---|
| E1 | Who Giggled at the Primordial Hush? | When entering combat, immediately gains 5 "Wishpower." When Aeon ★ Aha is present, Elation DMG dealt by all ally targets merrymakes by 15%. |
| E2 | Between THEIR Eyes and Yours | Enhances the "Elation" Path Ascension effects: upgrades "Faces of Elation ★ Ex Nihilo" from Lv.1 (30% DEF ignore / 12% CRIT Rate) to Lv.2 (60% DEF ignore / 20% CRIT Rate); the 10% Bliss recovery ratio is unchanged (nanoka references series skill `151129` Lv.2; values taken from the Innate Trace parameter table). |
| E3 | A Stacked Deck of Sorrow and Joy | Ultimate Lv. +2, up to a maximum of Lv. 15. Basic ATK Lv. +1, up to a maximum of Lv. 10. Elation Skill Lv. +1, up to a maximum of Lv. 15. |
| E4 | A Joke's Fate Boxed in Black | The multiplier of the True DMG dealt by Elation Skill increases by 25% of its original value. When Aeon ★ Aha deals Elation DMG, an additional 100% of the total "Certified Banger" held by teammates will be taken into account. |
| E5 | Moi Onstage and Me Offstage | Skill Lv. +2, up to a maximum of Lv. 15. Talent Lv. +2, up to a maximum of Lv. 15. Elation Skill Lv. +1, up to a maximum of Lv. 15. |
| E6 | For THEY Said: You Are Elation | Enemy targets always carry an "Elation Debt" effect that claims at least 20% of their Max HP. After Aeon ★ Aha uses Ultimate for the first time, Aha's action advances by 100%, and Aha gains 100 Punchline. |

> Source: nanoka 4.7.51 `ranks` (E1–E6 names and English effect text, placeholders resolved from `param_list`); the E2 series-skill reference is expanded with the `151129` Lv.2 parameters.

## Recommended Relics

**Main stats**（nanoka `relics.property_list`）: Body CRIT Rate / CRIT DMG · Feet SPD · Link Rope HP% · Planar Sphere DEF%

**Recommended sub-stats**: CRIT Rate / CRIT DMG / SPD

#### 4-Piece Set

| Relic Set |
|---|
| [[zh_cn/relic/隧洞遗器/戏梦点星的伶人\|Dreamlit Actor]] |
| [[zh_cn/relic/隧洞遗器/应天涉远的卜者\|Diviner of Distant Reach]] |
| [[zh_cn/relic/隧洞遗器/重循苦旅的司铎\|Sacerdos' Relived Ordeal]] |

#### 2-Piece Set

| Relic Set |
|---|
| [[zh_cn/relic/位面饰品/神的瞬息欢愉\|God's Moment of Joy]] |
| [[zh_cn/relic/位面饰品/生命的翁瓦克\|Sprightly Vonwacq]] |
| [[zh_cn/relic/位面饰品/折断的龙骨\|Broken Keel]] |

> Set lists are taken from nanoka `relics.set4_id_list` = [133, 130, 121] and `set2_id_list` = [329, 308, 310], aligned to the library's relic files by entity ID (no additions or omissions). The 4.7 Planar Ornament "God's Moment of Joy" is entity ID 329.

> Recommended Light Cones: 5★ "Upon the First Echo of 'Aha' (Elation)" (entity ID 23065, Version 4.7 Update Details), 5★ "Tomorrow, Together (Elation)," 4★ "Mushy Shroomy's Adventures (Elation)" — taken from nanoka `lightcones` = [23065, 22007, 21064]. All three have entries under `zh_cn/lightcone/欢愉/`; this card's write scope is limited to `en_us/character/**`, so no cross-category double links are added here.

---

*文件生成时间：2026-11-14 · Entity data from nanoka 4.7.51 character 1511 (`/en/character/1511.json`) and the Version 4.7 Update Details "2. New Character" section; English name "Aeon ★ Aha" is the official English name. Character stories: all five `chara_info.stories` entries are `null` and the official notice publishes none → no "Character Story" section is created, per the sourcing discipline. Values (stats / materials / effect numbers) are identical to the zh_cn source file `zh_cn/character/欢愉/星神★阿哈_量子_五星.md`.*
