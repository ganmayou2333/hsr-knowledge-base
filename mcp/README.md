# HSR 知识库 · MCP 框架

> **定位**：把豆包/其他 LLM 客户端对知识库的操作，从「手写脚本 + 手工 grep」升级为**受控工具调用**。
> **边界**：**只读 + 校验 + 统计**。不提供任何写文件工具——写入一律走「工单 → 豆包执行 → Lead 审核」。
> **版本**：1.0.0（2026-09-30）

---

## 一、为什么需要它

上一阶段暴露的真实问题，几乎都是「脚本/口径/路径」类的人为失误：

| 已发生的问题 | MCP 对应解法 |
|---|---|
| `fix_obtain_list.py` 缺 `re.MULTILINE` → dry-run 命中 0 | 工具内置正确实现，无脚本可写错 |
| `verify_fields.py` 的 `classify()` 用旧前缀 → 全库误判为 `other`（空跑） | `kb_validate_fields` 会**先剥语言根目录**再分类 |
| `skip_dirs` 未排除 `StarRailRes-master` → 计数被污染 | 统一跳过两个克隆目录与 `temp/` |
| 每次统计都要现写 `count_version.py` | `kb_status` 一条调用返回版本分布 |
| 规范章节要靠人找 | `kb_spec_section(heading=…)` 直接返回某一节 |

---

## 二、目录结构

```
mcp/
├── README.md                         ← 本文件
├── python/
│   ├── hsr_mcp_server.py             ← 主服务（零依赖 · stdio JSON-RPC）
│   └── selftest.py                   ← 自测（拉起服务并逐工具调用）
├── node/
│   ├── hsr-mcp-server.mjs            ← Node 版（同样零依赖）
│   └── selftest.mjs
└── config/
    └── mcp_client_config.example.json ← 客户端接入示例
```

**零依赖**：Python 只用标准库；Node 只用 `node:fs / node:path / node:readline`。无需安装 `mcp` / `@modelcontextprotocol/sdk`（想换官方 SDK 时，只需替换 transport，handler 不变）。

---

## 三、工具清单（9 个 · 全部只读）

| 工具 | 作用 | 关键参数 |
|---|---|---|
| `kb_status` | 各目录数据版本分布（等价 `count_version.py`） | `prefix`（默认 `zh_cn`） |
| `kb_search` | 关键字/正则全文搜索 | `query`, `path`, `regex`, `limit`, `context` |
| `kb_read` | 读文件（带行号） | `path`, `offset`, `limit` |
| `kb_list` | glob 列举文件 | `pattern`, `max` |
| `kb_validate_fields` | 字段校验（元信息/必备字段/章节/重复ID） | `path` |
| `kb_validate_links` | Obsidian 双链校验 | `path`, `limit` |
| `kb_missing_fields` | 统计物品库缺「获得途径/说明」 | `path` |
| `kb_spec_section` | 取《格式规范与要求.md》某一节 | `heading` |
| `kb_prompt_modules` | 列出/读取 `docs/prompts/` 模块 | `name`（省略则列清单） |

**资源（resources）**：格式规范、数据来源、提示词管理总纲、核心/参数/剧情/MCP 模块、4.6 对账基线、待补充清单。
**提示词（prompts）**：`core` / `params_46` / `quest` —— 客户端可直接拉取提示词模块。

---

## 四、接入方式

把 `mcp/config/mcp_client_config.example.json` 里的路径换成你本机的，然后按客户端要求放进其 MCP 配置：

```json
{
  "mcpServers": {
    "hsr-kb": {
      "command": "python",
      "args": ["G:\\HSR\\mcp\\python\\hsr_mcp_server.py"],
      "env": { "HSR_ROOT": "G:\\HSR" }
    }
  }
}
```

Node 版把 `command/args` 换成 `node` + `…\\mcp\\node\\hsr-mcp-server.mjs` 即可（两者工具语义一致，可任选或并存）。

---

## 五、自测（**务必先跑**）

```powershell
# Python 版
python G:\HSR\mcp\python\selftest.py
# 或只测单个工具
python G:\HSR\mcp\python\selftest.py kb_status

# Node 版
node G:\HSR\mcp\node\selftest.mjs
```

自测会依次验证：`initialize` → `tools/list` → 9 个工具各调一次 → `resources/list` + `resources/read` → `prompts/list` + `prompts/get`，并打印每步结果。

> ⚠️ **交付状态说明（诚实声明）**：本框架由 Lead 编写，但**未在本机执行过任何一行**——当前会话的 shell 被沙箱阻断（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\HSR)`），无法运行 Python/Node，也无法做语法检查。因此代码处于「**已交付、待自测**」状态：请先按本节跑自测，把输出发回，我再据实修正。

---

## 六、安全设计

1. **路径沙箱**：所有路径 `resolve` 后必须落在 `HSR_ROOT` 内，越界直接报错。
2. **只读**：没有写入/删除/移动类工具；`fs.readFileSync` / `Path.read_text` 之外无副作用。
3. **输出限额**：单文件读取 ≤ 400 KB；列表 ≤ 500；搜索 ≤ 200 条——防止把上下文一口气吃光。
4. **跳过重目录**：`.git` `.obsidian` `node_modules` `.tmp_build` `temp` 以及 `StarRailRes-master/_repo/_data`。
5. **错误即上报**：工具异常按 MCP 约定返回 `isError: true`，不静默吞掉。

---

## 七、与存量脚本的关系

`scripts/verify_fields.py`、`scripts/verify_links.py`、`scripts/compare_srr_ids.py` **保留不动**（历史可追溯）；MCP 工具是**修正版的并行实现**。

若后续决定统一，建议：先用 MCP 工具跑出基线，再决定是否让脚本调用同一套逻辑（避免两处实现漂移）。

---

## 八、后续扩展（**需另行放行**）

| 扩展 | 说明 | 风险 |
|---|---|---|
| `kb_wiki_bwiki` | 封装 `wiki.biligame.com/sr/api.php` 取 wikitext（本阶段已手工验证可行） | 中（外部网络） |
| `kb_mihoyo_probe` | 探测米游社 WIKI API（现已知 `channel_id=48` 无效） | 中 |
| `kb_patch` | 受控写入：默认 dry-run，需带工单号与范围校验 | **高**（会改 `zh_cn/`） |
| `kb_workorder` | 读写工单状态，把 W-4.6-xx 的生命周期工具化 | 低 |

按现有分工：**只读工具由 Lead 维护；任何写入类工具必须经用户放行，并在提示词管理中登记红线。**
