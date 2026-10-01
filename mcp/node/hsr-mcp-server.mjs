#!/usr/bin/env node
/**
 * HSR 知识库 MCP 服务（Node 版 · 只读 · 零依赖 · stdio JSON-RPC 2.0）
 *
 * 与 mcp/python/hsr_mcp_server.py 工具语义一致；无需安装 @modelcontextprotocol/sdk。
 * 若想改用官方 SDK，只需把本文件的 transport 换成 StdioServerTransport 并注册同一批 handler。
 *
 * 环境变量：HSR_ROOT（默认 G:\HSR）
 */
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";

const PROTOCOL_VERSION = "2024-11-05";
const SERVER_NAME = "hsr-kb";
const SERVER_VERSION = "1.0.0";
const ROOT = path.resolve(process.env.HSR_ROOT || "G:\\HSR");

const SKIP_DIRS = new Set([
  ".git", ".obsidian", "node_modules", ".tmp_build",
  "temp", "StarRailRes-master", "StarRailRes_repo", "StarRailRes_data",
]);
const LANG_ROOTS = new Set(["zh_cn", "zh_tw", "en_us", "ja_jp", "ko_kr"]);

const MAX_READ_BYTES = 400_000;
const MAX_LIST = 500;
const MAX_SEARCH = 200;

// ---------------------------------------------------------------- 基础

function safeRel(rel) {
  const p = path.resolve(ROOT, String(rel).replace(/^[/\\]+/, ""));
  if (p !== ROOT && !p.startsWith(ROOT + path.sep)) throw new Error(`路径越界：${rel}`);
  return p;
}

function* iterMd(root) {
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    let entries = [];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (!SKIP_DIRS.has(e.name)) stack.push(full);
      } else if (e.name.endsWith(".md")) {
        yield full;
      }
    }
  }
}

const relPosix = (p) => path.relative(ROOT, p).split(path.sep).join("/");

function readText(p) {
  const st = fs.statSync(p);
  if (st.size > MAX_READ_BYTES) throw new Error(`文件过大（>${MAX_READ_BYTES} 字节）`);
  return fs.readFileSync(p, "utf8");
}

function getVersion(txt) {
  for (const line of txt.split(/\r?\n/).slice(0, 10)) {
    if (line.startsWith("> 数据版本：")) return line.replace("> 数据版本：", "").trim();
  }
  return "无";
}

function getMeta(txt) {
  const meta = {};
  for (const key of ["数据来源", "数据版本", "实体ID", "官方Wiki"]) {
    const m = txt.match(new RegExp(`^> ${key}：(.+)$`, "m"));
    if (m) meta[key] = m[1].trim();
  }
  return meta;
}

function globToRe(glob) {
  const esc = glob.replace(/[.+^${}()|[\]\\]/g, "\\$&");
  return new RegExp("^" + esc.replace(/\*\*/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\u0000/g, ".*") + "$");
}

// ---------------------------------------------------------------- 工具

function toolKbStatus(args) {
  const prefix = args.prefix || "zh_cn";
  const base = safeRel(prefix);
  if (!fs.existsSync(base)) return { error: `目录不存在：${prefix}` };
  const stat = new Map(), totals = new Map();
  for (const p of iterMd(base)) {
    const ver = getVersion(readText(p));
    const parts = path.relative(base, p).split(path.sep);
    const key = parts.length > 2 ? parts.slice(0, 2).join("/") : (parts.length > 1 ? parts[0] : ".");
    stat.set(`${key}\u0000${ver}`, (stat.get(`${key}\u0000${ver}`) || 0) + 1);
    totals.set(ver, (totals.get(ver) || 0) + 1);
  }
  const lines = [`# 版本分布（${prefix}）`, "", "| 目录 | 版本 | 文件数 |", "|---|---|---|"];
  [...stat.entries()].sort().forEach(([k, n]) => {
    const [key, ver] = k.split("\u0000");
    lines.push(`| ${key} | ${ver} | ${n} |`);
  });
  lines.push("", "## 合计", "");
  [...totals.entries()].sort((a, b) => b[1] - a[1]).forEach(([ver, n]) => lines.push(`- \`${ver}\`：${n}`));
  lines.push(`- **总计**：${[...totals.values()].reduce((a, b) => a + b, 0)}`);
  return { text: lines.join("\n"), totals: Object.fromEntries(totals) };
}

function toolKbSearch(args) {
  const base = safeRel(args.path || "zh_cn");
  if (!fs.existsSync(base)) return { error: `路径不存在：${args.path}` };
  const limit = Math.min(args.limit || 50, MAX_SEARCH);
  const ctx = args.context || 0;
  const re = new RegExp(args.regex ? args.query : args.query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "m");
  const hits = [];
  let scanned = 0;
  for (const p of iterMd(base)) {
    scanned++;
    const ls = readText(p).split(/\r?\n/);
    for (let i = 0; i < ls.length; i++) {
      if (re.test(ls[i])) {
        const text = ctx ? ls.slice(Math.max(0, i - ctx), i + ctx + 1).join("\n") : ls[i];
        hits.push({ file: relPosix(p), line: i + 1, text });
        if (hits.length >= limit) break;
      }
    }
    if (hits.length >= limit) break;
  }
  const out = [`# 搜索 \`${args.query}\`（${args.path || "zh_cn"}，扫描 ${scanned} 个文件，命中 ${hits.length} 条）`, ""];
  hits.forEach((h) => out.push(`- \`${h.file}:${h.line}\` ${h.text}`));
  return { text: out.join("\n"), hits };
}

function toolKbRead(args) {
  const p = safeRel(args.path);
  if (!fs.existsSync(p) || !fs.statSync(p).isFile()) return { error: `文件不存在：${args.path}` };
  const offset = Math.max(1, args.offset || 1);
  const limit = Math.min(args.limit || 200, 2000);
  const ls = readText(p).split(/\r?\n/);
  const chunk = ls.slice(offset - 1, offset - 1 + limit);
  const body = chunk.map((t, i) => `${offset + i}\t${t}`).join("\n");
  return { text: `# ${relPosix(p)}（共 ${ls.length} 行，显示 ${offset}-${offset + chunk.length - 1}）\n\n${body}` };
}

function toolKbList(args) {
  const pattern = args.pattern || "zh_cn/**/*.md";
  const cap = Math.min(args.max || 200, MAX_LIST);
  const re = globToRe(pattern);
  const files = [];
  for (const p of iterMd(ROOT)) {
    const r = relPosix(p);
    if (re.test(r)) files.push(r);
  }
  files.sort();
  const out = [`# 匹配 \`${pattern}\`：${files.length} 个文件（显示前 ${Math.min(cap, files.length)}）`, ""];
  files.slice(0, cap).forEach((f) => out.push(`- ${f}`));
  return { text: out.join("\n"), total: files.length };
}

function classify(rel) {
  let parts = rel.split("/");
  if (LANG_ROOTS.has(parts[0])) parts = parts.slice(1);
  const p = parts.join("/");
  if (p.startsWith("character/")) return "character";
  if (p.startsWith("lightcone/")) return "lightcone";
  if (p.startsWith("items/")) return "items";
  if (p.startsWith("relic/")) return "relic";
  if (p.startsWith("events/")) return "activity";
  if (p.startsWith("enemies/")) return "enemy";
  if (p.startsWith("stages/")) return "stage";
  if (p.startsWith("simulated/")) {
    if (p.includes("/祝福/")) return "blessing";
    if (p.includes("/奇物/")) return "curio";
    if (p.includes("/事件/")) return "event";
    if (p.includes("/区块/")) return "block";
    if (p.includes("/差分宇宙/")) return "diff";
  }
  return "other";
}

const REQUIRE = {
  character: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["角色名称", "命途", "属性", "稀有度"], sections: ["## 配音演员", "## 基础属性", "## 战技"] },
  lightcone: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["光锥名称", "命途", "评级"], sections: ["## 背景故事", "## 叠影效果"] },
  items: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["物品名称", "用途", "类型"], optional_sections: ["## 说明", "## 获得途径"] },
  relic: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["名称", "类型"], sections: ["## 套装效果", "## 部位"] },
  activity: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["活动名称", "类型", "开放时间"], sections: ["## 玩法说明"] },
  enemy: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["敌人名称", "类型", "弱点属性"], sections: ["## 技能与机制"] },
  stage: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["关卡名称", "类型"], sections: ["## 玩法机制", "## 主要掉落"] },
  blessing: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["名称", "类型"], sections: ["## 效果"] },
  curio: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["名称", "类型"], sections: ["## 效果"] },
  event: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["名称", "类型"], sections: [] },
  block: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["名称", "类型"], sections: [] },
  diff: { meta: ["数据来源", "数据版本", "实体ID"], basic: ["名称", "类型"], sections: [] },
};

function basicTable(txt) {
  const d = {};
  for (const m of txt.matchAll(/^\| ([^|]+) \| ([^|]*) \|/gm)) {
    const k = m[1].trim(), v = m[2].trim();
    if (k && v && v !== "值") d[k] = v;
  }
  return d;
}

function toolKbValidateFields(args) {
  const base = safeRel(args.path || "zh_cn");
  const issues = new Map(), known = new Map(), ids = new Map();
  let details = 0;
  for (const p of iterMd(base)) {
    const txt = readText(p);
    const meta = getMeta(txt);
    if (!meta["实体ID"]) continue;
    details++;
    const cat = classify(relPosix(p));
    const rule = REQUIRE[cat];
    if (!rule) continue;
    for (const k of rule.meta) if (!meta[k]) push(issues, `${cat}|缺元信息:${k}`, relPosix(p));
    const basic = basicTable(txt);
    for (const k of rule.basic) if (!basic[k]) push(issues, `${cat}|缺基本字段:${k}`, relPosix(p));
    for (const sec of rule.sections || []) if (!txt.includes(sec)) push(issues, `${cat}|缺章节:${sec}`, relPosix(p));
    for (const sec of rule.optional_sections || []) if (!txt.includes(sec)) push(known, `${cat}|缺可选章节:${sec}`, relPosix(p));
    push(ids, `${cat}|${meta["实体ID"]}`, relPosix(p));
  }
  const dups = [...ids.entries()].filter(([, v]) => v.length > 1);
  const out = [`# 字段校验（${args.path || "zh_cn"}）`, "", `- 详情文件数：**${details}**`,
    `- 异常项类型：**${issues.size}** ｜ 已知待补充类型：**${known.size}** ｜ 重复实体ID：**${dups.length}**`, "", "## 异常（需处理）"];
  [...issues.entries()].sort((a, b) => b[1].length - a[1].length).slice(0, 30)
    .forEach(([k, v]) => out.push(`- [${k.replace("|", "] ")}] × ${v.length}，例：${v[0]}`));
  out.push("", "## 已知待补充（不计异常）");
  [...known.entries()].sort((a, b) => b[1].length - a[1].length).slice(0, 20)
    .forEach(([k, v]) => out.push(`- [${k.replace("|", "] ")}] × ${v.length}`));
  if (dups.length) {
    out.push("", "## 重复实体ID（同分类内）");
    dups.slice(0, 20).forEach(([k, v]) => out.push(`- [${k.replace("|", "] ")}] × ${v.length}：${v.slice(0, 3).join(", ")}`));
  }
  return { text: out.join("\n"), detail_files: details, issue_types: issues.size, known_types: known.size, dup_ids: dups.length };
}

function push(map, key, val) {
  if (!map.has(key)) map.set(key, []);
  map.get(key).push(val);
}

function toolKbValidateLinks(args) {
  const base = safeRel(args.path || "zh_cn");
  const limit = Math.min(args.limit || 50, 500);
  const existing = new Set();
  for (const p of iterMd(ROOT)) existing.add(relPosix(p));
  const dead = [];
  let total = 0;
  for (const p of iterMd(base)) {
    const txt = readText(p);
    for (const m of txt.matchAll(/\[\[([^\]]+)\]\]/g)) {
      total++;
      let link = m[1].replace(/\\\|/g, "|").split("|")[0].trim().replace(/^!/, "");
      if (!link) continue;
      const cands = [link, link + ".md"];
      if (link.includes("#")) cands.push(link.split("#")[0]);
      if (!cands.some((c) => existing.has(c))) dead.push({ file: relPosix(p), target: link });
    }
  }
  const out = [`# 双链校验（${args.path || "zh_cn"}）`, "", `- 链接总数：**${total}**`, `- 死链：**${dead.length}**`, ""];
  dead.slice(0, limit).forEach((d) => out.push(`- \`${d.file}\` → \`${d.target}\``));
  if (dead.length > limit) out.push(`- …（其余 ${dead.length - limit} 条省略）`);
  return { text: out.join("\n"), total_links: total, dead: dead.length };
}

function toolKbMissingFields(args) {
  const base = safeRel(args.path || "zh_cn/items");
  const noSource = [], noDesc = [];
  let detail = 0;
  for (const p of iterMd(base)) {
    const txt = readText(p);
    if (!txt.includes("实体ID")) continue;
    detail++;
    if (!txt.includes("## 获得途径")) noSource.push(relPosix(p));
    if (!txt.includes("## 说明") && !txt.includes("## Description")) noDesc.push(relPosix(p));
  }
  const out = [`# 缺字段统计（${args.path || "zh_cn/items"}）`, "", `- 详情文件：**${detail}**`,
    `- 缺「获得途径」：**${noSource.length}**`, `- 缺「说明」：**${noDesc.length}**`, ""];
  [...noSource.slice(0, 10), ...noDesc.slice(0, 10)].forEach((x) => out.push(`- 例：${x}`));
  return { text: out.join("\n"), detail_files: detail, missing_source: noSource.length, missing_desc: noDesc.length };
}

function toolKbSpecSection(args) {
  const p = path.join(ROOT, "格式规范与要求.md");
  if (!fs.existsSync(p)) return { error: "格式规范与要求.md 不存在" };
  const lines = readText(p).split(/\r?\n/);
  const start = lines.findIndex((l) => l.startsWith("##") && l.includes(args.heading));
  if (start < 0) return { error: `未找到含「${args.heading}」的章节`, headings: lines.filter((l) => l.startsWith("## ")) };
  let end = lines.length;
  for (let j = start + 1; j < lines.length; j++) if (lines[j].startsWith("## ")) { end = j; break; }
  return { text: `# 格式规范与要求.md › ${lines[start].trim()}\n\n${lines.slice(start, end).join("\n")}` };
}

function toolKbPromptModules(args) {
  const dir = path.join(ROOT, "docs", "prompts");
  const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => f.endsWith(".md")).sort() : [];
  if (!args.name) {
    const out = ["# 提示词模块清单", ""];
    files.forEach((f) => out.push(`- \`docs/prompts/${f}\`（${fs.statSync(path.join(dir, f)).size} 字节）`));
    return { text: out.join("\n"), modules: files.map((f) => `docs/prompts/${f}`) };
  }
  const hit = files.find((f) => f === args.name || f.replace(/\.md$/, "") === args.name || f.includes(args.name));
  if (!hit) return { error: `未找到模块：${args.name}` };
  return { text: readText(path.join(dir, hit)) };
}

const TOOLS = [
  { name: "kb_status", description: "统计知识库各目录的数据版本分布（等价 count_version.py，修正跳过目录）", inputSchema: { type: "object", properties: { prefix: { type: "string" } } }, fn: toolKbStatus },
  { name: "kb_search", description: "按关键字/正则全文搜索 Markdown", inputSchema: { type: "object", properties: { query: { type: "string" }, path: { type: "string" }, regex: { type: "boolean" }, limit: { type: "integer" }, context: { type: "integer" } }, required: ["query"] }, fn: toolKbSearch },
  { name: "kb_read", description: "读取文件（带行号）", inputSchema: { type: "object", properties: { path: { type: "string" }, offset: { type: "integer" }, limit: { type: "integer" } }, required: ["path"] }, fn: toolKbRead },
  { name: "kb_list", description: "按 glob 列举知识库文件", inputSchema: { type: "object", properties: { pattern: { type: "string" }, max: { type: "integer" } } }, fn: toolKbList },
  { name: "kb_validate_fields", description: "字段级校验（元信息/必备字段/章节/重复ID，修正 classify 前缀缺陷）", inputSchema: { type: "object", properties: { path: { type: "string" } } }, fn: toolKbValidateFields },
  { name: "kb_validate_links", description: "Obsidian 双链校验（0 死链目标）", inputSchema: { type: "object", properties: { path: { type: "string" }, limit: { type: "integer" } } }, fn: toolKbValidateLinks },
  { name: "kb_missing_fields", description: "统计物品库缺「获得途径」「说明」的文件数", inputSchema: { type: "object", properties: { path: { type: "string" } } }, fn: toolKbMissingFields },
  { name: "kb_spec_section", description: "按标题关键字取《格式规范与要求.md》的某一节", inputSchema: { type: "object", properties: { heading: { type: "string" } }, required: ["heading"] }, fn: toolKbSpecSection },
  { name: "kb_prompt_modules", description: "列出或读取 docs/prompts 下的提示词模块", inputSchema: { type: "object", properties: { name: { type: "string" } } }, fn: toolKbPromptModules },
];

const RESOURCES = [
  ["hsr://spec/format", "格式规范与要求.md", "格式规范总纲"],
  ["hsr://doc/data-sources", "数据来源.md", "数据来源总览"],
  ["hsr://prompts/readme", "docs/prompts/README.md", "提示词管理总纲"],
  ["hsr://prompts/core", "docs/prompts/10_核心_版本无关.md", "核心提示词（常驻）"],
  ["hsr://prompts/params-4.6", "docs/prompts/20_参数_4.6.md", "4.6 版本参数"],
  ["hsr://prompts/quest", "docs/prompts/30_模块_剧情获取.md", "剧情获取模块"],
  ["hsr://prompts/mcp", "docs/prompts/60_模块_MCP.md", "MCP 模块说明"],
  ["hsr://ops/reconcile-4.6", "docs/对账_4.6.md", "4.6 对账审核基线"],
  ["hsr://ops/pending", "docs/待补充清单.md", "待补充清单"],
];

const PROMPTS = [
  ["core", "常驻核心提示词", "docs/prompts/10_核心_版本无关.md"],
  ["params_46", "4.6 版本参数与交付流程", "docs/prompts/20_参数_4.6.md"],
  ["quest", "剧情文本获取与回填模块", "docs/prompts/30_模块_剧情获取.md"],
];

// ---------------------------------------------------------------- JSON-RPC

const send = (o) => process.stdout.write(JSON.stringify(o) + "\n");
const ok = (id, result) => send({ jsonrpc: "2.0", id, result });
const fail = (id, code, message) => send({ jsonrpc: "2.0", id, error: { code, message } });

function handle(msg) {
  const { method, id } = msg;
  const params = msg.params || {};
  if (method === "initialize") {
    return ok(id, {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: { tools: {}, resources: {}, prompts: {} },
      serverInfo: { name: SERVER_NAME, version: SERVER_VERSION },
    });
  }
  if (method === "notifications/initialized" || method === "initialized" || method === "ping") {
    return method === "ping" ? ok(id, {}) : undefined;
  }
  if (method === "tools/list") {
    return ok(id, { tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) });
  }
  if (method === "tools/call") {
    const t = TOOLS.find((x) => x.name === params.name);
    if (!t) return fail(id, -32602, `未知工具：${params.name}`);
    try {
      const res = t.fn(params.arguments || {});
      if (res.error) return ok(id, { content: [{ type: "text", text: res.error }], isError: true });
      return ok(id, { content: [{ type: "text", text: res.text || "" }] });
    } catch (e) {
      return ok(id, { content: [{ type: "text", text: `工具执行失败：${e.message}` }], isError: true });
    }
  }
  if (method === "resources/list") {
    return ok(id, {
      resources: RESOURCES.filter(([, f]) => fs.existsSync(path.join(ROOT, f)))
        .map(([uri, , d]) => ({ uri, name: uri, description: d, mimeType: "text/markdown" })),
    });
  }
  if (method === "resources/read") {
    const hit = RESOURCES.find(([u]) => u === params.uri);
    if (!hit) return fail(id, -32602, `未知资源：${params.uri}`);
    const p = path.join(ROOT, hit[1]);
    if (!fs.existsSync(p)) return fail(id, -32602, `资源不存在：${hit[1]}`);
    return ok(id, { contents: [{ uri: hit[0], mimeType: "text/markdown", text: readText(p) }] });
  }
  if (method === "prompts/list") {
    return ok(id, { prompts: PROMPTS.map(([name, description]) => ({ name, description, arguments: [] })) });
  }
  if (method === "prompts/get") {
    const hit = PROMPTS.find(([n]) => n === params.name);
    if (!hit) return fail(id, -32602, `未知提示词：${params.name}`);
    return ok(id, {
      description: hit[1],
      messages: [{ role: "user", content: { type: "text", text: readText(path.join(ROOT, hit[2])) } }],
    });
  }
  if (id !== undefined && id !== null) fail(id, -32601, `未实现的方法：${method}`);
}

if (!fs.existsSync(ROOT)) {
  process.stderr.write(`HSR_ROOT 不存在：${ROOT}\n`);
  process.exit(1);
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on("line", (line) => {
  const s = line.trim();
  if (!s) return;
  let msg;
  try {
    msg = JSON.parse(s);
  } catch {
    return;
  }
  try {
    handle(msg);
  } catch (e) {
    if (msg && msg.id !== undefined) fail(msg.id, -32603, `内部错误：${e.message}`);
  }
});
