---
name: steel-skill-creator
description: Turn recurring browser workflows into reusable, parameterized agent workflows. Use when the user repeats the same browser task, the task has clear inputs and success criteria, and the agent can safely record the task twice in Steel to package a repeatable workflow.
---

# Steel Skill Creator

Use Steel Skill Creator to turn recurring browser workflows into reusable agent workflows.

## Install

```
npx skills add steel-dev/skills --skill steel-skill-creator
```

After adding the Steel Skills marketplace in Claude Code:

```
/plugin install steel-skill-creator@steel-skills
```

## Use When

- The user repeats the same browser task.
- The task has clear inputs and success criteria.
- The agent can safely record the task twice in Steel.
- You want a repeatable workflow the agent can run again later.

## Example Prompts

- "Turn this weekly report download into a reusable workflow."
- "Capture this search workflow twice and make it parameterized."
- "Package this repeated browser task so the agent can run it again next week."

## Related Skills

- Use `steel-browser` to drive recording sessions.
- Use `steel-session-debugging` for failed recordings.
- Use `steel-reliability` for bot/proxy/CAPTCHA reliability issues.

## Source

https://docs.steel.dev/overview/skills/available-skills/steel-skill-creator
