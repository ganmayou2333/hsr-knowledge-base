#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSR 知识库 MCP 服务（只读 · 零依赖 · stdio JSON-RPC 2.0）

设计原则
- **零依赖**：只用 Python 标准库，不装任何 SDK
- **只读**：不提供任何写文件工具（写入一律走工单 + Lead 审核）
- **路径沙箱**：所有路径解析后必须落在 HSR_ROOT 内
- **修正存量脚本的两个缺陷**：
  1. 原 verify_fields.py 的 classify() 用 'character/' 前缀判断，迁移到 zh_cn/ 后全部误判为 other → 本实现先剥语言根目录
  2. 原脚本 skip_dirs 未排除 StarRailRes-master → 本实现统一排除

环境变量
- HSR_ROOT  知识库根目录，默认 G:\\HSR
"""
import json
import os
import re
import sys
import fnmatch
from pathlib import Path

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "hsr-kb"
SERVER_VERSION = "1.0.0"

ROOT = Path(os.environ.get("HSR_ROOT", r"G:\HSR")).resolve()

# 扫描时统一跳过的目录（含两个 StarRailRes 克隆与临时目录）
SKIP_DIRS = {
    ".git", ".obsidian", "node_modules", ".tmp_build",
    "temp", "StarRailRes-master", "StarRailRes_repo", "StarRailRes_data",
}
LANG_ROOTS = ("zh_cn", "zh_tw", "en_us", "ja_jp", "ko_kr")

MAX_READ_BYTES = 400_000
MAX_LIST = 500
MAX_SEARCH = 200


# ---------------------------------------------------------------- 基础工具

def safe_rel(rel: str) -> Path:
    """解析路径并保证落在 ROOT 内。"""
    p = (ROOT / rel.lstrip("/\\")).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError(f"路径越界：{rel}")
    return p


def iter_md(root: Path):
    """遍历 .md 文件，跳过 SKIP_DIRS。"""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith(".md"):
                yield Path(dirpath) / f


def rel_posix(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def read_text(p: Path) -> str:
    if p.stat().st_size > MAX_READ_BYTES:
        raise ValueError(f"文件过大（>{MAX_READ_BYTES} 字节），请用 offset/limit 分段读取")
    return p.read_text(encoding="utf-8", errors="ignore")


def get_version(txt: str) -> str:
    for line in txt.splitlines()[:10]:
        if line.startswith("> 数据版本："):
            return line.replace("> 数据版本：", "").strip()
    return "无"


def get_meta(txt: str) -> dict:
    meta = {}
    for key in ("数据来源", "数据版本", "实体ID", "官方Wiki"):
        m = re.search(rf"^> {key}：(.+)$", txt, re.M)
        if m:
            meta[key] = m.group(1).strip()
    return meta


# ---------------------------------------------------------------- 工具实现

def tool_kb_status(args):
    prefix = args.get("prefix", "zh_cn")
    base = safe_rel(prefix)
    if not base.exists():
        return {"error": f"目录不存在：{prefix}"}

    stat, totals = {}, {}
    for p in iter_md(base):
        ver = get_version(read_text(p))
        parts = p.relative_to(base).parts
        key = "/".join(parts[:2]) if len(parts) > 2 else (parts[0] if len(parts) > 1 else ".")
        stat[(key, ver)] = stat.get((key, ver), 0) + 1
        totals[ver] = totals.get(ver, 0) + 1

    lines = [f"# 版本分布（{prefix}）", ""]
    lines.append("| 目录 | 版本 | 文件数 |")
    lines.append("|---|---|---|")
    for (key, ver), n in sorted(stat.items()):
        lines.append(f"| {key} | {ver} | {n} |")
    lines += ["", "## 合计", ""]
    for ver, n in sorted(totals.items(), key=lambda x: -x[1]):
        lines.append(f"- `{ver}`：{n}")
    lines.append(f"- **总计**：{sum(totals.values())}")
    return {"text": "\n".join(lines), "totals": totals}


def tool_kb_search(args):
    query = args["query"]
    path = args.get("path", "zh_cn")
    use_regex = bool(args.get("regex", False))
    limit = min(int(args.get("limit", 50)), MAX_SEARCH)
    ctx = int(args.get("context", 0))
    base = safe_rel(path)
    if not base.exists():
        return {"error": f"路径不存在：{path}"}

    pat = re.compile(query if use_regex else re.escape(query), re.M)
    hits, scanned = [], 0
    for p in iter_md(base):
        scanned += 1
        try:
            txt = read_text(p)
        except ValueError:
            continue
        ls = txt.splitlines()
        for i, line in enumerate(ls):
            if pat.search(line):
                block = ls[max(0, i - ctx): i + ctx + 1] if ctx else [line]
                hits.append({"file": rel_posix(p), "line": i + 1, "text": "\n".join(block)})
                if len(hits) >= limit:
                    break
        if len(hits) >= limit:
            break
    out = [f"# 搜索 `{query}`（{path}，扫描 {scanned} 个文件，命中 {len(hits)} 条）", ""]
    for h in hits:
        out.append(f"- `{h['file']}:{h['line']}` {h['text']}")
    return {"text": "\n".join(out), "hits": hits}


def tool_kb_read(args):
    p = safe_rel(args["path"])
    if not p.is_file():
        return {"error": f"文件不存在：{args['path']}"}
    offset = max(1, int(args.get("offset", 1)))
    limit = min(int(args.get("limit", 200)), 2000)
    ls = read_text(p).splitlines()
    chunk = ls[offset - 1: offset - 1 + limit]
    body = "\n".join(f"{offset + i}\t{t}" for i, t in enumerate(chunk))
    return {"text": f"# {rel_posix(p)}（共 {len(ls)} 行，显示 {offset}-{offset + len(chunk) - 1}）\n\n{body}"}


def tool_kb_list(args):
    pattern = args.get("pattern", "zh_cn/**/*.md")
    cap = min(int(args.get("max", 200)), MAX_LIST)
    files = [rel_posix(p) for p in iter_md(ROOT) if fnmatch.fnmatch(rel_posix(p), pattern)]
    files.sort()
    shown = files[:cap]
    out = [f"# 匹配 `{pattern}`：{len(files)} 个文件（显示前 {len(shown)}）", ""]
    out += [f"- {f}" for f in shown]
    return {"text": "\n".join(out), "total": len(files)}


def _classify(rel: str):
    """修正版：先剥语言根目录，再判分类。"""
    parts = rel.split("/")
    if parts and parts[0] in LANG_ROOTS:
        parts = parts[1:]
    path = "/".join(parts)
    if path.startswith("character/"):
        return "character"
    if path.startswith("lightcone/"):
        return "lightcone"
    if path.startswith("items/"):
        return "items"
    if path.startswith("relic/"):
        return "relic"
    if path.startswith("events/"):
        return "activity"
    if path.startswith("enemies/"):
        return "enemy"
    if path.startswith("stages/"):
        return "stage"
    if path.startswith("simulated/"):
        if "/祝福/" in path:
            return "blessing"
        if "/奇物/" in path:
            return "curio"
        if "/事件/" in path:
            return "event"
        if "/区块/" in path:
            return "block"
        if "/差分宇宙/" in path:
            return "diff"
    return "other"


REQUIRE = {
    "character": {"meta": ["数据来源", "数据版本", "实体ID"],
                  "basic": ["角色名称", "命途", "属性", "稀有度"],
                  "sections": ["## 配音演员", "## 基础属性", "## 战技"]},
    "lightcone": {"meta": ["数据来源", "数据版本", "实体ID"],
                  "basic": ["光锥名称", "命途", "评级"], "sections": ["## 背景故事", "## 叠影效果"]},
    "items": {"meta": ["数据来源", "数据版本", "实体ID"],
              "basic": ["物品名称", "用途", "类型"],
              "optional_sections": ["## 说明", "## 获得途径"]},
    "relic": {"meta": ["数据来源", "数据版本", "实体ID"],
              "basic": ["名称", "类型"], "sections": ["## 套装效果", "## 部位"]},
    "activity": {"meta": ["数据来源", "数据版本", "实体ID"],
                 "basic": ["活动名称", "类型", "开放时间"], "sections": ["## 玩法说明"]},
    "enemy": {"meta": ["数据来源", "数据版本", "实体ID"],
              "basic": ["敌人名称", "类型", "弱点属性"], "sections": ["## 技能与机制"]},
    "stage": {"meta": ["数据来源", "数据版本", "实体ID"],
              "basic": ["关卡名称", "类型"], "sections": ["## 玩法机制", "## 主要掉落"]},
    "blessing": {"meta": ["数据来源", "数据版本", "实体ID"],
                 "basic": ["名称", "类型"], "sections": ["## 效果"]},
    "curio": {"meta": ["数据来源", "数据版本", "实体ID"],
              "basic": ["名称", "类型"], "sections": ["## 效果"]},
    "event": {"meta": ["数据来源", "数据版本", "实体ID"], "basic": ["名称", "类型"], "sections": []},
    "block": {"meta": ["数据来源", "数据版本", "实体ID"], "basic": ["名称", "类型"], "sections": []},
    "diff": {"meta": ["数据来源", "数据版本", "实体ID"], "basic": ["名称", "类型"], "sections": []},
}


def _basic_table(txt):
    d = {}
    for m in re.finditer(r"^\| ([^|]+) \| ([^|]*) \|", txt, re.M):
        k, v = m.group(1).strip(), m.group(2).strip()
        if k and v and v != "值":
            d[k] = v
    return d


def tool_kb_validate_fields(args):
    base = safe_rel(args.get("path", "zh_cn"))
    issues, known, ids, details = {}, {}, {}, 0
    for p in iter_md(base):
        txt = read_text(p)
        meta = get_meta(txt)
        if "实体ID" not in meta:
            continue
        details += 1
        cat = _classify(rel_posix(p))
        rule = REQUIRE.get(cat)
        if not rule:
            continue
        for k in rule["meta"]:
            if k not in meta:
                issues.setdefault((cat, f"缺元信息:{k}"), []).append(rel_posix(p))
        basic = _basic_table(txt)
        opt = rule.get("optional_basic", [])
        for k in rule["basic"]:
            if not basic.get(k):
                bucket = known if k in opt else issues
                bucket.setdefault((cat, f"缺基本字段:{k}"), []).append(rel_posix(p))
        for sec in rule.get("sections", []):
            if sec not in txt:
                issues.setdefault((cat, f"缺章节:{sec}"), []).append(rel_posix(p))
        for sec in rule.get("optional_sections", []):
            if sec not in txt:
                known.setdefault((cat, f"缺可选章节:{sec}"), []).append(rel_posix(p))
        ids.setdefault((cat, meta["实体ID"]), []).append(rel_posix(p))

    dups = {k: v for k, v in ids.items() if len(v) > 1}
    out = [f"# 字段校验（{args.get('path', 'zh_cn')}）", "",
           f"- 详情文件数：**{details}**",
           f"- 异常项类型：**{len(issues)}** ｜ 已知待补充类型：**{len(known)}** ｜ 重复实体ID：**{len(dups)}**", ""]
    out.append("## 异常（需处理）")
    for (cat, kind), fl in sorted(issues.items(), key=lambda x: -len(x[1]))[:30]:
        out.append(f"- [{cat}] {kind} × {len(fl)}，例：{fl[0]}")
    out.append("\n## 已知待补充（不计异常）")
    for (cat, kind), fl in sorted(known.items(), key=lambda x: -len(x[1]))[:20]:
        out.append(f"- [{cat}] {kind} × {len(fl)}")
    if dups:
        out.append("\n## 重复实体ID（同分类内）")
        for (cat, eid), fl in list(dups.items())[:20]:
            out.append(f"- [{cat}] {eid} × {len(fl)}：{fl[:3]}")
    return {"text": "\n".join(out), "detail_files": details,
            "issue_types": len(issues), "known_types": len(known), "dup_ids": len(dups)}


def tool_kb_validate_links(args):
    base = safe_rel(args.get("path", "zh_cn"))
    limit = min(int(args.get("limit", 50)), 500)
    existing = {rel_posix(p) for p in iter_md(ROOT)}
    dead, total = [], 0
    for p in iter_md(base):
        txt = read_text(p)
        for m in re.finditer(r"\[\[([^\]]+)\]\]", txt):
            total += 1
            raw = m.group(1)
            link = raw.replace("\\|", "|").split("|")[0].strip().lstrip("!")
            if not link:
                continue
            cands = [link, link + ".md"]
            if "#" in link:
                cands.append(link.split("#")[0])
            if not any(c in existing for c in cands):
                dead.append({"file": rel_posix(p), "target": link})
    out = [f"# 双链校验（{args.get('path', 'zh_cn')}）", "",
           f"- 链接总数：**{total}**", f"- 死链：**{len(dead)}**", ""]
    for d in dead[:limit]:
        out.append(f"- `{d['file']}` → `{d['target']}`")
    if len(dead) > limit:
        out.append(f"- …（其余 {len(dead) - limit} 条省略）")
    return {"text": "\n".join(out), "total_links": total, "dead": len(dead)}


def tool_kb_missing_fields(args):
    base = safe_rel(args.get("path", "zh_cn/items"))
    no_source, no_desc, detail = [], [], 0
    for p in iter_md(base):
        txt = read_text(p)
        if "实体ID" not in txt:
            continue
        detail += 1
        if "## 获得途径" not in txt:
            no_source.append(rel_posix(p))
        if "## 说明" not in txt and "## Description" not in txt:
            no_desc.append(rel_posix(p))
    out = [f"# 缺字段统计（{args.get('path', 'zh_cn/items')}）", "",
           f"- 详情文件：**{detail}**",
           f"- 缺「获得途径」：**{len(no_source)}**",
           f"- 缺「说明」：**{len(no_desc)}**", ""]
    out += [f"- 例：{x}" for x in (no_source[:10] + no_desc[:10])]
    return {"text": "\n".join(out), "detail_files": detail,
            "missing_source": len(no_source), "missing_desc": len(no_desc)}


def tool_kb_spec_section(args):
    heading = args["heading"]
    p = ROOT / "格式规范与要求.md"
    if not p.is_file():
        return {"error": "格式规范与要求.md 不存在"}
    txt = read_text(p)
    lines = txt.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("##") and heading in line:
            start = i
            break
    if start is None:
        heads = [l for l in lines if l.startswith("## ")]
        return {"error": f"未找到含「{heading}」的章节", "headings": heads}
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    body = "\n".join(lines[start:end])
    return {"text": f"# 格式规范与要求.md › {lines[start].strip()}\n\n{body}"}


def tool_kb_prompt_modules(args):
    d = ROOT / "docs" / "prompts"
    files = sorted(d.glob("*.md")) if d.is_dir() else []
    name = args.get("name")
    if not name:
        out = ["# 提示词模块清单", ""]
        out += [f"- `{rel_posix(p)}`（{p.stat().st_size} 字节）" for p in files]
        return {"text": "\n".join(out), "modules": [rel_posix(p) for p in files]}
    target = None
    for p in files:
        if p.name == name or p.stem == name or name in p.name:
            target = p
            break
    if target is None:
        return {"error": f"未找到模块：{name}"}
    return {"text": read_text(target)}


TOOLS = [
    ("kb_status", "统计知识库各目录的数据版本分布（等价 count_version.py，修正跳过目录）",
     {"type": "object", "properties": {"prefix": {"type": "string", "description": "根，默认 zh_cn"}}}),
    ("kb_search", "按关键字/正则全文搜索 Markdown",
     {"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string"},
                                       "regex": {"type": "boolean"}, "limit": {"type": "integer"},
                                       "context": {"type": "integer"}}, "required": ["query"]}),
    ("kb_read", "读取文件（带行号）",
     {"type": "object", "properties": {"path": {"type": "string"}, "offset": {"type": "integer"},
                                       "limit": {"type": "integer"}}, "required": ["path"]}),
    ("kb_list", "按 glob 列举知识库文件",
     {"type": "object", "properties": {"pattern": {"type": "string"}, "max": {"type": "integer"}}}),
    ("kb_validate_fields", "字段级校验（元信息/必备字段/章节/重复ID，修正 classify 前缀缺陷）",
     {"type": "object", "properties": {"path": {"type": "string"}}}),
    ("kb_validate_links", "Obsidian 双链校验（0 死链目标）",
     {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}}),
    ("kb_missing_fields", "统计物品库缺「获得途径」「说明」的文件数",
     {"type": "object", "properties": {"path": {"type": "string"}}}),
    ("kb_spec_section", "按标题关键字取《格式规范与要求.md》的某一节",
     {"type": "object", "properties": {"heading": {"type": "string"}}, "required": ["heading"]}),
    ("kb_prompt_modules", "列出或读取 docs/prompts 下的提示词模块",
     {"type": "object", "properties": {"name": {"type": "string"}}}),
]
HANDLERS = {
    "kb_status": tool_kb_status, "kb_search": tool_kb_search, "kb_read": tool_kb_read,
    "kb_list": tool_kb_list, "kb_validate_fields": tool_kb_validate_fields,
    "kb_validate_links": tool_kb_validate_links, "kb_missing_fields": tool_kb_missing_fields,
    "kb_spec_section": tool_kb_spec_section, "kb_prompt_modules": tool_kb_prompt_modules,
}

RESOURCES = [
    ("hsr://spec/format", "格式规范与要求.md", "格式规范总纲"),
    ("hsr://doc/data-sources", "数据来源.md", "数据来源总览"),
    ("hsr://prompts/readme", "docs/prompts/README.md", "提示词管理总纲"),
    ("hsr://prompts/core", "docs/prompts/10_核心_版本无关.md", "核心提示词（常驻）"),
    ("hsr://prompts/params-4.6", "docs/prompts/20_参数_4.6.md", "4.6 版本参数"),
    ("hsr://prompts/quest", "docs/prompts/30_模块_剧情获取.md", "剧情获取模块"),
    ("hsr://prompts/mcp", "docs/prompts/60_模块_MCP.md", "MCP 模块说明"),
    ("hsr://ops/reconcile-4.6", "docs/对账_4.6.md", "4.6 对账审核基线"),
    ("hsr://ops/pending", "docs/待补充清单.md", "待补充清单"),
]

PROMPTS = [
    ("core", "常驻核心提示词", "docs/prompts/10_核心_版本无关.md"),
    ("params_46", "4.6 版本参数与交付流程", "docs/prompts/20_参数_4.6.md"),
    ("quest", "剧情文本获取与回填模块", "docs/prompts/30_模块_剧情获取.md"),
]


# ---------------------------------------------------------------- JSON-RPC

def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def ok(mid, result):
    send({"jsonrpc": "2.0", "id": mid, "result": result})


def err(mid, code, message):
    send({"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}})


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}

    if method == "initialize":
        ok(mid, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
        return
    if method in ("notifications/initialized", "initialized"):
        return
    if method == "ping":
        ok(mid, {})
        return
    if method == "tools/list":
        ok(mid, {"tools": [
            {"name": n, "description": d, "inputSchema": s} for n, d, s in TOOLS]})
        return
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        fn = HANDLERS.get(name)
        if not fn:
            err(mid, -32602, f"未知工具：{name}")
            return
        try:
            res = fn(args)
        except Exception as e:  # 工具异常按 MCP 约定返回 isError
            ok(mid, {"content": [{"type": "text", "text": f"工具执行失败：{e}"}], "isError": True})
            return
        if "error" in res:
            ok(mid, {"content": [{"type": "text", "text": res["error"]}], "isError": True})
            return
        ok(mid, {"content": [{"type": "text", "text": res.get("text", "")}]})
        return
    if method == "resources/list":
        ok(mid, {"resources": [
            {"uri": u, "name": n, "description": d, "mimeType": "text/markdown"}
            for u, f, d in RESOURCES if (ROOT / f).is_file()]})
        return
    if method == "resources/read":
        uri = params.get("uri")
        for u, f, _ in RESOURCES:
            if u == uri:
                p = ROOT / f
                if not p.is_file():
                    err(mid, -32602, f"资源不存在：{f}")
                    return
                ok(mid, {"contents": [{"uri": u, "mimeType": "text/markdown", "text": read_text(p)}]})
                return
        err(mid, -32602, f"未知资源：{uri}")
        return
    if method == "prompts/list":
        ok(mid, {"prompts": [
            {"name": n, "description": d, "arguments": []} for n, d, _ in PROMPTS]})
        return
    if method == "prompts/get":
        name = params.get("name")
        for n, d, f in PROMPTS:
            if n == name:
                ok(mid, {"description": d, "messages": [
                    {"role": "user", "content": {"type": "text", "text": read_text(ROOT / f)}}]})
                return
        err(mid, -32602, f"未知提示词：{name}")
        return
    if mid is not None:
        err(mid, -32601, f"未实现的方法：{method}")


def main():
    if not ROOT.is_dir():
        sys.stderr.write(f"HSR_ROOT 不存在：{ROOT}\n")
        sys.exit(1)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            handle(msg)
        except Exception as e:
            mid = msg.get("id") if isinstance(msg, dict) else None
            if mid is not None:
                err(mid, -32603, f"内部错误：{e}")


if __name__ == "__main__":
    main()
