---
name: use-pstack-workflows
description: For substantive coding work (features, refactoring, bug fixes, PR reviews), read and apply pstack workflows from .cursor/skills/pstack/
---

# Use pstack Workflows for ai-news-bot

For substantive coding work (features, refactoring, bug fixes, PR reviews), read and apply **complete upstream pstack** bundled in `.cursor/skills/pstack/`.

## Entry Point

**Read first**: `.cursor/skills/pstack/skills/poteto-mode/SKILL.md`

This is the main pstack workflow skill with:
- Complete workflow triggers
- All core principles (with references to principle-* skills)
- Playbook selection logic (references to playbooks/*.md)
- Instructions to read referenced skills as needed

## Following References

poteto-mode references other skills and playbooks. They are ALL bundled:

- **Skills**: `.cursor/skills/pstack/skills/[skill-name]/SKILL.md`
  - Example: `how`, `why`, `interrogate`, `architect`, `arena`, `swarm`, etc.
- **Principles**: `.cursor/skills/pstack/skills/principle-[name]/SKILL.md`
  - Example: `principle-prove-it-works`, `principle-fix-root-causes`, etc.
- **Playbooks**: `.cursor/skills/pstack/skills/poteto-mode/playbooks/[name].md`
  - Example: `bug-fix.md`, `feature.md`, `refactoring.md`, etc.

All paths are relative to `.cursor/skills/pstack/`.

## ai-news-bot Project Constraints

In addition to pstack workflows, always honor:

- One PR = one SPEC.md milestone
- Tests: `uv run pytest`
- Lint: `uv run ruff check . && uv run ruff format --check .`
- External calls behind interfaces, tests use fixtures
- Prompts in `prompts/`, config in `sources.yaml`
- Pydantic validation + HTML escaping
- One source failure doesn't stop entire run
- No secrets in code

## Upstream Bundle

**Complete upstream pstack** (571 files, 8MB) from:
- **Source**: https://github.com/cursor/plugins
- **Commit**: 2776ddd2355d6d6c8747d3964600f28daf62f049
- **License**: MIT (Copyright 2026 Lauren Tan)
- **Provenance**: See `.cursor/skills/pstack/PROVENANCE.md`
- **Integrity**: Verified via `.cursor/skills/pstack/MANIFEST.sha256`

This router is a LOCAL ADAPTATION for ai-news-bot. The bundled pstack is byte-for-byte upstream.

## Notes

- poteto-mode has `disable-model-invocation: true` - it won't auto-trigger
- This router provides project default: read poteto-mode, follow its references
- All referenced dependencies are bundled and accessible
- No condensing, no summaries - complete upstream preserved
