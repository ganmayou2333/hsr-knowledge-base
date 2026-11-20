# Wiki PR 预览：运行状态与接入条件

本方案目前只生成并校验预览输入，还没有公开的 PR 内容预览，也没有自动发布或清理服务。独立仓库 `ganmayou2333/hsr-knowledge-base-preview` 已创建，Pages 暂以其 `main` 的静态占位页发布；占位页不包含 PR 内容。正式站的 GitHub Pages 不应被预览部署覆盖。PR 工作流可以由投稿者修改，因此它的成功结果本身不能作为独立可信检查。

用户选择使用独立的 GitHub Pages 预览站，接受审核状态延迟。Pages 是静态托管，不能运行下述 Python 审核服务。静态页面只在快照不超过 15 分钟、浏览器能核对当前 PR 和审核记录时显示“已有人工批准（快照，可能延迟）”；审核者权限发生变化时，状态可能在快照到期前滞后，获取或核验失败则显示未审查。浏览器访问 GitHub API 还可能受限流影响。15 分钟是失效上限，不是发布或同步频率保证；定时发布失败或排队时可能长时间显示未审查。

外部 PR 的运行关联仍有已知缺口（#41）：GitHub 有时在工作流运行和对应 check suite 中都返回空的 `pull_requests`。例如 2026-11-21 复核的 `github/docs` 运行 44763860127（suite 121163780687，`pull_request_target`）和 `cli/cli` 运行 44657416158（suite 120881046666，`pull_request`）均如此。不能仅凭相同提交、分支名或 check suite 推断运行属于哪个 PR；当前实现跳过无法绑定的预览，其余可安全绑定的 PR 仍可处理。这两例不能代替本仓库 fork 的端到端验收。

本仓库的真实 fork 也已复现该现象：草稿 PR #44 从 `Hikarifly/hsr-knowledge-base` 提交，最小 `pull_request` 探测运行 44801922468 成功，但其运行记录和 check suite 121266314550 的 `pull_requests` 均为空。探测工作流未检出 PR 文件，也没有部署或使用发布凭据。这只验证了普通 PR 事件的关联缺口；可信 `pull_request_target` 检查尚未进入默认分支，仍未完成本仓库的端到端联调。

同一 fork 分支随后被用于指向隔离测试基线的 PR #45，运行 44802545276 也成功且 PR 关联为空。PR #45 的状态检查同时显示了 #44 的旧运行和本次新运行：检查附着于同一提交不能证明它属于当前 PR 或目标基线。隔离测试基线中的最小 `pull_request_target` 工作流在本次观察期间未出现运行；这次试验未能验证该事件。GitHub 的[事件说明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target)指出，GitHub.com 的 `pull_request_target` 运行在目标仓库默认分支的上下文中；本次探测工作流只放在隔离基线上，未放入默认分支，因而不能作为真实可信事件验收。测试未修改 `main`。

2026-11-21 合并基础功能后，可信工作流已进入默认分支。真实 fork 探测 PR #48 以当前 `main` 为基线，普通 `pull_request` 构建运行 44810577760 和可信 `pull_request_target` 数据检查运行 44810577529 均成功，但两次运行的 `pull_requests` 均为空；成功检查仍不能单靠提交或工作流名称与具体 PR 安全绑定，外部预览尚不可用。测试 PR 已关闭、未合并。此前重新打开旧基线 PR #44 时，运行 44808289456 的事件目标 SHA 仍为合并前版本，在检查前的状态核对处失败；后续新事件通过该核对，但由于旧分支含 4 处现已修复的失效链接，可信扫描失败。这些结果不能证明端到端预览发布或审查状态已完成。

关于签名证明的后续调查：GitHub 的 [OIDC 声明](https://docs.github.com/en/actions/reference/security/oidc)包含事件、ref、仓库、运行 ID 和 attempt 等字段，可作为研究运行身份绑定的线索；但这些字段本身并不证明 PR 构建脚本或内容可信，也不能替代对签名、产物摘要、目标版本与当前 PR 状态的验证。GitHub 的[标准产物证明流程](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)要求 `id-token: write` 和 `attestations: write`；外部 fork 的普通 PR 运行默认受到[只读权限限制](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)。因此不能假设该流程在外部 fork 中可用，也不能为此打开向不可信 PR 发送写令牌的设置。是否存在满足权限边界的证明方式仍需真实测试，当前发布校验没有采用这一机制。

静态页面加载及重新验证时还会查询对应提交的最新构建和可信数据检查；新检查失败、运行中、无法关联 PR 或无法查询时隐藏预览。外部 PR 还要求未过期的批准快照与当前审核记录一致；撤销、过期或无法核实时隐藏预览。审核者权限变化仍可能在快照到期前滞后。页面每 90 秒及重新获得可见性时重新验证，并每 15 秒复核审核状态，因此状态变化不会即时反映。额外的匿名 API 请求可能更快触发 GitHub 限流，此时预览会不可用，不能把这种行为描述为稳定的实时服务。

独立仓库的项目 Pages 与正式站可能共享同一个浏览器源（origin）；路径分离不能代替隔离。发布前仍须验证可信外壳、沙箱和 CSP 在实际 Pages 上的效果。跨仓库发布需要独立的最小权限凭据或其他可验证的授权机制；不得将宽权限个人令牌直接写入配置。发布步骤不得执行 PR 提供的代码。

`docs/templates/preview-pages-workflow.yml` 是供独立预览仓库审查的工作流模板，不会在本仓库运行。它每 10 分钟尝试从本仓库可信的 `main` 检出发布代码，整理预览，再由独立任务部署 Pages；整理或发布前复核失败不会进入部署任务。复核会检查每个已收录 PR 的当前状态、最新检查及外部投稿的批准，无法消除复核后至实际部署之间的时间窗口。`SOURCE_READ_TOKEN` 仅提供给整理步骤，部署权限仅在部署任务中授予。定时触发可能延迟，运行失败也不会刷新快照。安装前必须先完成 #41 的可信检查启用和真实联调，核实令牌所需的源仓库只读权限（包括产物和审核者权限查询）；切换独立仓库 Pages 来源到 GitHub Actions，并验证回滚占位页的方法。不要把模板复制到正式站仓库，也不要把未经审查的分支作为发布代码来源。

### 源仓库凭据准备

建议为预览发布单独创建仅选择 `ganmayou2333/hsr-knowledge-base` 的细粒度令牌，设置失效时间，并从只读权限开始验证：

| 仓库权限 | 用途 |
|---|---|
| Actions：Read | 查询工作流及运行、列出和下载构建产物 |
| Pull requests：Read | 查询 PR 和审核记录 |
| Metadata：Read | 查询仓库元信息与协作者权限 |

这些是依据 GitHub 的[细粒度令牌 REST 权限表](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)对当前调用整理出的候选权限，不等于已用新令牌完成实测。必须在 #41 联调中验证内部与外部 PR、下载产物以及审核者权限查询；未知权限或查询失败不能视为批准。不要将目前登录 `gh` 使用的宽权限令牌作为此 secret，也不要把令牌写入仓库、日志或聊天。

完成令牌创建后，可在可信终端交互式运行 `gh secret set SOURCE_READ_TOKEN --repo ganmayou2333/hsr-knowledge-base-preview`，按提示输入令牌；无需把令牌写在命令参数中。轮换时重新设置该 secret 并撤销旧令牌，随后用可信流程验证读取和失败行为。创建 secret 本身不会启用或发布工作流。

## 已有组件

- `wiki-quality.yml` 构建 Wiki 并生成预览包；包内内容仍是不可信数据。
- `wiki-trusted-data.yml` 使用目标分支的扫描程序检查 PR 数据，在检查前后核对 PR 仍处于打开状态且提交与目标版本未变。工作流需先进入默认分支才能响应事件；草稿 PR 中的文件不会自动启用。该检查只覆盖数据规则，不证明 PR 提供的构建脚本或产物可信。
- `tools/stage_preview.py` 校验并转换单个 PR 的预览包，并要求相同 PR、提交和目标版本的独立数据检查通过；`tools/preview_catalog.py` 重新生成多 PR 目录，并重新核验该检查。二者都不部署网站。
- `python -m tools.reconcile_previews OWNER/REPO preview_shell 输出目录` 可发现当前 PR 和最新检查，暂存合格产物并生成新目录；输出目录必须不存在。它不切换或部署线上站点，且需要先启用独立检查才能与真实 GitHub 端到端联调。
- `python -m tools.preview_release OWNER/REPO preview_shell 专用目录` 可在受信任的本机专用目录中生成新版本，复核后原子切换 `current`；失败保留现有版本。清理只处理带本项目标识且至少保留 10 分钟的旧版本，并保留上一个版本。异常退出可能留下 `.publish-lock`，应确认没有进程运行后人工处理。该命令不提供外网服务，也不会自行定期运行。
- `tools/preview_review_server.py` 可通过 `--site-root 专用目录` 读取当前版本并提供预览和短期审核状态；每次缓存更新时重新核验最新工作流运行及外部 PR 的批准，查询失败或状态变化则预览不可用。生产环境需要独立 HTTPS 托管、只读 GitHub 凭据和访问限流。它不负责生成版本或清理。

独立检查工作流会从外部 PR 检出内容用于数据扫描，因此显式启用了 checkout 的 `allow-unsafe-pr-checkout`。该任务不得运行 PR 提供的代码、安装其依赖、使用其工作流、缓存或提供发布凭据；后续修改必须保留这些边界。检查器和基线必须来自可信目标分支。

**外部 PR 当前不可用：** GitHub 的运行记录对 fork 投稿可能返回空的 `pull_requests` 列表。例如 `github/docs` 的 `pull_request_target` 运行 44763860127 和 `cli/cli` 的 `pull_request` 运行 44657416158 均出现该情况。现有实现无法据此安全绑定 PR，会跳过该 PR 并继续处理其他 PR；不能将它误认为已支持外部投稿。需先设计并实测可信的 PR、提交和目标版本绑定方式（见 #41），不可仅凭相同提交 SHA 或工作流名称放行。API 故障或格式错误仍会终止整次更新。

## 公开前仍需完成

1. 在真实 GitHub 运行中验证暂存及目录生成时的独立检查绑定，并接入部署前复核；不能只按工作流名称或 PR 自报结果放行。验证外部 PR 时也需覆盖此绑定。
2. 配置可信定时触发，将本地整理、原子切换及关闭或合并后的清理接成持续运行的流程，确保多个 PR 并存，并在失败时保留可恢复的有效版本。
3. 准备与正式站分离的 HTTPS 托管及最小权限只读凭据，验证访问限流、审核状态更新与撤销、不可用时的行为，以及声明和隔离效果。
4. 在目标分支启用独立检查后，用真实内部和外部 PR 验证整个流程；配置所需的分支保护，并由另一位有权限的协作者完成最终人工审查。

上述条件完成并实测前，不应把预览入口公开或把现有组件描述为完整的自动发布系统。
