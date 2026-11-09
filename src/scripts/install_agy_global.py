#!/usr/bin/env python3
"""Safe installer to sync .agents/global_config/* into ~/.gemini/ for Antigravity."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
GLOBAL_TEMPLATE_DIR = WORKSPACE_ROOT / ".agents" / "global_config"
HOME_GEMINI = Path.home() / ".gemini"


def _backup(path: Path) -> None:
    if path.is_file():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_suffix(f"{path.suffix}.bak_{stamp}")
        shutil.copy2(path, backup_path)
        print(f"[backup] {path} -> {backup_path}")


def _merge_json(src_path: Path, dst_path: Path) -> None:
    src_data = json.loads(src_path.read_text(encoding="utf-8"))
    if dst_path.is_file():
        try:
            dst_data = json.loads(dst_path.read_text(encoding="utf-8"))
        except Exception:
            dst_data = {}
    else:
        dst_data = {}

    # Deep merge 1 level for userSettings / mcpServers / plugins
    for k, v in src_data.items():
        if isinstance(v, dict) and isinstance(dst_data.get(k), dict):
            for sub_k, sub_v in v.items():
                dst_data[k][sub_k] = sub_v
        else:
            dst_data[k] = v

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    _backup(dst_path)
    dst_path.write_text(json.dumps(dst_data, indent=2) + "\n", encoding="utf-8")
    print(f"[installed] {dst_path}")


def main() -> None:
    config_dir = HOME_GEMINI / "config"
    cli_dir = HOME_GEMINI / "antigravity-cli"
    config_dir.mkdir(parents=True, exist_ok=True)
    cli_dir.mkdir(parents=True, exist_ok=True)

    # 1. Global GEMINI.md
    src_gemini = GLOBAL_TEMPLATE_DIR / "GEMINI.md"
    for dst_gemini in (HOME_GEMINI / "GEMINI.md", config_dir / "GEMINI.md"):
        _backup(dst_gemini)
        shutil.copy2(src_gemini, dst_gemini)
        print(f"[installed] {dst_gemini}")

    # 2. Global config.json (permissions & plugins)
    _merge_json(GLOBAL_TEMPLATE_DIR / "config.json", config_dir / "config.json")

    # 3. Global mcp_config.json
    _merge_json(GLOBAL_TEMPLATE_DIR / "mcp_config.json", config_dir / "mcp_config.json")

    # 4. CLI settings.json
    _merge_json(GLOBAL_TEMPLATE_DIR / "settings.json", cli_dir / "settings.json")

    print("\nGlobal Antigravity configuration successfully synced!")


if __name__ == "__main__":
    main()
