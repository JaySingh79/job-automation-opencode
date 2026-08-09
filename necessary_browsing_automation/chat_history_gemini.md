# Full Technical Discussion & Reference Guide

This document contains the complete record of the conversation, research, setup instructions, architecture designs, and technical guides covering:
1. **Best Memory Skills & MCP Servers for Claude (Sorted by Stars)**
2. **Setup Guide for `@modelcontextprotocol/server-memory`**
3. **MCP Data Exchange & Transport Mechanics (JSON-RPC over HTTP/SSE & stdio)**
4. **Security, Privacy, and Performance of Local Knowledge Graphs**
5. **Firecrawl Alternatives (Open-Source & High-Credit Cloud APIs)**
6. **Bypassing LinkedIn Anti-Bot Protections & Cookie/Proxy Management**
7. **Automating LinkedIn Easy Apply Pipeline with Claude Code & Cloud Browsers**

---

## 1. Best Memory Skills for Claude on GitHub (Sorted by Stars)

| Rank | Repository | Stars (Approx.) | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| **1** | [**`modelcontextprotocol/servers`**](https://github.com/modelcontextprotocol/servers) | **~89,000+** | Official MCP | The official Anthropic Model Context Protocol repository containing `@modelcontextprotocol/server-memory`, an open-source **Knowledge Graph memory server** designed for persistent entity and relation memory. |
| **2** | [**`thedotmack/claude-mem`**](https://github.com/thedotmack/claude-mem) | **~89,000+** | Claude Skill / MCP | Dedicated persistent context plugin and memory server specifically designed for Claude Code and Claude Desktop. Captures background session output and injects relevant context automatically. |
| **3** | [**`mem0ai/mem0`**](https://github.com/mem0ai/mem0) | **~62,000+** | Memory Framework / MCP | Universal long-term memory layer for AI agents. Provides adaptive, user-specific, and session-aware memory with native Claude API and MCP integration. |
| **4** | [**`alirezarezvani/claude-skills`**](https://github.com/alirezarezvani/claude-skills) | **~23,000+** | Skill Collection | Large collection of curated skills and prompt modules for Claude, including cross-session context retainers and project memory templates. |
| **5** | [**`getzep/graphiti`**](https://github.com/getzep/graphiti) | **~20,000+** | Knowledge Graph | Temporal knowledge graph framework for building dynamic agent memory for Claude, allowing LLMs to update, search, and manage evolving facts over time. |
| **6** | [**`adamkwhite/claude-memory-mcp`**](https://github.com/adamkwhite/claude-memory-mcp) | Community Favorite | MCP Server | Sub-millisecond full-text search and memory storage system built for Claude Code and Cursor with low overhead. |
| **7** | [**`mkreyman/mcp-memory-keeper`**](https://github.com/mkreyman/mcp-memory-keeper) | Community Favorite | MCP Server | Persistent context keeper optimized for multi-file refactoring and long programming sessions with per-project isolation. |
| **8** | [**`hanfang/claude-memory-skill`**](https://github.com/hanfang/claude-memory-skill) | Lightweight | File-based Skill | Minimalist, low-friction file-system memory skill that maintains hierarchical project summaries and notes across Claude runs. |

---

## 2. Setup Guide for `modelcontextprotocol/servers` (`server-memory`)

### Prerequisites
- Node.js (v18 or higher): Verify with `node -v`.

### Option A: Claude Desktop Setup

1. Open or create your `claude_desktop_config.json`:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Add the configuration block:
   ```json
   {
     "mcpServers": {
       "memory": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-memory"
         ],
         "env": {
           "MEMORY_FILE_PATH": "C:/Users/YOUR_USERNAME/.claude/memory.json"
         }
       }
     }
   }
   ```
3. Restart Claude Desktop completely.

### Option B: Claude Code CLI Setup
Register the server globally via terminal:
```bash
claude mcp add --scope global memory -e MEMORY_FILE_PATH=~/.claude/memory.json -- npx -y @modelcontextprotocol/server-memory
```

### Option C: Cursor / Windsurf / Roo Code Setup
Add to your editor's `mcp.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "/absolute/path/to/your/memory.json"
      }
    }
  }
}
```

---

## 3. MCP Data Exchange & Transport Mechanics

### Transport Layers
- **Local (`stdio`):** Default for subprocess execution. Uses standard input/output pipes with newline-delimited JSON-RPC messages.
- **Remote (`HTTP + SSE`):**
  - **Client -> Server:** `HTTP POST` requests (`Content-Type: application/json`).
  - **Server -> Client:** `HTTP GET` streaming via `Server-Sent Events` (`Accept: text/event-stream`).

### Data Message Format (JSON-RPC 2.0)
All payload exchanges follow standard JSON-RPC 2.0 format:
- **Handshake (`initialize`):** Protocol version negotiation, client/server capabilities.
- **Tool Registration (`tools/list`):** Exposes schemas (`create_entities`, `create_relations`, `read_graph`, `search_nodes`).
- **Tool Execution Request (`tools/call`):**
  ```json
  {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "create_entities",
      "arguments": {
        "entities": [
          {
            "name": "PortRL Project",
            "entityType": "Software",
            "observations": ["Uses Python 3.12"]
          }
        ]
      }
    }
  }
  ```

---

## 4. Security, Privacy, and Performance of Knowledge Graphs

### Security Architecture
1. **Local Storage:** The graph file (`memory.json`) remains on your local disk.
2. **No Exposed Network Ports:** Local `stdio` mode creates no web listener or open HTTP ports.
3. **API Privacy:** Data sent to Anthropic API is protected under Commercial Data Privacy terms (not used for model training).

### Latency Performance
- **Local Graph Lookup:** ~1ms to 5ms (Loaded into Node.js RAM).
- **Anthropic API Network Hop:** ~200ms to 500ms.
- **LLM Text Generation:** ~1000ms to 3000ms.
- **Conclusion:** Local JSON lookup adds negligible latency (< 1% of response time).

---

## 5. Firecrawl Alternatives (Open-Source & High-Credit Cloud APIs)

| Tool | Hosting Model | Pricing / Credit Limit | Key Strengths |
| :--- | :--- | :--- | :--- |
| **Crawl4AI** | Open-Source (Docker) | **Unlimited** (Self-hosted) | #1 Open-Source alternative; Playwright JS rendering, LLM chunking/extraction, markdown output. |
| **Spider.cloud** | Cloud API + Open Source (Rust) | Pay-as-you-go (~100x cheaper) | Ultra-fast Rust engine, `/crawl` and `/scrape` endpoints, anti-bot bypass, high volume scaling. |
| **Steel.dev** | Open-Source / Cloud | **Unlimited** (Self-hosted) | Purpose-built Cloud Browser infrastructure for AI agent browser sessions. |
| **Jina Reader** | Cloud API (`r.jina.ai`) | ~1M free tokens/mo | Simple URL prefix to markdown converter (`r.jina.ai/URL`). |

---

## 6. Bypassing LinkedIn Anti-Bot Protections

### Why Standard Scrapers Fail on LinkedIn
1. **Authwall:** Forces login for profiles and company pages.
2. **HTTP 999:** Custom anti-bot status code block.
3. **Fingerprinting:** Analyzes TLS fingerprints, Canvas, WebGL, and `navigator.webdriver`.

### Solutions & How to Extract `li_at` Cookie

#### How to Get `li_at` Cookie:
1. Log in to [linkedin.com](https://www.linkedin.com).
2. Press **F12** to open Developer Tools.
3. Go to **Application** tab -> **Cookies** -> `https://www.linkedin.com`.
4. Copy the value of the **`li_at`** cookie.

#### Proxy String Structure:
```python
proxy = "http://username:password@proxy-server-address:port"
```

#### High-Volume Architecture Principles:
- **Never use 1 cookie across 1000 IPs:** Single account session sending requests from multiple IPs simultaneously gets banned.
- **Cookie + IP Pairing (Sticky Sessions):** Pair 1 account cookie with 1 static residential IP.
- **Rate Limits:** Keep request rates human-like (2–5 requests/min per account with random jitter).

---

## 7. Automating LinkedIn Easy Apply with Claude Code & Cloud Browsers

### Pipeline Components
1. **Claude Code / Agent:** Formulates job search criteria, evaluates job descriptions, generates screening answers.
2. **Cloud Browser (Steel.dev / Browserbase):** Manages headless Playwright browser sessions with persistent `li_at` cookies and stealth plugins.
3. **Knowledge Base (`profile.json`):** User resume data, skills, work history, and standard screening Q&A defaults.
4. **Tracker DB:** Logs applied Job IDs to prevent duplicate applications.

### Sample Playwright Automation Snippet
```python
import asyncio
from playwright.async_api import async_playwright

STEEL_CONNECT_URL = "wss://connect.steel.dev?apiKey=YOUR_STEEL_API_KEY"

async def run_easy_apply_pipeline():
    async with async_playwright() as p:
        # Connect to remote cloud browser
        browser = await p.chromium.connect_over_cdp(STEEL_CONNECT_URL)
        context = await browser.new_context()

        # Inject session cookie
        await context.add_cookies([{
            "name": "li_at",
            "value": "YOUR_LI_AT_COOKIE",
            "domain": ".www.linkedin.com",
            "path": "/"
        }])

        page = await context.new_page()
        
        # Navigate to Easy Apply search
        await page.goto("https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&f_AL=true")
        await page.wait_for_selector(".jobs-search-results-list")

        # Parse jobs and execute application steps...
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_easy_apply_pipeline())
```
