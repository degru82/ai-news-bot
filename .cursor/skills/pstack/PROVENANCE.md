# pstack Provenance and Integrity

## Upstream Source

**Repository**: https://github.com/cursor/plugins
**Commit SHA**: 2776ddd2355d6d6c8747d3964600f28daf62f049
**Date**: 2026-11-06
**Path**: pstack/
**License**: MIT (Copyright 2026 Lauren Tan)

## Bundle Contents

This directory contains the COMPLETE pstack subtree from upstream at the pinned commit above, preserved byte-for-byte including:

- All 58+ skills (skills/)
- All playbooks (skills/poteto-mode/playbooks/)
- All reference docs (skills/*/references/)
- All principle skills (skills/principle-*/)
- Agent definitions (agents/)
- Documentation (docs/)
- Adapter documentation (docs/harness/)
- README, LICENSE, plugin.json

**Total files**: 571
**Total size**: 8.0MB

## Integrity Verification

File hashes are stored in `MANIFEST.sha256`.

To verify integrity:
```bash
cd .cursor/skills/pstack
sha256sum -c MANIFEST.sha256 --quiet
echo $?  # Should be 0 if all files match
```

## Synchronization

To update from upstream:

```bash
# From repository root
bash scripts/sync-pstack.sh [commit-sha]
```

This script:
1. Fetches specified commit from upstream
2. Replaces pstack/ directory
3. Regenerates MANIFEST.sha256
4. Updates this PROVENANCE.md
5. Requires manual review and commit

## Local Adaptations

Local project-specific files (NOT from upstream):
- `../.cursor/skills/use-pstack-workflows/SKILL.md` - router skill for ai-news-bot
- `../../../CLAUDE.md` - project instructions referencing pstack
- `../../../docs/wiki/05-operations/pstack-integration.md` - integration docs

These are clearly separated from upstream pstack and labeled as adaptations.

## Upstream Changes

This is a static bundle. To track upstream changes:
```bash
git log --oneline 2776ddd2355d6d6c8747d3964600f28daf62f049..HEAD -- pstack/ \
  --repo https://github.com/cursor/plugins
```

## License Compliance

MIT License permits redistribution provided:
- Copyright notice preserved (✓ LICENSE file)
- Permission text preserved (✓ LICENSE file)
- Disclaimer preserved (✓ LICENSE file)
- Original unchanged (✓ byte-for-byte copy)

See `LICENSE` for full text.
