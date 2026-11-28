# Issue #43：PR 预览产物下载重试策略（本地实现记录）

> **状态：本地实现与本地测试完成，未提交、未推送、未在 GitHub Actions 运行验证。**
> 本文所有「GitHub 上的观测」均来自只读 API 查询，未触发任何工作流，也不代表新方案已经在 GitHub 生效。
> 关联：[Issue #43](https://github.com/ganmayou2333/hsr-knowledge-base/issues/43)、[PR #37](https://github.com/ganmayou2333/hsr-knowledge-base/pull/37)、Issue #40、#41。

## 一、问题回顾

`.github/workflows/wiki-quality.yml` 在 PR 构建中上传 `wiki-preview-*.zip` 后立即下载做往返校验。Issue #43 记录的运行里，首次下载会间歇失败，等待 5 秒后重试成功：

- 44773668618、44783124684：首次提示按名称找不到产物；
- 44783579861：日志列出产物 ID `14651138977`，但按该 ID 获取时提示找不到；等待 5 秒后同一次运行内成功，摘要与上传一致，随后 `cmp` 与包验证通过。

原工作流前两次下载使用 `continue-on-error`，5 秒、10 秒后重试；第三次失败或内容不一致时任务失败。问题有三点：

1. 首次失败仍会在成功运行里留下错误 annotation，容易被误读为「运行失败」或「重试无意义」；
2. Jobs API 的首次下载步骤 `conclusion` 为 `success`，无法仅凭 step conclusion 判断首次是否真的成功；
3. 重试对所有错误一视同仁，权限不足、真正缺失、摘要不符也会被无差别等待重试；失败时缺少分类信息。

## 二、本会话的只读复核（2026-11-28）

只读查询 `gh issue view 43`：issue 状态 `OPEN`，当前无评论（截至查询时）。只读查询 Actions run/job/annotation API，复核 Issue 中列出的样本：

| 运行 | 元数据 | 重试相关步骤 | annotation（运行结束后可读） |
|---|---|---|---|
| 44783579861 | `pull_request`，`codex/wiki-rebuild`，conclusion `success` | 首次下载 step conclusion `success`（`continue-on-error` 掩盖失败），等待 5 秒与「Retry preview download」均执行且成功，最终下载 skipped，重试成功后的往返校验成功 | `Unable to download artifact(s): No artifacts found for ID: 14651138977 ... Try specifying a github-token with actions:read scope.` |
| 44783124684 | 同上分支，conclusion `success` | 首次下载 step conclusion `success`，等待与重试执行且成功，最终下载 skipped，往返校验成功 | `Unable to download artifact(s): Artifact not found for name: wiki-preview-37-1f971ba5a6392052d5e73eb6bfd9598206809624-1 ...` |
| 44773668618 | 同上分支，conclusion `success` | 首次下载 step conclusion `success`，等待与重试执行且成功，最终下载 skipped，往返校验成功 | `Unable to download artifact(s): Artifact not found for name: wiki-preview-37-9c428315dca5fbe2b6c4ecf91f71f9b6e754d5b8-1 ...` |

补充观测：读取最近 12 次已完成的 PR Wiki quality 运行（44803836939 至 46099524874，2026-11-20 至 2026-11-28）。其中 3 次执行了「Retry preview download」且成功，均为 2026-11-20 的 44809812498、44810162428、44810577760；其余 9 次未执行重试。另有一次 46052006340 运行失败，失败步骤是「Check real Wiki in preview viewer」，与产物下载无关。这是有限时间窗口的样本，**不能作为长期故障率**，也不能证明失败根因。

结论边界：

- 「首次下载失败→数秒后成功」与产物可见性延迟一致，但**没有证据证明是服务端传播延迟**，也不能排除其他暂时性错误；
- annotation 文本是在运行结束后通过 Checks API 读到的；下载动作的错误消息不会作为 step output 暴露给后续步骤；
- 因此新方案不依赖读取动作的错误文本，而是用工作流自身可观测的状态重建失败分类。

补充只读代码核对：下载 `actions/download-artifact` v8.0.2 的 `dist/index.js`（仅阅读，未执行），确认：

- 单产物下载在 `streamExtract` 完成解包后才比较摘要，`digest-mismatch: error` 在解包完成后才抛出，因此摘要不符时解包目录中通常已有 `wiki-preview.zip`；
- 名称找不到的错误文本为 `Artifact not found for name: ...`，按 ID 找不到为 `No artifacts found for ID: ...`；
- 下载客户端对 blob 下载错误有 5 次、间隔 5 秒的内部重试。

以上是代码阅读结论，未在 Actions 运行中验证。

## 三、新方案

### 3.1 总体

- 仍旧使用 `actions/download-artifact@v8`，保留 `digest-mismatch: error`；
- 最多 **3 次尝试**，失败后退避 **5 秒、10 秒**（即最多 2 次重试）；
- 每次失败先由只读诊断步骤生成「规范化失败文本」，再交给纯逻辑策略模块决定「是否重试、等多久、为什么」；
- 不可重试错误直接失败；最终失败仍由最后一个下载步骤（无 `continue-on-error`）让任务失败；
- 首次结果通过独立的 summarize 步骤记录 `outcome`（不是 `conclusion`），避免 `continue-on-error` 造成误读；
- 往返校验步骤（`cmp` + `extract_preview_zip` + 必需文件/页面/图标检查）**内容不变**，仍是成功判据。

### 3.2 失败分类与动作

| 分类 | 触发/识别方式 | 是否重试 | 说明 |
|---|---|---|---|
| `name-not-found` | 只读诊断探测到本次 run 的 artifact 列表按名称返回 0 项，或文本为 `Artifact not found for name: ...` / `Unable to find any artifacts for the associated workflow` | 是，最多 3 次 | 已知的可见性延迟形态；超过次数即失败，不冒充成功 |
| `id-not-found` | 文本为 `No artifacts found` / `No artifacts found for ID: ...` 等 | 是，最多 3 次 | Issue 样本形态之一；策略层支持，当前工作流按名称下载 |
| `permission-or-404` | 只读探测返回 401/403/404（或 `Resource not accessible` 等） | 否 | 权限不足或运行/产物确定不可见，重试无意义 |
| `digest-mismatch` | 下载目录里的 `wiki-preview.zip` 与上传时记录的 SHA-256 不一致 | 否 | `digest-mismatch: error` 已让该次下载失败；本地字节不同说明完整性异常 |
| `unknown` | 其他未识别文本 | 是，最多 3 次 | 保守处理：有限次重试后最终失败，不会误判成功 |
| `success` | 无失败文本 | 否 | 无需重试 |

### 3.3 纯逻辑模块

新增 `tools/artifact_retry_policy.py`：

- `decide(attempt, failure_text, waited_seconds)`：
  - 输入：1-based 尝试序号、上次失败文本（`None`/空表示成功）、已等待秒数；
  - 输出：`RetryDecision(category, retry, wait_seconds, reason, attempts_remaining)`；
  - 规则：3 次上限；可重试分类在 attempt 1/2 分别等待 5/10 秒；`waited_seconds` 用于避免重复等待；
  - 不访问网络、不读取仓库内容（CLI 只在调用方显式给出 `--failure-file` 时读取该文件）。
- CLI 供工作流调用：成功/允许重试退出码 0；不可重试或次数用尽退出码 1（步骤失败 → 快速失败）；`--diagnose-only` 仅用于「下载步骤本身已让任务失败」的最终诊断，不能改变任务结论。

### 3.4 工作流改动（`.github/workflows/wiki-quality.yml`）

新增/调整的步骤顺序：

1. `Record uploaded preview digest`：上传后记录 `wiki-preview.zip` 的 SHA-256；
2. `Write preview download diagnostics helper`：生成只读诊断脚本（用 `gh api` 列出本次 run 的 artifact、比较下载文件摘要）；
3. `Download preview input for round-trip verification (attempt 1)`：`continue-on-error: true`；
4. `Classify preview download attempt 1`（仅失败时）+ `Decide retry after preview download attempt 1`：策略判定；不可重试则步骤失败；
5. `Wait before preview download attempt 2`：`sleep` 策略给出的秒数；
6. attempt 2 重复 4–5；
7. `Final preview download (attempt 3, failure fails the job)`：**无 `continue-on-error`**；
8. `Diagnose final preview download failure`（`failure()` 且有失败时）：只写日志/summary，`--diagnose-only`，不改变任务结论；
9. `Verify downloaded preview input`：原有 run 块逐字不变（由本地自检比对确认）；
10. `Summarize preview download`（`always()`）：列出三次下载 `outcome`、上传摘要、每次尝试的分类与等待、最终结论；重试成功时输出 `::warning::`，首次成功输出 `::notice::`，未通过输出 `::error::`。

权限从 `contents: read` 增加只读的 `actions: read`，用于诊断探测。

### 3.5 为什么不用动作的错误文本

`continue-on-error` 只暴露 step `outcome`，动作的错误消息不会进入后续步骤的上下文；annotation 是运行结束后通过 Checks API 复核的（见第二节）。因此诊断步骤自行构造规范化文本：

- 下载目录里已有 `wiki-preview.zip`：与上传摘要比较；不一致 → `digest-mismatch`，一致但动作仍失败 → `unknown`（不冒充成功）；
- 下载目录无文件：调用 `gh api repos/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID/artifacts?name=<name>`：
  - 0 项 → `name-not-found`（可重试）；
  - ≥1 项 → `unknown`（动作已失败，按暂时性传输错误有限重试）；
  - 401/403/404 → `permission-or-404`（直接失败）；
  - 其他探测错误 → `unknown`（有限重试，绝不据此声称成功）。

注意：artifact API 返回的 `digest` 是**归档容器**（artifact 压缩包）的摘要，不是容器内 `wiki-preview.zip` 的摘要。因此不能把 API digest 与上传文件 SHA-256 直接比较；工作流只比较解包后的 `wiki-preview.zip` 与上传摘要，避免把正常下载误判成摘要不符。该结论来自对 `actions/download-artifact@v8` 与 `@actions/artifact` 源码顺序的阅读，未在运行中实测。

## 四、负例处理

| 负例 | 新方案行为 | 验收边界 |
|---|---|---|
| 权限不足（401/403） | 诊断步骤识别为 `permission-or-404`，策略退出码 1，后续尝试跳过，任务失败 | 由探测文本决定；尚未在真实 CI 注入该错误 |
| 运行/产物确定 404 | 同上，直接失败，不做 5/10 秒重试 | 尚未在真实 CI 注入 |
| 摘要不符 | `digest-mismatch: error` 使下载动作失败；诊断比较下载文件与上传摘要后直接失败 | 依赖动作在摘要比较前已解包（v8.0.2 dist 代码阅读如此，运行期未实测） |
| 产物确实不存在（名称始终不可见） | 3 次尝试后仍 `name-not-found` → 最终下载步骤失败；不误判成功 | 无法与「长时间可见性延迟」区分，只能靠次数上限 |
| 服务不可用/5xx/网络中断 | 下载客户端内部已有 5 次、间隔 5 秒的 blob 下载重试；若仍失败，诊断为 `unknown` → 策略再有限重试 3 次 | 未做故障注入 |
| 三次均失败 | 第三次下载步骤无 `continue-on-error`，动作失败直接使任务失败；诊断步骤只补充信息 | 语义与旧方案一致且更明确 |
| 首次成功 | attempt 2/3 跳过，校验执行，summary 输出「首次成功」notice | 本地测试覆盖解析与校验，未在 GitHub 运行 |
| 重试后成功 | attempt 1 记为 failure（summary 与日志），重试成功，校验执行，输出 warning 明确说明「曾经真实失败」 | 未在 GitHub 运行 |

## 五、本地验证（不等于 GitHub 验证）

2026-11-28 在 Windows、Python 3.14.9、Git Bash 执行：

- `python -X utf8 -m unittest tools.test_preview_roundtrip_workflow tools.test_artifact_retry_policy -v` → `Ran 17 tests ... OK`；
  - 其中 `tools.test_preview_roundtrip_workflow` 直接解析工作流「Verify downloaded preview input」的 run 块，完整包通过；缺失、追加篡改、等长篡改、无效 ZIP、包内容缺失均按预期失败。
- `python -X utf8 .tmp_issues/agent5_selfcheck.py` → 全部 PASS，覆盖：
  - PyYAML 解析工作流、19 个 `run:` 块 `bash -n` 通过；
  - 「Verify downloaded preview input」run 块与改动前逐字节一致；
  - 三次下载均为 `actions/download-artifact@v8` 且 `digest-mismatch: error`，attempt 1/2 为 `continue-on-error`，attempt 3 不是；
  - 用 stub `gh` 模拟：名称不可见 → `name-not-found` 重试；产物已列出但下载失败 → `unknown` 重试；403/404 → 直接失败；下载文件摘要不一致 → `digest-mismatch` 直接失败；probe 未知错误 → 有限重试。
- 新增测试加入工作流 unittest 清单行：`tools.test_artifact_retry_policy`。

自检脚本位于 `.tmp_issues/agent5_selfcheck.py`（未提交，仅本地证据）。这些验证只覆盖脚本逻辑与 YAML 结构，**不覆盖** GitHub Actions 的 token 权限、`gh` 可用性、运行中 artifact API 行为、真实失败注入与 UI annotation。

## 六、仍需真实 CI 验证的事项

以下均**未验证**，不得表述为已在 GitHub 生效：

1. 推送后触发真实 `pull_request` 运行，确认 YAML 被 GitHub 接受（本地 PyYAML 通过不代表 Actions 表达式/上下文检查通过）。
2. `actions: read` 在 `pull_request`（尤其来自 fork 的 PR）中是否可用，以及在 `workflow_call`（由 `pages.yml` 调用、`push` 事件）下的权限裁剪是否影响（该路径不会进入下载步骤，但需确认不报错）。GitHub 文档说明可用 `permissions` 为 fork 仓库添加 `read` 权限、写权限会被降为只读（[Changing the permissions in a forked repository](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)），因此预期可用；但这是文档推断，仍需真实 fork PR 运行确认。
3. `ubuntu-latest` 的 `gh` 版本与 `repos/{owner}/{repo}/actions/runs/{run_id}/artifacts?name=` 在运行中（run 未完成）的返回行为，以及 401/403/404 的实际错误文本是否被现有匹配命中。
4. 摘要不符时 `actions/download-artifact@v8` 是否如 v8.0.2 dist 代码那样在比较摘要前完成解包（决定诊断能否看到本地文件）；若不能，摘要错误将退化为有限重试后失败。运行期未实测。
5. 注入权限错误、确定 404、真正缺失、5xx/网络错误、摘要不符，确认分类与「直接失败/有限重试」符合预期；本地 stub 测试不能替代。
6. 观察重试成功时的 UI：首次失败 annotation 仍在（动作层面无法消除），但 summary 与 `::warning::` 需清晰可读；确认没有新的误导性 annotation。
7. 多运行、跨时间窗口的失败率与分类分布；不得用本次 12 次样本外推长期概率。
8. `docs/preview-artifact-diagnostics.md` 仍描述旧的两段式 `continue-on-error` 方案，本文不改动它（不在本任务写入范围）；若本方案合入，需要单独更新该文档。
9. Issue #43 尚未写入工单/进度评论（本会话禁止 GitHub 写操作），需要由 Lead 或后续有写权限的会话补记；验收项不能因本地测试通过而勾选。

## 七、改动文件

- `.github/workflows/wiki-quality.yml`：重试/诊断/汇总步骤与 `actions: read` 权限、unittest 清单行。
- `tools/artifact_retry_policy.py`：纯逻辑策略与 CLI（新增）。
- `tools/test_artifact_retry_policy.py`：策略与 CLI 测试（新增）。
- `docs/issue-43-预览产物下载重试.md`：本文。
- `tools/test_preview_roundtrip_workflow.py`：未修改（其解析的步骤名与 run 块保持不变，自检确认逐字节一致）。
