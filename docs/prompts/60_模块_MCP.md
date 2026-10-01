> ⚠️ **2026-10-01 迁移公告**：MCP 工具层已抽出为独立项目 [markdown-kb-mcp](https://github.com/ganmayou2333/markdown-kb-mcp)（profile 驱动、零依赖、10 个工具、MIT）。本库内 `mcp/` 目录已移除；下文出现的 `mcp/` 路径均为历史记录。

# 60 · 模块：MCP 工具层（只读）

> **装载条件**：**不需要**作为提示词文本装载。
> MCP 工具的 schema 由客户端在 `tools/list` 时自动注入上下文，占用的是**工具通道**而非提示词预算。
> 但当任务涉及「校验 / 统计 / 检索」时，本模块说明**用哪个工具、替代哪一步手工操作**。

---

## M.1 工具 ↔ 原手工步骤对照

| 原手工步骤 | 改用工具 | 说明 |
|---|---|---|
| 现写 `count_version.py` 统计版本分布 | `kb_status` | 已内置正确的跳过目录规则 |
| `cd zh_cn && python ../scripts/verify_fields.py` | `kb_validate_fields` | 免去「必须在 `zh_cn/` 下运行」的坑 |
| `python scripts/verify_links.py` | `kb_validate_links` | 已排除两个 StarRailRes 克隆 |
| grep 找内容 | `kb_search` | 支持正则与上下文行 |
| glob 数文件 | `kb_list` | 支持 `**` 通配 |
| 打开格式规范找章节 | `kb_spec_section` | 按标题关键字取整节 |
| 读提示词模块 | `kb_prompt_modules` | 可列清单或按名读取 |
| 手数缺「获得途径/说明」 | `kb_missing_fields` | 返回计数与样例 |

## M.2 使用纪律（红线）

1. **工具是只读的**：任何写入/新建/删除**都不存在对应工具**，必须回到「工单 → 执行 → Lead 审核」流程。
2. **工具报错 ≠ 可绕过**：`isError: true` 时如实上报，不得改用别的方式「绕过去拿数据」。
3. **数字以工具输出为准**：工单要求「贴原始输出」时，直接贴工具返回文本（含参数），不得手抄/改写。
4. **不得把工具当搜索万能钥匙**：跨库检索仍要遵守 `10_核心` 的引用纪律与来源要求。
5. **只读范围 ≠ 可外发**：工具只暴露 `HSR_ROOT` 内的内容，不得用其读取仓库外路径（路径沙箱会拒绝）。

## M.3 与阶段 E（自检）的衔接

20_参数 阶段 E 原写「能跑脚本就跑脚本」——现更新为优先顺序：

1. `kb_validate_fields` + `kb_validate_links`（工具，结果直接贴）
2. 工具不可用时，退回 `scripts/*.py`——**两者运行目录相反**：
   - `verify_fields.py` → 在 `zh_cn/` 下运行
   - `verify_links.py` → 在**仓库根**运行（在 `zh_cn/` 下会误报近万死链，2026-10-01 实例：9838 条）
3. 两者都不可用 → 人工核对并说明方式

## M.4 扩展预留（**需用户放行**）

- `kb_wiki_bwiki`：封装 BWiki MediaWiki API（本阶段手工验证可行：`action=parse&prop=wikitext`）
- `kb_patch`：受控写入（默认 dry-run + 工单号 + 范围校验）——**高风险，必须单独放行**

> 维护责任：MCP 层由 **Lead** 维护；工具的行为变更需同步更新本模块与 `mcp/README.md`。
