#!/bin/bash
# Sync pstack from upstream repository (idempotent)
# Usage: bash scripts/sync-pstack.sh [commit-sha]
# Default: 2776ddd2355d6d6c8747d3964600f28daf62f049

set -e

COMMIT=${1:-2776ddd2355d6d6c8747d3964600f28daf62f049}
REPO_URL="https://github.com/cursor/plugins.git"
TEMP_DIR=$(mktemp -d)
PSTACK_DIR=".cursor/skills/pstack"
STAGE_DIR=$(mktemp -d)
BACKUP_DIR=""

trap 'rm -rf "$TEMP_DIR" "$STAGE_DIR"' EXIT

echo "=== Syncing pstack from upstream ==="
echo "Commit: $COMMIT"
echo

# Clone upstream
echo "1. Cloning upstream repository..."
git clone --depth 1 --no-checkout "$REPO_URL" "$TEMP_DIR" >/dev/null 2>&1
cd "$TEMP_DIR"
git fetch --depth 1 origin "$COMMIT" >/dev/null 2>&1
git checkout "$COMMIT" >/dev/null 2>&1

# Verify pstack directory exists
if [ ! -d "pstack" ]; then
    echo "ERROR: pstack/ not found in upstream at $COMMIT"
    exit 1
fi

# Count files
FILE_COUNT=$(find pstack -type f | wc -l)
echo "   Found $FILE_COUNT files in upstream pstack/"
echo

cd - > /dev/null

# Stage new bundle (preserve dotfiles)
echo "2. Staging new bundle..."
if ! cp -a "$TEMP_DIR/pstack/." "$STAGE_DIR/"; then
    echo "ERROR: Failed to copy upstream files"
    exit 1
fi
echo "   Staged to temporary directory"
echo

# Generate manifest (deterministic sort, exclude local metadata)
echo "3. Generating manifest..."
cd "$STAGE_DIR"
find . -type f -not -name "MANIFEST.sha256" -not -name "PROVENANCE.md" -exec sha256sum {} \; 2>/dev/null | LC_ALL=C sort -k2 > MANIFEST.sha256
MANIFEST_COUNT=$(wc -l < MANIFEST.sha256)
echo "   Generated manifest with $MANIFEST_COUNT hashes"
cd - > /dev/null
echo

# Generate provenance (deterministic, no wall clock)
echo "4. Generating provenance..."
cat > "$STAGE_DIR/PROVENANCE.md" << EOF
# pstack Provenance and Integrity

## Upstream Source

**Repository**: https://github.com/cursor/plugins
**Commit SHA**: $COMMIT
**Path**: pstack/
**License**: MIT (Copyright 2026 Lauren Tan)

## Bundle Contents

This directory contains the COMPLETE pstack subtree from upstream at the pinned commit above, preserved byte-for-byte.

**Total files**: $MANIFEST_COUNT
**Upstream commit**: $COMMIT

## Integrity Verification

File hashes are stored in \`MANIFEST.sha256\`.

Verify offline integrity (self-consistency):
\`\`\`bash
cd .cursor/skills/pstack
sha256sum --strict -c MANIFEST.sha256
\`\`\`

Verify provenance (byte-comparison with upstream):
\`\`\`bash
bash scripts/verify-upstream.sh $COMMIT
\`\`\`

## License Compliance

MIT License permits redistribution provided copyright, permission, and disclaimer are preserved.
See \`LICENSE\` for full text.
EOF

echo "   Generated provenance"
echo

# Validate staged bundle
echo "5. Validating staged bundle..."
cd "$STAGE_DIR"
if sha256sum --strict -c MANIFEST.sha256 >/dev/null 2>&1; then
    echo "   ✓ Staged bundle integrity valid"
else
    echo "   ✗ Staged bundle integrity check failed"
    cd - > /dev/null
    exit 1
fi
cd - > /dev/null
echo

# Backup and replace bundle
echo "6. Replacing bundle..."
if [ -d "$PSTACK_DIR" ]; then
    BACKUP_DIR=$(mktemp -d)
    if ! cp -a "$PSTACK_DIR/." "$BACKUP_DIR/"; then
        echo "ERROR: Failed to backup existing bundle"
        exit 1
    fi
    echo "   Backed up existing bundle"
fi

if ! rm -rf "$PSTACK_DIR"; then
    echo "ERROR: Failed to remove old bundle"
    if [ -n "$BACKUP_DIR" ]; then
        echo "   Old bundle preserved at $BACKUP_DIR (manual cleanup required)"
    fi
    exit 1
fi

mkdir -p "$(dirname "$PSTACK_DIR")"
if ! mv "$STAGE_DIR" "$PSTACK_DIR"; then
    echo "ERROR: Failed to move staged bundle"
    if [ -n "$BACKUP_DIR" ]; then
        echo "   Restoring from backup..."
        mv "$BACKUP_DIR" "$PSTACK_DIR"
    fi
    exit 1
fi

if [ -n "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
fi

echo "   Replaced $PSTACK_DIR with $MANIFEST_COUNT files"
echo

echo "=== Sync complete ==="
echo
echo "Verify integration:"
echo "  bash scripts/verify-pstack-integration.sh"
echo
echo "Verify upstream match:"
echo "  bash scripts/verify-upstream.sh $COMMIT"
echo
echo "If satisfied, commit:"
echo "  git add .cursor/skills/pstack"
echo "  git commit -m 'Update pstack to $COMMIT'"
