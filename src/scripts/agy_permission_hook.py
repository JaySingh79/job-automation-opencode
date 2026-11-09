#!/usr/bin/env python3
"""Antigravity PreToolUse permission hook enforcing .opencode/opencode.json parity.

Reads the Antigravity PreToolUse JSON payload from stdin and outputs a JSON
decision ("allow", "ask", or "deny") to stdout.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


def _normalize(path_str: str) -> str:
    try:
        resolved = str(Path(path_str).resolve())
    except Exception:
        resolved = path_str
    return resolved.replace("\\", "/").lower()


def _check_file_permission(tool_name: str, target_path: str) -> dict[str, str]:
    if not target_path:
        return {"decision": "allow"}

    norm = _normalize(target_path)
    basename = os.path.basename(norm)

    # Explicit allow from opencode.json: "*.env.example": "allow"
    if basename == ".env.example":
        return {"decision": "allow"}

    # Explicit denies from opencode.json:
    # "*.env", "*.env.*", "*.pem", "*.key", "**/secrets/**", "*/runs/**", "**/opencode.json"
    if (
        basename == ".env"
        or basename.startswith(".env.")
        or fnmatch.fnmatch(basename, "*.env")
        or fnmatch.fnmatch(basename, "*.pem")
        or fnmatch.fnmatch(basename, "*.key")
    ):
        return {
            "decision": "deny",
            "reason": f"Access to secret/key file '{basename}' is denied by workspace permission policy.",
        }

    if "/secrets/" in norm or norm.endswith("/secrets"):
        return {
            "decision": "deny",
            "reason": "Access to '**/secrets/**' is denied by workspace permission policy.",
        }

    if "/runs/" in norm or norm.endswith("/runs"):
        return {
            "decision": "deny",
            "reason": "Access to '*/runs/**' is strictly denied by workspace permission policy.",
        }

    if basename == "opencode.json":
        return {
            "decision": "deny",
            "reason": "Access to '**/opencode.json' is denied by workspace permission policy.",
        }

    # External directory protection ("external_directory": "deny", "../**": "deny")
    ws_norm = _normalize(str(WORKSPACE_ROOT))
    if not norm.startswith(ws_norm):
        # Allow Antigravity brain/artifact/builtin directories under .gemini
        if "/.gemini/" in norm:
            return {"decision": "allow"}
        return {
            "decision": "deny",
            "reason": f"External directory access outside workspace ({WORKSPACE_ROOT}) is denied.",
        }

    return {"decision": "allow"}


def _check_command_permission(command_line: str) -> dict[str, str]:
    if not command_line:
        return {"decision": "allow"}

    cmd = command_line.strip()
    if re.search(r"\bgit\s+config\s+--global\s+user\.(name|email)\b", cmd, re.IGNORECASE):
        return {
            "decision": "ask",
            "reason": "Modifying global git user.name or user.email requires explicit confirmation.",
        }

    return {"decision": "allow"}


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw)
        tool_call = payload.get("toolCall") or {}
        tool_name = (tool_call.get("name") or "").lower()
        args = tool_call.get("args") or {}

        if tool_name in {
            "view_file",
            "write_to_file",
            "replace_file_content",
            "multi_replace_file_content",
        }:
            target = (
                args.get("AbsolutePath")
                or args.get("TargetFile")
                or args.get("path")
                or ""
            )
            result = _check_file_permission(tool_name, str(target))
            print(json.dumps(result))
            return

        if tool_name == "run_command":
            cmd = args.get("CommandLine") or args.get("command") or ""
            result = _check_command_permission(str(cmd))
            print(json.dumps(result))
            return

        print(json.dumps({"decision": "allow"}))
    except Exception:
        # Never block execution on unexpected hook parsing errors
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
