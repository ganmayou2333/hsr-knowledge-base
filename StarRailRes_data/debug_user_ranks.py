# -*- coding: utf-8 -*-
"""检查用户镜流/三月七星魂表格解析"""
import re, os

for name, fp in [('镜流', r'G:\HSR\character\毁灭\镜流_冰_五星.md'),
                 ('三月七', r'G:\HSR\character\存护\三月七_冰_四星.md')]:
    text = open(fp, encoding='utf-8').read()
    sm = re.search(r'##\s*星魂(.*?)(?=\n## |\Z)', text, re.S)
    print('=' * 60)
    print(name, '星魂章节:')
    for line in sm.group(1).splitlines():
        line = line.strip()
        if line.startswith('|'):
            le = line.replace(r'\|', '\x00')
            cells = [c.strip() for c in le.strip('|').split('|')]
            print('  cells:', [c.replace('\x00', '|') for c in cells])
