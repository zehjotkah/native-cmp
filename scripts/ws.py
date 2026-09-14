"""Tiny wrapper around the Webstudio CLI MCP shortcuts."""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMP = ROOT / ".temp"


def call(tool, payload=None, dry_run=False, attempt=1, refresh=False):
    try:
        return _call_once(tool, payload, dry_run, refresh or attempt > 1)
    except RuntimeError as error:
        if tool.startswith(("list-", "get-", "verify-", "search-", "inspect-", "update-", "bind-props")) and attempt < 6 and "MCP_TOOL_FAILED" in str(error):
            import time
            time.sleep(attempt * 2)
            return call(tool, payload, dry_run, attempt + 1, True)
        raise


def _call_once(tool, payload=None, dry_run=False, refresh=False):
    TEMP.mkdir(exist_ok=True)
    args = ["npx", "--yes", "webstudio@latest", tool]
    if payload is not None:
        path = TEMP / f"call-{tool}.json"
        path.write_text(json.dumps(payload))
        args += ["--input-file", str(path)]
    if dry_run:
        args.append("--dry-run")
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(result.stderr[-2000:])
        raise
    if not data.get("ok"):
        raise RuntimeError(f"{tool} failed: {json.dumps(data.get('error'))[:3000]}")
    warnings = [d for d in data.get("meta", {}).get("session", {}).get("diagnostics", []) if d.get("level") not in ("info",)]
    if warnings:
        print(f"[{tool}] diagnostics:", json.dumps(warnings)[:2000])
    return data["data"]


def instances(page_path, max_depth=20):
    items, cursor = [], None
    while True:
        payload = {"pagePath": page_path, "maxDepth": max_depth, "limit": 200}
        if cursor:
            payload["cursor"] = cursor
        data = call("list-instances", payload)
        items += data["instances"]
        cursor = data.get("nextCursor")
        if not cursor:
            return items


def tokens():
    """All design tokens as {name: id} (paged)."""
    out, cursor = {}, None
    while True:
        payload = {"limit": 200}
        if cursor:
            payload["cursor"] = cursor
        data = call("list-design-tokens", payload)
        out.update({t["name"]: t["id"] for t in data["tokens"]})
        cursor = data.get("nextCursor")
        if not cursor:
            return out
