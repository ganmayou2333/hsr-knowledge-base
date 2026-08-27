$ErrorActionPreference = 'Continue'
$dir = 'G:/HSR/StarRailRes_data'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Set-Location $dir

$files = @(
    'characters.json',
    'character_ranks.json',
    'character_skills.json',
    'character_skill_trees.json',
    'character_promotions.json'
)

$sources = @(
    { param($f) "https://cdn.jsdelivr.net/gh/Mar-7th/StarRailRes@main/index_new/cn/$f" },
    { param($f) "https://raw.githubusercontent.com/Mar-7th/StarRailRes/main/index_new/cn/$f" },
    { param($f) "https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/index_new/cn/$f" }
)

foreach ($f in $files) {
    $ok = $false
    foreach ($src in $sources) {
        $url = & $src $f
        Write-Output "Trying $url"
        curl.exe -sL --max-time 60 -o $f $url
        if ((Test-Path $f) -and (Get-Item $f).Length -gt 1000) {
            $ok = $true
            Write-Output "OK $f -> $((Get-Item $f).Length) bytes"
            break
        } else {
            Write-Output "FAIL $url"
        }
    }
    if (-not $ok) { Write-Output "ALL-SOURCES-FAILED $f" }
}
Write-Output "=== DONE ==="
Get-ChildItem | Select-Object Name, Length | Format-Table -AutoSize
