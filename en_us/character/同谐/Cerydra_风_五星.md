# Cerydra

> 数据来源：[https://hsr.nanoka.cc/character/1412](https://hsr.nanoka.cc/character/1412)
> 官方Wiki：[https://bbs.mihoyo.com/sr/wiki/content/5583/detail](https://bbs.mihoyo.com/sr/wiki/content/5583/detail)
> 数据版本：4.5
> 实体ID：1412

---

## 基本信息

| 属性 | 值 |
|---|---|
| 角色名称 | Cerydra |
| 命途 | Harmony |
| 属性 | Wind |
| 稀有度 | ★★★★★ |
| 阵营 | 翁法罗斯 |
| 角色介绍 | 北境帝国，失落的王朝，寒冷的疆土燃烧着征伐的野心。 君主刻律德菈，执握「律法」火种的黄金裔，布局设子，与神相弈，审判异心的罪囚，为此世奠定逐火的基业 ——「这绝非终点，翁法罗斯的征途，当是银河群星！」 |
| 城邦 | 奥赫玛 |
| 神权 | 「公正之秤，塔兰顿」 |
| 定位 | 可以使队友连续施放两次战技的辅助型角色 |

### 配音演员

| 语言 | 声优 |
|---|---|
| 日语 | 高尾奏音 |
| 英语 | Rhiannon Moushall |
| 中文 | 时欣蕾 |
| 韩语 | 김윤채 |

---

## 基础属性（Lv.80）

| 属性 | 数值 |
|---|---|
| 基础生命值 | 1,358 |
| 基础攻击力 | 621 |
| 基础防御力 | 485 |
| 基础速度 | 99 |
| 嘲讽 | 100 |
| 能量上限 | 130 |

---

## 晋阶材料（Lv.1 → Lv.80）

| 材料 | 数量 |
|---|---|
| [[zh_cn/items/Virtual/Virtual/信用点\|信用点]] | 308,000 |
| [[zh_cn/items/Material/AvatarRank/暮晖烬蕾\|暮晖烬蕾]] | 65 |
| [[zh_cn/items/Material/CommonMonsterDrop/预兆似有若无\|预兆似有若无]] | 15 |
| [[zh_cn/items/Material/CommonMonsterDrop/悲鸣由远及近\|悲鸣由远及近]] | 15 |
| [[zh_cn/items/Material/CommonMonsterDrop/哀叹漫无止息\|哀叹漫无止息]] | 15 |

---
## 技能材料

技能等级上限：普攻 1→6 / 战技 1→10 / 终结技 1→10 / 天赋 1→10

| 材料 | 数量 |
|---|---|
| [[zh_cn/items/Virtual/Virtual/信用点\|信用点]] | 2,197,500 |
| [[zh_cn/items/Material/WeeklyMonsterDrop/命运的足迹\|命运的足迹]] | 6 |
| [[zh_cn/items/Material/TracePath/云际音符\|云际音符]] | 12 |
| [[zh_cn/items/Material/TracePath/空际小节\|空际小节]] | 53 |
| [[zh_cn/items/Material/TracePath/天外乐章\|天外乐章]] | 101 |
| [[zh_cn/items/Material/WeeklyMonsterDrop/阳雷的遥想\|阳雷的遥想]] | 9 |
| [[zh_cn/items/Material/CommonMonsterDrop/预兆似有若无\|预兆似有若无]] | 33 |
| [[zh_cn/items/Material/CommonMonsterDrop/悲鸣由远及近\|悲鸣由远及近]] | 46 |
| [[zh_cn/items/Material/CommonMonsterDrop/哀叹漫无止息\|哀叹漫无止息]] | 28 |

---
## 战技
### 普攻：King's Castling
- **类型**：Basic ATK
- **简述**：Deals minor Wind DMG to one enemy.
- **最大等级**：10
- **效果模板**：Deals Wind DMG equal to #1[i]% of Cerydra's ATK to one designated enemy.

- **等级数值表**：
  | 等级 | 参数1(%) |
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

- **参数说明**：
  - `#1[i]`% → 参数1(%)：上下文「体造成等同于刻律德菈___%攻击力的风属性伤」

- **满级效果**：Deals Wind DMG equal to 140% of Cerydra's ATK to one designated enemy.

### 战技：Pawn's Promotion
- **类型**：Skill
- **简述**：Grants "Military Merit" to an ally character and gives Charge to Cerydra. When Charge reaches 6 points, automatically upgrades the ally character's "Military Merit" to "Peerage." The character with "Peerage" increases the CRIT DMG for their dealt Skill DMG, increases All-Type RES PEN, and can trigger Coup de Main.
- **最大等级**：15
- **效果模板**：Grants "Military Merit" to one designated ally character and gives Cerydra #2[i] points of Charge. Charge is capped at #3[i] points. When Charge reaches #4[i] points, automatically upgrades the character's "Military Merit" to "Peerage" and dispels their Crowd Control debuffs. The character with "Peerage" is considered to have "Military Merit" simultaneously. The character with "Peerage" increases the CRIT DMG for their dealt Skill DMG by #1[i]%, increases their All-Type RES PEN by #5[f1]%, and triggers Coup de Main when using their Skill on enemy targets. After Coup de Main ends, consumes #4[i] points of Charge to revert "Peerage" to "Military Merit."

- **等级数值表**：
  | 等级 | 参数1(%) | 参数2 | 参数3 | 参数4 | 参数5 |
  |---|---|---|---|---|---|
  | Lv.1 | 36% | 1 | 8 | 6 | 8% |
  | Lv.2 | 39.6% | 1 | 8 | 6 | 8.2% |
  | Lv.3 | 43.2% | 1 | 8 | 6 | 8.4% |
  | Lv.4 | 46.8% | 1 | 8 | 6 | 8.6% |
  | Lv.5 | 50.4% | 1 | 8 | 6 | 8.8% |
  | Lv.6 | 54% | 1 | 8 | 6 | 9% |
  | Lv.7 | 58.5% | 1 | 8 | 6 | 9.25% |
  | Lv.8 | 63% | 1 | 8 | 6 | 9.5% |
  | Lv.9 | 67.5% | 1 | 8 | 6 | 9.75% |
  | Lv.10 | 72% | 1 | 8 | 6 | 10% |
  | Lv.11 | 75.6% | 1 | 8 | 6 | 10.2% |
  | Lv.12 | 79.2% | 1 | 8 | 6 | 10.4% |
  | Lv.13 | 82.8% | 1 | 8 | 6 | 10.6% |
  | Lv.14 | 86.4% | 1 | 8 | 6 | 10.8% |
  | Lv.15 | 90% | 1 | 8 | 6 | 11% |

- **参数说明**：
  - `#1[i]`% → 参数1(%)：上下文「技伤害的暴击伤害提高___%、全属性抗性穿透」
  - `#2[i]`点 → 参数2：上下文「功】并使刻律德菈获得___点充能。充能上限#」
  - `#3[i]`点 → 参数3：上下文「i]点充能。充能上限___点。当充能达到#4」
  - `#4[i]`点 → 参数4：上下文「袭。奇袭结束后，消耗___点充能使【爵位】变」
  - 参数5：效果模板中无对应 `#5[i]` 占位符（预留参数/其他属性）

- **满级效果**：Grants "Military Merit" to one designated ally character and gives Cerydra 1 points of Charge. Charge is capped at 8 points. When Charge reaches 6 points, automatically upgrades the character's "Military Merit" to "Peerage" and dispels their Crowd Control debuffs. The character with "Peerage" is considered to have "Military Merit" simultaneously. The character with "Peerage" increases the CRIT DMG for their dealt Skill DMG by 90%, increases their All-Type RES PEN by #5[f1]%, and triggers Coup de Main when using their Skill on enemy targets. After Coup de Main ends, consumes 6 points of Charge to revert "Peerage" to "Military Merit."

### 终结技：Scholar's Mate
- **类型**：Ultimate
- **简述**：Gains Charge. Deals Wind DMG to all enemies.
- **最大等级**：15
- **效果模板**：Gains #2[i] Charge. Deals Wind DMG equal to #1[i]% of Cerydra's ATK to all enemies. If no character on the field has "Military Merit," prioritizes granting "Military Merit" to the first character in the current team.

- **等级数值表**：
  | 等级 | 参数1(%) | 参数2 |
  |---|---|---|
  | Lv.1 | 144% | 2 |
  | Lv.2 | 153.6% | 2 |
  | Lv.3 | 163.2% | 2 |
  | Lv.4 | 172.8% | 2 |
  | Lv.5 | 182.4% | 2 |
  | Lv.6 | 192% | 2 |
  | Lv.7 | 204% | 2 |
  | Lv.8 | 216% | 2 |
  | Lv.9 | 228% | 2 |
  | Lv.10 | 240% | 2 |
  | Lv.11 | 249.6% | 2 |
  | Lv.12 | 259.2% | 2 |
  | Lv.13 | 268.8% | 2 |
  | Lv.14 | 278.4% | 2 |
  | Lv.15 | 288% | 2 |

- **参数说明**：
  - `#1[i]`% → 参数1(%)：上下文「体造成等同于刻律德菈___%攻击力的风属性伤」
  - `#2[i]`点 → 参数2：上下文「获得___点充能。对敌方全体」

- **满级效果**：Gains 2 Charge. Deals Wind DMG equal to 288% of Cerydra's ATK to all enemies. If no character on the field has "Military Merit," prioritizes granting "Military Merit" to the first character in the current team.

### 天赋：Ave Imperator
- **类型**：Talent
- **简述**：The character with "Military Merit" increases their ATK. When they use Basic ATK or Skill, Cerydra gains Charge. After the character with "Military Merit" uses an attack, Cerydra additionally deals minor Wind Additional DMG.
- **最大等级**：15
- **效果模板**：The character with "Military Merit" increases ATK by an amount equal to #2[f1]% of Cerydra's ATK. When the character uses Basic ATK or Skill, Cerydra gains #1[i] Charge. During Coup de Main, Cerydra cannot gain Charge. After the character with "Military Merit" uses an attack, Cerydra additionally deals 1 instance of Wind Additional DMG equal to #3[i]% of her ATK. This effect can trigger up to #4[i] time(s). The trigger count resets every time Cerydra uses her Ultimate. "Military Merit" only takes effect on the most recent target. When the target changes, Cerydra's Charge is reset to 0.

- **等级数值表**：
  | 等级 | 参数1 | 参数2 | 参数3(%) | 参数4 |
  |---|---|---|---|---|
  | Lv.1 | 1 | 18% | 30% | 20 |
  | Lv.2 | 1 | 18.6% | 33% | 20 |
  | Lv.3 | 1 | 19.2% | 36% | 20 |
  | Lv.4 | 1 | 19.8% | 39% | 20 |
  | Lv.5 | 1 | 20.4% | 42% | 20 |
  | Lv.6 | 1 | 21% | 45% | 20 |
  | Lv.7 | 1 | 21.75% | 48.75% | 20 |
  | Lv.8 | 1 | 22.5% | 52.5% | 20 |
  | Lv.9 | 1 | 23.25% | 56.25% | 20 |
  | Lv.10 | 1 | 24% | 60% | 20 |
  | Lv.11 | 1 | 24.6% | 63% | 20 |
  | Lv.12 | 1 | 25.2% | 66% | 20 |
  | Lv.13 | 1 | 25.8% | 69% | 20 |
  | Lv.14 | 1 | 26.4% | 72% | 20 |
  | Lv.15 | 1 | 27% | 75% | 20 |

- **参数说明**：
  - `#1[i]`点 → 参数1：上下文「战技时使刻律德菈获得___点充能，奇袭期间无」
  - 参数2：效果模板中无对应 `#2[i]` 占位符（预留参数/其他属性）
  - `#3[i]`% → 参数3(%)：上下文「成1次等同于刻律德菈___%攻击力的风属性附」
  - `#4[i]`次 → 参数4：上下文「伤害，该效果最多触发___次，刻律德菈每次施」

- **满级效果**：The character with "Military Merit" increases ATK by an amount equal to #2[f1]% of Cerydra's ATK. When the character uses Basic ATK or Skill, Cerydra gains 1 Charge. During Coup de Main, Cerydra cannot gain Charge. After the character with "Military Merit" uses an attack, Cerydra additionally deals 1 instance of Wind Additional DMG equal to 75% of her ATK. This effect can trigger up to 20 time(s). The trigger count resets every time Cerydra uses her Ultimate. "Military Merit" only takes effect on the most recent target. When the target changes, Cerydra's Charge is reset to 0.

### 秘技：First-Move Advantage
- **类型**：Technique
- **简述**：Grants "Military Merit" to the current active character. Automatically uses Skill on the character with "Military Merit" at the start of the next battle.
- **最大等级**：1
- **效果模板**：After using Technique, gains "Military Merit." When switching the active character, "Military Merit" transfers to the current active character. At the start of the next battle, automatically uses Skill 1 time on the character with "Military Merit" without consuming any Skill Points.

- **满级效果**：After using Technique, gains "Military Merit." When switching the active character, "Military Merit" transfers to the current active character. At the start of the next battle, automatically uses Skill 1 time on the character with "Military Merit" without consuming any Skill Points.（参数见等级数值表）

## 附加能力（行迹）

| 编号 | 名称 | 解锁条件 | 效果模板 | 效果 | 解锁材料 |
|---|---|---|---|---|---|
| 附加能力1 | 来者 | 晋阶2 | 刻律德菈的攻击力大于#1[i]时，每超过#2[i]点攻击力可使自身暴击伤害提高#3[i]%，最多提高#4[i]%。 | 刻律德菈的攻击力大于2000时，每超过100点攻击力可使自身暴击伤害提高18%，最多提高360%。 | 信用点×5000、云际音符×3、阳雷的遥想×1 |
| 附加能力2 | 见者 | 晋阶4 | 刻律德菈的暴击率提高#1[i]%。当刻律德菈的充能小于上限时，持有【军功】的角色施放终结技时使刻律德菈获得#2[i]点充能，该效果单场战斗中可以触发1次。 | 刻律德菈的暴击率提高100%。当刻律德菈的充能小于上限时，持有【军功】的角色施放终结技时使刻律德菈获得1点充能，该效果单场战斗中可以触发1次。 | 信用点×20000、空际小节×5、命运的足迹×1、阳雷的遥想×1 |
| 附加能力3 | 征服者 | 晋阶6 | 施放战技时，使自身和持有【军功】的队友速度提高#2[i]点，持续#3[i]回合。持有【军功】的角色施放普攻或战技时，为刻律德菈恢复#1[i]点能量。 | 施放战技时，使自身和持有【军功】的队友速度提高20点，持续3回合。持有【军功】的角色施放普攻或战技时，为刻律德菈恢复5点能量。 | 信用点×160000、天外乐章×8、命运的足迹×1、阳雷的遥想×1 |

## 总属性加成

| 属性 | 加成 |
|---|---|
| 生命值 | 10% |
| 攻击力 | 18% |
| 风属性伤害提高 | 22.4% |

---

## 星魂

| 星魂 | 名称 | 效果 |
|---|---|---|
| E1 | Seize the Crowns of All | The character with "Military Merit" ignores 16% of the targets' DEF when dealing DMG. If "Military Merit" has been upgraded to "Peerage," then the character additionally ignores 20% of the targets' DEF when dealing Skill DMG. When Cerydra uses her Skill, regenerates 2 Energy for the designated ally target. |
| E2 | Forge the Dreams of Many | The character with "Military Merit" deals 40% increased DMG. While a teammate on the field has "Military Merit," Cerydra's DMG dealt increases by 160%. |
| E3 | Torch the Laws of Old | Skill Lv. +2, up to a maximum of Lv. 15.<br>Basic ATK Lv. +1, up to a maximum of Lv. 10. |
| E4 | Remake the Realms of Men | Increases Ultimate's DMG multiplier by 240%. |
| E5 | Help and Hurt Repaid in Full | Ultimate Lv. +2, up to a maximum of Lv. 15.<br>Talent Lv. +2, up to a maximum of Lv. 15. |
| E6 | A Journey Set Starward | The character with "Military Merit" increases their All-Type RES PEN by 20%, and the multiplier for the Additional DMG triggered via "Military Merit" increases by 300%. While a teammate on the field has "Military Merit," Cerydra's All-Type RES PEN increases by 20%. |

---

## 推荐遗器

**主词条推荐**：攻击力 / 速度 / 攻击力 / 能量恢复效率

**推荐副词条**：攻击力 / 速度 / 暴击伤害

#### 4件套推荐

| 遗器套装 | 效果 |
|---|---|
| [[zh_cn/relic/隧洞遗器/重循苦旅的司铎\|重循苦旅的司铎]] | 对我方单体目标施放战技或终结技时，使技能目标的暴击伤害提高18%，持续2回合，该效果最多叠加2次。 |
| [[zh_cn/relic/隧洞遗器/晨昏交界的翔鹰\|晨昏交界的翔鹰]] | 当装备者施放终结技后，使其行动提前25%。 |
| [[zh_cn/relic/隧洞遗器/野穗伴行的快枪手\|野穗伴行的快枪手]] | 使装备者的速度提高6%，普攻造成的伤害提高10%。 |

#### 2件套推荐

| 遗器套装 | 效果 |
|---|---|
| [[zh_cn/relic/位面饰品/沉陆海域露莎卡\|沉陆海域露莎卡]] | 使装备者的能量恢复效率提高5%，如果装备者不是编队中的第一位角色，使编队中的第一位角色攻击力提高12%。 |
| [[zh_cn/relic/位面饰品/不老者的仙舟\|不老者的仙舟]] | 使装备者的生命上限提高12%。当装备者的速度大于等于120时，我方全体攻击力提高8%。 |
| [[zh_cn/relic/位面饰品/太空封印站\|太空封印站]] | 使装备者的攻击力提高12%。当装备者的速度大于等于120时，攻击力额外提高12%。 |

---

## 推荐光锥

### [[zh_cn/lightcone/同谐/金血铭刻的时代.md|金血铭刻的时代]]

- **基础属性**：生952 攻635 防463
- **推荐度**：★★★★★
- **技能名**：征服
- **效果**：使装备者的攻击力提高【64%/80%/96%/112%/128%】。施放终结技攻击后恢复1个战技点，装备者对我方单体角色施放战技后，使目标造成的战技伤害提高【54%/67.5%/81%/94.5%/108%】，持续3回合。

### [[zh_cn/lightcone/同谐/夜色流光溢彩.md|夜色流光溢彩]]

- **基础属性**：生952 攻635 防463
- **推荐度**：★★★★★
- **技能名**：抚慰
- **效果**：我方角色每次攻击时，使装备者获得1层【歌咏】，每层【歌咏】使装备者的能量恢复效率提高【3.0%/3.5%/4.0%/4.5%/5.0%】，最多叠加5层。装备者施放终结技时，移除【歌咏】并获得【华彩】，【华彩】使装备者的攻击力提高【48%/60%/72%/84%/96%】，使我方全体造成的伤害提高【24%/28%/32%/36%/40%】，持续1回合。

### [[zh_cn/lightcone/同谐/永远的迷境饭.md|永远的迷境饭]]

- **基础属性**：生952 攻476 防330
- **推荐度**：★★★★
- **技能名**：真香
- **效果**：使装备者的攻击力提高【16%/20%/24%/28%/32%】。装备者施放战技后，攻击力提高【8%/10%/12%/14%/16%】，该效果最多叠加3层。

### [[zh_cn/lightcone/同谐/舞！舞！舞！.md|舞！舞！舞！]]

- **基础属性**：生952 攻423 防396
- **推荐度**：★★★★
- **技能名**：停不下来啦！
- **效果**：当装备者施放终结技后，我方全体行动提前【16%/18%/20%/22%/24%】。

## 推荐队伍

| 主C | 辅助 | 生存 |
|---|---|---|
| [[zh_cn/character/毁灭/白厄_物理_五星.md\|白厄]] | [[zh_cn/character/同谐/刻律德菈_风_五星.md\|刻律德菈]] | [[zh_cn/character/同谐/星期日_虚数_五星.md\|星期日]] |
| [[zh_cn/character/丰饶/藿藿_风_五星.md\|藿藿]] | [[zh_cn/character/智识/那刻夏_风_五星.md\|那刻夏]] | [[zh_cn/character/记忆/开拓者_冰_五星.md\|开拓者•记忆]] |
| [[zh_cn/character/记忆/开拓者_冰_五星.md\|开拓者•记忆]] | [[zh_cn/character/巡猎/Archer_量子_五星.md\|Archer]] | [[zh_cn/character/同谐/花火_量子_五星.md\|花火]] |
| [[zh_cn/character/同谐/布洛妮娅_风_五星.md\|布洛妮娅]] |  |  |

*文件生成时间：2026-08-27*

## 角色故事
北境帝国，失落的王朝，寒冷的疆土燃烧着征伐的野心。
君主刻律德菈，执握「律法」火种的黄金裔，布局设子，与神相弈，审判异心的罪囚，为此世奠定逐火的基业
——「这绝非终点，翁法罗斯的征途，当是银河群星！」

### 角色故事·其一 （解锁条件：角色等级20）

北境帝国许珀耳，严寒的国土燃烧着不熄的野心。
自那无嗣的君主陨落，继位者悬空，帝国已然四分五裂，内战不止。

失去家园的难民踏上乞讨为生之路，受伤的女孩因那一头罕见的蓝发在皑皑冰雪中格外显眼。
「只有受塔兰顿赐福的王室，才有如同火焰一般飘扬的蓝发，也唯有天选之人，才能流淌金色的鲜血……」
只因偶然的一瞥，野心勃勃的贵族将乞儿收养，向外散播着流浪王女的传言。

她被带上辉煌的高台，贵族高举她的手臂，那刺破的指尖滴下如同黎明一般浓郁的金血。
台下民众眼神狂热，那灼热的期待似乎要将她一同点燃。

「从此刻起，你就是王女『刻律德菈』。」
贵族将她带入宫殿，她穿上华美沉重的服装。
「刻律…德菈？」
只因一刻犹豫，脸上火辣的刺痛几乎让她流下眼泪。
「我是，我是…刻律…德菈……
「我是刻律德菈。
「我是。」
她忍住自己的颤抖，任由耳边的哭喊远去
——那是上一任王女的哀嚎。

她日复一日地学习皇室礼仪，直到狭窄的束腰再也不会让她疼痛，直到她能面不改色地大声演讲——
「王女年幼，我将摄政，统理许珀耳帝国政务。」贵族以她的名义收拢人心，将王室之权据为己有。
「反正都是任人摆弄的弃子，她扮演得还不错，可以留着。」阴影里，新任的摄政王对宰相窃笑。

幽闭的时光望不到尽头，稚龄的「王女」将目光从远方隐约的星空移开，落回眼前的棋盘。
这是她用于自保的游戏。

「骄傲的王女，你的眼睛似乎总在观察，也似乎总在隐藏，就像……」
「就像什么？」
悄然几手间，她将要抵达棋盘的边境。
「就像…将要燃起的火焰……」

老师苦笑着掷下棋子，千百次的对弈中，已没有王女无法解开的棋局。

### 角色故事·其二 （解锁条件：角色等级40）

宫女与侍卫无权无势，却是流动的宫廷中无孔不入的眼线——
她以恩惠拉拢，搜集情报，布下纵横交错的棋路。
与新王不和的旧贵族暗中谋划反叛，将刺客安排入王的禁卫军——
她假意与之合作，布下借刀杀人的「马」。
帝国人民爱戴她虚假的血统，于是她体恤孤老，扶助弱小——
那日益高涨的名声为她拉拢人心，布下力量磅礴的「车」。

「请于幕匿三刻，帐中相候，有要事密告——您忠诚的宰相。」
各怀鬼胎的重臣意欲外征，当密信交付于她，她知晓关键的「象」已经出现。

烛火在帐内勾勒出虚伪的影子。宰相脸上挂着笑容，就像一幅失色的画。
「北地不似那温暖的南方。」他指向桌上的地图，「蜗居于此，许珀耳必亡。我已联络大陆上最优秀的佣兵，王希望您能亲征……」

她未尝不知自己已被视弃子，一旦失败便要背负一切责任。
但她已等待太久，不孤注一掷，怎可颠覆一切？

穿越埃普斯群山，她抓住吕奎亚城发动反抗战争的机会，率军击溃他们的同时将金血将领福特图多收入麾下，更为自己赢得军心。
一城、两城、三城…许珀耳的军队如火焰燎原，当蓝发的少女高举旗帜，铁蹄将踏破她所指向的国度——
她望着初具雏形的大军，知晓最后的「兵」也已即位。

在那漆黑的雪夜，凯旋的王女骑乘银白的骏马，带领大军撞开国门，宣读崭新的律令——
「今日起，我将为许珀耳带来公正！」

摄政的「王」从寝宫中被拖出，拒绝服从的臣子与旧部尽皆倒在军士的锋刃之下。
「她…她不是刻律德菈！」
她站在高台，划破手腕，黄金血伴随众人的嗤笑滴落，将「王」的绝望淹没。
「摄政王荒淫无道，大乱天下，我以『律法』之名宣判汝——」

北地的寒风中，她的蓝发猎猎飞舞，如同火焰般耀眼。
「火刑！」

火光中，她戴上了那顶属于帝王的冠冕——她唯一的战利品。
一簇幽蓝色的火苗自冠冕顶端燃起，此后再不曾熄灭。

### 角色故事·其三 （解锁条件：角色等级60）

三相的神谕自雅努萨波利斯，传向大地上无尽纷争的城邦。
「拯救世界…从来不是执棋者的兴趣。」
她品味神谕，熊熊燃烧的未来仿佛就在眼前——
「但与那自视为主宰的神明相争，乃至走向天外…的确是旷古而绝世的一局！」

漫漫长夜中，她如璀璨的灯火吸引流淌金血的人子：
奥赫玛的议院中，黄金裔与平民共享争论与决议的公民权。
宏伟的图书馆拔地而起，逐火的使命人人皆可获取。
军队的旧习被废除，深海的游鱼搁浅在陆地，循着血与火的气味成为她的剑旗。
奥赫玛的政坛中，圣城的「金织」冉冉升起，金丝的颤动将众人的命运彼此连缀。
……

但那棋盘以黄金之血勾勒，她的对手是神明。即便她以燃烧之痛换来冠冕，以永驻幼年换取未来，胜利的天平似乎从未真正倾向人子。
「逐火是不断失却的旅途……
「唯有同等的代价，才能交换同等的胜利。但要击落神明，还远远不够……」
她日日夜夜推演，不愿自己的忧虑被人看见。

「既然你是棋手，我们便是棋子，对吧？」
不等她的回答，以剑为琴的少女洗去手上的血腥，点了点头。
「我明白了。」
唯有此时，那高傲的女皇才会罕见地沉默。
「如果可以……」
她的脸上浮现一丝似有若无的苦涩。
「不，没有如果。」

猎夺「海洋」火种的战役前，她再一次站在高台，望着五百位屏息等待谕令的臣子。

「诸位——」
当她的声音响起，欢呼声响彻云霄。
「今日，『海洋』将为我们倾覆，那『毁灭』的巨兽将成为无往而不利的武器，为征服星海举杯吧！」

她知道前方是有去无回的血海，但她必须扮演斩钉截铁的君王。
再一次，她仿佛听到老师的告诫——

「棋是牺牲的艺术。
因此，棋手须首先立下必死的决心。」

### 角色故事·其四 （解锁条件：角色等级80）

「啪嗒……」
血滴入水中，掀起金色的涟漪。

「剑旗爵，你可曾想过，此战之后，我们该去往何方？」
执剑的少女沉默许久，摇了摇头。
「等到反叛的浪花散尽，我们就去向星海，那里一定有你想要的清澈大海。」
她露出一抹微笑，挥杖向天。
「众神让我们相互厮杀，让翁法罗斯自绝于银河，我便要剑指众神。无论是天下的众神，还是天外的众神。」

「啪嗒……」
血滴入水中，掀起金色的涟漪。

「剑旗爵，若有一天，我命令你向我挥剑，你会怎么办？」
少女继续沉默以对，以为那不过又是一个残忍的玩笑。
「请一定用最锋利的剑刃。这样，才对得起那些因我而牺牲的将士。」
她将代表自己的棋子掷出棋局——
「瞧，有舍才有得，棋路宽阔多了。」

「啪嗒……」
血滴入水中，掀起金色的涟漪。

「剑旗爵，你觉得谁能在我们身后，接过逐火的重任？」
她们不约而同看向了远处的「金织」。
「这尾小金鳟，终会变成池中的大鱼儿。」

「啪嗒……」
血滴入水中，掀起金色的涟漪。

「许多人猜测我向塔兰顿交易了什么，百战百胜的力量，还是律法的权能…呵，那根本无需神明的帮助……」

故人身影消散，她感到寒冷逼近，天空漆黑一片，仿佛没有星光的洞穴。
很久以前，她也曾在彻骨的寒冷中，亲眼见到流着黄金血的孩子被带走。

「可在那吃人的世道，让自己拥有黄金的血…才有推翻这一切的机会，哪怕…我将以此模样度过一生……」

蓝发的女孩闭上双眼。
「但真正的愿望自始至终…只有一个……」
从几乎冻毙荒野的乞儿，到傀儡一般的王女，到与神相争的领袖，她亲手将自己擢升为棋手，又亲手将自己当作弃子抹去——

「我要，征服世间不公的命运！」
