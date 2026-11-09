import type { Plugin } from "@opencode-ai/plugin"

export default (async () => {
  return {
    "experimental.chat.system.transform": async (_input, output) => {
      await Bun.write(
        ".opencode/system-prompt.md",
        output.system.join("\n\n")
      )
    },
  }
}) satisfies Plugin
