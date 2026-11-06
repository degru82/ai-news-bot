---
name: use-pstack-for-coding
description: For substantive coding work (features, refactoring, bug fixes, PR reviews) in this project, load and follow pstack workflows from the installed plugin. Automatically applies to coding requests.
---

# Use pstack for Coding in ai-news-bot

For substantive coding work (features, refactoring, bug fixes, PR reviews), **read and follow the actual pstack skills** from the installed plugin.

## Plugin Installation Required

**User must install pstack plugin first** (one-time per environment):

- Cursor: `/add-plugin pstack` then `/setup-pstack`
- Claude Code: `/plugin marketplace add cursor/plugins`, `/plugin install pstack@cursor-plugins`, `/pstack:setup-pstack`  
- Grok Bot: Plugin may be available depending on account configuration

Without installation, you cannot access the full skill files. This project skill provides routing only.

## Skill Loading Instructions

### For Cursor Agents

When you receive a substantive coding request (bug fix, feature, refactoring, PR review):

1. **Read the actual pstack poteto-mode skill**: The installed pstack plugin provides skills at `~/.cursor/plugins/cache/cursor-public/9717366/[hash]/skills/poteto-mode/SKILL.md` or similar plugin cache location.

2. **Follow its playbook selection logic**: poteto-mode matches the task to a playbook (bug-fix, feature, refactoring, etc.) and provides step-by-step instructions.

3. **Read referenced skills**: As the playbook directs, read supporting skills like `/how`, `/why`, `/interrogate`, and principle skills.

4. **If pstack plugin is not installed or not found**: Apply the core principles below as fallback, but note the limitation to the user.

### For Claude Code Agents

Read and apply guidance from CLAUDE.md which provides:
- pstack installation instructions
- Core principles extracted from upstream
- Project-specific requirements

Claude Code agents: prefix pstack commands with `/pstack:` (e.g., `/pstack:poteto-mode`).

### For Grok Bot and Other Tools

Read project instructions from CLAUDE.md and apply documented principles. Full pstack workflows may not be available without native plugin support.

## Core Principles (Fallback Only)

If you cannot access the actual pstack skills, apply these extracted principles from pstack (upstream: https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack):

1. **Prove It Works**: Verify with real artifacts (run commands, show actual output)
2. **Laziness Protocol**: Smallest change, prefer deletion
3. **Fix Root Causes**: Trace to first failure point, not symptoms
4. **Type System Discipline**: Pydantic validation at boundaries, trust internal types
5. **Boundary Discipline**: Guards at system boundaries (HTTP, file I/O), pure business logic
6. **Test Behavior Not Implementation**: Assert user-observable behavior
7. **Sequence Verifiable Units**: Small verifiable commits
8. **Never Block on Human**: Proceed and present, confirm only irreversible actions

## Project-Specific Requirements

Always honor ai-news-bot policies:

- **SPEC.md compliance**: One PR = one milestone
- **Tests + Lint**: `uv run pytest` and `uv run ruff check .` before PR
- **Interface isolation**: External calls (HTTP, Anthropic, SMTP) behind interfaces, tests use fixtures
- **No hardcoding**: Prompts in `prompts/`, config in `sources.yaml`
- **Validation**: Pydantic schemas + HTML escaping
- **Source isolation**: One source failure must not stop entire run
- **No secrets**: Never commit keys, subscribers, credentials

## Example: Bug Fix Request

**User request**: "Fix the bug where arXiv replace items are being collected"

**Your response**:
1. Attempt to read pstack poteto-mode skill from installed plugin
2. If found: Follow bug-fix playbook (reproduce, root-cause, fix, verify)
3. If not found: Note limitation, apply core principles above
4. In either case: Honor project requirements (tests, lint, SPEC.md)

## Upstream Attribution

**Source**: https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack  
**License**: MIT (Copyright 2026 Lauren Tan)  
**Plugin version**: 0.15.36 (commit 2776ddd, verified 2026-11-06)

This project skill is a **loader/router**, not a copy of pstack. It directs agents to read actual upstream skills from the installed plugin.

For questions about pstack: Read `poteto-help` skill from installed plugin, or visit https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/README.md
