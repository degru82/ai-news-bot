# use-pstack-for-coding Skill

This skill directs Cursor agents to load and follow actual pstack workflows from the installed plugin.

## What It Does

- **Automatically discovered** for substantive coding requests (features, bugs, refactoring, PR reviews)
- **Routes agent** to read real pstack SKILL.md files from installed plugin
- **Provides fallback** core principles if plugin not accessible
- **Preserves project policy** (SPEC.md, tests, lint requirements)

## What It Is NOT

- NOT a copy of pstack skills (would violate copyright)
- NOT a summary that replaces skill reading
- NOT automatic (user must install pstack plugin)

## How It Works

1. User installs pstack plugin: `/add-plugin pstack`
2. User makes coding request (no slash command needed)
3. Cursor auto-discovers this skill based on description
4. Skill directs agent to read actual poteto-mode SKILL.md from plugin cache
5. Agent follows real pstack playbooks and references other skills as directed

## Dependencies

- Requires pstack plugin installed (user action)
- Cursor: `~/.cursor/plugins/cache/cursor-public/9717366/[hash]/skills/`
- Fallback to core principles if plugin not accessible

## Upstream

- Source: https://github.com/cursor/plugins/tree/2776ddd/pstack
- License: MIT (Copyright 2026 Lauren Tan)
- This skill is a loader only, not a derivative work
