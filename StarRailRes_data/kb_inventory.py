# -*- coding: utf-8 -*-
import os, glob

HSR = r'G:\HSR'
for cat in ['character', 'lightcone', 'relic', 'items']:
    base = os.path.join(HSR, cat)
    files = glob.glob(os.path.join(base, '**', '*.md'), recursive=True)
    print(f"{cat}: {len(files)} 个文件")
    # 子目录统计
    subs = {}
    for f in files:
        rel = os.path.relpath(f, base)
        top = rel.split(os.sep)[0] if os.sep in rel else '(根目录)'
        subs[top] = subs.get(top, 0) + 1
    for k in sorted(subs):
        print(f"    {k}: {subs[k]}")
