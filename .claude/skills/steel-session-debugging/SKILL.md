---
name: steel-session-debugging
description: Diagnose failed Steel browser sessions from logs, traces, replay artifacts, and metadata. Use when a Steel session failed, timed out, stalled, or produced unexpected output, when the user provides a session ID / replay / screenshot / log snippet, or when evidence is needed before recommending a fix.
---

# Steel Session Debugging Skill

Use Steel Session Debugging to diagnose failed Steel browser sessions from logs, traces, replay artifacts, and metadata.

## Install

```
npx skills add steel-dev/skills --skill steel-session-debugging
```

After adding the Steel Skills marketplace in Claude Code:

```
/plugin install steel-session-debugging@steel-skills
```

## Use When

- A Steel session failed, timed out, stalled, or produced unexpected output.
- The user provides a session ID, replay, screenshot, log snippet, or failure report.
- The agent needs evidence before recommending a fix.

## Example Prompts

- "Debug why Steel session `sess_123` failed after login."
- "Use the traces and logs to explain what happened in this run."
- "Classify the failure and tell me the next verification step."

## Related Skills

- Use `steel-reliability` after evidence collection when the fix is bot detection, CAPTCHA, proxy, profile identity, login persistence, pacing, or retry strategy.

## Source

https://docs.steel.dev/overview/skills/available-skills/steel-session-debugging
