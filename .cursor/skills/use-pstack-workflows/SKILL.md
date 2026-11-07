---
name: use-pstack-workflows
description: For substantive coding work (features, refactoring, bug fixes, PR reviews), read and apply pstack workflows from .cursor/skills/pstack/poteto-mode/SKILL.md
---

# Use pstack Workflows for Coding

For substantive coding work (features, refactoring, bug fixes, PR reviews), **read and apply the actual pstack poteto-mode skill** bundled in this repository.

## Instructions for All Agents

**Before starting substantive coding work, read:**

`.cursor/skills/pstack/poteto-mode/SKILL.md`

This file contains:
- Complete workflow triggers (when to use each approach)
- Core principles (Prove It Works, Fix Root Causes, etc.)
- Playbook selection logic
- Project-specific constraints for ai-news-bot

**Key sections to read:**
1. Non-negotiables - workflow triggers
2. Principles - core engineering principles
3. Playbooks - when to use each (bug fix, feature, refactoring, etc.)
4. Project-specific constraints - ai-news-bot requirements

## Project Requirements

Always honor ai-news-bot policies from poteto-mode SKILL.md:

- One PR = one SPEC.md milestone
- Tests pass: `uv run pytest`
- Lint passes: `uv run ruff check .`
- External calls behind interfaces
- No hardcoding (use `prompts/`, `sources.yaml`)
- Pydantic validation + HTML escaping
- No secrets in code

## Upstream Attribution

**Source**: https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack
**License**: MIT (Copyright 2026 Lauren Tan) - see `.cursor/skills/pstack/LICENSE`
**This repository contains**: Condensed pstack with poteto-mode skill for project use
**Full plugin**: Install from https://github.com/cursor/plugins for complete capabilities

## Notes

- `disable-model-invocation: true` on poteto-mode means it won't auto-trigger
- This router skill provides project-level entry point
- Agents must explicitly read poteto-mode SKILL.md as instructed above
- This satisfies the requirement for "actual skill reading" not summaries
