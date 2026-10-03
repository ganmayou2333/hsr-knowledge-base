# tools/github-wiki —— GitHub Wiki 策展入口（8 页）

> 建立：2026-10-03 ｜ 维护：Lead ｜ 依据：`docs/github_wiki可行性评估.md`、`docs/github_wiki策展大纲.md`
> **定位：Wiki 只做入口，不放正文。** 正文由静态站点（GitHub Pages）承载。

---

## 一、为什么只做 8 页

官方文档明示：**wiki 有 5,000 文件软上限**，超出「部分页面无法访问」，并**建议改用 GitHub Pages**。本库 `zh_cn` 有 **6,665** 页，且 Wiki 是**扁平命名空间**（实测重名会导致 **696～939 页互相覆盖**），因此**全库镜像不可行**。结论见 `docs/github_wiki可行性评估.md`。

## 二、本目录文件 = Wiki 页名 1:1

| 文件 | 对应 Wiki 页面 | 备注 |
|---|---|---|
| `Home.md` | `Home` | **特殊页名**：Wiki 首页 |
| `_Sidebar.md` | `_Sidebar` | **特殊页名**：侧边栏（Wiki **不支持 TOC**，导航只能手写） |
| `项目简介.md` | `项目简介` | |
| `许可与合规.md` | `许可与合规` | |
| `数据来源.md` | `数据来源` | |
| `贡献指南.md` | `贡献指南` | |
| `更新日志.md` | `更新日志` | |
| `路线图与待补.md` | `路线图与待补` | |

上传时**去掉 `.md` 后缀即为页名**（`Home.md` → `Home`）。

## 三、启用与上传

### 前置（需仓库管理员操作）

1. **可见性**：Wiki 的可见性**随仓库**——要让 Wiki 公开，仓库必须先 **Public**；保持私有则需账号为 **Pro / Team / Enterprise**。
2. **启用**：仓库 **Settings → Features → 勾选 `Wikis`**。
3. 启用后点击 Wiki → **Create the first page**（保存一次，`<repo>.wiki.git` 才会被创建）。

### 方式 A：网页粘贴（8 页，最省事）

对每个文件：Wiki → **New page** → 页名填文件名（去掉 `.md`）→ 粘贴正文 → 保存。`_Sidebar` 与 `Home` 用同样的方式建。

### 方式 B：本地克隆批量推送

```powershell
# Wiki 是独立 git 仓库
git clone https://github.com/<owner>/<repo>.wiki.git  G:\HSR\.tmp_wiki
Copy-Item G:\HSR\tools\github-wiki\*.md  G:\HSR\.tmp_wiki\ -Force
cd G:\HSR\.tmp_wiki
git add -- Home.md _Sidebar.md 项目简介.md 许可与合规.md 数据来源.md 贡献指南.md 更新日志.md 路线图与待补.md
git commit -m "wiki: 策展入口 8 页（Lead 拟稿）"
git push origin master      # 注意：wiki 仓库默认分支是 master
```

> 首次需先按「前置」第 3 步在网页创建 `Home`，否则 `ls-remote` 会返回 **Repository not found**（本项目 2026-10-03 实测即为此状态）。

## 四、维护纪律

1. **Wiki 不放正文**：一旦开始搬正文就会撞上 5,000 上限与扁平重名。
2. **数字以实测为准**：`Home.md` 的规模数字每轮由脚本刷新，**不得手写**；统计时**排除 `.tmp_*` 工作副本**。
3. **单一真相在 vault**：改动一律先改 `G:\HSR`，再同步本目录，再推 Wiki。
4. **不含图片**：符合「图片零入库」红线；引用图片用外链。
