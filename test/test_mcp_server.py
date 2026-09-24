import os
import re

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def server_params():
    """
    Configure through environment variables.

    Windows defaults to npx.cmd.
    Set:
      PLAYWRIGHT_MCP_USER_DATA_DIR=C:\\path\\to\\User Data
      PLAYWRIGHT_MCP_PROFILE_DIR=Profile 1   # optional; used as an assertion
      PLAYWRIGHT_MCP_SERVER_PACKAGE=@playwright/mcp@latest
    """
    command = os.getenv("MCP_COMMAND", "npx.cmd" if os.name == "nt" else "npx")
    package = os.getenv("PLAYWRIGHT_MCP_SERVER_PACKAGE", "@playwright/mcp@latest")

    args = [package]

    user_data_dir = os.getenv("PLAYWRIGHT_MCP_USER_DATA_DIR")
    if user_data_dir:
        args += ["--user-data-dir", user_data_dir]

    # Keep this headed so you can visually confirm which browser opens.
    # Set MCP_HEADLESS=1 if you want CI/headless testing.
    if os.getenv("MCP_HEADLESS") == "1":
        args += ["--headless"]

    return StdioServerParameters(
        command=command,
        args=args,
        env=os.environ.copy(),
    )


async def connect():
    transport = stdio_client(server_params())
    streams = await transport.__aenter__()
    read, write = streams

    session = ClientSession(read, write)
    await session.__aenter__()
    await session.initialize()

    return transport, session


async def disconnect(transport, session):
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_mcp_handshake_and_tools():
    transport, session = await connect()
    try:
        result = await session.list_tools()
        names = {tool.name for tool in result.tools}

        required = {
            "browser_navigate",
            "browser_snapshot",
        }

        missing = required - names
        assert not missing, f"Missing Playwright MCP tools: {sorted(missing)}"
    finally:
        await disconnect(transport, session)


@pytest.mark.asyncio
async def test_browser_navigation_and_snapshot():
    transport, session = await connect()
    try:
        nav = await session.call_tool(
            "browser_navigate",
            {"url": "https://example.com"},
        )

        assert not getattr(nav, "isError", False), f"Navigation failed: {nav}"

        snapshot = await session.call_tool("browser_snapshot", {})
        text = str(snapshot)

        assert "Example Domain" in text, (
            "browser_snapshot did not contain expected page content.\n"
            f"Snapshot: {text[:4000]}"
        )
    finally:
        await disconnect(transport, session)


@pytest.mark.asyncio
async def test_profile_identity():
    """
    Diagnostic test for the Chrome-profile problem.

    It opens chrome://version and checks the rendered page for the configured
    user-data directory and/or profile directory.

    Note: Chrome's exact chrome://version rendering can vary by channel/version.
    If the page does not expose Profile Path through the MCP snapshot, this
    test fails with the actual snapshot so the mismatch is visible.
    """
    expected_user_data = os.getenv("PLAYWRIGHT_MCP_USER_DATA_DIR")
    expected_profile = os.getenv("PLAYWRIGHT_MCP_PROFILE_DIR")

    if not expected_user_data and not expected_profile:
        pytest.skip(
            "Set PLAYWRIGHT_MCP_USER_DATA_DIR and/or "
            "PLAYWRIGHT_MCP_PROFILE_DIR to enable profile verification."
        )

    transport, session = await connect()
    try:
        nav = await session.call_tool(
            "browser_navigate",
            {"url": "chrome://version"},
        )
        assert not getattr(nav, "isError", False), f"chrome://version failed: {nav}"

        snapshot = await session.call_tool("browser_snapshot", {})
        text = str(snapshot)

        normalized = text.replace("\\", "/").lower()

        if expected_user_data:
            expected = expected_user_data.replace("\\", "/").lower()
            # The profile path normally contains the user-data directory.
            assert expected in normalized, (
                "Configured user-data directory was not found in "
                "chrome://version output.\n\n"
                f"Expected: {expected_user_data}\n\n"
                f"Snapshot:\n{text[:12000]}"
            )

        if expected_profile:
            assert expected_profile.lower() in normalized, (
                "Configured Chrome profile directory was not found in "
                "chrome://version output.\n\n"
                f"Expected profile: {expected_profile}\n\n"
                f"Snapshot:\n{text[:12000]}"
            )
    finally:
        await disconnect(transport, session)
