# pstack Provenance and Integrity

## Upstream Source

**Repository**: https://github.com/cursor/plugins
**Commit SHA**: 2776ddd2355d6d6c8747d3964600f28daf62f049
**Path**: pstack/
**License**: MIT (Copyright 2026 Lauren Tan)

## Bundle Contents

This directory contains the COMPLETE pstack subtree from upstream at the pinned commit above, preserved byte-for-byte.

**Total files**: 573
**Upstream commit**: 2776ddd2355d6d6c8747d3964600f28daf62f049

## Integrity Verification

File hashes are stored in `MANIFEST.sha256`.

Verify offline integrity (self-consistency):
```bash
cd .cursor/skills/pstack
sha256sum --strict -c MANIFEST.sha256
```

Verify provenance (byte-comparison with upstream):
```bash
bash scripts/verify-upstream.sh 2776ddd2355d6d6c8747d3964600f28daf62f049
```

## License Compliance

MIT License permits redistribution provided copyright, permission, and disclaimer are preserved.
See `LICENSE` for full text.
