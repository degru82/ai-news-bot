#!/bin/bash
# Sync pstack from upstream repository
# Usage: bash scripts/sync-pstack.sh [commit-sha]
# Default: 2776ddd2355d6d6c8747d3964600f28daf62f049

set -e

COMMIT=${1:-2776ddd2355d6d6c8747d3964600f28daf62f049}
REPO_URL="https://github.com/cursor/plugins.git"
TEMP_DIR=$(mktemp -d)
PSTACK_DIR=".cursor/skills/pstack"

echo "=== Syncing pstack from upstream ==="
echo "Commit: $COMMIT"
echo "Temp dir: $TEMP_DIR"
echo

# Clone upstream
echo "1. Cloning upstream repository..."
git clone --depth 1 --no-checkout "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"
git fetch --depth 1 origin "$COMMIT"
git checkout "$COMMIT"

# Verify pstack directory exists
if [ ! -d "pstack" ]; then
    echo "ERROR: pstack/ not found in upstream at $COMMIT"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Count files
FILE_COUNT=$(find pstack -type f | wc -l)
echo "   Found $FILE_COUNT files in upstream pstack/"
echo

# Return to workspace
cd - > /dev/null

# Backup current
echo "2. Backing up current pstack..."
if [ -d "$PSTACK_DIR" ]; then
    mv "$PSTACK_DIR" "${PSTACK_DIR}.backup"
    echo "   Backed up to ${PSTACK_DIR}.backup"
fi
echo

# Copy new
echo "3. Copying upstream pstack..."
mkdir -p "$PSTACK_DIR"
cp -r "$TEMP_DIR/pstack/"* "$PSTACK_DIR/"
echo "   Copied $FILE_COUNT files"
echo

# Generate manifest
echo "4. Generating integrity manifest..."
cd "$PSTACK_DIR"
find . -type f -not -path "./PROVENANCE.md" -not -path "./MANIFEST.sha256" \
    -exec sha256sum {} \; | sort -k2 > MANIFEST.sha256
MANIFEST_COUNT=$(wc -l < MANIFEST.sha256)
echo "   Generated manifest with $MANIFEST_COUNT hashes"
cd - > /dev/null
echo

# Update provenance
echo "5. Updating PROVENANCE.md..."
cat > "$PSTACK_DIR/PROVENANCE.md" << EOF
# pstack Provenance and Integrity

## Upstream Source

**Repository**: https://github.com/cursor/plugins
**Commit SHA**: $COMMIT
**Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Path**: pstack/
**License**: MIT (Copyright 2026 Lauren Tan)

## Bundle Contents

This directory contains the COMPLETE pstack subtree from upstream at the pinned commit above, preserved byte-for-byte.

**Total files**: $MANIFEST_COUNT
**Upstream commit**: $COMMIT

## Integrity Verification

File hashes are stored in \`MANIFEST.sha256\`.

To verify integrity:
\`\`\`bash
cd .cursor/skills/pstack
sha256sum -c MANIFEST.sha256 --quiet
echo \$?  # Should be 0 if all files match
\`\`\`

## License Compliance

MIT License permits redistribution provided copyright, permission, and disclaimer are preserved.
See \`LICENSE\` for full text.
EOF

echo "   Updated PROVENANCE.md"
echo

# Cleanup
rm -rf "$TEMP_DIR"
if [ -d "${PSTACK_DIR}.backup" ]; then
    rm -rf "${PSTACK_DIR}.backup"
fi

echo "=== Sync complete ==="
echo
echo "Review changes:"
echo "  git status"
echo "  git diff .cursor/skills/pstack/PROVENANCE.md"
echo
echo "Verify integrity:"
echo "  cd .cursor/skills/pstack && sha256sum -c MANIFEST.sha256 --quiet"
echo
echo "If satisfied, commit:"
echo "  git add .cursor/skills/pstack"
echo "  git commit -m 'Update pstack to $COMMIT'"
