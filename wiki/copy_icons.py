#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
copy_icons.py — 只复制 KB 实际用到的 SRR 图标到 wiki/assets/icons/
用法：python wiki/copy_icons.py
零依赖。
"""
import os, re, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
# SRR 源：本地 master，或 CI 克隆到 .srr
CANDIDATES = [
    ROOT / "StarRailRes-master" / "icon",
    ROOT / ".srr" / "icon",
]
DST = ROOT / "wiki" / "assets" / "icons"
SRC = ROOT / "zh_cn"

# KB 顶层目录 → (SRR 子目录, 文件命名模板)
ICON_MAP = {
    "character": ("avatar", "{id}.png"),
    "lightcone": ("light_cone", "{id}.png"),
    "relic": ("relic", "{id}.png"),
    "items": ("item", "{id}.png"),
    "simulated": ("curio", "{id}.png"),
}
# 角色立绘（额外）
CHAR_BIG = ("character", "{id}.png")

def find_srr():
    for c in CANDIDATES:
        if c.exists():
            return c
    return None

def main():
    srr = find_srr()
    if not srr:
        print("[copy_icons] 未找到 SRR 图标源（StarRailRes-master/ 或 .srr/），跳过。")
        return
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    copied = 0
    total_bytes = 0
    missing = []

    for md in SRC.rglob("*.md"):
        rel = str(md.relative_to(SRC)).replace(os.sep, "/")
        top = rel.split("/")[0]
        if top not in ICON_MAP:
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        eid = None
        for line in text.splitlines()[:8]:
            m = re.match(r"^>\s*实体ID[:：]\s*(.+)", line)
            if m:
                eid = m.group(1).strip()
                break
        if not eid or eid.startswith("无"):
            continue
        # 取纯数字 ID（可能有后缀如 _0）
        eid_digits = re.match(r"(\d+)", eid)
        if not eid_digits:
            continue
        eid = eid_digits.group(1)

        sub, tpl = ICON_MAP[top]
        fname = tpl.format(id=eid)
        src = srr / sub / fname
        dst_sub = DST / sub
        dst_sub.mkdir(parents=True, exist_ok=True)
        dst = dst_sub / fname
        if src.exists():
            shutil.copy2(src, dst)
            copied += 1
            total_bytes += dst.stat().st_size
        else:
            missing.append(f"{top}/{rel} → {sub}/{fname}")

        # 角色额外复制立绘
        if top == "character":
            big_sub, big_tpl = CHAR_BIG
            big_src = srr / big_sub / big_tpl.format(id=eid)
            big_dst = DST / big_sub
            big_dst.mkdir(parents=True, exist_ok=True)
            big_dst_file = big_dst / big_tpl.format(id=eid)
            if big_src.exists():
                shutil.copy2(big_src, big_dst_file)
                copied += 1
                total_bytes += big_dst_file.stat().st_size

    print(f"[copy_icons] SRR 源: {srr}")
    print(f"[copy_icons] 复制 {copied} 个图标，{total_bytes/1024/1024:.2f} MB → {DST}")
    if missing:
        print(f"[copy_icons] {len(missing)} 个实体无图标（占位降级）：")
        for m in missing[:20]:
            print(f"  - {m}")
        if len(missing) > 20:
            print(f"  ... 其余 {len(missing)-20} 个略")

if __name__ == "__main__":
    main()
