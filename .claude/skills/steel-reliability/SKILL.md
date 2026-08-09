---
name: steel-reliability
description: Handle Steel bot-detection, CAPTCHA, proxy, identity, login persistence, pacing, and retry strategy. Use when a site returns 403 / access-denied / verify-human pages, CAPTCHA solving loops, proxy behavior needs diagnosis, or login/profile/credential/pacing/retry policy affects success.
---

# Steel Reliability Skill

Use Steel Reliability for bot-detection, CAPTCHA, proxy, identity, login persistence, pacing, and retry strategy.

## Install

```
npx skills add steel-dev/skills --skill steel-reliability
```

After adding the Steel Skills marketplace in Claude Code:

```
/plugin install steel-reliability@steel-skills
```

## Use When

- A site returns 403, access denied, verify-human pages, or redirect loops.
- CAPTCHA solving fails in loops.
- Steel-managed proxy or BYOP proxy behavior needs diagnosis.
- Login state, profiles, credentials, identity, pacing, or retry policy affects success.

## Example Prompts

- "Plan the least invasive mitigation for this 403."
- "Show me a safe BYOP pattern on Hobby."
- "Should this login workflow use profiles, credentials, or both?"

## Related Skills

- Use `steel-session-debugging` first when the failure class is unknown and you need logs, traces, replay links, or screenshots.

## Source

https://docs.steel.dev/overview/skills/available-skills/steel-reliability
