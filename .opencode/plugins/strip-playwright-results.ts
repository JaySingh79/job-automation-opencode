import type { Plugin } from "@opencode-ai/plugin"

const PLAYWRIGHT_TOOLS = new Set([
  "browser_navigate",
  "browser_navigate_back",
  "browser_navigate_back",
  "browser_click",
  "browser_hover",
  "browser_drag",
  "browser_drop",
  "browser_type",
  "browser_fill_form",
  "browser_select_option",
  "browser_press_key",
  "browser_wait_for",
  "browser_snapshot",
  "browser_take_screenshot",
  "browser_tabs",
  "browser_close",
  "browser_find",
  "browser_evaluate",
  "browser_console_messages",
  "browser_network_requests",
  "browser_resize",
])

function isPlaywrightTool(tool: string) {
  // OpenCode prefixes MCP tools with the MCP server name.
  // Example:
  //   playwright_browser_snapshot
  //
  // If your MCP server is named differently, this also handles
  // any server prefix as long as the actual tool name is in the set.
  const toolName = tool.includes("_")
    ? tool.substring(tool.indexOf("_") + 1)
    : tool

  return PLAYWRIGHT_TOOLS.has(toolName)
}

export const PlaywrightContextPrune: Plugin = async () => {
  return {
    "experimental.chat.messages.transform": async (_input, output) => {
      // Find the most recent completed Playwright tool result.
      let latestPlaywrightPart:
        | {
            type: "tool"
            state: { status: "completed"; output: string }
          }
        | undefined

      for (const message of output.messages) {
        for (const part of message.parts) {
          if (part.type !== "tool") continue
          if (!isPlaywrightTool(part.tool)) continue
          if (part.state.status !== "completed") continue

          latestPlaywrightPart = part
        }
      }

      // Remove old Playwright outputs from the model-facing context.
      for (const message of output.messages) {
        for (const part of message.parts) {
          if (part.type !== "tool") continue
          if (!isPlaywrightTool(part.tool)) continue
          if (part.state.status !== "completed") continue

          // Always preserve the latest Playwright result.
          if (part === latestPlaywrightPart) continue

          part.state.output =
            "[Previous Playwright tool result omitted from context]"
        }
      }
    },
  }
}