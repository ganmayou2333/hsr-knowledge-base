# -*- coding: utf-8 -*-
"""
MCP 服务自测（零依赖）

用法：
    python mcp/python/selftest.py            # 全量自测
    python mcp/python/selftest.py kb_status  # 只调某个工具

它会以子进程方式启动 hsr_mcp_server.py，走 stdio 发 JSON-RPC，
依次验证：initialize → tools/list → 每个只读工具各调一次。
"""
import json
import subprocess
import sys
from pathlib import Path

SERVER = Path(__file__).with_name("hsr_mcp_server.py")

CALLS = [
    ("kb_status", {"prefix": "zh_cn"}),
    ("kb_list", {"pattern": "docs/prompts/*.md"}),
    ("kb_read", {"path": "README.md", "limit": 5}),
    ("kb_search", {"query": "数据版本：4.6", "path": "zh_cn/character", "limit": 3}),
    ("kb_missing_fields", {"path": "zh_cn/items"}),
    ("kb_validate_links", {"path": "zh_cn/relic", "limit": 5}),
    ("kb_validate_fields", {"path": "zh_cn/character"}),
    ("kb_spec_section", {"heading": "文件命名规范"}),
    ("kb_prompt_modules", {}),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    p = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", bufsize=1,
    )

    def rpc(obj):
        p.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
        p.stdin.flush()
        line = p.stdout.readline()
        if not line:
            raise RuntimeError("服务端无响应（可能启动失败）：" + (p.stderr.read() or ""))
        return json.loads(line)

    try:
        init = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "selftest", "version": "1.0"}}})
        info = init.get("result", {}).get("serverInfo", {})
        caps = init.get("result", {}).get("capabilities", {})
        print(f"[1] initialize ✅ {info.get('name')} v{info.get('version')} 能力={sorted(caps)}")

        tools = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}).get("result", {}).get("tools", [])
        print(f"[2] tools/list ✅ 共 {len(tools)} 个工具：{', '.join(t['name'] for t in tools)}")

        for i, (name, args) in enumerate(CALLS, start=3):
            if only and name != only:
                continue
            res = rpc({"jsonrpc": "2.0", "id": i, "method": "tools/call",
                       "params": {"name": name, "arguments": args}})
            content = res.get("result", {}).get("content", [{}])
            text = content[0].get("text", "") if content else ""
            flag = "⚠️ isError" if res.get("result", {}).get("isError") else "✅"
            head = text.splitlines()[0] if text else "(空)"
            print(f"[{i}] {name} {flag} {head[:80]}")

        res = rpc({"jsonrpc": "2.0", "id": 90, "method": "resources/list"}).get("result", {}).get("resources", [])
        print(f"[90] resources/list ✅ {len(res)} 个资源")
        if res:
            got = rpc({"jsonrpc": "2.0", "id": 91, "method": "resources/read",
                       "params": {"uri": res[0]["uri"]}})
            n = len(got.get("result", {}).get("contents", [{}])[0].get("text", ""))
            print(f"[91] resources/read ✅ {res[0]['uri']} → {n} 字符")

        pr = rpc({"jsonrpc": "2.0", "id": 92, "method": "prompts/list"}).get("result", {}).get("prompts", [])
        print(f"[92] prompts/list ✅ {len(pr)} 个提示词：{', '.join(x['name'] for x in pr)}")
        if pr:
            got = rpc({"jsonrpc": "2.0", "id": 93, "method": "prompts/get",
                       "params": {"name": pr[0]["name"]}})
            n = len(got.get("result", {}).get("messages", [{}])[0].get("content", {}).get("text", ""))
            print(f"[93] prompts/get ✅ {pr[0]['name']} → {n} 字符")

        print("\n自测完成。")
    finally:
        try:
            p.stdin.close()
        except Exception:
            pass
        p.terminate()


if __name__ == "__main__":
    main()
