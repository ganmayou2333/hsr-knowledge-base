# tools/mediawiki —— 本库 → MediaWiki 演示实例工具集

> 建立：2026-10-03 ｜ 维护：Lead ｜ 状态：**可用**（已实测跑通全库 6,668 页导入）
> 定位：把 `zh_cn/` 的 Markdown 知识库**镜像**成一个可在浏览器里检索/编辑的 MediaWiki 站点。
> **本目录只放工具脚本**；PHP 运行时与 MediaWiki 本体**不入库**（见下「实例目录」）。

---

## 一、实例目录（不入库，可随时删除）

| 路径 | 内容 | 大小 |
|---|---|---|
| `G:\HSR\.tmp_mediawiki\php\` | PHP **8.3.35**（NTS x64，解压即用，无需系统安装） | ~30 MB |
| `G:\HSR\.tmp_mediawiki\mediawiki-1.42.5\` | MediaWiki **1.42.5** 官方发行包（含 `vendor/`） | ~180 MB |
| `G:\HSR\.tmp_mediawiki\mwdata\` | **SQLite 数据库**（`my_wiki.sqlite` 等） | ~10 MB |
| `G:\HSR\.tmp_mediawiki\export_all\` | 由 `md2mw.py` 生成的 `.wiki` + `manifest.json` | ~30 MB |
| `G:\HSR\.tmp_mediawiki\compat_backup\` | 对 MW 源码打补丁前的**原件备份** | 小 |

> `.tmp_mediawiki/` 已被 `.gitignore` 覆盖，**不入库**；删除该目录即可完全卸载（含全部补丁）。

## 二、本目录文件

| 文件 | 作用 |
|---|---|
| `md2mw.py` | 把 `zh_cn/**/*.md` 转成 MediaWiki wikitext：`# 标题`→页面标题；`> 数据来源/实体ID/数据版本/官方Wiki`→`{{实体}}` 参数（`> 创建时间/更新时间` 丢弃）；`##`→`==`；Markdown 表格→MediaWiki 表格；列表/粗斜体/外链转换；`[[zh_cn/路径\|显示]]`→`[[页面标题\|显示]]`（未收录则降级为纯文本）；**同名标题自动加「（一级目录）」后缀去重** |
| `dshImport.php` | 单进程批量导入脚本（走 MediaWiki `PageUpdater` API，数千页数分钟完成）。**放到 MediaWiki 根的 `maintenance/` 下运行** |
| `Common.css` | 瑞士风外观 → 写入 `MediaWiki:Common.css`（Helvetica 栈 / 8px 栅格 / 全直角 / 细线 / 唯一瑞士红 `#E30613` / 禁阴影渐变） |
| `Template-实体.wiki` | 通用实体信息框 `Template:实体` 源码（含**自动归类**与 `<templatedata>`） |
| `start-mediawiki.cmd` | **一键启停**：`start-mediawiki.cmd`（起）/ `stop`（停）/ `status`（查） |

## 三、常用操作

```powershell
# 0) 起站（双击亦可）
G:\HSR\.tmp_mediawiki\start-mediawiki.cmd
#    站点 http://127.0.0.1:8788/   管理员 Admin / HsrAdmin2026!

# 1) 导出（vault → .wiki）
python G:\HSR\tools\mediawiki\md2mw.py --out G:\HSR\.tmp_mediawiki\export_all

# 2) 导入（在 MediaWiki 根目录跑）
cd G:\HSR\.tmp_mediawiki\mediawiki-1.42.5
& G:\HSR\.tmp_mediawiki\php\php.exe maintenance\dshImport.php --dir="G:\HSR\.tmp_mediawiki\export_all" --user=Admin

# 3) 单页/小批（edit.php 只从 stdin 读正文，且忽略「无变化」的编辑）
cmd /c ""G:\HSR\.tmp_mediawiki\php\php.exe" maintenance\edit.php --user=Admin --summary="说明" "页面标题" < "文件.wiki""
```

## 四、环境必备（否则会报错）

1. **临时目录必须在工作区内**：跑任何 PHP 前设
   `$env:TMPDIR='G:\HSR\.tmp_mediawiki\tmp'; $env:TMP=$env:TMPDIR; $env:TEMP=$env:TMPDIR`
   （否则 MediaWiki 报「找不到可写临时目录」）
2. **`is_writable()` 兼容层**：本机 PHP 的 `is_writable()` 对**任何路径**恒返回 false（写入却正常），
   MediaWiki 多处依赖它 → 已加 `dsh_compat.php`（真实写探测）并把 MW 核心 **12 文件 / 17 处**
   的 `is_writable(` 替换为 `dsh_is_writable(`；原件备份见 `compat_backup/`。
   **重装 MediaWiki 后需重新打此补丁。**
3. `php.ini` 需启用：`pdo_sqlite` `sqlite3` `mbstring` `intl` `openssl` `fileinfo` `curl` `xml` `dom` `zlib` `sodium`；
   并设 `auto_prepend_file = "G:\HSR\.tmp_mediawiki\dsh_compat.php"`。
4. `LocalSettings.php` 需 `wfLoadExtension( 'ParserFunctions' );` 与 `wfLoadExtension( 'TemplateData' );`。
5. 端口：站点用 **8788**（`8080` 被 Steam 的 `steamwebhelper` 占用）。

## 五、已知限制

- 页面标题含 MediaWiki 非法字符 `{ } # < > [ ] |` 的源文件会被跳过 → `md2mw.py` 已对**同名**去重，
  但**非法字符**需人工净化（本库 17 个此类标题已在 2026-10-03 处理为全角形式）。
- 模板改版后**已存在页面不会自动重建分类**，需重存该页或跑 `maintenance/refreshLinks.php`。
- 站点仅作**本机演示**：`php -S` 单进程、SQLite、无上传、无缓存；不适合对外提供服务。
