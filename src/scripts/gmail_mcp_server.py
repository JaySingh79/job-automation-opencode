"""Convenience CLI launcher for the Gmail Automation MCP Server (`src/scripts/gmail_mcp_server.py`)."""

from __future__ import annotations

import sys

from src.scripts.gmail_mcp.server import main

if __name__ == "__main__":
    sys.exit(main())
