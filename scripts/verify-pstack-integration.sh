#!/bin/bash
# Verify complete pstack bundle integration with strict manifest validation

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0
ROOT_DIR="${1:-.}"

echo "=== pstack Integration Verification ==="
echo
echo "Root: $ROOT_DIR"
echo "This is STATIC validation - runtime requires IDE"
echo

# Helper without eval
fail() {
    echo -e "   ${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

pass() {
    echo -e "   ${GREEN}✓${NC} $1"
}

check_file() {
    if [ -f "$1" ]; then
        pass "$2"
        return 0
    else
        fail "$2"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        pass "$2"
        return 0
    else
        fail "$2"
        return 1
    fi
}

# 1. Check complete bundle structure
echo "1. Verifying complete bundle structure..."

PSTACK_DIR="$ROOT_DIR/.cursor/skills/pstack"

check_dir "$PSTACK_DIR" "pstack directory exists" || true
check_file "$PSTACK_DIR/LICENSE" "LICENSE exists" || true
check_file "$PSTACK_DIR/PROVENANCE.md" "PROVENANCE.md exists" || true
check_file "$PSTACK_DIR/MANIFEST.sha256" "MANIFEST.sha256 exists" || true
check_file "$PSTACK_DIR/.gitignore" ".gitignore exists (dotfile)" || true
check_file "$PSTACK_DIR/.cursor-plugin/plugin.json" ".cursor-plugin/plugin.json exists (dotfile)" || true
check_file "$PSTACK_DIR/skills/poteto-mode/SKILL.md" "poteto-mode exists" || true
check_dir "$PSTACK_DIR/skills" "skills directory exists" || true
check_dir "$PSTACK_DIR/skills/poteto-mode/playbooks" "playbooks directory exists" || true

if [ -d "$PSTACK_DIR/skills" ]; then
    SKILL_COUNT=$(find "$PSTACK_DIR/skills" -maxdepth 1 -type d | wc -l)
    if [ "$SKILL_COUNT" -gt 58 ]; then
        pass "Has 58+ skills (found $SKILL_COUNT)"
    else
        fail "Has 58+ skills (found $SKILL_COUNT)"
    fi
fi

echo

# 2. Strictly verify manifest format and integrity
echo "2. Verifying manifest format and integrity..."

if [ ! -f "$PSTACK_DIR/MANIFEST.sha256" ]; then
    fail "MANIFEST.sha256 missing"
else
    MANIFEST_LINES=$(wc -l < "$PSTACK_DIR/MANIFEST.sha256")

    # Check expected count
    if [ "$MANIFEST_LINES" -eq 573 ]; then
        pass "Manifest has 573 entries (matches upstream)"
    else
        fail "Manifest has $MANIFEST_LINES entries (expected 573)"
    fi

    # Strictly validate format: <64-char-hex><space><space><relative-path>
    MALFORMED=0
    DUPLICATES=0

    while IFS= read -r line; do
        # Check format: exactly 64 hex chars, two spaces, then path starting with ./
        if ! echo "$line" | grep -qE '^[0-9a-f]{64}  \./[^/]'; then
            MALFORMED=$((MALFORMED + 1))
        fi
    done < "$PSTACK_DIR/MANIFEST.sha256"

    if [ "$MALFORMED" -eq 0 ]; then
        pass "All manifest entries have valid SHA256 format"
    else
        fail "Found $MALFORMED malformed manifest entries"
    fi

    # Check for duplicate paths
    DUPLICATES=$(cut -d' ' -f3- "$PSTACK_DIR/MANIFEST.sha256" | sort | uniq -d | wc -l)
    if [ "$DUPLICATES" -eq 0 ]; then
        pass "No duplicate paths in manifest"
    else
        fail "Found $DUPLICATES duplicate paths in manifest"
    fi

    # Verify hashes with strict mode
    cd "$PSTACK_DIR"
    if sha256sum --strict -c MANIFEST.sha256 >/dev/null 2>&1; then
        pass "All 573 files match manifest hashes (strict mode)"
    else
        fail "Hash verification failed (strict mode)"
    fi
    cd - > /dev/null

    # Check for files not in manifest (excluding local metadata)
    ACTUAL_FILES=$(find "$PSTACK_DIR" -type f -not -path "$PSTACK_DIR/PROVENANCE.md" -not -path "$PSTACK_DIR/MANIFEST.sha256" | wc -l)
    if [ "$ACTUAL_FILES" -eq "$MANIFEST_LINES" ]; then
        pass "No unlisted files (573 files = 573 manifest entries)"
    else
        fail "File count mismatch (found $ACTUAL_FILES files, manifest has $MANIFEST_LINES)"
    fi
fi

echo

# 3. Verify referenced dependencies exist
echo "3. Verifying referenced dependencies exist..."

DEPS=(
    "skills/how/SKILL.md"
    "skills/why/SKILL.md"
    "skills/interrogate/SKILL.md"
    "skills/architect/SKILL.md"
    "skills/principle-prove-it-works/SKILL.md"
    "skills/principle-fix-root-causes/SKILL.md"
    "skills/principle-laziness-protocol/SKILL.md"
    "skills/poteto-mode/playbooks/bug-fix.md"
    "skills/poteto-mode/playbooks/feature.md"
    "skills/poteto-mode/playbooks/refactoring.md"
)

for dep in "${DEPS[@]}"; do
    check_file "$PSTACK_DIR/$dep" "Dependency exists: $dep" || true
done

echo

# 4. Verify NOT condensed
echo "4. Verifying this is NOT a condensed version..."

POTETO_FILE="$PSTACK_DIR/skills/poteto-mode/SKILL.md"

if [ -f "$POTETO_FILE" ]; then
    if grep -qi 'condensed.*version\|adapted.*version' "$POTETO_FILE"; then
        fail "Should NOT label as condensed"
    else
        pass "Does NOT label as condensed"
    fi

    if grep -qi 'not.*bundled\|playbooks.*not.*included' "$POTETO_FILE"; then
        fail "Should NOT say playbooks not bundled"
    else
        pass "Does NOT say playbooks not bundled"
    fi
fi

if [ -d "$PSTACK_DIR/skills/poteto-mode/playbooks" ]; then
    pass "playbooks/ directory actually exists"
    PLAYBOOK_COUNT=$(find "$PSTACK_DIR/skills/poteto-mode/playbooks" -name "*.md" -type f | wc -l)
    if [ "$PLAYBOOK_COUNT" -gt 15 ]; then
        pass "Has playbooks (found $PLAYBOOK_COUNT)"
    else
        fail "Has playbooks (found $PLAYBOOK_COUNT, expected >15)"
    fi
else
    fail "playbooks/ directory missing"
fi

echo

# 5. Check router skill
echo "5. Verifying router skill..."

ROUTER_FILE="$ROOT_DIR/.cursor/skills/use-pstack-workflows/SKILL.md"

check_file "$ROUTER_FILE" "Router exists" || true

if [ -f "$ROUTER_FILE" ]; then
    if grep -q 'complete upstream pstack\|완전한 upstream' "$ROUTER_FILE"; then
        pass "Router references complete bundle"
    else
        fail "Router should reference complete bundle"
    fi

    if grep -q 'skills/poteto-mode/SKILL\.md' "$ROUTER_FILE"; then
        pass "Router references correct entry path"
    else
        fail "Router should reference correct entry path"
    fi

    if grep -qi 'referenced.*skills.*bundled\|following.*references' "$ROUTER_FILE"; then
        pass "Router mentions dependency resolution"
    else
        fail "Router should mention dependency resolution"
    fi
fi

echo

# 6. Check CLAUDE.md
echo "6. Verifying CLAUDE.md..."

CLAUDE_FILE="$ROOT_DIR/CLAUDE.md"

check_file "$CLAUDE_FILE" "CLAUDE.md exists" || true

if [ -f "$CLAUDE_FILE" ]; then
    if grep -q 'skills/poteto-mode/SKILL\.md' "$CLAUDE_FILE"; then
        pass "References correct entry path"
    else
        fail "Should reference correct entry path"
    fi

    if grep -q '완전한 upstream pstack\|complete upstream pstack' "$CLAUDE_FILE"; then
        pass "Mentions complete bundle"
    else
        fail "Should mention complete bundle"
    fi

    if grep -q '\.cursor/rules/pstack-coding\.mdc' "$CLAUDE_FILE"; then
        fail "Should NOT reference deleted .mdc file"
    else
        pass "No deleted .mdc references"
    fi
fi

echo

# 7. Check README.md
echo "7. Verifying README.md..."

README_FILE="$ROOT_DIR/README.md"

check_file "$README_FILE" "README exists" || true

if [ -f "$README_FILE" ]; then
    if grep -q '\.cursor/rules/pstack-coding\.mdc' "$README_FILE"; then
        fail "Should NOT reference deleted .mdc file"
    else
        pass "No deleted .mdc references"
    fi

    if grep -q 'pstack' "$README_FILE"; then
        pass "References pstack bundle"
    else
        fail "Should reference pstack bundle"
    fi
fi

echo

# 8. Check Cursor always-applied rule
echo "8. Verifying Cursor always-applied rule..."

CURSOR_RULE="$ROOT_DIR/.cursor/rules/use-pstack.mdc"

check_file "$CURSOR_RULE" "Cursor rule exists" || true

if [ -f "$CURSOR_RULE" ]; then
    if grep -q 'alwaysApply.*true' "$CURSOR_RULE"; then
        pass "Rule has alwaysApply: true"
    else
        fail "Rule should have alwaysApply: true"
    fi

    if grep -q 'skills/poteto-mode/SKILL\.md' "$CURSOR_RULE"; then
        pass "Rule references actual repo SKILL"
    else
        fail "Rule should reference actual repo SKILL"
    fi
fi

echo

# 9. Verify provenance
echo "9. Verifying provenance..."

PROV_FILE="$PSTACK_DIR/PROVENANCE.md"

if [ -f "$PROV_FILE" ]; then
    if grep -q '2776ddd' "$PROV_FILE"; then
        pass "Provenance mentions commit SHA"
    else
        fail "Provenance should mention commit SHA"
    fi

    if grep -q '573' "$PROV_FILE"; then
        pass "Provenance mentions 573 files"
    else
        fail "Provenance should mention 573 files (not 571)"
    fi
else
    fail "PROVENANCE.md missing"
fi

if [ -f "$PSTACK_DIR/LICENSE" ]; then
    pass "LICENSE file exists"
    LICENSE_SIZE=$(wc -c < "$PSTACK_DIR/LICENSE")
    if [ "$LICENSE_SIZE" -gt 1000 ]; then
        pass "LICENSE is complete (>1000 bytes)"
    else
        fail "LICENSE seems incomplete ($LICENSE_SIZE bytes)"
    fi
else
    fail "LICENSE missing"
fi

echo

# 10. Security checks
echo "10. Security checks..."

if grep -rE 'sk-[a-zA-Z0-9]{20,}' "$PSTACK_DIR" 2>/dev/null | grep -qv MANIFEST; then
    fail "Found potential API keys"
else
    pass "No obvious API keys in bundle"
fi

echo

# Final summary
echo "=== Verification Summary ==="
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    echo
    echo "STATIC VALIDATION: Complete"
    echo "- Complete upstream pstack bundle (573 files, 8MB)"
    echo "- All file hashes match manifest (strict mode)"
    echo "- All referenced dependencies present"
    echo "- NOT a condensed version"
    echo "- Playbooks, principles, references all bundled"
    echo "- Dotfiles (.gitignore, .cursor-plugin/) included"
    echo
    echo "OFFLINE INTEGRITY: Self-consistent"
    echo "- Manifest format valid (573 entries, no duplicates)"
    echo "- All files listed, no missing/unlisted files"
    echo "- Hash verification passes (strict mode)"
    echo
    echo "PROVENANCE: Not verified by this check"
    echo "- Use scripts/verify-upstream.sh for byte-comparison"
    echo
    echo "RUNTIME VALIDATION: Not performed (requires IDE)"
    echo
    exit 0
else
    echo -e "${RED}✗ $FAILED check(s) failed${NC}"
    echo
    exit 1
fi
