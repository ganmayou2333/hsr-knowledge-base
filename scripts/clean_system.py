# -*- coding: utf-8 -*-
"""
Windows 系统垃圾清理工具（安全版）
清理：用户临时目录 / Windows 临时目录 / 回收站 / 浏览器缓存 / 项目临时文件
不碰系统关键文件，失败项自动跳过并报告。
用法：python clean_system.py [--dry-run] [--project <项目目录>]
      --project 默认取脚本所在仓库根目录（跨平台；不再硬编码 Windows 盘符路径）
"""
import os, sys, shutil, subprocess, argparse, ctypes
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 本脚本的「清空回收站」一步只对 Windows 有意义（用 Shell.Application COM）。
# 其它平台（Linux/WSL/macOS）没有回收站概念 → 该步整体降级跳过，其余清理照常。
IS_WINDOWS = os.name == 'nt'

def is_admin():
    if not IS_WINDOWS:
        return os.geteuid() == 0
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def dir_size(path):
    """计算目录大小（字节），失败返回 0"""
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
    except:
        pass
    return total

def clean_dir(path, label, dry_run=False):
    """清理目录下所有内容，保留目录本身"""
    path = Path(path)
    if not path.exists():
        print(f'  [跳过] {label}: 路径不存在')
        return 0
    before = dir_size(str(path))
    removed = 0
    errors = 0
    try:
        for item in path.iterdir():
            try:
                if dry_run:
                    removed += 1
                    continue
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=False)
                else:
                    item.unlink()
                removed += 1
            except Exception as e:
                errors += 1
    except Exception as e:
        print(f'  [错误] {label}: {e}')
    after = dir_size(str(path))
    freed = before - after
    print(f'  [完成] {label}: 清理 {removed} 项, 释放 {freed/1024/1024:.1f} MB' + (f', 失败 {errors} 项' if errors else ''))
    return freed

def clean_recycle_bin(dry_run=False):
    """清空回收站（仅 Windows；其它平台无此概念，整体跳过）"""
    if not IS_WINDOWS:
        print('  [跳过] 回收站: 当前平台无回收站概念（仅 Windows 适用）')
        return 0
    if dry_run:
        print('  [预览] 回收站: 将清空')
        return 0
    try:
        # 使用 Shell.Application COM 对象清空回收站，避免 PowerShell 交互问题
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             '(New-Object -ComObject Shell.Application).NameSpace(0xA).Items() | ForEach-Object { $_.InvokeVerb("delete") }'],
            capture_output=True, text=True, timeout=60
        )
        print('  [完成] 回收站: 已清空')
        return 0
    except subprocess.TimeoutExpired:
        print('  [跳过] 回收站: 操作超时')
        return 0
    except Exception as e:
        print(f'  [跳过] 回收站: {e}')
        return 0

def clean_browser_cache(dry_run=False):
    """清理 Chrome / Edge 缓存"""
    total = 0
    local = os.environ.get('LOCALAPPDATA', '')
    browsers = [
        ('Chrome', os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default', 'Cache')),
        ('Chrome Code Cache', os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache')),
        ('Edge', os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')),
        ('Edge Code Cache', os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Default', 'Code Cache')),
    ]
    for name, path in browsers:
        total += clean_dir(path, f'浏览器缓存-{name}', dry_run)
    return total

def main():
    parser = argparse.ArgumentParser(description='Windows 系统垃圾清理工具')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际删除')
    parser.add_argument('--project', default=str(Path(__file__).resolve().parent.parent),
                        help='项目目录（清理其临时文件）；默认 = 本脚本所在仓库根目录')
    args = parser.parse_args()

    print('=' * 50)
    print('Windows 系统垃圾清理工具' + ('（预览模式，不实际删除）' if args.dry_run else ''))
    print(f'管理员权限: {"是" if is_admin() else "否（部分系统目录可能无法清理）"}')
    print('=' * 50)

    total_freed = 0

    print('\n[1/6] 用户临时目录')
    total_freed += clean_dir(os.environ.get('TEMP', ''), '用户临时目录 %TEMP%', args.dry_run)

    print('\n[2/6] Windows 临时目录')
    total_freed += clean_dir(r'C:\Windows\Temp', 'Windows 临时目录', args.dry_run)

    print('\n[3/6] 回收站')
    total_freed += clean_recycle_bin(args.dry_run)

    print('\n[4/6] 浏览器缓存（Chrome / Edge）')
    total_freed += clean_browser_cache(args.dry_run)

    print('\n[5/6] Windows 更新缓存（需管理员）')
    if is_admin():
        total_freed += clean_dir(r'C:\Windows\SoftwareDistribution\Download', 'Windows 更新缓存', args.dry_run)
    else:
        print('  [跳过] 需要管理员权限，未清理')

    print('\n[6/6] 项目临时文件')
    proj = Path(args.project)
    if proj.exists():
        for tmpdir in ['.tmp_build', 'temp', '__pycache__']:
            total_freed += clean_dir(str(proj / tmpdir), f'项目临时-{tmpdir}', args.dry_run)
    else:
        print(f'  [跳过] 项目目录不存在: {proj}')

    print('\n' + '=' * 50)
    print(f'清理完成，共释放约 {total_freed/1024/1024:.1f} MB' + ('（预览模式，实际未删除）' if args.dry_run else ''))
    print('=' * 50)

if __name__ == '__main__':
    main()
