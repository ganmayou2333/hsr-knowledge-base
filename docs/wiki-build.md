# Wiki 干净检出构建与验证

Wiki 页面和索引在本地生成，不随仓库分发。生成器会读取构建工作区中的 `data/zh_cn/` Markdown；被忽略但实际存在的文件也会参与构建。不要将含本机忽略文件的页面数当成线上或干净检出的页面数。历史统计的时间和口径见 [metrics.md](metrics.md)。

下列构建与检查使用 Python 标准库，无需安装第三方 Python 包；浏览器交互测试和 CI 完整环境另见 [wiki/README.md](../wiki/README.md)。

在仓库根目录、干净检出中运行（Python 3；项目 CI 使用 3.11）：

```sh
python wiki/copy_icons.py
python wiki/build_wiki.py
python tools/check_quality.py
python tools/verify_site.py
python tools/verify_docs.py
```

`copy_icons.py` 从 `StarRailRes-master/icon` 或 `.srr/icon` 读取图标；干净检出没有这两个目录时，它会提示并跳过，生成的站点使用缺图占位。**已有构建目录可能保留旧图标**：无图标复现应使用新检出，不要把跳过复制当作已清除旧文件。正式 Pages 和 PR 构建工作流另行拉取 StarRailRes 的固定提交 `dbe8cdfcfb0bf657b9fe1cf92d5537f118ccb487`；下载失败会使对应工作流失败，不会证明带图标构建成功。图标取不到时，以上无图标构建仍可用，但不能据此验证带图标的展示。

## 一次干净检出记录

2026-11-21，在 Windows、Python 3.14.9、干净检出的提交 `f493e20bdf7c15d54dc19f5e9ed5bb291f6a25b4` 上，未提供图标源：复制步骤提示跳过；构建生成 6,517 个页面，站点报告死链 0、未收录 32（降级为文本）；质量检查、站点检查和文档检查通过。站点检查独立复算的页面、搜索标题和报告数量一致。此记录仅证明该输入和环境下的无图标构建；CI 的不同 Python 版本及带图标构建须以其实际运行结果为准。

2026-11-27，在 Windows、Python 3.14.9、干净工作树的 `main` 提交 `a1461fbbdff86dd99f12847b85097de5426eaed9` 上重复上述步骤：无图标源，复制步骤跳过；构建 6,517 页，搜索标题 6,517 条；站点报告与独立复算均为死链 0、未收录 32；数据区双链现存 0、基线 0，字段异常 0，质量、站点和文档检查均通过。此记录不覆盖图标展示或完整浏览器交互检查。

构建输出包含生成时间等环境相关内容，不承诺全目录逐字节一致。比较应先固定提交和输入文件，并对照页面与索引数量、死链和未收录报告，再针对需求核查具体页面。外部图标、被忽略文件、运行环境和生成时间均可能影响结果。

PR 预览产物下载重试与排查记录见 [preview-artifact-diagnostics.md](preview-artifact-diagnostics.md)。
