# tools/git-history-scan.ps1 —— 公开前的 git 全历史安全扫描（Lead 工具）
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File tools\git-history-scan.ps1
# 扫描项：①历史大文件 ②全历史机密特征串 ③敏感文件路径 ④作者邮箱泄露 ⑤HEAD 残留
# 设计：用 `git cat-file --batch-all-objects` 单进程批处理（避免逐对象起子进程，9 万对象也不会卡）

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host '=== 0) 规模 ===' -ForegroundColor Cyan
$gitSize = (Get-ChildItem -LiteralPath "$Root\.git" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
'  .git 体积        : {0:N1} MB' -f ($gitSize / 1MB)
'  提交数           : ' + (git rev-list --all --count)
'  分支数 / 标签数  : ' + (git branch -a | Measure-Object).Count + ' / ' + (git tag | Measure-Object).Count

Write-Host "`n=== 1) 历史大文件（blob > 1 MB）===" -ForegroundColor Cyan
$tmp = Join-Path $env:TEMP 'git_objs_scan.txt'
git cat-file --batch-all-objects --batch-check='%(objecttype) %(objectname) %(objectsize)' > $tmp 2>$null
$blobs = Get-Content -LiteralPath $tmp | Where-Object { $_ -like 'blob *' } | ForEach-Object {
    $p = $_ -split ' '; [pscustomobject]@{ sha = $p[1]; size = [int64]$p[2] }
}
'  blob 总数        : ' + $blobs.Count
$big = $blobs | Where-Object { $_.size -gt 1MB } | Sort-Object size -Descending
'  >1MB 的 blob 数  : ' + ($big | Measure-Object).Count
if ($big) {
    $map = @{}
    git rev-list --objects --all 2>$null | ForEach-Object {
        $p = $_ -split ' ', 2; if ($p.Count -eq 2) { $map[$p[0]] = $p[1] }
    }
    $big | Select-Object -First 20 | ForEach-Object {
        '    {0,8:N2} MB  {1}  {2}' -f ($_.size / 1MB), $_.sha.Substring(0, 8), ($map[$_.sha] | Select-Object -First 1)
    }
}
Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue

Write-Host "`n=== 2) 全历史机密特征串 ===" -ForegroundColor Cyan
$patterns = @(
    'ghp_[A-Za-z0-9]{20,}', 'github_pat_[A-Za-z0-9_]{20,}', 'AKIA[0-9A-Z]{16}',
    'sk-[A-Za-z0-9]{20,}', 'BEGIN [A-Z ]*PRIVATE KEY', 'xox[baprs]-[A-Za-z0-9-]{10,}',
    '(?i)(api[_-]?key|passwd|password)\s*[:=]\s*[''"][^''"]{12,}'
)
$commits = git rev-list --all 2>$null
foreach ($p in $patterns) {
    $hit = git grep -I -l -E $p $commits -- 2>$null | Select-Object -First 3
    if ($hit) { "  [!] 命中 $p"; $hit | ForEach-Object { "        $_" } }
    else { "  [OK] 无命中 $p" }
}

Write-Host "`n=== 3) 敏感文件路径（历史中曾新增）===" -ForegroundColor Cyan
$added = git log --all --diff-filter=A --pretty=format: --name-only 2>$null | Sort-Object -Unique
foreach ($s in '.env', 'id_rsa', 'id_ed25519', '.pem', 'credential', '.npmrc', '.git-credentials') {
    $h = $added | Where-Object { $_ -like "*$s*" }
    if ($h) { "  [!] 曾出现 $s → " + (($h | Select-Object -First 2) -join ' , ') }
    else { "  [OK] 未出现 $s" }
}

Write-Host "`n=== 4) 历史中的作者邮箱（公开后可见）===" -ForegroundColor Cyan
git log --all --format='%ae' 2>$null | Sort-Object -Unique | ForEach-Object { '    ' + $_ }

Write-Host "`n=== 5) 大文件是否仍在 HEAD ===" -ForegroundColor Cyan
$bigPaths = @()
if ($big) {
    $map2 = @{}
    git rev-list --objects --all 2>$null | ForEach-Object { $p = $_ -split ' ', 2; if ($p.Count -eq 2) { $map2[$p[0]] = $p[1] } }
    $bigPaths = $big | ForEach-Object { $map2[$_.sha] } | Where-Object { $_ }
}
$head = git ls-files
foreach ($bp in $bigPaths) {
    if ($head -contains $bp) { "  [!] 仍在 HEAD: $bp" } else { "  [OK] 已不在 HEAD: $bp" }
}
Write-Host "`n扫描完成。" -ForegroundColor Green
