# Wiki PR 预览 / 可信检查 / 合并治理：四 issue 现状复核证据（2026-11-28）

> 用途：复核 issue #36、#40、#41、#42 的真实现状，逐条对照验收项，产出可复核的状态证据。
> 性质：**只读取证**。本次未部署、未创建或轮换凭据、未创建/修改 PR、未触发 GitHub Actions、未执行任何 git 写命令、未写入 GitHub（`gh` 仅用只读 API）。本文件是唯一写入产物。
> 复核对象：工作区 `G:\HSR`（仓库 `ganmayou2333/hsr-knowledge-base`，分支 `main`）。本地 `HEAD` = 远端 `main` = `d7e0daf79414e4c080851fdfe3c8c9c230514eb1`（E17）。
> 取证时间：2026-11-28 11:14–11:26（UTC+8；GitHub API 与页面均为该时段快照，之后可能变化）。
> 工作区说明：复核期间工作区存在其他协作者产生的未提交改动（如 `.github/workflows/wiki-quality.yml` 修改、`tools/artifact_retry_policy.py` 等未跟踪文件）。本报告引用的 `tools/*.py`、`.github/workflows/wiki-trusted-data.yml`、`docs/preview-operations.md` 与 `HEAD` 一致（`git status --porcelain tools/` 仅显示未跟踪文件）；单元测试命令取自 `HEAD` 的 CI 命令。

**三条不能混用的边界（本报告反复强调）：**

1. **代码合并 ≠ 已部署**：实现进入 `main` 不等于独立预览仓库已切换发布来源或真实预览已可访问。
2. **本地单测通过 ≠ 真实 fork 联调**：模拟元数据、模拟事件、内存改状态都不等于 GitHub 真实事件。
3. **自动检查通过 ≠ 人工独立审查**：同一人或自动检查不能替代非作者、具备权限的独立审查；需要人工独立审查的项不能由执行者本人替代。

---

## 一、结论摘要

| Issue | GitHub 状态 | 已落地的代码/测试 | 真实 GitHub / 线上证据 | 验收判断 |
|---|---|---|---|---|
| #36 隔离的公开预览与审查状态 | open（E19） | PR #54 已合并部分预览、审查状态与安全校验实现；相关单测通过 | 公开预览页仍是占位页（HTTP 200，标题「尚未开放」，E10）；没有真实 PR 预览 | **未完成**：无部署、无真实多 PR/审批状态浏览器验证 |
| #40 部署独立 Pages 并自动更新与清理 | open（E19） | 预览外壳、目录组装、原子切换、清理、发布前复核等本地组件；工作流模板 | 预览仓库 `main` 只有 `README.md` + 占位 `index.html`；Pages 仍是 `legacy` 分支发布，最后构建 `d31d6d2`（2026-11-20）；无预览工作流、0 个 Actions secret（E8/E9/E15） | **未完成**：只有占位页，PR 内容预览/自动发布/清理均未部署 |
| #41 可信检查与真实 PR 联调 | open（E19） | 可信检查工作流已在 `main`；v2 收据、可信构建、收据↔工件关联、取件原型均有单测 | **新证据**：2026-11-28 真实内部 PR #55 的可信运行 `46099524983` 产出了真实 v2 收据与 `trusted-wiki-preview` 工件（E12/E13）；外部 fork 只有 v1 收据（PR #48，E14）；未见消费/发布接入（生产代码无导入） | **部分完成**：生产者侧 v2 真实运行已出现；外部 fork v2、发布前复核接入、端到端发布仍未完成 |
| #42 合并检查与独立审查 | open（E19） | 分支保护与必需检查已配置（API 可复核） | `main` 保护：必需 `Build and check`（app 15368）、**必需批准数 0**、管理员受约束、禁强推/删除、rulesets 为空、协作者 2 人（E2/E3/E4）。PR #37 有 `Hikarifly` 批准；PR #54、#55 **零 review**、`reviewDecision` 为空即被合并（E5/E16） | **未完成**：当前批次没有独立人工审查；保护仅配置读取，未做违规合并验证 |

补充：GitHub 上 `gh run list --workflow 'Trusted Wiki data checks'` 已能查到 **14 次真实 `pull_request_target` 运行**（E11），因此「尚无真实 pull_request_target 运行」属于历史状态，已被现状推翻。但这 14 次运行的 `pull_requests` 关联字段**全部为空**，外部投稿的绑定缺口仍未解决。

---

## 二、复核口径与测试结果

### 2.1 代码基准

- 本地 `HEAD` 与远端 `main` 均为 `d7e0daf79414e4c080851fdfe3c8c9c230514eb1`（E17），即 PR #55 合并后的提交。
- `gh` 版本 2.104.0，登录账号 `ganmayou2333`（只读 API 查询）。本次所有 GitHub 查询均为 `gh api` / `gh pr view` / `gh run list` 读取，没有写操作。

### 2.2 单元测试（E1）

在仓库根目录执行任务指定的 CI 同款命令：

```text
python -X utf8 -m unittest tools.test_trusted_quality tools.test_trusted_workflow_guard tools.test_trusted_preview_build tools.test_trusted_preview_artifact tools.test_trusted_preview_fetch tools.test_trusted_receipt tools.test_preview_catalog tools.test_reconcile_previews tools.test_preview_release tools.test_verify_preview_publication -v
```

结果：`Ran 76 tests in 7.805s` → `OK`，退出码 0。输出中出现的 `RuntimeError: failure` 等 traceback 来自「构建失败不留产物」等故意失败用例，对应用例随后为 `ok`。

需要注意：
- 这是**本地**运行结果，不等于 GitHub Actions 已运行同一命令（远端 PR #55 的 `Build and check` 成功见 E5，但那是该 PR 当时的状态，不覆盖本次复核）。
- 单测大量使用模拟 GitHub 响应；只有 `tools.test_trusted_receipt` 的部分用例基于真实收据的本地副本。

### 2.3 只读查询清单

完整命令与输出摘要见附录 A。数据均为 2026-11-28 11:14–11:26（UTC+8）快照；GitHub 状态随时可能变化，后续复核须重新查询。

> 表格字段说明：任务要求的「未完成」与「阻塞原因」合并在「未完成（含阻塞原因）」一列，两者均在单元格内写明。

---

## 三、Issue #36「为 Wiki PR 提供隔离的公开预览与审查状态」

### 3.1 验收对照

| # | 验收项（原文） | 已实现代码位置 | 已验证证据 | 未完成（含阻塞原因） | 下一步 |
|---|---|---|---|---|---|
| 1 | 仅检查通过的当前 PR 版本可预览；新增提交和检查失败时不显示过时版本为已通过 | `tools/reconcile_previews.py:51-99`（选择该 head 的最新运行，失败/运行中/重跑保守处理）；`tools/reconcile_previews.py:135-140`（build 与 trusted 均须 success）；`tools/stage_preview.py:196-205`（暂存时复核最新运行）；`tools/verify_preview_publication.py:16-42`（发布前复核）；`tools/preview_catalog.py:30-65`（组装时复核） | E1：`test_reconcile_previews` 13 项、`test_preview_catalog` 10 项、`test_verify_preview_publication` 4 项通过 | **未在真实预览站验证**。且实测 14 次可信运行的 `pull_requests` 均为空，`latest_run` 会在 `reconcile_previews.py:63-67` 直接抛 `MissingRunAssociation`，按现状发现流程会跳过这些 PR | 先解决 #41 的 PR↔运行绑定，再在独立 Pages 上用真实 PR 验证「新提交/失败→隐藏旧版本」 |
| 2 | 正式站和多个预览同时可用，关闭和合并后预览被清理 | `tools/preview_catalog.py:126-188`（多 PR 目录）；`tools/preview_catalog.py:33-40`（closed PR 返回 False，被省略）；`tools/reconcile_previews.py:145-150`（外部 PR 审批 + 暂存）；`tools/preview_release.py:26-44`（只清理带项目标记的旧版本）；`tools/preview_release.py:98`（保留上一版本） | E1：`test_preview_catalog.test_multiple_prs_remain_and_closed_or_stale_previews_disappear` 等通过；E7/E8/E17：正式站与预览仓库确实是两个仓库、两套 Pages（正式站 `build_type=workflow`，预览仓库 `legacy`） | 没有线上「多 PR 并存」「关闭/合并后清理」「失败保留可恢复版本」实测；公开页面仍是占位页（E10）。阻塞：预览站未部署。 | 部署后用多个真实 PR 观察增删；补失败/恢复演练记录 |
| 3 | 审批、撤销及新提交均能正确反映，信息不可由 PR 页面伪造 | `tools/preview_review.py:39-77`（只认非作者、具备 write 权限、`commit_id == head` 的 APPROVED）；`:88-134`（快照前后一致性、权限查询失败不算批准）；`preview_shell/shell.js:62-106`（浏览器按快照与实时 reviews/main SHA 复核）；`preview_shell/index.html:6,19`（CSP + `sandbox="allow-scripts"`）；`preview_shell/frame.js:60`（DOMParser 解析出的脚本在沙箱内才执行） | E1：`test_preview_review`、`test_preview_catalog.test_review_service_failure_leaves_preview_without_approval` 等通过；`docs/preview-operations.md:65,118` 声称本机 Edge 测试通过，**本轮未复跑浏览器测试** | 真实 Pages 上的声明栏防篡改、沙箱/CSP、外部网络/直接导航限制、批准撤销与新提交的浏览器表现均未验证；15 分钟快照延迟只在文档与代码中体现。阻塞：预览站未部署。 | 部署后用真实审批/撤销/新提交做浏览器验证；浏览器测试结果需另行留证 |
| 4 | 覆盖外部 PR 的安全边界，并记录配置、测试和恢复方法 | `tools/trusted_quality.py:32-72`（拒绝符号链接/特殊文件、拒绝会被扫描器跳过的 `zh_cn` 目录）；`tools/trusted_preview_build.py:25-87`（可信代码 + 不可信 Markdown、无令牌、无 PR 脚本）；`.github/workflows/wiki-trusted-data.yml:5-121`；`docs/preview-operations.md:29-41,87-94` | E1：trusted 相关 42 项单测通过；E11：6 次真实 fork 头运行（`head_repository.id=1465815327`）均为 success/failure；E14：真实 fork v1 收据可下载 | 外部 fork 的 v2 端到端（v2 收据 → 可信预览工件 → 发布前复核 → 发布）未验证；撤销、API 故障未实测；恢复方法只写在文档，未演练 | 在真实外部 fork 上触发 v2 运行，按发布前复核链路完成一次全链路演练 |

### 3.2 关键事实

- 公开预览页 `https://ganmayou2333.github.io/hsr-knowledge-base-preview/` 返回 HTTP 200，正文 1580 字节，标题「Wiki PR 预览 · 尚未开放」，正文明确写「当前没有可用的 PR 预览」（E10）。这只能证明占位页可访问，不能证明 PR 内容预览。
- #36 依赖的「仅当前通过检查的版本」在代码层有多重复核，但真实发布链路的最后一环（独立 Pages 部署）不存在（见 #40）。
- 由于 GitHub 对运行返回空的 `pull_requests`，当前发现逻辑对外部**和内部** PR 都可能保守跳过（`docs/preview-operations.md:19` 已记录内部 PR #53 的情况；本次 14 次运行全部为空，E11）。

### 3.3 结论

**#36 未完成。** 可以声称的是「相关代码与单元测试已合并」；不能声称「公开预览已可用」「多 PR 并存已实测」「审批状态已在线上正确反映」。

---

## 四、Issue #40「部署独立 GitHub Pages 并自动更新与清理」

### 4.1 验收对照

| # | 验收项（原文） | 已实现代码位置 | 已验证证据 | 未完成（含阻塞原因） | 下一步 |
|---|---|---|---|---|---|
| 1 | 独立 Pages 正常发布，正式站不受影响；多 PR 和关闭、合并、失败、恢复场景有实测记录 | `docs/templates/preview-pages-workflow.yml`（整理 + 部署两任务）；`tools/reconcile_previews.py`；`tools/preview_release.py`；`tools/verify_preview_publication.py` | E8/E9：预览仓库 Pages `status=built`、`build_type=legacy`、来源 `main:/`；最后构建 `d31d6d20f48a...`（2026-11-20T16:36:03Z）；仅 1 次 `github-pages` 部署（2026-11-20T16:36:35Z）；E15：仓库根只有 `README.md` 与 `index.html`，无 `.github/workflows`、0 个 Actions secret；E17：正式站 HTTP 200，正式站部署到 `d7e0daf`（2026-11-28T02:48:06Z） | **没有 PR 内容发布**；没有多 PR、关闭/合并清理、失败/恢复实测；模板尚未安装。阻塞：未创建 `SOURCE_READ_TOKEN`、未把预览仓库 Pages 来源切到 GitHub Actions、未完成 #41 联调 | 先完成 #41；创建最小权限只读凭据；安装模板并切换 Pages 来源；保留占位页回滚路径 |
| 2 | 真实 Pages 上验证声明栏及沙箱隔离、外部网络和直接导航限制；考虑 Pages 可能与正式站共用浏览器源 | `preview_shell/index.html:6,19`（CSP、iframe sandbox）；`preview_shell/shell.js:292-296`（重建 sandbox iframe 与 srcdoc CSP）；`preview_shell/frame.js:15-40`（只允许预览内路径导航） | 只有本地代码与（文档声称的）本机 Edge 测试；真实 Pages 上未部署 PR 预览，无法验证 | 未部署；同源隔离（`github.io` 路径分离不等于 origin 隔离）未实测 | 部署后用真实页面检查 CSP/sandbox/外链/直接导航与同源影响 |
| 3 | 审核批准、撤销、提交变化及快照过期均经浏览器验证，用户可见状态不夸大实时性 | `preview_shell/shell.js:5`（`SNAPSHOT_MAX_AGE_MS = 15 分钟`）；`:45-60`（批准状态到期回退）；`:62-106`（90 秒/可见性刷新与 main SHA 复核）；`tools/preview_review.py` | 单测覆盖部分逻辑；文档 `docs/preview-operations.md:65,118` 声称本机 Edge 测试通过，**非线上、非本轮复跑** | 真实浏览器事件（批准、撤销、新提交、快照过期）未在 Pages 上验证；快照延迟是设计而非实测数据 | 部署后逐场景录屏/留证；明确「15 分钟是失效上限，不是刷新保证」 |
| 4 | 运维文档包括凭据最小权限、配置、部署、故障处理和回滚；无凭据泄露 | `docs/preview-operations.md:27-41`（模板安装条件、候选只读权限、`gh secret set` 交互式设置与轮换）、`:87-94`（公开前仍需完成事项）；模板本身在 `docs/templates/preview-pages-workflow.yml` | E15：预览仓库 Actions secret 数为 0（未配置凭据）；本次检索 `SOURCE_READ_TOKEN/ghp_/github_pat_` 未发现明文令牌（E20） | 凭据未创建、未验证最小权限、未轮换；回滚/故障处理未演练；部署步骤未真实运行 | 创建仅选源仓库的细粒度只读令牌，按文档验证读取/失败行为，记录轮换与回滚演练 |

### 4.2 关键事实

- 预览仓库 `ganmayou2333/hsr-knowledge-base-preview` 创建于 2026-11-20；`main` 只有两次提交（`Initial commit`、`Add preview holding page`），之后没有新提交（E15）。因此页面内容仍是 2026-11-20 的占位页。
- 预览 Pages 的 `build_type` 是 `legacy`（从 `main` 分支根目录发布），不是 Actions 发布；模板 `docs/templates/preview-pages-workflow.yml` 只有 53 行，尚未复制到预览仓库。
- 正式站 `https://ganmayou2333.github.io/hsr-knowledge-base/` 返回 200，且最新部署 SHA 为本地/远端 `main` 的 `d7e0daf`（E17），说明正式站独立运行；但这不能替代「预览站不影响正式站」的功能验证。

### 4.3 结论

**#40 未完成。** 目前只完成「独立仓库 + 占位页」；公开 PR 内容预览、自动发布、清理、多 PR、失败恢复、凭据与回滚均未落地。**不能把代码合并或占位页 200 说成「预览站已上线」。**

---

## 五、Issue #41「启用可信数据检查并完成真实 PR 联调」

### 5.1 验收对照

| # | 验收项（原文） | 已实现代码位置 | 已验证证据 | 未完成（含阻塞原因） | 下一步 |
|---|---|---|---|---|---|
| 1 | 留存内部及外部 PR 的真实运行、产物和判定证据；当前版本的合格检查才能放行 | `.github/workflows/wiki-trusted-data.yml:5-121`（可信数据检查、可达构建、收据、预览工件上传）；`tools/trusted_receipt.py:35-100`；`tools/trusted_preview_artifact.py:15-93`；`tools/trusted_preview_fetch.py:19-72` | E11：14 次真实 `pull_request_target` 运行；E12/E13：内部 PR #55 的 `46099524983`（成功）产出 v2 收据 `15244971658` 与 `trusted-wiki-preview` 工件 `15245180923`（14,167,051 字节，未过期），SHA-256 与 API digest 一致；本地对真实数据把 PR 状态模拟为 `open` 后，`validate_receipt(..., require_workflow_sha=True)` 与 `select_trusted_preview` 均接受（返回工件 `15245180923`）；E14：外部 PR #48 的 v1 收据仍可下载与校验（legacy 模式） | **外部 fork 没有 v2 运行**（最新 fork 运行在 2026-11-21 UTC，而 v2 收据提交 `bfeb43d11` 随 PR #54 于 2026-11-27T18:54Z 才进 `main`）；内部 v2 证据的 PR 已合并，真实状态校验会拒绝，接受结论来自**模拟 state=open**；没有任何发布消费者接入 v2 工件。阻塞：外部 fork 无 v2 运行、运行↔PR 空关联、无发布接入。 | 用真实外部 fork 触发 v2 运行，下载并按 ID 校验 v2 收据与预览工件；接入发布前复核 |
| 2 | 失效、失败、未完成、重跑和 API 不可用时行为符合保守原则，旧成功结果不会被错误沿用 | `tools/reconcile_previews.py:51-99`（创建时间/启动时间/重跑一致）；`tools/trusted_preview_artifact.py:28-64`（同 head 最新运行，失败也阻挡）；`tools/trusted_receipt.py`（关闭、重跑、失败、过期、类型错误）；`tools/preview_review.py:88-134`（API 快照一致性） | E1：76 项单测通过，含 `test_reconcile_previews`、`test_trusted_preview_artifact`、`test_trusted_receipt`、`test_trusted_preview_fetch` 的失败/重跑/过期/API 失败用例；E11：真实存在失败运行 `44866281377` 与成功运行并存 | 没有通过真实 GitHub 事件（关闭、重跑、API 故障、限流）验证；文档中的「关闭/重跑/过期」均为本地内存修改模拟；v1 收据在 `require_workflow_sha=True` 时被拒绝（E14），但真实 v2 消费者尚未接入 | 设计真实事件演练（关闭 PR、重跑 run、模拟 API 失败），留存 GitHub 时间线与输出 |
| 3 | 部署流程在发布前重新验证绑定；测试与运维说明覆盖权限和信任边界 | `tools/verify_preview_publication.py:16-61`；`docs/templates/preview-pages-workflow.yml:30-40`（整理后、上传前调用 `verify_preview_publication`）；`docs/preview-operations.md` | `test_verify_preview_publication` 4 项通过；模板代码在仓库内存在 | 模板未安装到预览仓库；没有真实部署触发过发布前复核；复核到部署之间的竞态未消除（代码注释自述） | 安装模板后，用真实 PR 验证「目录组装→发布前复核→部署」全链路并留日志 |

### 5.2 真实运行与工件证据（E11–E14）

**运行面：**

- 可信工作流 `Trusted Wiki data checks` 已进入默认分支（工作流 `id=425388250`，`state=active`，E11），共 14 次 `pull_request_target` 运行（2026-11-20 至 2026-11-28）。
- 其中 6 次的头仓库是 `Hikarifly/hsr-knowledge-base`（fork，`head_repository.id=1465815327`），其余 8 次头仓库是主仓库 `1348409427`。
- **14 次运行的 `pull_requests` 字段全部为空**（E11）。这既解释了发现流程为何保守跳过，也说明「空关联」不是 fork 独有。

**内部 PR #55（v2，真实）：**

- 运行 `46099524983`：`event=pull_request_target`、`status=completed`、`conclusion=success`、`run_attempt=1`、`head_sha=7c4bd55c14b4a74dc71aa510542b9ddef06d5385`、`base=647c19f350e2e1e6aae6559b81b198cd0ade9745`（E12）。
- 工件：
  - `trusted-check-receipt-55-46099524983-1`（id `15244971658`，335 字节，`expired=false`，到期 2026-12-05T02:44:41Z）；
  - `trusted-wiki-preview-55-46099524983-1`（id `15245180923`，14,167,051 字节，`expired=false`，到期 2026-12-05T02:44:43Z）（E12）。
- 下载后 SHA-256 分别等于 API 的 digest（`fac2cec7...`、`b560b13f...`）；收据内容为 `version: 2`、`pr: 55`、`head/base` 与运行一致、`workflow_sha == base`（E13）。
- 内层 `wiki-preview.zip` 可读：6,713 个条目、6,700 个 `pages/*.html`、`index.html` 存在、`testzip()` 无错误；没有图标是可信构建**有意排除** `wiki/assets/icons`（`tools/trusted_preview_build.py:46-52`），不是损坏（E13）。
- 本地校验：PR #55 当前是 `MERGED`，`validate_receipt` 因 `state != open` 拒绝；仅在内存把状态改为 `open` 后通过（`(46099524983, 1)`），`select_trusted_preview` 返回预览工件 `15245180923`（E13）。**这是模拟状态，不是真实重新打开 PR，也不构成发布授权。**

**外部 fork PR #48（v1，真实）：**

- PR 状态：`CLOSED`、`isDraft=true`、`mergedAt=null`、`closedAt=2026-11-27T18:31:06Z`；head `53e28a08...`、base `2c424eb8...`（E6）。
- 可信运行 `44866284478`：成功、attempt 1、`pull_requests=[]`、check suite `121434833906` 的 `pull_requests=[]`；头仓库 `1465815327`（E14）。
- 收据工件 `14691489753`（322 字节，当前未过期，到期 2026-11-28T04:28:44Z）内容为 **version 1**、无 `workflow_sha`（E14）。
- 本地校验：`require_workflow_sha=False` 时接受 `(44866284478, 1)`；`require_workflow_sha=True` 时拒绝（E14）。因此 **v1 不能作为 v2 预览绑定证据**。

**消费/发布接入现状：**

- 生产代码中没有模块导入 `tools.trusted_preview_fetch` / `tools.trusted_preview_artifact` / `tools.trusted_receipt`；只有测试导入（E18）。`reconcile_previews.py:149` 仍暂存普通 `wiki-quality` 构建产物，而不是 `trusted-wiki-preview` 工件。
- `docs/templates/preview-pages-workflow.yml` 调用 `reconcile_previews` + `verify_preview_publication`，按现版本也不会消费 v2 可信预览工件。
- 结论：v2 工件目前是**已生产、未消费**；「当前版本的合格检查才能放行」在真实发布链路上没有执行体。

### 5.3 正文中三个未勾选子项

| 子项 | 现状 | 判断 |
|---|---|---|
| 为可信检查和构建产物设计不可由投稿者伪造的 PR 编号、head、base 和运行 attempt 绑定，覆盖 GitHub 返回空关联的场景 | 收据里已有 pr/head/base/run/attempt/workflow_sha；但运行↔PR 的空关联仍未解决，`latest_run`/`trusted_check` 仍要求 `pull_requests` 非空 | **未完成** |
| 对无法安全绑定的外部 PR 限定影响范围，同时保证 API 故障不会误发布旧结果；验证其他合格 PR 可以继续刷新 | 代码保守跳过无法绑定/API 错误时中止（单测覆盖）；没有真实 API 故障或多 PR 刷新实测 | **部分完成**（代码层，未实测） |
| 使用真实 fork 的 `pull_request` 和 `pull_request_target` 运行端到端验证绑定、撤销及异常处理，补充测试和运维说明 | 有真实 fork v1 运行与本地模拟；没有 v2、撤销、端到端发布 | **未完成** |

### 5.4 结论

**#41 部分完成。** 可以声称「可信检查工作流已在 `main` 生效并有 14 次真实运行」「内部 v2 收据与可信预览工件已由真实运行产出」「收据/工件关联原型可用真实数据复核」。不能声称「外部 fork 已联调完成」「v2 已接入发布」「撤销/API 故障已实测」。

---

## 六、Issue #42「配置合并检查并完成 Wiki 批次独立审查」

### 6.1 验收对照

| # | 验收项（原文） | 已实现/配置位置 | 已验证证据 | 未完成（含阻塞原因） | 下一步 |
|---|---|---|---|---|---|
| 1 | 仓库保护及必需检查有可复核的配置和验证记录；无法配置时记录原因与替代安排 | GitHub 仓库设置（非代码）；记录见 issue 评论与 `docs/preview-operations.md:43-53` | E2：`GET branches/main/protection` 返回 `required_status_checks.checks=[{context:"Build and check",app_id:15368}]`、`required_approving_review_count=0`、`dismiss_stale_reviews=true`、`enforce_admins=true`、`allow_force_pushes=false`、`allow_deletions=false`、`strict=false`；E3：`rulesets=[]`、`rules/branches/main=[]`；E4：协作者 `ganmayou2333`（admin）与 `Hikarifly`（write） | 未做违规推送/违规合并实验，不能证明规则实际阻断；未审计组织级 ruleset/策略；「必需批准」已从 1 调整为 0，原验收里的「至少 1 个批准」同等要求不再由保护强制 | 记录「配置已读取 + 未做实际违规测试」；如需独立审查，必须另行以流程/人工要求补足，不能依赖当前 0 批准保护 |
| 2 | 有非作者、具备相应权限的协作者审查最终提交，审查意见已处置，批准有效 | GitHub 审查记录 + `tools/preview_review.py:39-77` | E5：PR #37 于 2026-11-20T20:03:33Z 合并（UTC+8 2026-11-21 04:03:33）；`Hikarifly` 于 20:03:00Z 对头提交 `f381cffa...` 提交 APPROVED，审查正文为空；该提交 `Build and check` 成功。E16：PR #54、#55 的 reviews 均为 `[]`，`reviewDecision` 为空 | 当前批次（#54/#55）**没有独立人工审查**；PR #37 的批准只覆盖旧头提交且正文为空，不能推断规范/数据/预览安全边界均被逐项核验；审查者权限为当前查询结果，不能证明批准时权限。阻塞：后续批次未安排独立审查。 | 由非作者且具备权限者审查后续最终提交并留下可复核结论；在合并前重新核对作者、头提交、批准提交与权限 |
| 3 | 最终 PR 检查通过，未完成项均被追踪并按批次要求处置；在此之前 PR 保持草稿、不合并 | issue 跟踪 + 分支保护 | E5：PR #37 的 `Build and check` success；E16/E17：PR #54（2026-11-27T18:54:48Z）与 #55（2026-11-28T02:46:15Z）均 `MERGED`，检查通过；四个 issue 仍 `open`（E19） | 「最终 PR 保持草稿直到批次完成」已不适用于已合并的 #37/#54/#55；#54/#55 在无 review 情况下合并，说明独立审查要求没有真正执行。阻塞：保护已改为 0 批准，未强制独立审查。 | 明确后续批次是否仍要求独立审查；若要求，应在合并前完成，而不是事后补记 |

### 6.2 关键事实

- `main` 当前**受保护**：必需检查 `Build and check`（GitHub Actions，app 15368）、必需批准数 **0**、新提交撤销过期批准、管理员同样受保护、禁强推/删除、不要求分支严格同步（E2）。仓库 ruleset 列表与分支 rules API 均为空（E3），因此「GitHub 当前报告受阻」只能依赖分支保护读取，不能证明绕过路径被阻止。
- 协作者当前为 2 人：`ganmayou2333`（admin，仓库所有者）与 `Hikarifly`（write）（E4）。2026-11-21 评论中「仅所有者一位协作者」是过期快照。
- PR #37：已合并，合并前有 `Hikarifly` 的 APPROVED（对 `f381cffa...`），`Build and check` 成功；审查正文为空（E5）。
- PR #54、#55：均无 review（`[]`），`reviewDecision` 为空，仍被合并（E16）。这与 issue #42 的验收项 2 直接冲突。
- 当前没有开放的 PR（E17），因此无法在不新建 PR 的前提下做新的审查/合并联调；本轮也不允许创建 PR。

### 6.3 结论

**#42 未完成。** 分支保护与必需检查的**配置**可以复核（但必需批准数为 0，且未做实际违规合并验证）；**当前批次没有独立人工审查**，这项不能由自动检查或执行者本人替代。

---

## 七、不得声称已完成的项

以下任何一条都不应写成「已完成 / 已上线 / 已生效」：

1. **独立预览 Pages 已部署 PR 内容预览**：公开页仍是占位页（E10），预览仓库没有新提交、没有预览工作流（E15）。
2. **自动发布、定时刷新、关闭/合并清理已上线**：代码在本地，模板未安装，无线上运行记录。
3. **真实 Pages 上的声明栏、CSP、sandbox、外部网络/直接导航限制已验证**：只有本地代码与文档声称的本机浏览器测试，本轮未复跑。
4. **外部 fork 已完成端到端联调**：仅有 v1 真实收据；没有 fork 的 v2 运行、没有发布前复核、没有发布。
5. **v2 可信预览工件已接入发布/发现/暂存**：生产代码无导入，`reconcile_previews.py:149` 仍用普通构建产物（E18）。
6. **普通 PR 构建产物已安全绑定**：`pull_requests` 空关联问题仍在，14 次运行全部为空（E11）。
7. **发布凭据已创建/轮换并验证最小权限**：预览仓库 Actions secret 数为 0（E15）。
8. **多 PR、关闭、合并、失败、恢复场景有实测记录**：只有单测与本地模拟，没有线上记录。
9. **API 故障、限流、重跑、关闭等真实事件已验证**：均为本地内存模拟；真实 GitHub 事件未触发。
10. **独立人工审查已完成**：PR #54、#55 零 review；PR #37 的批准只覆盖旧提交且正文为空（E5/E16）。
11. **分支保护已通过违规合并实验验证**：只读取了配置，没有尝试违规操作（E2/E3）。
12. **15 分钟快照/90 秒刷新/审核状态延迟等运行行为已在线上验证**：这些是代码与文档中的设计值。
13. **v2 收据的模拟接受等于真实 PR 打开联调**：PR #55 已合并，接受结论依赖内存改 `state=open`（E13）。

---

## 八、零风险可立即做的小修（清单，本次未实施）

以下均为**文档措辞/快照更新**，不涉及代码、workflow、部署、凭据或数据区；列出供有写权限的人决定，本次一律未改：

1. `docs/preview-operations.md:108`：把「版本 2 尚未在 GitHub 实际运行」改为「2026-11-28 内部 PR #55 的可信运行 `46099524983` 已产出真实 v2 收据与 `trusted-wiki-preview` 工件；消费者仍未接入，外部 fork 仍无 v2 运行」。
2. `docs/preview-operations.md:100,104`：更新「可信构建原型未接入 workflow」「工作流改动仅在本地、尚未实际运行」——现 `wiki-trusted-data.yml:72-73` 已调用 `trusted_preview_build.py`，`main` 上已有 14 次真实运行。
3. `docs/preview-operations.md:45,51`（#42 小节）：补一条同日晚些时候的现状：「必需批准数已调整为 0；远端 `main` 已到 `d7e0daf`，本地与远端一致（0 ahead）」；现有「1 个批准 / `a1461fbb` / 本地 172 个未推送提交」是更早快照。
4. `docs/preview-operations.md:15,57`：注明 PR #48 已于 2026-11-27T18:31:06Z 关闭（未合并、草稿），其 v1 工件到期时间 2026-11-28T04:28:44Z。
5. `docs/preview-operations.md:19` 附近：补充 2026-11-28 复核结果——14 次 `pull_request_target` 运行的 `pull_requests` 全部为空，空关联不只影响 fork，内部 PR 也会被跳过。
6. 在本证据文件落盘后，于 `docs/preview-operations.md` 顶部或「已有组件」处加一行指向 `docs/evidence/preview-status-2026-11-28.md` 的溯源链接（不改任何结论）。
7. 在 `docs/preview-operations.md:5` 的「还没有公开的 PR 内容预览」后补上最后核实时间与占位页构建 SHA `d31d6d2`（2026-11-20），避免读者把旧快照当实时状态。
8. 对 issue #36/#40/#41/#42 各追加一条「2026-11-28 复核证据见 …」的评论（**需要 GitHub 写权限，本轮禁止**；仅列为后续动作，不属于「立即可做」的仓库小修）。

---

## 九、文档与代码/现状不一致（只指出，本次不修改）

| 位置 | 文档说法 | 现状证据 | 判断 |
|---|---|---|---|
| `docs/preview-operations.md:108` | 「版本 2 尚未在 GitHub 实际运行，不能用旧的真实版本 1 收据作为版本 2 联调证据」 | E12/E13：真实运行 `46099524983` 已产出 v2 收据与 v2 预览工件 | **明确过时**；应更新，但仍不能据此说「v2 已联调/已发布」 |
| `docs/preview-operations.md:51` | 「分支保护继续要求 … 和 1 个批准」 | E2：`required_approving_review_count=0` | **与当前 API 不一致**；同一天 issue #42 评论已记录调整为 0 |
| `docs/preview-operations.md:51` | 「头提交为 `a1461fbb...`；本地 main 相对该远端头有 172 个尚未推送的提交」 | E17：远端 `main = d7e0daf...`，与本地 `HEAD` 相同 | **过期快照**（文中已用「当时」限定，但读者容易误读为现状） |
| `docs/preview-operations.md:100` | 「该原型最初未接入 workflow … 尚无真实 PR 的产物绑定」 | `wiki-trusted-data.yml:72-73` 已调用；但「真实 PR 产物绑定」仍需限定为普通构建产物与 PR 的绑定 | **前后半句需分开更新**：已接入 workflow，未接入发布消费者 |
| `docs/preview-operations.md:104` | 「该工作流改动仅在本地，尚未推送或实际运行」 | E11：`main` 上 14 次真实运行 | **明确过时**（该段本身标注为 2026-11-27 的本地状态，但未标注已被后续取代） |
| `docs/preview-operations.md:15` | 「2026-11-27 对仍开放的真实 fork PR #48 …」 | E6：PR #48 于 2026-11-27T18:31:06Z 关闭 | 日期化叙述可保留，但应补「现已关闭」 |
| `docs/templates/preview-pages-workflow.yml:30-40` | 模板用 `reconcile_previews` 组装后发布 | 代码现状：`reconcile_previews` 仍暂存普通 `wiki-quality` 产物，v2 可信预览工件无消费者（E18） | **不是文档笔误，是设计缺口**；安装模板前需先决定是否改用 v2 工件 |
| `docs/preview-operations.md:71` | 「收据代码尚未接入发现、暂存、页面或发布流程」 | E18：确认无生产导入 | **一致**，非不一致项 |

---

## 十、未验证 / 待核事项

- 分支保护的**实际阻断效果**：未做违规合并/强推/删除实验；组织级规则未审计。
- 外部 fork 的 **v2** 收据、v2 可信预览工件与发布前复核：不存在真实运行。
- **发布消费者**：v2 工件如何进入发现、暂存、发布前复核，尚无代码。
- **真实浏览器**：独立 Pages 上的 CSP/sandbox/外链/直接导航/同源影响；本轮未复跑文档声称的 Edge 测试。
- **真实事件**：关闭 PR、重跑、失败、API 故障、限流对发布流程的影响，未在 GitHub 上实测。
- **多 PR 并发**：没有两个以上真实 PR 同时可预览的记录。
- **凭据**：未创建、未验证最小权限、未轮换；未验证 `SOURCE_READ_TOKEN` 所需的 Actions/PR/Metadata 只读权限是否足够。
- **清理/恢复**：原子切换、回滚占位页、失败保留上一版本，均无真实部署演练。
- **时间竞态**：`verify_preview_publication` 的复核与部署之间仍有时间窗（代码注释自述），未量化。
- PR #48 v1 收据的到期时间 2026-11-28T04:28:44Z：本次查询时尚未过期，之后是否还能下载未验证。
- 工作区其他协作者的未提交改动（含 `.github/workflows/wiki-quality.yml`）未纳入本次验证；本报告结论以 `HEAD d7e0daf` 为准。

---

## 附录 A：证据清单（命令与输出摘要）

> 原始输出保存在本机 `.tmp_issues/agent6-*`（临时目录，不随仓库提交）。时间为 UTC+8。

| ID | 命令 | 时间 | 输出摘要 |
|---|---|---|---|
| E1 | `python -X utf8 -m unittest tools.test_trusted_quality tools.test_trusted_workflow_guard tools.test_trusted_preview_build tools.test_trusted_preview_artifact tools.test_trusted_preview_fetch tools.test_trusted_receipt tools.test_preview_catalog tools.test_reconcile_previews tools.test_preview_release tools.test_verify_preview_publication -v` | 11:14 | `Ran 76 tests in 7.805s` / `OK` / exit 0 |
| E2 | `gh api repos/ganmayou2333/hsr-knowledge-base/branches/main/protection` | 11:15 | `required_status_checks.checks=[{context:"Build and check",app_id:15368}]`；`required_approving_review_count=0`；`dismiss_stale_reviews=true`；`enforce_admins=true`；`allow_force_pushes=false`；`allow_deletions=false`；`strict=false`；`required_conversation_resolution=false` |
| E3 | `gh api repos/ganmayou2333/hsr-knowledge-base/rulesets`；`gh api repos/ganmayou2333/hsr-knowledge-base/rules/branches/main` | 11:15 | 两次均返回 `[]` |
| E4 | `gh api 'repos/ganmayou2333/hsr-knowledge-base/collaborators?per_page=100'` | 11:15 | `ganmayou2333`（admin/maintain/push/triage/pull）、`Hikarifly`（push/triage/pull，role_name=write） |
| E5 | `gh pr view 37 --json number,state,isDraft,headRefOid,baseRefOid,reviewDecision,mergeStateStatus,mergedAt,reviews,statusCheckRollup` | 11:16 | `MERGED`，`mergedAt=2026-11-20T20:03:33Z`，head `f381cffa...`；`Hikarifly` APPROVED（`2026-11-20T20:03:00Z`，body 空）；`Build and check` SUCCESS |
| E6 | `gh pr view 48 --json ...` | 11:16 | `CLOSED`、`isDraft=true`、`mergedAt=null`、`closedAt=2026-11-27T18:31:06Z`、head `53e28a08...`、base `2c424eb8...`；检查含 1 次失败 `44866281377` 与成功 `44866284478` |
| E7 | `gh api repos/ganmayou2333/hsr-knowledge-base-preview` | 11:15 | 公开仓库，`created_at=2026-11-20T16:34:00Z`，`default_branch=main`，`has_pages=true`，`pushed_at=2026-11-20T16:35:56Z` |
| E8 | `gh api repos/ganmayou2333/hsr-knowledge-base-preview/pages` | 11:15 | `status=built`、`build_type=legacy`、`source={branch:"main",path:"/"}`、`html_url=https://ganmayou2333.github.io/hsr-knowledge-base-preview/` |
| E9 | `gh api .../pages/builds/latest`；`gh api '.../deployments?per_page=10'` | 11:15 | 最后构建 `commit=d31d6d20f48a...`、`status=built`、`created_at=2026-11-20T16:36:03Z`；仅 1 次 `github-pages` 部署（`2026-11-20T16:36:35Z`，sha `d31d6d2...`） |
| E10 | `curl.exe -sS -o .tmp_issues/agent6-preview-page.html -w "%{http_code} %{content_type} %{size_download}" https://ganmayou2333.github.io/hsr-knowledge-base-preview/` | 11:16 | `200 text/html; charset=utf-8 1580`；页面标题「Wiki PR 预览 · 尚未开放」，正文「当前没有可用的 PR 预览」 |
| E11 | `gh run list --workflow 'Trusted Wiki data checks' --limit 10`；`gh api '.../actions/runs?event=pull_request_target&per_page=50'`；`gh api .../actions/workflows/wiki-trusted-data.yml` | 11:17 | 工作流 `id=425388250`、`state=active`；`total_count=14`；14 次均 `pull_requests=[]`；头仓库为 fork `1465815327` 的 6 次、主仓库 `1348409427` 的 8 次；最新 `46099524983`（2026-11-28T02:44:17Z，success） |
| E12 | `gh api .../actions/runs/46099524983`；`gh api .../actions/runs/46099524983/artifacts` | 11:18 | 运行成功、attempt 1、base `647c19f...`；工件 `trusted-check-receipt-55-46099524983-1`（`15244971658`，335B）、`trusted-wiki-preview-55-46099524983-1`（`15245180923`，14,167,051B），均 `expired=false` |
| E13 | 下载两个工件 → SHA-256 比对 → 读取收据 → `validate_receipt` / `select_trusted_preview`；内层 ZIP 检查 | 11:19 | SHA-256 与 API digest 一致；收据 `version:2, pr:55, head:7c4bd55..., base:647c19f..., run:46099524983, attempt:1, workflow_sha:647c19f...`；当前 `state=MERGED` 被拒绝，内存改 `open` 后接受 `(46099524983,1)`，`select_trusted_preview` 返回 `15245180923`；内层 6,713 项 / 6,700 个 HTML，`testzip()` 无错 |
| E14 | 下载 `14691489753` → 读取收据 → `validate_receipt`；`gh api .../check-suites/121434833906` | 11:20 | 收据 `version:1`、pr 48、head `53e28a08...`、base `2c424eb8...`、head_repo `1465815327`；`require_workflow_sha=False` 接受、`True` 拒绝；suite `pull_requests=[]` |
| E15 | `gh api .../hsr-knowledge-base-preview/contents/`；`.../contents/.github/workflows`（404）；`.../actions/secrets`；`.../commits?per_page=5` | 11:20 | 根目录仅 `README.md`（101B）、`index.html`（1580B）；无 `.github/workflows`；`total_count=0` secrets；仅 2 次提交（`Add preview holding page`、`Initial commit`） |
| E16 | `gh api .../pulls/54/reviews`；`.../pulls/55/reviews`；`gh pr view 54/55` | 11:21 | 两者 reviews 均为 `[]`；#54 `MERGED`（2026-11-27T18:54:48Z）、#55 `MERGED`（2026-11-28T02:46:15Z）；`reviewDecision` 均空 |
| E17 | 最终快照：`branches/main`、protection、collaborators、`gh pr list --state open`、curl 预览页/正式站、`pages/builds/latest`、secrets | 11:21:03 | 远端/本地 main 均 `d7e0daf...`；approvals 0、checks `Build and check`、admins true、force/delete false、strict false；rulesets 0；协作者 2；开放 PR 0；预览页 200；正式站 200，正式站部署 SHA `d7e0daf`（2026-11-28T02:48:06Z）；预览页最后构建 `d31d6d2`（2026-11-20）；预览 secrets 0 |
| E18 | `Select-String -Path tools/*.py -Pattern 'trusted_preview_fetch\|trusted_preview_artifact\|trusted_receipt\|select_trusted_preview\|download_trusted_preview'` | 11:22 | 生产代码无导入；仅测试文件引用；`reconcile_previews.py:149` 用 `stage(...)` 暂存普通产物 |
| E19 | `gh api repos/.../issues/{36,40,41,42}` | 11:22 | 四个 issue 均为 `open`；评论数分别 1/2/3/4 |
| E20 | `Select-String -Path docs/preview-operations.md,.github/workflows/*.yml -Pattern 'SOURCE_READ_TOKEN\|ghp_\|github_pat_'` | 11:22 | 仅 `docs/preview-operations.md:27,41` 的说明性引用，未发现明文令牌 |
