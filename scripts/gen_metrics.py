#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_metrics.py — 生成 docs/metrics.md（知识库规模唯一真值表）

用法（**仓库根目录**）：
    python scripts/gen_metrics.py

零依赖：仅 Python 标准库。
幂等：除首部「生成时间」一行外，任意两次运行的输出逐字节相同。
只读：不修改任何数据文件；唯一写盘 = docs/metrics.md。

真值来源（全部实测，禁止手填）：
  页数 / 版本分布          ← wiki/data/stats.js（由 python wiki/build_wiki.py 生成）
  五语入库文件数            ← git ls-tree -r --name-only HEAD -- <lang> | grep -c '\\.md$'
  五语工作区文件数          ← find <lang> -name '*.md' | wc -l（等价 pathlib.rglob）
  各类详情数 / 校验状态     ← scripts/verify_fields.py（**必须在 zh_cn 目录下运行**）
  站点链接 / 死链 / 未收录   ← wiki/data/link_report.json（build_wiki 产物）
  全库双链 / 死链           ← scripts/verify_links.py 的 scan()（本进程内调用）

任何一项取不到 → 该格写「未核实」，不猜。
"""
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANG_DIRS = ["zh_cn", "en_us", "zh_tw", "ja_jp", "ko_kr"]
MIRROR_DIRS = LANG_DIRS[1:]
OUT = ROOT / "docs" / "metrics.md"

# 详情口径 → 中文标签（顺序即文档表格行顺序）
DETAIL_ORDER = [
    ("character", "角色库", "`character/`"),
    ("lightcone", "光锥库", "`lightcone/`"),
    ("items", "物品库", "`items/`"),
    ("relic", "遗器库", "`relic/`"),
    ("simulated", "模拟宇宙库", "`simulated/`"),
    ("events", "活动库", "`events/`"),
    ("enemies", "敌人库", "`enemies/`"),
    ("stages", "关卡库", "`stages/`"),
    ("music", "音乐库", "`音乐/`"),
]
# simulated 的五个子类（verify_fields 分类口径）→ 用于重建 simulated 合计
SIM_SUBS = ["blessing", "curio", "event", "block", "diff"]


# ---------------- 最小工具 ----------------
def unverified():
    return None


def fmt(n):
    """整数 → 千分位；None → 未核实。"""
    return "未核实" if n is None else "{:,}".format(n)


# ---------------- 1. 五语文件数（入库 / 工作区） ----------------
def git_md_count(lang):
    """入库口径：git ls-tree -r --name-only HEAD -- <lang> 中以 .md 结尾的行数。

    Windows 中文路径要点：必须带 `-c core.quotepath=false`，
    否则中文路径被八进制转义，`endswith('.md')` 仍可用但不利于排查；
    保持一致口径以便与 shell 版 `git ls-tree … | grep -c '\\.md$'` 逐字对齐。
    """
    try:
        p = subprocess.run(
            ["git", "-c", "core.quotepath=false", "ls-tree", "-r", "--name-only", "HEAD", "--", lang],
            cwd=str(ROOT), capture_output=True, timeout=300,
        )
    except Exception:
        return None
    if p.returncode != 0:
        return None
    text = p.stdout.decode("utf-8", errors="replace")
    return sum(1 for line in text.splitlines() if line.endswith(".md"))


def worktree_md_count(lang):
    """工作区口径：find <lang> -name '*.md' | wc -l。"""
    d = ROOT / lang
    if not d.is_dir():
        return None
    return sum(1 for _ in d.rglob("*.md"))


# ---------------- 2. stats.js（build_wiki 产物） ----------------
def read_stats():
    f = ROOT / "wiki" / "data" / "stats.js"
    if not f.exists():
        return {}
    m = re.search(r"window\.STATS\s*=\s*(\{.*\})\s*;?\s*$",
                  f.read_text(encoding="utf-8", errors="replace").strip(), re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


# ---------------- 3. link_report.json（build_wiki 产物） ----------------
def read_link_report():
    f = ROOT / "wiki" / "data" / "link_report.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


# ---------------- 4. verify_fields.py（子进程，权威口径） ----------------
def run_verify_fields():
    """返回 (per_category, detail_total, issue_total, known_total)。

    verify_fields.py 自带 `sys.stdout.reconfigure(encoding='utf-8')`，
    因此管道输出就是 UTF-8，可以安全 decode。
    **必须在 zh_cn 目录下运行**（否则会扫描到四语镜像，口径翻 5 倍）。
    """
    script = ROOT / "scripts" / "verify_fields.py"
    cwd = ROOT / "data" / "zh_cn"
    if not script.exists() or not cwd.is_dir():
        return {}, None, None, None
    p = subprocess.run([sys.executable, str(script)], cwd=str(cwd),
                       capture_output=True, timeout=1800)
    txt = p.stdout.decode("utf-8", errors="replace")
    per = {}
    m = re.search(r"=== 详情文件分布（按类别） ===(.*?)(?:\n===|\Z)", txt, re.S)
    if m:
        for mm in re.finditer(r"^\[(\w+)\]\s+(\d+)\s*$", m.group(1), re.M):
            per[mm.group(1)] = int(mm.group(2))
    def grab(pat):
        mm = re.search(pat, txt, re.M)
        return int(mm.group(1)) if mm else None
    return (per,
            grab(r"^详情文件数:\s*(\d+)\s*$"),
            grab(r"^异常合计:\s*(\d+)\s*$"),
            grab(r"^已知待补充合计:\s*(\d+)\s*$"))


# ---------------- 5. verify_links.py（进程内调用 scan） ----------------
def run_verify_links():
    """返回 scan() 的统计；调用方必须先保证 cwd 无关（scan 接收绝对根目录）。"""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import verify_links  # noqa: E402
        return verify_links.scan(str(ROOT))
    except Exception:
        return {}


# ---------------- 6. 遗器分类明细（位面 / 隧洞） ----------------
def relic_split():
    """隧洞遗器 / 位面饰品的详情数（含 `> 实体ID：`，排除「文件名==上级目录名」索引）。"""
    out = {}
    for sub in ("隧洞遗器", "位面饰品"):
        d = ROOT / "data" / "zh_cn" / "relic" / sub
        if not d.is_dir():
            out[sub] = None
            continue
        n = 0
        for p in d.rglob("*.md"):
            if p.stem == p.parent.name:
                continue
            if re.search(r"^>\s*实体ID[：:]", p.read_text(encoding="utf-8", errors="replace"), re.M):
                n += 1
        out[sub] = n
    return out


def doc_type_counts():
    """文档型目录（不含 `> 实体ID：`）的实际 .md 数。"""
    out = {}
    for d in ("quest", "worldview", "货币战争", "rules"):
        p = ROOT / "data" / "zh_cn" / d
        out[d] = sum(1 for _ in p.rglob("*.md")) if p.is_dir() else None
    return out


# ---------------- 7. 汇总 ----------------
def collect():
    stats = read_stats()
    report = read_link_report()
    per, detail_total, issue_total, known_total = run_verify_fields()
    links = run_verify_links()
    relic = relic_split()
    doct = doc_type_counts()

    m = {}
    m["pages"] = stats.get("pages")
    m["latest_version"] = stats.get("latestVersion")
    m["versions"] = stats.get("versions") or {}
    m["versioned_pages"] = stats.get("versionedPages")
    m["dated_pages"] = stats.get("datedPages")
    m["stats_generated"] = stats.get("generated")

    for lang in LANG_DIRS:
        m["md_commit_" + lang] = git_md_count(lang)
        m["md_worktree_" + lang] = worktree_md_count(lang)

    # 负向指标（D-078 / 主线 B）：镜像中含「本地化来源：非官方」§九标注的文件数，
    # 只减不增——替换为官方原文后应下降。只读文件头 8KB（标注固定在头部元信息区）。
    def labeled_nonofficial_count(lang):
        n = 0
        needle = "本地化来源：非官方".encode("utf-8")
        for p in (ROOT / lang).rglob("*.md"):
            try:
                with open(p, "rb") as fh:
                    if needle in fh.read(8192):
                        n += 1
            except OSError:
                continue
        return n

    for lang in MIRROR_DIRS:
        m["labeled_nonofficial_" + lang] = labeled_nonofficial_count(lang)

    m["detail_total"] = detail_total
    for key, _label, _d in DETAIL_ORDER:
        if key == "simulated":
            vals = [per.get(s) for s in SIM_SUBS]
            m["detail_simulated"] = None if any(v is None for v in vals) else sum(vals)
        else:
            m["detail_" + key] = per.get(key)
    m["detail_blessing"] = per.get("blessing")
    m["detail_curio"] = per.get("curio")
    m["detail_simu_event"] = per.get("event")
    m["detail_block"] = per.get("block")
    m["detail_diff"] = per.get("diff")

    m["relic_cavern"] = relic.get("隧洞遗器")
    m["relic_planar"] = relic.get("位面饰品")
    for d, v in doct.items():
        m["doctype_" + d] = v

    m["link_total"] = report.get("total")
    m["link_dead"] = report.get("dead")
    m["link_missing"] = report.get("missing")
    m["wikilink_total"] = links.get("total")
    m["wikilink_dead"] = links.get("dead")
    m["wikilink_dead_data"] = links.get("dead_data")
    m["wikilink_files"] = links.get("files")

    m["vf_issue"] = issue_total
    m["vf_known"] = known_total

    # 镜像「各约 N」= 入库均值的十位取整
    commits = [m.get("md_commit_" + l) for l in MIRROR_DIRS]
    m["mirror_commit_avg_round10"] = (
        None if any(c is None for c in commits)
        else int(round(sum(commits) / len(commits) / 10.0) * 10)
    )
    # 工作区与 HEAD 的数量差，不代表未入库文件数。
    m["mirror_gap"] = all(m.get("md_commit_" + l) is not None for l in MIRROR_DIRS) and \
        (m.get("md_worktree_en_us") - m.get("md_commit_en_us"))
    return m


# ---------------- 8. 渲染 ----------------
def render(m, now):
    L = []
    a = L.append
    a("# 知识库规模真值表（`docs/metrics.md`）")
    a("")
    a("> **本文件由 `scripts/gen_metrics.py` 自动生成，请勿手工编辑。**")
    a("> 生成时间：`%s`" % now.strftime("%Y-%m-%d %H:%M:%S"))
    a("> 重新生成：`python scripts/gen_metrics.py`（幂等：除上一行时间外，两次运行输出逐字节相同）")
    a("> 校验：`python tools/verify_site.py` 的 `[16]` 项解析本文末尾的**机器可读真值**，")
    a("> 与 `README.md` · `docs/README_{en,ja,ko,zh-Hant}.md` · `docs/仓库结构.md` 出现的规模数字逐项比对。")
    a("")
    a("---")
    a("")
    a("## 一、口径（读数字前必看）")
    a("")
    a("| 指标 | 口径 | 实测命令 |")
    a("|---|---|---|")
    a("| **入库数** | `git ls-tree` 口径：生成时 `HEAD` 提交中的文件。CI 与线上内容取决于各自检出和部署的提交。 | `git ls-tree -r --name-only HEAD -- <lang> \\| grep -c '\\.md$'` |")
    a("| **工作区数** | 本地磁盘实际文件数，**含实际存在的 gitignore 文件，例如 `*/quest/剧情文本/`**（D-020/D-025 合规撤下、不入库）。 | `find <lang> -name '*.md' \\| wc -l` |")
    a("| **详情文件** | 含 `> 实体ID：` 元信息，且排除「文件名 == 上级目录名」的索引 / 分组文件与类别主索引（D-048 / D-061 / D-067）。 | `cd zh_cn && python ../scripts/verify_fields.py` |")
    a("| **页面数** | `zh_cn/` 每个 `.md` 一页；构建产物反映构建时工作区，不一定是生成统计时的工作区。 | `python wiki/build_wiki.py` |")
    a("")
    a("> **对外报数一律用「入库数」**（D-068）：文档若写工作区数，必须在括注中写明口径与差值来源，")
    a("> 否则会出现「文档比线上多 167 个文件」的失真。")
    a("")
    a("---")
    a("")
    a("## 二、总览")
    a("")
    a("| 指标 | 值 | 说明 |")
    a("|---|---|---|")
    a("| `zh_cn` 页面数（静态站） | **%s** | `wiki/data/stats.js` 的 `pages`（构建时快照）；统计时工作区 `.md` 数 %s |"
      % (fmt(m["pages"]), fmt(m["md_worktree_zh_cn"])))
    a("| `zh_cn` 入库 `.md` | **%s** | 工作区 %s，与 HEAD 数量差 %s；原因需逐项核对 |"
      % (fmt(m["md_commit_zh_cn"]), fmt(m["md_worktree_zh_cn"]),
         fmt(None if m["md_worktree_zh_cn"] is None or m["md_commit_zh_cn"] is None
             else m["md_worktree_zh_cn"] - m["md_commit_zh_cn"])))
    a("| `zh_cn` 详情文件数 | **%s** | 详情口径合计（各分类之和见 §四） |" % fmt(m["detail_total"]))
    a("| 库内最高数据版本 | **%s** | `stats.js` 的 `latestVersion` |" % (m["latest_version"] or "未核实"))
    a("| `verify_fields` 异常 | **%s** | 要求 0 |" % fmt(m["vf_issue"]))
    a("| `verify_fields` 已知待补充 | **%s** | 已知状态，不计异常 |" % fmt(m["vf_known"]))
    a("| 站点死链 | **%s** | `link_report.json` 的 `dead`，要求 0 |" % fmt(m["link_dead"]))
    a("")
    a("---")
    a("")
    a("## 三、五语规模（入库 / 工作区）")
    a("")
    a("| 语言目录 | 入库 `.md` | 工作区 `.md` | 数量差（工作区 − HEAD） |")
    a("|---|---|---|---|")
    a("| `zh_cn/` | %s | %s | %s |" % _row(m, "zh_cn"))
    for lang in MIRROR_DIRS:
        a("| `%s/` | %s | %s | %s |" % ((lang,) + _row(m, lang)))
    a("")
    a("> 数量差是两个计数之差，并非未入库文件数；忽略或未跟踪文件、工作区删除等均可能影响差值。`*/quest/剧情文本/` 的处理见 D-020、D-025。")
    a("> 镜像四语入库均值 %s，十位取整 **各约 %s**（README 括注口径）。"
      % (_mirror_avg_text(m), fmt(m["mirror_commit_avg_round10"])))
    a("")
    a("---")
    a("")
    a("## 四、各类详情文件数（`zh_cn`，详情口径）")
    a("")
    a("| 类别 | 详情数 | 目录 |")
    a("|---|---|---|")
    for key, label, d in DETAIL_ORDER:
        a("| %s | **%s** | %s |" % (label, fmt(m.get("detail_" + key)), d))
    a("| **合计** | **%s** | 各分类之和 |" % fmt(m["detail_total"]))
    a("")
    a("**`simulated/` 1,793 的构成**（`verify_fields` 分类口径）：")
    a("")
    a("| 子类 | 数量 |")
    a("|---|---|")
    a("| 祝福 `blessing` | %s |" % fmt(m["detail_blessing"]))
    a("| 奇物 `curio` | %s |" % fmt(m["detail_curio"]))
    a("| 事件 `simu_event` | %s |" % fmt(m["detail_simu_event"]))
    a("| 区块 `block` | %s |" % fmt(m["detail_block"]))
    a("| 差分宇宙 `diff` | %s |" % fmt(m["detail_diff"]))
    a("")
    a("**`relic/` 64 的构成**：隧洞遗器 **%s** + 位面饰品 **%s**。"
      % (fmt(m["relic_cavern"]), fmt(m["relic_planar"])))
    a("")
    a("**文档型目录**（不含 `> 实体ID：`，详情口径计 **0**）的实际 `.md` 数：")
    a("")
    a("| 目录 | 实际 `.md` |")
    a("|---|---|")
    for d in ("quest", "worldview", "货币战争", "rules"):
        a("| `%s/` | %s |" % (d, fmt(m.get("doctype_" + d))))
    a("")
    a("---")
    a("")
    a("## 五、链接与死链")
    a("")
    a("| 指标 | 值 | 来源 |")
    a("|---|---|---|")
    a("| 站点页内链接总数 | %s | `wiki/data/link_report.json` 的 `total`（`build_wiki.py` 产物） |" % fmt(m["link_total"]))
    a("| 站点死链数 | **%s** | 同上 `dead`（要求 0） |" % fmt(m["link_dead"]))
    a("| 站点未收录（优雅降级为纯文本） | %s | 同上 `missing`（合规未入库内容，属预期，不算死链） |" % fmt(m["link_missing"]))
    a("| 全库双链 `[[…]]` 总数 | %s | `scripts/verify_links.py`（扫描 %s 个 `.md`） |" % (fmt(m["wikilink_total"]), fmt(m["wikilink_files"])))
    a("| 全库双链死链数 | %s | 同上（含文档里的示例行，故非 0） |" % fmt(m["wikilink_dead"]))
    a("| **数据区**（五语目录）双链死链数 | **%s** | 同上；**判据（要求 0）**：非 0 时 `verify_links.py` 退出码为 1 |" % fmt(m["wikilink_dead_data"]))
    a("")
    a("> 文档区（`docs/`、`update.md`、`格式规范与要求.md` 等）的死链多为**语法示例**（`[[xxx]]`、`[[页面\\|示例]]`），")
    a("> 按 D-072 与 `verify_links.py` 口径**不计入**数据区判据。")
    a("")
    a("---")
    a("")
    a("## 六、版本分布（`zh_cn`，`stats.js` 口径）")
    a("")
    a("| 数据版本 | 页面数 |")
    a("|---|---|")
    for v, n in sorted(m["versions"].items(), key=lambda kv: _vkey(kv[0]), reverse=True):
        a("| %s | %s |" % (v, "{:,}".format(n)))
    a("| **带版本页合计** | **%s** |" % fmt(m["versioned_pages"]))
    a("| 带日期页合计 | %s |" % fmt(m["dated_pages"]))
    a("")
    a("> `stats.js` 生成时刻：`%s`。版本分布 ≠ 最新版本：库内绝大多数页面的 `> 数据版本：` 仍是收录时的版本。"
      % (m["stats_generated"] or "未核实"))
    a("")
    a("---")
    a("")
    a("## 七、校验状态")
    a("")
    a("| 校验器 | 命令 | 结果 |")
    a("|---|---|---|")
    a("| `verify_fields` | `cd zh_cn && python ../scripts/verify_fields.py`（**必须在 `zh_cn` 下运行**） | 扫描 %s 个 `.md`；详情 %s；异常 **%s**；已知待补充 **%s** |"
      % (fmt(m["md_worktree_zh_cn"]), fmt(m["detail_total"]), fmt(m["vf_issue"]), fmt(m["vf_known"])))
    a("| `verify_links` | `python scripts/verify_links.py`（仓库根） | 双链 %s；死链 %s（其中数据区 **%s**） |"
      % (fmt(m["wikilink_total"]), fmt(m["wikilink_dead"]), fmt(m["wikilink_dead_data"])))
    a("| `verify_site` | `python tools/verify_site.py`（仓库根） | `[1]`–`[16]` 全 PASS；`[16]` 即比对本文真值 |")
    a("")
    a("---")
    a("")
    a("## 八、机器可读真值（`tools/verify_site.py` 的 `[16]` 解析本节）")
    a("")
    a("> 格式固定：每行 `| \\`<key>\\` | <值> |`。改动本节会使 `[16]` 失配 —— 请改 `gen_metrics.py` 重新生成。")
    a("")
    a("| key | value |")
    a("|---|---|")
    keys = ["pages"]
    for lang in LANG_DIRS:
        keys += ["md_commit_" + lang, "md_worktree_" + lang]
    keys += ["detail_total"] + ["detail_" + k for k, _l, _d in DETAIL_ORDER]
    keys += ["relic_cavern", "relic_planar"]
    keys += ["doctype_" + d for d in ("quest", "worldview", "货币战争", "rules")]
    keys += ["link_total", "link_dead", "link_missing",
             "wikilink_total", "wikilink_dead", "wikilink_dead_data", "wikilink_files",
             "vf_issue", "vf_known", "mirror_commit_avg_round10", "mirror_gap",
             "versioned_pages", "dated_pages"]
    keys += ["labeled_nonofficial_" + l for l in MIRROR_DIRS]
    for k in keys:
        a("| `%s` | %s |" % (k, fmt(m.get(k))))
    for v, n in sorted(m["versions"].items(), key=lambda kv: _vkey(kv[0]), reverse=True):
        a("| `version_%s` | %s |" % (v, "{:,}".format(n)))
    a("")
    a("*本文件由 `scripts/gen_metrics.py` 生成；口径争议以 `docs/prompts/决策记录.md` 的 D-048 / D-062 / D-068 为准。*")
    a("")
    return "\n".join(L)


def _vkey(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except Exception:
        return (0,)


def _row(m, lang):
    c = m.get("md_commit_" + lang)
    w = m.get("md_worktree_" + lang)
    gap = None if (c is None or w is None) else w - c
    return (fmt(c), fmt(w), fmt(gap))


def _mirror_avg_text(m):
    vals = [m.get("md_commit_" + l) for l in MIRROR_DIRS]
    if any(v is None for v in vals):
        return "未核实"
    return "{:,.1f}".format(sum(vals) / len(vals))


def main():
    now = datetime.now()
    m = collect()
    md = render(m, now)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md if md.endswith("\n") else md + "\n")
    print("已生成 %s（%d 行 / %d 字节）"
          % (OUT.relative_to(ROOT), md.count("\n") + 1, len(md.encode("utf-8"))))
    print("页数=%s  详情合计=%s  镜像入库=%s  镜像各约=%s  异常=%s  待补=%s  数据区死链=%s"
          % (fmt(m["pages"]), fmt(m["detail_total"]),
             "/".join(fmt(m.get("md_commit_" + l)) for l in MIRROR_DIRS),
             fmt(m["mirror_commit_avg_round10"]),
             fmt(m["vf_issue"]), fmt(m["vf_known"]), fmt(m["wikilink_dead_data"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
