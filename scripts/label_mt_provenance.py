# -*- coding: utf-8 -*-
"""存量非官方本地化「追溯打标」脚本（issue #9 / 翻译办法 §九 / D-065）

背景
----
v2.0（2026-11-14，D-065）起，一律禁止机械/翻译手段生成正文，只收官方本地化原文。
存量中「非官方本地化」内容必须按《翻译办法》§九 在文件头部元信息区打标，三要素缺一不可：

    > 本地化来源：非官方（工具：<zhconv | LLM 模型名>；来源：<原始文本 URL 或 "zh_cn/<路径>">；时间：<YYYY-MM-DD>）

判定规则（逐条对应 §九）
----------------------
按「已撤下 > 已有官方来源 > 已标注 > 待打标」的优先级归类，四类互斥、合计 = 总文件数：

1. 已撤下      文件含「机器翻译内容已撤下」（§九.3：已撤下的不复活）。
               加 `--withdrawn-broad` 时，另把 W-4.6-19 版权撤下
               （「文字表达已撤下 / 本库已撤下照搬 / 已按权利人声明撤下 / 依来源站声明撤下」）一并归入。
2. 已有官方来源  头部元信息含官方域名（hoyoverse.com / mihoyo.com / static.nanoka.cc），
               且 URL 路径里带**该文件语言的**语言标记（en-us / zh-tw / ja-jp / ko-kr，
               或 static.nanoka.cc 的 en / ja / ko / zh-tw）→ 不打标。
               注意：nanoka 的 `zh/`、`zh-cn/`、`cn/` 属简体中文，zh_tw 引用它们算**非对应语言**
               → 归待打标（工具 zhconv）。`bbs.mihoyo.com/sr/wiki/...` 无语言段，同样不算。
3. 已标注      文件含「本地化来源：非官方」→ 跳过（幂等保证）。
4. 待打标      其余文件 → `--apply` 时插入 §九 标注行（无 `> 数据来源：` 锚点的跳过并单列）。

插入位置
--------
§九.2 要求「必须在 `> 数据来源：` 之后、正文之前」。默认 `--insert-at metadata-end`：
插在头部连续 `>` 元信息块末尾（保持「数据来源→版本→实体ID→…」既有次序，仍在 `---` 与正文之前）；
`--insert-at after-source`：紧贴 `> 数据来源：` 行之后插入。

幂等性
------
1) 已含 §九 标注 / 「机器翻译内容已撤下」/ 官方对应语言来源的文件一律跳过；
2) 标注行携带日期，写入后再次运行只会落到「已标注」，不会重复插入；
3) `--apply` 写盘前重新读取并复检（防止与并发修改打架），保留原 BOM 与行尾（CRLF/LF）；
   行尾混用（CRLF+LF 混杂）的文件跳过并告警。

用法
----
    python scripts/label_mt_provenance.py --dry-run                    # 默认：只出矩阵，不改文件
    python scripts/label_mt_provenance.py --dry-run --lang zh_tw --pilot 3
    python scripts/label_mt_provenance.py --apply --lang zh_tw --pilot 3   # 小步落地
    python scripts/label_mt_provenance.py --dry-run --json .tmp_label/matrix.json

    --lang en_us|zh_tw|ja_jp|ko_kr|all   默认 all（四个镜像语言；zh_cn 是基准，不参与）
    --pilot N                            每个所选语言只处理前 N 个待打标文件
    --llm-tool NAME                      非 zh_tw 语言的工具名（默认 DeepSeek）
    --source-mode auto|meta|zhcn         来源字段取「数据来源 URL」或「zh_cn/<路径>」（默认 auto=URL 优先）
    --date YYYY-MM-DD                    标注日期（默认今天）
    --root DIR                           在副本目录上跑（沙箱验证幂等；默认仓库根）
"""

import argparse
import collections
import datetime
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

LANGS = ["en_us", "zh_tw", "ja_jp", "ko_kr"]

# 官方本地化域名
OFFICIAL_HOSTS = ("hoyoverse.com", "mihoyo.com", "static.nanoka.cc")

# 官方发行源（issue #9 边界 3b）：官方商店曲目页 = 已有官方来源，不打标。
# 判定只看「该 URL 出现在头部元信息区」，不看语言路径（曲目页本身即分语言发行）。
STORE_HOSTS = ("music.apple.com", "vibe.naver.com")

# 「对应语言」的路径标记（小写比较）。
# zh / zh-cn / cn / chs 属简体中文，对 zh_tw 不算对应语言（本次口径说明）。
LANG_TOKENS = {
    "en_us": {"en-us", "en_us", "en", "english"},
    "zh_tw": {"zh-tw", "zh_tw", "zh-hant", "zhhant", "cht", "zhtw"},
    "ja_jp": {"ja-jp", "ja_jp", "ja", "jp", "japanese"},
    "ko_kr": {"ko-kr", "ko_kr", "ko", "kr", "korean"},
}

# 出现即说明另有非官方来源（仅用于提示，不影响分类）
# 注：music.apple.com / vibe.naver.com 属官方发行源（STORE_HOSTS），不在此列。
UNOFFICIAL_HINT_HOSTS = (
    "hsr.nanoka.cc",
    "github.com",
    "miyoushe.com",
    "biligame.com",
)

MARK_WITHDRAWN = "机器翻译内容已撤下"
# 版权撤下（W-4.6-19）：issue #9 边界 1 —— 这类文件「保持原样、不归机翻、不打标」，
# 独立成 kept 桶，不算「已撤下」也不写 §九 标注行。
MARK_WITHDRAWN_BROAD = re.compile(
    r"文字表达已撤下|本库已撤下照搬|已按权利人声明撤下|依来源站声明撤下"
)
MARK_LABEL = "本地化来源：非官方"
MARK_INLINE_EVIDENCE = re.compile(r"zhconv", re.I)

SRC_LINE_PREFIX = "> 数据来源："
META_LINE_PREFIX = "> "
URL_RE = re.compile(r"https?://[^\s\)\]）】，、；]+")

BUCKETS = ("official", "withdrawn", "kept", "labeled", "pending")
BUCKET_CN = {
    "official": "已有官方来源",
    "withdrawn": "已撤下",
    "kept": "保持原样",
    "labeled": "已标注",
    "pending": "待打标",
}


# --------------------------------------------------------------------------- io


def read_doc(path):
    """读文件 → (text, bom, newline)。text 统一成 \\n 行尾便于按行处理。"""
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf and crlf == lf:
        newline = "\r\n"
    elif crlf:
        newline = "mixed"
    else:
        newline = "\n"
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return text, bom, newline


def write_doc(path, text, bom, newline):
    out = text.replace("\n", newline).encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    with open(path, "wb") as fh:
        fh.write(out)


# ------------------------------------------------------------------ 头部解析


def header_lines(text):
    """头部元信息区：第 1 行起，到首个 `---` / `## ` 之前（最多 40 行）。"""
    out = []
    for i, line in enumerate(text.split("\n")):
        if i >= 40:
            break
        s = line.strip()
        if s == "---" or s.startswith("## "):
            break
        out.append(line)
    return out


def urls_of(blob):
    return URL_RE.findall(blob)


def url_tokens(url):
    body = re.sub(r"^https?://", "", url)
    parts = re.split(r"[/?#&=+;:（）()\[\]\s]", body)
    return [p.strip(".").lower() for p in parts if p.strip(".")]


def host_of(url):
    m = re.match(r"https?://([^/\s]+)", url)
    return m.group(1) if m else url


def official_match(url, lang):
    """该 URL 是否为「官方域名 + 对应语言路径」。返回 (bool, 说明)。"""
    if not any(h in url for h in OFFICIAL_HOSTS):
        return False, "非官方域名"
    hit = [t for t in url_tokens(url) if t in LANG_TOKENS[lang]]
    if hit:
        return True, "官方域名(%s) 语言标记=%s" % (host_of(url), "/".join(hit))
    return False, "官方域名(%s) 无对应语言路径" % host_of(url)


def find_src_line(lines):
    for i, line in enumerate(lines):
        if line.lstrip("\ufeff").startswith(SRC_LINE_PREFIX):
            return i
    return -1


def insert_index(lines, src_idx, insert_at):
    """新行插在 lines[idx] 之前。"""
    if insert_at == "after-source":
        return src_idx + 1
    idx = src_idx + 1
    while idx < len(lines) and lines[idx].startswith(META_LINE_PREFIX):
        idx += 1
    return idx


def meta_block_index(lines):
    """头部连续 `> ` 元信息块末尾的插入位（无 `> 数据来源：` 时的回退锚点）。"""
    n = min(len(lines), 40)
    i = 0
    while i < n and not lines[i].lstrip("\ufeff").startswith(META_LINE_PREFIX):
        s = lines[i].strip()
        if s == "---" or s.startswith("## "):
            return -1
        i += 1
    if i >= n:
        return -1
    j = i
    while j < n and lines[j].lstrip("\ufeff").startswith(META_LINE_PREFIX):
        j += 1
    return j


def anchor_of(lines, insert_at, fallback=True):
    """→ (插入位, 锚点类型 src|meta|none, 数据来源行下标)。"""
    src_idx = find_src_line(lines)
    if src_idx >= 0:
        return insert_index(lines, src_idx, insert_at), "src", src_idx
    if fallback:
        idx = meta_block_index(lines)
        if idx >= 0:
            return idx, "meta", -1
    return -1, "none", -1


# -------------------------------------------------------------------- 分类


def classify(text, lang):
    """返回 (bucket, info)；bucket ∈ official / withdrawn / labeled / pending。"""
    hdr = header_lines(text)
    hdr_blob = "\n".join(hdr)
    info = {
        "official_urls": [],       # 官方域名 + 对应语言
        "official_reason": "",
        "official_any": [],        # 官方域名（不论语言）
        "official_store": [],      # 官方发行源曲目页（music.apple.com / vibe.naver.com）
        "unofficial_urls": [],
        "withdrawn_hit": "",
        "keep_hit": "",
        "force_zhcn": False,       # 改判件：来源字段强制写 zh_cn/<路径>
        "labeled": False,
        "inline_evidence": False,
        "detail": False,
        "src_line": "",
        "src_url": "",
        "src_idx": -1,
    }

    if MARK_WITHDRAWN in text:
        info["withdrawn_hit"] = MARK_WITHDRAWN
    else:
        m = MARK_WITHDRAWN_BROAD.search(text)
        if m:
            info["keep_hit"] = m.group(0)

    for u in urls_of(hdr_blob):
        if any(h in u for h in OFFICIAL_HOSTS):
            info["official_any"].append(u)
        if any(h in u for h in STORE_HOSTS):
            info["official_store"].append(u)
        if any(h in u for h in UNOFFICIAL_HINT_HOSTS):
            info["unofficial_urls"].append(u)
        ok, reason = official_match(u, lang)
        if ok:
            info["official_urls"].append(u)
            info["official_reason"] = reason

    info["labeled"] = MARK_LABEL in text
    info["inline_evidence"] = bool(MARK_INLINE_EVIDENCE.search(hdr_blob))
    info["detail"] = any(
        l.lstrip("\ufeff").startswith("> 实体ID：") for l in hdr
    )

    lines = text.split("\n")
    src_idx = find_src_line(lines)
    if src_idx >= 0:
        info["src_idx"] = src_idx
        info["src_line"] = lines[src_idx]
        hit = urls_of(lines[src_idx])
        if hit:
            info["src_url"] = hit[0]

    # 优先级：已撤下(strict) > 已有官方来源 > 保持原样(版权撤下) > 已标注 > 待打标
    if MARK_WITHDRAWN in text:
        return "withdrawn", info
    if info["official_urls"] or info["official_store"]:
        return "official", info
    if info["keep_hit"]:
        return "kept", info
    if info["labeled"]:
        return "labeled", info
    return "pending", info


# ---------------------------------------------------------------- 标注行生成


def rel_lang_path(path, lang):
    """语言目录内的相对路径（统一 / 分隔，去掉 --root 带来的 ./ 前缀）。"""
    p = path.replace(os.sep, "/")
    while p.startswith("./"):
        p = p[2:]
    return p[len(lang) + 1:] if p.startswith(lang + "/") else p


def build_source_field(path, lang, info, args, root):
    rel = rel_lang_path(path, lang)
    zhcn = "zh_cn/" + rel
    if info.get("force_zhcn"):
        return zhcn, "zh_cn 路径（改判件：官方 URL 只覆盖名称/属性，正文经 zhconv）"
    if args.source_mode == "zhcn":
        exists = os.path.exists(os.path.join(root, "zh_cn", rel))
        return zhcn, "zh_cn 路径" + ("" if exists else "（zh_cn 无对应文件）")
    if args.source_mode == "meta":
        if info["src_url"]:
            return info["src_url"], "数据来源 URL"
        return zhcn, "zh_cn 路径（数据来源行无 URL）"
    if info["src_url"]:  # auto
        return info["src_url"], "数据来源 URL"
    return zhcn, "zh_cn 路径（数据来源行无 URL）"


def tool_for(lang, args):
    """工具署名：--tool-map 优先，其次 zhconv(zh_tw) / --llm-tool（其余语言）。"""
    if getattr(args, "tool_map", None) and lang in args.tool_map:
        return args.tool_map[lang]
    return "zhconv" if lang == "zh_tw" else args.llm_tool


def build_label(lang, path, info, args, root):
    source, src_kind = build_source_field(path, lang, info, args, root)
    tool = tool_for(lang, args)
    line = "> 本地化来源：非官方（工具：%s；来源：%s；时间：%s）" % (tool, source, args.date)
    return line, src_kind


# -------------------------------------------------------------------- 扫描


def collect(root, langs, insert_at="metadata-end", fallback=True):
    rows = []
    for lang in langs:
        base = os.path.join(root, lang)
        paths = []
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    paths.append(os.path.join(dirpath, fn))
        paths.sort(key=lambda p: p.replace(os.sep, "/"))
        for p in paths:
            text, bom, newline = read_doc(p)
            bucket, info = classify(text, lang)
            idx, kind, _ = anchor_of(text.split("\n"), insert_at, fallback)
            rows.append(
                {"lang": lang, "path": p, "text": text, "bom": bom,
                 "newline": newline, "bucket": bucket, "info": info,
                 "anchor": idx, "anchor_kind": kind}
            )
    return rows


def short(path):
    p = path.replace(os.sep, "/")
    return p[2:] if p.startswith("./") else p


def reclassify_broad(rows):
    """--withdrawn-broad：把版权撤下的文件并入已撤下（旧口径，默认关闭）。"""
    for r in rows:
        if r["bucket"] in ("pending", "kept") and r["info"]["keep_hit"]:
            r["bucket"] = "withdrawn"
    return rows


def reclassify_reclaim(rows, args, root):
    """边界 3a：官方 URL 只覆盖名称/属性、正文经 zhconv 的文件 → 改判为待打标。

    判据：bucket==official 且头部行内已有 zhconv 说明（info.inline_evidence）。
    改判后：工具=zhconv，来源=原 `zh_cn/<路径>`（force_zhcn）。
    """
    hit = []
    for r in rows:
        if r["bucket"] != "official" or not r["info"]["inline_evidence"]:
            continue
        if r["info"]["labeled"]:      # 已有 §九 标注 → 交给 §九.1 流程，不在此插入
            continue
        if args.reclaim_langs and r["lang"] not in args.reclaim_langs:
            continue
        r["bucket"] = "pending"
        r["info"]["force_zhcn"] = True
        hit.append(r)
    return hit


def final_bucket(text, lang, args):
    """与 reclassify_* 一致的落盘前复检口径：→ (bucket, info)。"""
    b, info = classify(text, lang)
    if (args.reclaim and info["inline_evidence"] and not info["labeled"]
            and (not args.reclaim_langs or lang in args.reclaim_langs)
            and b == "official"):
        b = "pending"
    if args.withdrawn_broad and b == "kept":
        b = "withdrawn"
    return b, info


# -------------------------------------------------------------------- 报告


def build_matrix(rows, langs, args_pilot):
    table = collections.OrderedDict()
    for lang in langs:
        table[lang] = collections.OrderedDict((b, 0) for b in BUCKETS)
        table[lang]["total"] = 0
    for r in rows:
        table[r["lang"]]["total"] += 1
        table[r["lang"]][r["bucket"]] += 1

    # 抽样：--pilot 给定时取该语言前 N 个（与被处理文件一致），否则在待打标序列上等距取 3 个
    pending = collections.OrderedDict((lang, []) for lang in langs)
    for r in rows:
        if r["bucket"] == "pending":
            pending[r["lang"]].append(r)
    samples = collections.OrderedDict()
    for lang in langs:
        seq = pending[lang]
        if args_pilot is None:
            k = len(seq)
            idxs = sorted({0, k // 2, k - 1} & set(range(k))) if k else []
            samples[lang] = [seq[i] for i in idxs]
        else:
            samples[lang] = seq[: min(args_pilot, 3)]

    out = ["| 语言 | 总文件 | 已有官方来源 | 已撤下 | 保持原样 | 已标注 | 待打标 | 抽样 3 例 |",
           "|---|---|---|---|---|---|---|---|"]
    for lang in langs:
        t = table[lang]
        cell = "<br>".join(
            "`%s`" % short(rel_lang_path(r["path"], lang)) for r in samples[lang]
        ) or "—"
        out.append(
            "| %s | %d | %d | %d | %d | %d | **%d** | %s |"
            % (lang, t["total"], t["official"], t["withdrawn"], t["kept"],
               t["labeled"], t["pending"], cell)
        )
    tot = {b: sum(table[l][b] for l in langs) for b in BUCKETS}
    out.append(
        "| **合计** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | — |"
        % (sum(table[l]["total"] for l in langs), tot["official"], tot["withdrawn"],
           tot["kept"], tot["labeled"], tot["pending"])
    )
    return "\n".join(out), table, samples


def sample_detail(samples, args, root):
    out = []
    for lang, items in samples.items():
        for r in items:
            info = r["info"]
            label, src_kind = build_label(lang, r["path"], info, args, root)
            reasons = []
            if info["src_idx"] < 0:
                if r["anchor_kind"] == "meta":
                    reasons.append("无 `> 数据来源：` 行 → 回退到头部元信息块末尾插入")
                else:
                    reasons.append("**无锚点（既无 `> 数据来源：` 也无 `>` 元信息块）→ --apply 将跳过**")
            elif info["src_url"]:
                reasons.append("数据来源 URL = `%s`（非官方域名 / 非对应语言）" % info["src_url"])
            else:
                reasons.append("数据来源行无 URL（锚点第 %d 行）" % (info["src_idx"] + 1))
            if info["official_store"]:
                reasons.append("头部另有官方发行源曲目页：`%s`" % info["official_store"][0])
            if info["official_any"]:
                reasons.append("头部另有官方域名 URL 但无对应语言标记：`%s`" % info["official_any"][0])
            if info["inline_evidence"]:
                reasons.append("头部行内已有 zhconv 说明（非 §九 标准行）")
            if info["force_zhcn"]:
                reasons.append("**边界 3a 改判件**（官方 URL 只覆盖名称/属性，正文经 zhconv）")
            if not info["detail"]:
                reasons.append("非详情文件（头部无 `> 实体ID：`）")
            if r["anchor_kind"] == "src":
                anchor = "第 %d 行 `> 数据来源：` 之后（%s）" % (
                    info["src_idx"] + 1, "紧贴该行" if args.insert_at == "after-source" else "元信息块末尾")
            elif r["anchor_kind"] == "meta":
                anchor = "第 %d 行之后（头部 `>` 元信息块末尾，回退锚点）" % r["anchor"]
            else:
                anchor = "无（不可写，跳过）"
            out.append("- `%s`" % short(r["path"]))
            out.append("  - 判定：待打标")
            out.append("  - 依据：%s" % "；".join(reasons))
            out.append("  - 来源字段口径：%s" % src_kind)
            out.append("  - 插入锚点：%s" % anchor)
            out.append("  - 拟插入：`%s`" % label)
    return "\n".join(out)


def build_notes(rows, langs, args):
    stats = collections.Counter()
    no_src, inline, mixed_nl, non_detail, official_any_offlang = [], [], [], [], []
    official_inline, kept, store, meta_fallback = [], [], [], []
    no_src_kind = collections.OrderedDict()
    for r in rows:
        info, bucket = r["info"], r["bucket"]
        if r["newline"] == "mixed":
            mixed_nl.append(r["path"])
        if bucket == "pending":
            if r["anchor_kind"] == "none":
                no_src.append(r["path"])
                rel = rel_lang_path(r["path"], r["lang"])
                if rel.startswith("quest/剧情文本/"):
                    kind = "quest/剧情文本（本机保留、已 gitignore）"
                elif rel.startswith("quest/"):
                    kind = "quest 索引"
                elif not info["detail"]:
                    kind = "规则/索引/文章（无实体ID）"
                else:
                    kind = "其他详情文件"
                no_src_kind[kind] = no_src_kind.get(kind, 0) + 1
            elif r["anchor_kind"] == "meta":
                meta_fallback.append(r["path"])
            if info["inline_evidence"]:
                inline.append(r["path"])
            if not info["detail"]:
                non_detail.append(r["path"])
            if info["official_any"] and not info["official_urls"]:
                official_any_offlang.append(r["path"])
        if bucket == "official":
            stats["official"] += 1
            if info["official_store"]:
                stats["official_store"] += 1
                store.append(r["path"])
            if info["labeled"]:
                stats["official_and_labeled"] += 1
            if info["unofficial_urls"]:
                stats["official_mixed"] += 1
            if info["inline_evidence"]:
                stats["official_inline"] += 1
                official_inline.append(r["path"])
        if bucket == "kept":
            stats["kept"] += 1
            if info["keep_hit"] != MARK_WITHDRAWN and info["keep_hit"]:
                kept.append(r["path"])
        if bucket == "labeled":
            stats["labeled"] += 1

    notes = [
        "撤下口径：%s（仅 `%s` 算已撤下）；版权撤下（W-4.6-19：`文字表达已撤下` 等）"
        "归「保持原样」，不归机翻、不打标"
        % ("broad（旧口径，本次不用）" if args.withdrawn_broad else "**strict**（issue #9 边界 1）",
           MARK_WITHDRAWN),
        "保持原样（版权撤下标记命中且在版本库内/待处理序列）：%d%s"
        % (len(kept), ("，样例：" + "、".join("`%s`" % short(x) for x in kept[:2])) if kept else ""),
        "已有官方来源中属官方发行源曲目页（music.apple.com / vibe.naver.com，边界 3b，不打标）：%d%s"
        % (stats["official_store"], ("，样例：" + "、".join("`%s`" % short(x) for x in store[:2])) if store else ""),
        "待打标中无 `> 数据来源：` 行 → 回退到头部 `>` 元信息块末尾插入（边界内，仍属写入）：%d"
        % len(meta_fallback),
        "待打标中彻底无锚点（`--apply` 跳过、单列）：%d%s"
        % (len(no_src), ("（" + "；".join("%s %d" % (k, v) for k, v in no_src_kind.items()) + "）")
           if no_src_kind else ""),
        "待打标中头部有官方域名 URL 但无对应语言路径（如 bbs.mihoyo.com 中文 Wiki、nanoka `zh` JSON）：%d"
        % len(official_any_offlang),
        "待打标中头部行内已有 zhconv 说明但缺 §九 标准行（apply 后会出现双处说明，建议人工复核）：%d"
        % len(inline),
        "待打标中非详情文件（头部无 `> 实体ID：`，多为索引/规则/文章）：%d" % len(non_detail),
        "已归「已有官方来源」但头部另有非官方来源 URL（部分来源，建议人工复核）：%d"
        % stats["official_mixed"],
        "其中头部行内已写「经 zhconv 处理」的（官方 URL 只覆盖部分字段）：%d %s"
        % (len(official_inline),
           ("（" + "、".join("`%s`" % short(x) for x in official_inline[:3]) + "）") if official_inline else ""),
        "同时有官方来源与 §九 标注（§九.1 应换官方后删标注）：%d" % stats["official_and_labeled"],
        "行尾混用（CRLF/LF 混杂，`--apply` 跳过）：%d" % len(mixed_nl),
    ]
    for name, lst in (("无锚点样例", no_src), ("行内 zhconv 样例", inline),
                      ("官方域名非对应语言样例", official_any_offlang),
                      ("回退锚点样例", meta_fallback)):
        if lst:
            notes.append("%s：%s" % (name, "、".join("`%s`" % short(x) for x in lst[:3])))
    return "\n".join("- " + n for n in notes)


def apply_list(rows, pilot):
    out, per_lang = [], collections.Counter()
    for r in rows:
        if r["bucket"] != "pending":
            continue
        if pilot is not None and per_lang[r["lang"]] >= pilot:
            continue
        per_lang[r["lang"]] += 1
        out.append(r)
    return out


# ---------------------------------------------------------------------- main


def main(argv=None):
    global STORE_HOSTS
    ap = argparse.ArgumentParser(
        description="存量非官方本地化追溯打标（翻译办法 §九 / issue #9）· 默认 dry-run，不改文件"
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="只输出矩阵与抽样清单（默认）")
    mode.add_argument("--apply", action="store_true", help="实际插入标注行")
    ap.add_argument("--lang", default="all", choices=["all"] + LANGS)
    ap.add_argument("--pilot", type=int, default=None, help="每个语言只处理前 N 个待打标文件")
    ap.add_argument("--llm-tool", default="LLM（模型未记录）",
                    help="非 zh_tw 语言的工具署名（默认「LLM（模型未记录）」：历史译文模型未逐文件记录，禁止编造模型名）")
    ap.add_argument("--tool-map", default=None,
                    help="按语言覆盖工具署名，格式 zh_tw=zhconv,en_us=LLM（模型未记录）")
    ap.add_argument("--store-hosts", default=",".join(STORE_HOSTS),
                    help="官方发行源域名（逗号分隔，命中即「已有官方来源」不打标）")
    ap.add_argument("--reclaim-langs", default="zh_tw",
                    help="边界 3a 改判限定语言（逗号分隔；空=全部语言）")
    ap.add_argument("--no-reclaim-official-inline", dest="reclaim", action="store_false",
                    help="关闭边界 3a：官方来源但头部有 zhconv 说明的文件保持「已有官方来源」")
    ap.add_argument("--no-anchor-fallback", dest="anchor_fallback", action="store_false",
                    help="关闭回退锚点：无 `> 数据来源：` 的文件一律跳过")
    ap.add_argument("--source-mode", default="auto", choices=["auto", "meta", "zhcn"])
    ap.add_argument("--date", default=datetime.date.today().isoformat(), help="标注日期 YYYY-MM-DD")
    ap.add_argument("--insert-at", default="metadata-end", choices=["metadata-end", "after-source"])
    ap.add_argument("--withdrawn-broad", action="store_true",
                    help="旧口径：版权撤下（W-4.6-19）也归入已撤下（issue #9 不采用）")
    ap.add_argument("--root", default=".", help="仓库根（沙箱验证时指向副本）")
    ap.add_argument("--json", default=None, help="矩阵 + 待打标清单写入 JSON")
    ap.add_argument("--list", type=int, default=10, help="额外打印 N 个待打标文件（0=不打印）")
    args = ap.parse_args(argv)

    if args.pilot is not None and args.pilot < 1:
        ap.error("--pilot 需 >= 1")

    # 工具署名映射（issue #9 边界 2）
    base_map = {"zh_tw": "zhconv"}
    for lang in LANGS:
        base_map.setdefault(lang, args.llm_tool)
    if args.tool_map:
        for pair in args.tool_map.split(","):
            if not pair.strip():
                continue
            k, _, v = pair.partition("=")
            k = k.strip()
            if k not in LANGS:
                ap.error("--tool-map 未知语言：%s" % k)
            base_map[k] = v.strip()
    args.tool_map = base_map
    args.reclaim_langs = [x.strip() for x in args.reclaim_langs.split(",") if x.strip()]
    STORE_HOSTS = tuple(h.strip() for h in args.store_hosts.split(",") if h.strip())

    langs = LANGS if args.lang == "all" else [args.lang]
    root = args.root

    rows = collect(root, langs, args.insert_at, args.anchor_fallback)
    reclaimed = reclassify_reclaim(rows, args, root) if args.reclaim else []
    if args.withdrawn_broad:
        rows = reclassify_broad(rows)

    print("=" * 78)
    print("存量非官方本地化追溯打标 · %s" % ("APPLY（写盘）" if args.apply else "DRY-RUN（不写盘）"))
    print("依据：翻译办法 §九 / D-065（2026-11-14）· 语言=%s（zh_cn 为基准，不参与）" % ",".join(langs))
    print("工具署名：%s" % "；".join("%s=%s" % (l, args.tool_map[l]) for l in LANGS))
    print("日期=%s · 插入=%s · 来源=%s · 撤下口径=%s · 官方发行源=%s"
          % (args.date, args.insert_at, args.source_mode,
             "broad（旧口径）" if args.withdrawn_broad else "strict",
             ",".join(STORE_HOSTS)))
    print("边界 3a 改判（官方+zhconv 说明 → 待打标，语言=%s）：%d 个"
          % (",".join(args.reclaim_langs) or "全部", len(reclaimed)))
    print("=" * 78)

    matrix, table, samples = build_matrix(rows, langs, args.pilot)
    print("\n## 标注状态矩阵（语言 × 标注状态）\n")
    print(matrix)

    print("\n## 口径说明与边界提示\n")
    print(build_notes(rows, langs, args))

    if any(samples[l] for l in langs):
        print("\n## 抽样明细（每语言 3 例；dry-run 拟插入行，不改文件）\n")
        print(sample_detail(samples, args, root))

    if args.list:
        n = 0
        lines = []
        for r in rows:
            if r["bucket"] != "pending":
                continue
            if n >= args.list:
                break
            n += 1
            lines.append("- %s" % short(r["path"]))
        print("\n## 待打标清单（前 %d 条）\n" % args.list)
        print("\n".join(lines))
        total_pending = sum(table[l]["pending"] for l in langs)
        if total_pending > n:
            print("- …（共 %d 个待打标，仅列前 %d）" % (total_pending, n))

    todo = apply_list(rows, args.pilot)
    no_anchor = [r for r in todo if r["anchor_kind"] == "none"]
    meta_anchor = [r for r in todo if r["anchor_kind"] == "meta"]
    mixed_nl = [r for r in todo if r["newline"] == "mixed"]
    writable = [r for r in todo
                if r["anchor_kind"] != "none" and r["newline"] != "mixed"]

    print("\n## 执行统计\n")
    print("- 本次纳入处理（--pilot=%s）：%d 个待打标文件"
          % ("不限" if args.pilot is None else args.pilot, len(todo)))
    print("- 可写：%d（其中回退到头部 `>` 元信息块末尾：%d）；无锚点跳过：%d；行尾混用跳过：%d"
          % (len(writable), len(meta_anchor), len(no_anchor), len(mixed_nl)))
    if no_anchor:
        print("- 无锚点样例：%s" % "、".join("`%s`" % short(r["path"]) for r in no_anchor[:5]))

    if args.apply:
        inserted, failed = 0, []
        for r in writable:
            cur, cur_bom, cur_nl = read_doc(r["path"])
            if cur != r["text"]:
                failed.append((r["path"], "读取后内容已变化，跳过（防并发覆盖）"))
                continue
            bucket2, _ = final_bucket(cur, r["lang"], args)
            if bucket2 != "pending":
                failed.append((r["path"], "复检为 %s，跳过" % BUCKET_CN[bucket2]))
                continue
            label, _ = build_label(r["lang"], r["path"], r["info"], args, root)
            doc = cur.split("\n")
            aidx, akind, _ = anchor_of(doc, args.insert_at, args.anchor_fallback)
            if aidx < 0:
                failed.append((r["path"], "复检时已无锚点，跳过"))
                continue
            doc.insert(aidx, label)
            write_doc(r["path"], "\n".join(doc), cur_bom, cur_nl)
            inserted += 1
        print("- 已插入标注：%d 个文件" % inserted)
        if failed:
            print("- 复检失败并跳过：%d" % len(failed))
            for p, why in failed[:20]:
                print("  - %s：%s" % (short(p), why))
        print("- 复核：再跑 --dry-run，对应语言「已标注」应等于本次插入数、「待打标」相应下降")
    else:
        print("- DRY-RUN：未修改任何文件。确认矩阵后再 --apply（建议先 --lang zh_tw --pilot 3）")

    if args.json:
        path = os.path.abspath(args.json)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "mode": "apply" if args.apply else "dry-run",
            "langs": langs,
            "rules": {
                "date": args.date, "insert_at": args.insert_at,
                "source_mode": args.source_mode,
                "withdrawn": "broad" if args.withdrawn_broad else "strict",
                "llm_tool": args.llm_tool, "pilot": args.pilot,
            },
            "matrix": {lang: dict(table[lang]) for lang in langs},
            "pending": [
                {
                    "lang": r["lang"],
                    "path": short(r["path"]),
                    "bucket": r["bucket"],
                    "source_url": r["info"]["src_url"],
                    "has_anchor": r["info"]["src_idx"] >= 0,
                    "label": build_label(r["lang"], r["path"], r["info"], args, root)[0],
                }
                for r in rows
            ],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print("- JSON 已写：%s（%d 条）" % (args.json, len(payload["pending"])))

    return 0


if __name__ == "__main__":
    sys.exit(main())
