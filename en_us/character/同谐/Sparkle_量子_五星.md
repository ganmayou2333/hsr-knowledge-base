# Sparkle

> 数据来源：[https://hsr.nanoka.cc/character/1306](https://hsr.nanoka.cc/character/1306)
> 官方Wiki：[https://bbs.mihoyo.com/sr/wiki/content/2087/detail](https://bbs.mihoyo.com/sr/wiki/content/2087/detail)
> 数据版本：4.5
> 实体ID：1306

---

## Basic Info

| Attribute | Value |
|---|---|
| Character Name | Sparkle |
| Path | Harmony |
| Attribute | Quantum |
| Rarity | ★★★★★ |
| Faction | 假面愚者 |
| Introduction | A member of the Masked Fools, passionate yet unpredictable. She roams between major factions, amusing herself by turning the world upside down on her own. |
| Role | An auxiliary character that recovers and increases the maximum amount of combat skill points for our side. |

### Voice Actors

| Language | VA |
|---|---|
| Japanese | 上田麗奈 |
| English | Lizzie Freeman |
| Chinese | 赵爽 |
| Korean | 성예원 |

---

## Base Stats (Lv.80)

| Attribute | Value |
|---|---|
| Base HP | 1,397 |
| Base ATK | 524 |
| Base DEF | 485 |
| Base SPD | 101 |
| Taunt | 100 |
| Max Energy | 110 |

---

## Ascension Materials (Lv.1 → Lv.80)

| Materials | Qty |
|---|---|
| [[zh_cn/items/Virtual/Virtual/信用点\|Credit]] | 308,000 |
| [[zh_cn/items/Material/AvatarRank/炙梦喷枪\|Dream Flamer]] | 65 |
| [[zh_cn/items/Material/CommonMonsterDrop/思绪末屑\|Tatters of Thought]] | 15 |
| [[zh_cn/items/Material/CommonMonsterDrop/印象残晶\|Fragments of Impression]] | 15 |
| [[zh_cn/items/Material/CommonMonsterDrop/欲念碎镜\|Shards of Desires]] | 15 |

---
## Skill Materials

Skill level cap: Basic ATK 1→6 / Skill 1→10 / Ultimate 1→10 / Talent 1→10

| Materials | Qty |
|---|---|
| [[zh_cn/items/Virtual/Virtual/信用点\|Credit]] | 2,197,500 |
| [[zh_cn/items/Material/WeeklyMonsterDrop/命运的足迹\|Tracks of Destiny]] | 6 |
| [[zh_cn/items/Material/TracePath/云际音符\|Firmament Note]] | 12 |
| [[zh_cn/items/Material/TracePath/空际小节\|Celestial Section]] | 53 |
| [[zh_cn/items/Material/TracePath/天外乐章\|Heavenly Melody]] | 101 |
| [[zh_cn/items/Material/WeeklyMonsterDrop/蛀星孕灾的旧恶\|Past Evils of the Borehole Planet Disaster]] | 9 |
| [[zh_cn/items/Material/CommonMonsterDrop/思绪末屑\|Tatters of Thought]] | 33 |
| [[zh_cn/items/Material/CommonMonsterDrop/印象残晶\|Fragments of Impression]] | 46 |
| [[zh_cn/items/Material/CommonMonsterDrop/欲念碎镜\|Shards of Desires]] | 28 |

---
## Skills
### Basic ATK：Monodrama
- **Type**：Basic ATK
- **Summary**：Deals minor Quantum DMG to one enemy.
- **Max Level**：10
- **Effect Template**：Deals Quantum DMG equal to #1[i]% of Sparkle's ATK to one designated enemy.

- **Level Table**：
| Level | 参数1(%) |
  |---|---|
  | Lv.1 | 50% |
  | Lv.2 | 60% |
  | Lv.3 | 70% |
  | Lv.4 | 80% |
  | Lv.5 | 90% |
  | Lv.6 | 100% |
  | Lv.7 | 110% |
  | Lv.8 | 120% |
  | Lv.9 | 130% |
  | Lv.10 | 140% |

- **Parameter Notes**：
  - `#1[i]`% → 参数1(%)：上下文「方单体造成等同于花火___%攻击力的量子属性」

- **Max Effect**：Deals Quantum DMG equal to 140% of Sparkle's ATK to one designated enemy.

### Skill：Dreamdiver
- **Type**：Skill
- **Summary**：Increases an ally's CRIT DMG and advances their action.
- **Max Level**：15
- **Effect Template**：Increases the CRIT DMG of a designated ally by #1[f1]% of Sparkle's CRIT DMG plus #2[f1]%, lasting for #3[i] turn(s). And at the same time, advances this ally's action by #4[i]%.
When Sparkle uses this ability on herself, the Action Advance effect will not trigger.

- **Level Table**：
| Level | 参数1 | 参数2 | 参数3 | 参数4(%) |
  |---|---|---|---|---|
  | Lv.1 | 12% | 27% | 1 | 50% |
  | Lv.2 | 13.2% | 28.8% | 1 | 50% |
  | Lv.3 | 14.4% | 30.6% | 1 | 50% |
  | Lv.4 | 15.6% | 32.4% | 1 | 50% |
  | Lv.5 | 16.8% | 34.2% | 1 | 50% |
  | Lv.6 | 18% | 36% | 1 | 50% |
  | Lv.7 | 19.5% | 38.25% | 1 | 50% |
  | Lv.8 | 21% | 40.5% | 1 | 50% |
  | Lv.9 | 22.5% | 42.75% | 1 | 50% |
  | Lv.10 | 24% | 45% | 1 | 50% |
  | Lv.11 | 25.2% | 46.8% | 1 | 50% |
  | Lv.12 | 26.4% | 48.6% | 1 | 50% |
  | Lv.13 | 27.6% | 50.4% | 1 | 50% |
  | Lv.14 | 28.8% | 52.2% | 1 | 50% |
  | Lv.15 | 30% | 54% | 1 | 50% |

- **Parameter Notes**：
  - 参数1：效果模板中无对应 `#1[i]` 占位符（预留参数/其他属性）
  - 参数2：效果模板中无对应 `#2[i]` 占位符（预留参数/其他属性）
  - `#3[i]`回 → 参数3：上下文「#2[f1]%，持续___回合，并使该目标行」
  - `#4[i]`% → 参数4(%)：上下文「，并使该目标行动提前___%。 当花火对自身」

- **Max Effect**：Increases the CRIT DMG of a designated ally by #1[f1]% of Sparkle's CRIT DMG plus #2[f1]%, lasting for 1 turn(s). And at the same time, advances this ally's action by 50%.
When Sparkle uses this ability on herself, the Action Advance effect will not trigger.

### Ultimate：The Hero with a Thousand Faces
- **Type**：Ultimate
- **Summary**：Recovers Skill Points for allies and additionally increases the Vulnerability effect provided by Sparkle's Talent.
- **Max Level**：15
- **Effect Template**：Recovers #2[i] Skill Point(s) for allies. If Skill Points overflow during recovery, the excess points will be recorded, up to a max of #5[i] points. When an ally character's turn ends, if Skill Points are below the maximum, Sparkle consumes the recorded value to recover Skill Points until the upper limit is reached. Then, grants all allies "Cipher." For ally targets with "Cipher," each stack of Boost of DMG taken by enemies provided by Sparkle's Talent additionally increases by #3[f2]%, lasting for #4[i] turn(s).

- **Level Table**：
| Level | 参数1 | 参数2 | 参数3 | 参数4 |
  |---|---|---|---|---|
  | Lv.1 | 2 | 4 | 6% | 2 |
  | Lv.2 | 2 | 4 | 6.4% | 2 |
  | Lv.3 | 2 | 4 | 6.8% | 2 |
  | Lv.4 | 2 | 4 | 7.2% | 2 |
  | Lv.5 | 2 | 4 | 7.6% | 2 |
  | Lv.6 | 2 | 4 | 8% | 2 |
  | Lv.7 | 2 | 4 | 8.5% | 2 |
  | Lv.8 | 2 | 4 | 9% | 2 |
  | Lv.9 | 2 | 4 | 9.5% | 2 |
  | Lv.10 | 2 | 4 | 10% | 2 |
  | Lv.11 | 2 | 4 | 10.4% | 2 |
  | Lv.12 | 2 | 4 | 10.8% | 2 |
  | Lv.13 | 2 | 4 | 11.2% | 2 |
  | Lv.14 | 2 | 4 | 11.6% | 2 |
  | Lv.15 | 2 | 4 | 12% | 2 |

- **Parameter Notes**：
  - 参数1：效果模板中无对应 `#1[i]` 占位符（预留参数/其他属性）
  - `#2[i]`个 → 参数2：上下文「为我方恢复___个战技点，并使我方」
  - 参数3：效果模板中无对应 `#3[i]` 占位符（预留参数/其他属性）
  - `#4[i]`回 → 参数4：上下文「#3[f1]%，持续___回合。」

- **Max Effect**：Recovers 4 Skill Point(s) for allies. If Skill Points overflow during recovery, the excess points will be recorded, up to a max of #5[i] points. When an ally character's turn ends, if Skill Points are below the maximum, Sparkle consumes the recorded value to recover Skill Points until the upper limit is reached. Then, grants all allies "Cipher." For ally targets with "Cipher," each stack of Boost of DMG taken by enemies provided by Sparkle's Talent additionally increases by #3[f2]%, lasting for 2 turn(s).

### Talent：Red Herring
- **Type**：Talent
- **Summary**：Increases the team's Max Skill Points. Whenever an ally target consumes Skill Points, Sparkle gains 1 stack of "Figment." Each stack of "Figment" increases the DMG taken by all enemies.
- **Max Level**：15
- **Effect Template**：While Sparkle is on the battlefield, additionally increases the max number of Skill Points by #3[i]. Whenever an ally target consumes 1 Skill Point, Sparkle gains 1 stack of "Figment," with each stack increasing the DMG taken by all enemies by #2[f1]%. This effect lasts for #1[i] turn(s) and can stack up to #4[i] time(s).

- **Level Table**：
| Level | 参数1 | 参数2 | 参数3 | 参数4 |
  |---|---|---|---|---|
  | Lv.1 | 2 | 3% | 2 | 3 |
  | Lv.2 | 2 | 3.3% | 2 | 3 |
  | Lv.3 | 2 | 3.6% | 2 | 3 |
  | Lv.4 | 2 | 3.9% | 2 | 3 |
  | Lv.5 | 2 | 4.2% | 2 | 3 |
  | Lv.6 | 2 | 4.5% | 2 | 3 |
  | Lv.7 | 2 | 4.88% | 2 | 3 |
  | Lv.8 | 2 | 5.25% | 2 | 3 |
  | Lv.9 | 2 | 5.63% | 2 | 3 |
  | Lv.10 | 2 | 6% | 2 | 3 |
  | Lv.11 | 2 | 6.3% | 2 | 3 |
  | Lv.12 | 2 | 6.6% | 2 | 3 |
  | Lv.13 | 2 | 6.9% | 2 | 3 |
  | Lv.14 | 2 | 7.2% | 2 | 3 |
  | Lv.15 | 2 | 7.5% | 2 | 3 |

- **Parameter Notes**：
  - `#1[i]`回 → 参数1：上下文「f1]%，该效果持续___回合，最多可叠加#」
  - 参数2：效果模板中无对应 `#2[i]` 占位符（预留参数/其他属性）
  - `#3[i]`点 → 参数3：上下文「，战技点上限额外增加___点。当我方目标每消」
  - `#4[i]`层 → 参数4：上下文「i]回合，最多可叠加___层。」

- **Max Effect**：While Sparkle is on the battlefield, additionally increases the max number of Skill Points by 2. Whenever an ally target consumes 1 Skill Point, Sparkle gains 1 stack of "Figment," with each stack increasing the DMG taken by all enemies by #2[f1]%. This effect lasts for 2 turn(s) and can stack up to 3 time(s).

### Technique：Unreliable Narrator
- **Type**：Technique
- **Summary**：After using Technique, grants all allies Misdirect. Characters with Misdirect will not be detected by enemies, and entering combat while in Misdirect recovers Skill Points for allies and regenerates Energy for Sparkle.
- **Max Level**：1
- **Effect Template**：After using Technique, grants all allies Misdirect for #2[i] seconds. Characters with Misdirect will not be detected by enemies, and entering combat in the Misdirect state recovers #1[i] Skill Point(s) for the team and regenerates #2[i] Energy for Sparkle.

- **Level Table**：
| Level | 参数1 | 参数2 |
  |---|---|---|
  | Lv.1 | 3 | 20 |

- **Parameter Notes**：
  - `#1[i]`个 → 参数1：上下文「进入战斗时为我方恢复___个战技点。」
  - `#2[i]`秒 → 参数2：上下文「后，我方全体进入持续___秒的【迷误】状态。」

- **Max Effect**：After using Technique, grants all allies Misdirect for 20 seconds. Characters with Misdirect will not be detected by enemies, and entering combat in the Misdirect state recovers 3 Skill Point(s) for the team and regenerates 20 Energy for Sparkle.

## Trace Bonuses

| No. | Name | Unlock Condition | Effect Template | Effect | 解锁材料 |
|---|---|---|---|---|---|
| 附加能力1 | 岁时记 | 晋阶2 | 施放普攻时额外恢复#1[i]点能量。 | 施放普攻时额外恢复10点能量。 | 信用点×5000、云际音符×3、蛀星孕灾的旧恶×1 |
| 附加能力2 | 人造花 | 晋阶4 | 战技提供的暴击伤害提高效果会延长到目标下一个回合开始。 | 战技提供的暴击伤害提高效果会延长到目标下一个回合开始。 | 信用点×20000、空际小节×5、命运的足迹×1、蛀星孕灾的旧恶×1 |
| 附加能力3 | 夜想曲 | 晋阶6 | 我方全体的攻击力提高#4[i]%。当我方队伍中存在1名/2名/3名量子属性的角色时，我方量子属性的角色的攻击力额外提高#1[i]%/#2[i]%/#3[i]%。 | 我方全体的攻击力提高15%。当我方队伍中存在1名/2名/3名量子属性的角色时，我方量子属性的角色的攻击力额外提高5%/15%/30%。 | 信用点×160000、天外乐章×8、命运的足迹×1、蛀星孕灾的旧恶×1 |

## Stat Bonuses

| Attribute | 加成 |
|---|---|
| HP | 28% |
| 暴击伤害 | 24% |
| 效果抵抗 | 10% |

---

## Eidolons

| Eidolons | Name | Effect |
|---|---|---|
| E1 | Suspension of Disbelief | The Cipher effect granted by the Ultimate lasts for 1 extra turn. All allies with Cipher have their ATK increased by 40%. |
| E2 | Purely Fictitious | Every stack of the Talent's effect allows allies to additionally ignore 8% of the target's DEF when dealing DMG. |
| E3 | Pipedream | Skill Lv. +2, up to a maximum of Lv. 15.<br>Basic ATK Lv. +1, up to a maximum of Lv. 10. |
| E4 | Life Is a Gamble | The Ultimate recovers 1 more Skill Point. The Talent additionally increases the Max Skill Points by 1. |
| E5 | Parallax Truth | Ultimate Lv. +2, up to a maximum of Lv. 15.<br>Talent Lv. +2, up to a maximum of Lv. 15. |
| E6 | Narrative Polysemy | The CRIT DMG Boost effect provided by the Skill additionally increases by an amount equal to 30% of Sparkle's CRIT DMG. When Sparkle uses Skill, her Skill's CRIT DMG Boost effect will apply to all teammates with Cipher. When Sparkle uses her Ultimate, any single ally who benefits from her Skill's CRIT DMG Boost will spread that effect to teammates with Cipher. |

---

## Recommended Relics

**主词条推荐**：暴击伤害 / 速度 / 生命值 / 能量恢复效率

**推荐副词条**：暴击伤害 / 速度 / 效果抵抗

#### 4-Piece Set

| Relic Set | Effect |
|---|---|
| [[zh_cn/relic/隧洞遗器/重循苦旅的司铎\|Sacerdos' Relived Ordeal]] | 对我方单体目标施放战技或终结技时，使技能目标的暴击伤害提高18%，持续2回合，该效果最多叠加2次。 |
| [[zh_cn/relic/隧洞遗器/骇域漫游的信使\|Messenger Traversing Hackerspace]] | 当装备者对我方目标施放终结技时，我方全体速度提高12%，持续1回合，该效果无法叠加。 |
| [[zh_cn/relic/隧洞遗器/晨昏交界的翔鹰\|Eagle of Twilight Line]] | 当装备者施放终结技后，使其行动提前25%。 |

#### 2-Piece Set

| Relic Set | Effect |
|---|---|
| [[zh_cn/relic/位面饰品/沉陆海域露莎卡\|Lushaka, the Sunken Seas]] | 使装备者的能量恢复效率提高5%，如果装备者不是编队中的第一位角色，使编队中的第一位角色攻击力提高12%。 |
| [[zh_cn/relic/位面饰品/折断的龙骨\|Broken Keel]] | 使装备者的效果抵抗提高10%。当装备者的效果抵抗大于等于30%时，我方全体暴击伤害提高10%。 |
| [[zh_cn/relic/位面饰品/梦想之地匹诺康尼\|Penacony, Land of the Dreams]] | 使装备者的能量恢复效率提高5%。使队伍中与装备者属性相同的我方其他角色造成的伤害提高10%。 |

---

## Recommended Light Cones

### [[zh_cn/lightcone/同谐/游戏尘寰.md|Earthly Escapade]]

- **Base Stats**：HP1164 ATK529 DEF463
- **Rating**：★★★★★
- **Skill Name**：Capriciousness
- **Effect**：Increases the wearer's CRIT DMG by 32%. At the start of the battle, the wearer gains Mask, lasting for 3 turn(s). While the wearer has Mask, the wearer's teammates have their CRIT Rate increased by 10% and their CRIT DMG increased by 28%. For every 1 Skill Point the wearer recovers (including Skill Points that exceed the limit), they gain 1 stack of Radiant Flame. And when the wearer has 4 stacks of Radiant Flame, all the stacks are removed, and they gain Mask, lasting for 4 turn(s).

### [[zh_cn/lightcone/同谐/但战斗还未结束.md|But the Battle Isn't Over]]

- **Base Stats**：HP1164 ATK529 DEF463
- **Rating**：★★★★★
- **Skill Name**：Heir
- **Effect**：Increases the wearer's Energy Regeneration Rate by 10% and regenerates 1 Skill Point when the wearer uses their Ultimate on an ally. This effect can be triggered once after every 2 uses of the wearer's Ultimate. When the wearer uses their Skill, the next ally taking action (except the wearer) deals 30% more DMG for 1 turn(s).

### [[zh_cn/lightcone/同谐/舞！舞！舞！.md|Dance! Dance! Dance!]]

- **Base Stats**：HP952 ATK423 DEF396
- **Rating**：★★★★
- **Skill Name**：Cannot Stop It!
- **Effect**：When the wearer uses their Ultimate, all allies' actions are Advanced Forward by 16%.

### [[zh_cn/lightcone/同谐/过往未来.md|Past and Future]]

- **Base Stats**：HP952 ATK423 DEF396
- **Rating**：★★★★
- **Skill Name**：Kites From the Past
- **Effect**：When the wearer uses their Skill, the next ally taking action (except the wearer) deals 16% increased DMG for 1 turn(s).

### 与行星相会（量子队可用）

- **Base Stats**：HP1058 ATK423 DEF330
- **Rating**：★★★★
- **Skill Name**：Kites From the Past
- **Effect**：When the wearer uses their Skill, the next ally taking action (except the wearer) deals 16% increased DMG for 1 turn(s).

### [[zh_cn/lightcone/同谐/回到大地的飞行.md|A Grounded Ascent]]

- **Base Stats**：HP1164 ATK476 DEF529
- **Rating**：★★★★★
- **Skill Name**：Departing Anew
- **Effect**：After the wearer uses Skill or Ultimate on one ally character, the wearer regenerates #1[f1] Energy and the ability's target receives 1 stack of "Hymn" for 3 turn(s), stacking up to 3 time(s). Each stack of "Hymn" increases its holder's DMG dealt by 15%. After every 2 instance(s) of Skill or Ultimate the wearer uses on one ally character, recovers 1 Skill Point.

## Recommended Teams

| 主C | 辅助 | 生存 |
|---|---|---|
| [[zh_cn/character/巡猎/希儿_量子_五星.md\|Seele]] | [[zh_cn/character/同谐/花火_量子_五星.md\|花火]] | [[zh_cn/character/虚无/银狼_量子_五星.md\|银狼]] |
| [[zh_cn/character/存护/符玄_量子_五星.md\|符玄]] | [[zh_cn/character/毁灭/丹恒•饮月_虚数_五星.md\|丹恒•饮月]] | [[zh_cn/character/虚无/椒丘_火_五星.md\|椒丘]] |
| [[zh_cn/character/存护/砂金_虚数_五星.md\|Aventurine]] | [[zh_cn/character/虚无/黄泉_雷_五星.md\|Acheron]] | [[zh_cn/character/记忆/开拓者_冰_五星.md\|开拓者•记忆]] |
| [[zh_cn/character/记忆/开拓者_冰_五星.md\|开拓者•记忆]] | [[zh_cn/character/丰饶/玲可_量子_四星.md\|玲可]] | [[zh_cn/character/巡猎/Archer_量子_五星.md\|Archer]] |
| [[zh_cn/character/欢愉/爻光_物理_五星.md\|Yao Guang]] | [[zh_cn/character/存护/丹恒•腾荒_物理_五星.md\|Dan Heng • Permansor Terrae]] | [[zh_cn/character/智识/青雀_量子_四星.md\|青雀]] |

*文件生成时间：2026-08-27*

## Character Story
「假面愚者」的成员之一，难以捉摸，不择手段。
危险的戏剧大师，沉迷于扮演，身怀千张假面，能化万种面相。
财富、地位、权力…于花火而言都不重要，能让她出手的，唯有「乐趣」。

### Character Story·1（解锁条件：Character Level 20）

女孩是被遗弃的孤儿，活着，却不知自己在哪，从何而来，要往哪去——直到那个戏团路过，她跑去看，远远看到黑色双马尾少女像一条鱼，从舞台的这侧游到那侧。少女戴着面具，很多种面具，但这不妨碍她在舞台上的大笑与痛哭，即使与观众离得那么远，却像在他们眼皮底子下表演。游鱼也悄无声息地在女孩的面前跃起，再入水，泛起涟漪。

她才逐渐意识到自己的行为，是「自己」在「舞台下」观看「表演」。

她又去看了很多次，不分早晚。但她仍旧只是观众，舞台上的聚光灯不会落在自己身上。散场后，她去了后台，黑色双马尾少女递来一个面具。
「我可以吗？」
「为什么不呢？反正戴着面具，他们认为你是『花火』，那你就是。去吧。」

作为第四面墙的幕布拉开，灯光还没亮起，她看着台下，那儿只有一个黑洞，即使隔着面具也令人难安。她知道黑洞里坐着密密麻麻的人，他们看得到她，还听得到她说话，她总忍不住想着「花火」的表演，想调整自己的动作、声音、仪态，方方面面。

「就第一次来说，做得非常不错。」
「但那和你的『花火』…不一样。」
「这是个问题，但你不让别人知道，就不是问题…而且明天戏团就要走啦，所以只要你想，在这儿你就是花火，花火就是你。你想让她是什么样，就是什么样。」
她欲言又止，少女揉揉她的脑袋。
「除了你也没多少人来看我们，小戏团嘛，我们也不指望自己能扬名银河…偶尔能碰见你这样的孩子，能记住有这么个角色叫『花火』，就足够我高兴好一阵子啦…别哭，这个面具你留着，这就是你的面具。」
她点点头。
「听好了，只要戴上面具，你谁都是，也谁都不是…要是真想当演员，就别只盯着这个小小的台子，去更大的地方吧。」

### Character Story·2（解锁条件：Character Level 40）

女孩身为人偶一族的末裔，没有选择的权利，她拿到的是哪个面具，就必须依据「面具」的安排度过此生。人偶只是「面具」的载体罢了。

在他们的传说中，面具与人偶融合得越久，便越有可能使人偶获得灵魂，让他们看上去和「人」无异。但在人类的传说中，面具成了能令死去之人复生的工具——正因如此，她的族人日渐稀少。

然而她对成为人不感兴趣，只当个按部就班的人偶也不是什么坏事，反而遵守面具的命令，恐怕难逃被追杀的下场，但面具的意志却难以违背。

首先是动作。
按「面具」的意志，她开心时要露出甜美的笑，哭泣时要以手扶额，愤怒时要从齿缝里挤出字来，嫉妒时则要斜着眼睛，绝望时要大呼小叫。还有一些标志性的动作，比如她微微挑眉时必须要以左侧脸面向对方，表达爱意可以将手抬起，表现捂胸口的趋势，但最后得把手放下，因为轻咬下唇才能体现她真正的心意。

然后是声音。
按「面具」的意志，她快乐时的声调就应该高高扬起，抒情时就得柔声蜜语，陈述时就得沉稳平直，仇恨时就得咬牙切齿，悲伤时哭腔则是不可或缺的。

神奇的是，她就这样生活了许多年，完全融入了周围的环境，甚至成为了一名剧作家。从没有人怀疑她戴着面具。但她也禁不住思考，世界上有没有另外一种「面具」。也许戴上面具的人，会哈哈大笑着复仇，会眼含热泪着微笑，或者愤怒时则一言不发…也许会用最平静的语气，说着最刻薄的话。

由于「面具」的意志，她自然无法做到这点，但她是一名剧作家，让舞台上的角色如此表演，对她来说还是易如反掌。

某一天早晨，门铃响了，但门口不是她熟悉的邮递员。
「花火小姐，请问现在方便么？」
「我们看了您的新作，不知您是否对『面具』，有所了解呢……」


### Character Story·3（解锁条件：Character Level 60）

无貌的少女意识到自己一定受到了某种诅咒，不然为什么感受不到任何外部的刺激？痛感、味觉、嗅觉都很正常，她却无法对此做出反应，自然也丧失了喜怒哀乐，体会各种情绪的能力。她只能尽力弥补，试图提供不同的场景，通过观察来询问其他人的感受。

「…如果你在喝一杯很苦的茶，你觉得怎么样？会怎么喝？」
虽然被绑在椅子上不得动弹，但左边的流浪汉男士还是做出赞赏的姿势点点头，中间的女孩马上哭了起来，摇着头拒绝，右边的年长女士则嫌弃地皱了皱鼻子。

「如果你身处一个极其寒冷的小屋，手边只有这杯茶怎么办？」
男士自然不必说，女孩哭闹了一阵后接受了，女士则还是摆出拒绝的态度。

她不断变换预设，日以继夜地提问，直到受访者忍受不住昏了过去。她将他们送回家中，搜罗另一批人来接受她的采访。

那段时间，小镇里的居民都做着同一个噩梦，他们被关在一个地方，面容模糊的少女礼貌地向他们提问，他们没有拒绝的权利，只能对回答做一遍又一遍的补充，直到少女将每一处细节都面面俱到地记录在一个又一个纸面具上。一个写满了，就换下一个。

这个噩梦很快又被另一个噩梦取代了，居民们声称半夜会看到纸面具在空中飞舞，彼此交谈，它们隐隐发光，又转眼熄灭，就像夜空中的花火一般。他们每晚都会出现，仿佛是在小镇暗处生活的居民。

在一个幽暗的地下室，少女并不知晓这个噩梦。她搜集了足够多的资料——人们细微的情感，对不同事物的看法——用于制作更多的纸面具。她坚信，虽然自己无情无泪，但自己制作的那些面具却有血有肉，甚至终有一天，会成为真正的生命。

### Character Story·4（解锁条件：Character Level 80）

「有几个版本的身世特别招人喜欢。」到了愚者的「酒馆」，花火也只能大大方方地承认，「喜欢和相信是两码事，但大家更愿意相信自己喜欢的故事是真的。」

「撒谎？拜托，我不是为了讲一个精彩的故事，编一段博人眼球的经历…我是为了我自己才全心全意地锻炼和鞭策想象力，想象各种各样的生活，寻求刺激，然后尽我所能地表演、展现、还原，在想象力的气球爆破前的一秒，刹住车。」

「说真的，只有剧本当然不够，首先我自己就得毫无保留地相信我扮演的角色真的存在，然后我要想象这个角色还会出现在其他什么故事里，为了让表演的动机有逻辑，有情感，我总是要补充额外的信息。」

「然后，我觉得我才能抓住这个角色，不受其他人的影响。毕竟我可能还会碰到其他愚者，在确认彼此的身份前，我可不知道你们想干嘛。有时候，你们只是喜欢某个角色的外形，有时候你们就是想体验一下玩玩——我有时也会这样。」

「当然还有些人，只是把扮演当作一种交易手段，或者你们希望自己被当作其他人，因为这可能会带来不可预知的财富、地位、权力…总之我想说的是，在这样的环境里，除了我自己，谁能保证我不会偏离正轨，变成其他故事里的角色？没有！所以你看，我必须得不知疲倦地想象，还有扮演。」

「没有，我没有否认…这真的让我上瘾。我越想象，我就越沉迷于这些角色，沉迷于我为他们构造出的美妙的、悲惨的境遇，沉迷于他们在这些境遇下可能萌发的情绪……」

「当然，以前我当然想过那种人生…跟个戏团，当个演员，去不知名的星球表演几场，创造一个与自己同名的角色…但有一天，我突然想通了！」

「想要表演，还有比自己的人生更富感染力的舞台吗？」
