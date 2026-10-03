@echo off
REM ============================================================
REM  HSR 本地 MediaWiki 一键启动 / 停止
REM  实例位置：G:\HSR\.tmp_mediawiki（未入库，可整个删除）
REM  站点：http://127.0.0.1:8788/
REM  管理员：Admin / HsrAdmin2026!
REM ============================================================
setlocal
set BASE=G:\HSR\.tmp_mediawiki
set PHP=%BASE%\php\php.exe
set MW=%BASE%\mediawiki-1.42.5
set PORT=8788

if /I "%~1"=="stop" goto :stop
if /I "%~1"=="status" goto :status

:start
echo [1/3] 检查是否已在运行...
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }"
if errorlevel 1 (
  echo     端口 %PORT% 已被占用（可能已在运行）。想看状态请执行：%~nx0 status
  goto :eof
)

echo [2/3] 设置临时目录（须在工作区内，否则 MediaWiki 报「找不到可写临时目录」）...
set TMPDIR=%BASE%\tmp
set TMP=%BASE%\tmp
set TEMP=%BASE%\tmp
if not exist "%TMPDIR%" mkdir "%TMPDIR%"

echo [3/3] 启动 MediaWiki（窗口保持打开即为运行中，关闭窗口即停止）...
echo.
echo     站点地址： http://127.0.0.1:%PORT%/
echo     管理员：   Admin / HsrAdmin2026!
echo.
"%PHP%" -S 127.0.0.1:%PORT% -t "%MW%"
goto :eof

:stop
echo 停止占用 %PORT% 端口的进程...
powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($c) { $c | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force; Write-Host ('  已停止 PID ' + $_.OwningProcess) } } else { Write-Host '  没有进程在监听该端口' }"
goto :eof

:status
powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue; if ($c) { Write-Host ('运行中，PID ' + $c.OwningProcess) } else { Write-Host '未运行' }"
goto :eof
