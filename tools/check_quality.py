"""CI gate for the existing field checks and the tracked data-link baseline."""
import json
import pathlib
import re
import subprocess
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import verify_links


def main():
    baseline = json.loads((ROOT / "tools" / "quality_baseline.json").read_text(encoding="utf-8"))
    allowed = Counter(tuple(item) for item in baseline["dead_links"])
    actual = Counter(tuple(item) for item in verify_links.scan(str(ROOT))["dead_data_details"])
    new = actual - allowed
    resolved = allowed - actual
    print(f"数据区链接：现存 {sum(actual.values())}，基线 {sum(allowed.values())}，新增 {sum(new.values())}")
    for (source, target), count in sorted(new.items()):
        print(f"  新增 {count} 处: {source} -> {target}")
    for (source, target), count in sorted(resolved.items()):
        print(f"  基线已解决 {count} 处，可移除: {source} -> {target}")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_fields.py"), "--quality-count"],
        cwd=ROOT / "zh_cn", capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    match = re.fullmatch(r"([0-9]+)\n", result.stdout)
    if result.returncode or not match or int(match.group(1)):
        print("字段检查失败或无法识别结果", file=sys.stderr)
        # Human-readable diagnostics are untrusted text and never determine the gate.
        subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_fields.py")],
                       cwd=ROOT / "zh_cn", check=False)
        return 1
    print("字段异常合计: 0")
    if new:
        print("新增数据区失效链接", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
