# -*- coding: utf-8 -*-
"""统计 SRR index_new/cn 各数据文件记录数"""
import json, os

DIR = r'G:/HSR/StarRailRes_repo/index_new/cn'

desc = {
    'achievements.json': '成就',
    'avatars.json': '头像',
    'characters.json': '角色（基础档案+技能/星魂/行迹ID关联）',
    'character_promotions.json': '角色晋阶属性成长+晋阶材料',
    'character_ranks.json': '角色星魂（效果描述）',
    'character_skills.json': '角色技能（各等级数值参数）',
    'character_skill_trees.json': '角色行迹/技能树（解锁等级、材料、加成）',
    'descriptions.json': '角色/光锥 介绍文本',
    'elements.json': '属性（元素）',
    'items.json': '物品（材料/道具）',
    'light_cones.json': '光锥（基础档案+技能/星魂ID关联）',
    'light_cone_promotions.json': '光锥晋阶属性成长+晋阶材料',
    'light_cone_ranks.json': '光锥叠影效果',
    'nickname.json': '昵称',
    'paths.json': '命途',
    'properties.json': '属性项定义（生命/攻击/…）',
    'relics.json': '遗器（单件）',
    'relic_main_affixes.json': '遗器主词条',
    'relic_sets.json': '遗器套装',
    'relic_sub_affixes.json': '遗器副词条',
    'simulated_blessings.json': '模拟宇宙祝福',
    'simulated_blocks.json': '模拟宇宙区域',
    'simulated_curios.json': '模拟宇宙奇物',
    'simulated_events.json': '模拟宇宙事件',
}

print(f"{'文件':<28}{'记录数':>8}  说明")
print('-' * 90)
total = 0
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith('.json'):
        continue
    try:
        d = json.load(open(os.path.join(DIR, fn), encoding='utf-8'))
        n = len(d) if isinstance(d, (list, dict)) else 1
        total += n
    except Exception as e:
        n = f'ERR {e}'
    print(f"{fn:<28}{str(n):>8}  {desc.get(fn, '')}")
print('-' * 90)
print(f"数据文件总数: {len([f for f in os.listdir(DIR) if f.endswith('.json')])}  记录合计: {total}")
