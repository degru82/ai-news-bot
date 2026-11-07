#!/bin/bash
# Verify vendored pstack matches pinned upstream byte-for-byte
# This proves provenance, not just self-consistency

set -e

COMMIT_SHA="${1:-2776ddd2355d6d6c8747d3964600f28daf62f049}"
REPO_URL="https://github.com/cursor/plugins.git"
VENDOR_DIR=".cursor/skills/pstack"
WORKSPACE=$(pwd)

echo "=== Upstream Byte Comparison ==="
echo "Commit: $COMMIT_SHA"
echo "Vendor: $VENDOR_DIR"
echo

# Clone upstream to temp
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "1. Fetching upstream..."
git clone --depth 1 --no-checkout "$REPO_URL" "$TEMP_DIR" >/dev/null 2>&1
cd "$TEMP_DIR"
git fetch --depth 1 origin "$COMMIT_SHA" >/dev/null 2>&1
git checkout "$COMMIT_SHA" >/dev/null 2>&1
echo "   ✓ Fetched $COMMIT_SHA"
echo

# Count files
UPSTREAM_COUNT=$(find pstack -type f | wc -l)
echo "2. Upstream file count: $UPSTREAM_COUNT"

cd "$WORKSPACE"
VENDOR_COUNT=$(find "$VENDOR_DIR" -type f -not -path "$VENDOR_DIR/PROVENANCE.md" -not -path "$VENDOR_DIR/MANIFEST.sha256" | wc -l)
echo "   Vendor file count: $VENDOR_COUNT (excluding PROVENANCE.md, MANIFEST.sha256)"

if [ "$UPSTREAM_COUNT" -ne "$VENDOR_COUNT" ]; then
    echo "   ✗ File count mismatch"
    exit 1
fi
echo "   ✓ File counts match"
echo

# Byte-for-byte comparison
echo "3. Byte-for-byte comparison..."
DIFF_COUNT=0
MISSING_COUNT=0

while IFS= read -r upstream_file; do
    rel_path="${upstream_file#$TEMP_DIR/pstack/}"
    vendor_file="$WORKSPACE/$VENDOR_DIR/$rel_path"
    
    if [ ! -f "$vendor_file" ]; then
        echo "   ✗ Missing vendor: $rel_path"
        MISSING_COUNT=$((MISSING_COUNT + 1))
        continue
    fi
    
    if ! cmp -s "$upstream_file" "$vendor_file"; then
        echo "   ✗ Differs: $rel_path"
        DIFF_COUNT=$((DIFF_COUNT + 1))
    fi
done < <(find "$TEMP_DIR/pstack" -type f)

if [ "$DIFF_COUNT" -eq 0 ] && [ "$MISSING_COUNT" -eq 0 ]; then
    echo "   ✓ All $UPSTREAM_COUNT files match byte-for-byte"
else
    echo "   ✗ Found $DIFF_COUNT differing files, $MISSING_COUNT missing files"
    exit 1
fi
echo

echo "=== Provenance Verified ==="
echo "Vendor matches upstream $COMMIT_SHA exactly"
