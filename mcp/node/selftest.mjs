#!/usr/bin/env node
/**
 * MCP 服务自测（Node 版 · 零依赖）
 * 用法：node mcp/node/selftest.mjs [工具名]
 */
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SERVER = path.join(here, "hsr-mcp-server.mjs");

const CALLS = [
  ["kb_status", { prefix: "zh_cn" }],
  ["kb_list", { pattern: "docs/prompts/*.md" }],
  ["kb_read", { path: "README.md", limit: 5 }],
  ["kb_search", { query: "数据版本：4.6", path: "zh_cn/character", limit: 3 }],
  ["kb_missing_fields", { path: "zh_cn/items" }],
  ["kb_validate_links", { path: "zh_cn/relic", limit: 5 }],
  ["kb_validate_fields", { path: "zh_cn/character" }],
  ["kb_spec_section", { heading: "文件命名规范" }],
  ["kb_prompt_modules", {}],
];

const only = process.argv[2];
const child = spawn(process.execPath, [SERVER], { stdio: ["pipe", "pipe", "inherit"] });

let buf = "";
const pending = [];
child.stdout.on("data", (d) => {
  buf += d.toString("utf8");
  let i;
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    try {
      const obj = JSON.parse(line);
      const cb = pending.shift();
      if (cb) cb(obj);
    } catch {}
  }
});

let nextId = 1;
function rpc(method, params) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.push(resolve);
    child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
    setTimeout(() => reject(new Error(`超时：${method}`)), 15000);
  });
}

const head = (t) => (t || "").split("\n")[0].slice(0, 80) || "(空)";

try {
  const init = await rpc("initialize", { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "selftest", version: "1.0" } });
  console.log(`[1] initialize ✅ ${init.result.serverInfo.name} v${init.result.serverInfo.version} 能力=${Object.keys(init.result.capabilities).join(",")}`);

  const tools = (await rpc("tools/list", {})).result.tools;
  console.log(`[2] tools/list ✅ 共 ${tools.length} 个工具：${tools.map((t) => t.name).join(", ")}`);

  let i = 3;
  for (const [name, args] of CALLS) {
    if (only && name !== only) continue;
    const res = await rpc("tools/call", { name, arguments: args });
    const text = res.result?.content?.[0]?.text || "";
    console.log(`[${i}] ${name} ${res.result?.isError ? "⚠️ isError" : "✅"} ${head(text)}`);
    i++;
  }

  const rs = (await rpc("resources/list", {})).result.resources;
  console.log(`[90] resources/list ✅ ${rs.length} 个资源`);
  if (rs.length) {
    const got = await rpc("resources/read", { uri: rs[0].uri });
    console.log(`[91] resources/read ✅ ${rs[0].uri} → ${got.result.contents[0].text.length} 字符`);
  }

  const ps = (await rpc("prompts/list", {})).result.prompts;
  console.log(`[92] prompts/list ✅ ${ps.length} 个提示词：${ps.map((p) => p.name).join(", ")}`);
  if (ps.length) {
    const got = await rpc("prompts/get", { name: ps[0].name });
    console.log(`[93] prompts/get ✅ ${ps[0].name} → ${got.result.messages[0].content.text.length} 字符`);
  }
  console.log("\n自测完成。");
} catch (e) {
  console.error("自测失败：", e.message);
  process.exitCode = 1;
} finally {
  child.kill();
}
