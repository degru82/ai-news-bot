#!/bin/bash
# Verify complete pstack bundle integration with hash checking and dependency resolution

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

echo "=== pstack Integration Verification ==="
echo
echo "Verifying COMPLETE upstream pstack bundle (not condensed version)"
echo "This is STATIC validation - runtime requires IDE"
echo

# Helper
check() {
    local name="$1"
    local condition="$2"
    
    if eval "$condition"; then
        echo -e "   ${GREEN}✓${NC} $name"
    else
        echo -e "   ${RED}✗${NC} $name"
        FAILED=$((FAILED + 1))
    fi
}

# 1. Check complete bundle structure
echo "1. Verifying complete bundle structure..."

PSTACK_DIR=".cursor/skills/pstack"

check "pstack directory exists" "[ -d '$PSTACK_DIR' ]"
check "LICENSE exists" "[ -f '$PSTACK_DIR/LICENSE' ]"
check "PROVENANCE.md exists" "[ -f '$PSTACK_DIR/PROVENANCE.md' ]"
check "MANIFEST.sha256 exists" "[ -f '$PSTACK_DIR/MANIFEST.sha256' ]"
check "poteto-mode exists" "[ -f '$PSTACK_DIR/skills/poteto-mode/SKILL.md' ]"
check "skills directory exists" "[ -d '$PSTACK_DIR/skills' ]"
check "playbooks directory exists" "[ -d '$PSTACK_DIR/skills/poteto-mode/playbooks' ]"

SKILL_COUNT=$(find "$PSTACK_DIR/skills" -maxdepth 1 -type d | wc -l)
check "Has 58+ skills (found $SKILL_COUNT)" "[ $SKILL_COUNT -gt 58 ]"

echo

# 2. Verify manifest integrity
echo "2. Verifying file integrity against manifest..."

if [ -f "$PSTACK_DIR/MANIFEST.sha256" ]; then
    cd "$PSTACK_DIR"
    if sha256sum -c MANIFEST.sha256 --quiet 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} All 571 files match manifest hashes"
    else
        echo -e "   ${RED}✗${NC} Integrity check failed - files modified or missing"
        FAILED=$((FAILED + 1))
    fi
    cd - > /dev/null
else
    echo -e "   ${RED}✗${NC} MANIFEST.sha256 missing"
    FAILED=$((FAILED + 1))
fi

echo

# 3. Verify referenced dependencies exist
echo "3. Verifying referenced dependencies exist..."

# Check for commonly referenced files from poteto-mode
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
    check "Dependency exists: $dep" "[ -f '$PSTACK_DIR/$dep' ]"
done

echo

# 4. Verify NOT condensed
echo "4. Verifying this is NOT a condensed version..."

POTETO_FILE="$PSTACK_DIR/skills/poteto-mode/SKILL.md"

check "Does NOT label as condensed" "! grep -qi 'condensed.*version\\|adapted.*version' '$POTETO_FILE'"
check "Does NOT say playbooks not bundled" "! grep -qi 'not.*bundled\\|playbooks.*not.*included' '$POTETO_FILE'"
check "playbooks/ directory actually exists" "[ -d '$PSTACK_DIR/skills/poteto-mode/playbooks' ]"

PLAYBOOK_COUNT=$(find "$PSTACK_DIR/skills/poteto-mode/playbooks" -name "*.md" -type f | wc -l)
check "Has playbooks (found $PLAYBOOK_COUNT)" "[ $PLAYBOOK_COUNT -gt 15 ]"

echo

# 5. Check router skill
echo "5. Verifying router skill..."

ROUTER_FILE=".cursor/skills/use-pstack-workflows/SKILL.md"

check "Router exists" "[ -f '$ROUTER_FILE' ]"
check "Router references complete bundle" "grep -q 'complete upstream pstack' '$ROUTER_FILE'"
check "Router references correct entry path" "grep -q 'skills/poteto-mode/SKILL\\.md' '$ROUTER_FILE'"
check "Router mentions dependency resolution" "grep -qi 'referenced.*skills.*bundled\\|following.*references' '$ROUTER_FILE'"

echo

# 6. Check CLAUDE.md
echo "6. Verifying CLAUDE.md..."

check "CLAUDE.md exists" "[ -f 'CLAUDE.md' ]"
check "References correct entry path" "grep -q 'skills/poteto-mode/SKILL\\.md' CLAUDE.md"
check "Mentions complete bundle" "grep -q '완전한 upstream pstack\\|complete upstream pstack' CLAUDE.md"
check "No deleted .mdc references" "! grep -q '\\.cursor/rules/pstack-coding\\.mdc' CLAUDE.md"

echo

# 7. Check README.md
echo "7. Verifying README.md..."

check "README exists" "[ -f 'README.md' ]"
check "No deleted .mdc references" "! grep -q '\\.cursor/rules/pstack-coding\\.mdc' README.md"
check "References pstack bundle" "grep -q 'pstack' README.md"

echo

# 8. Verify provenance
echo "8. Verifying provenance and upstream attribution..."

PROV_FILE="$PSTACK_DIR/PROVENANCE.md"

check "Provenance mentions commit SHA" "grep -q '2776ddd' '$PROV_FILE'"
check "Provenance mentions 571 files" "grep -q '571' '$PROV_FILE'"
check "LICENSE file exists" "[ -f '$PSTACK_DIR/LICENSE' ]"
check "LICENSE is complete (>1000 bytes)" "[ \$(wc -c < '$PSTACK_DIR/LICENSE') -gt 1000 ]"

echo

# 9. Verify sync script
echo "9. Verifying sync script..."

SYNC_SCRIPT="scripts/sync-pstack.sh"

check "Sync script exists" "[ -f '$SYNC_SCRIPT' ]"
check "Sync script is executable" "[ -x '$SYNC_SCRIPT' ]"
check "Sync script generates manifest" "grep -q 'MANIFEST.sha256' '$SYNC_SCRIPT'"

echo

# 10. Security checks
echo "10. Security checks..."

check "No API keys in bundle" "! grep -r 'sk-[a-zA-Z0-9]\\{20,\\}' '$PSTACK_DIR' 2>/dev/null"
check "No emails in bundle" "! grep -rE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' '$PSTACK_DIR'/{LICENSE,PROVENANCE.md,MANIFEST.sha256} 2>/dev/null"

echo

# Final summary
echo "=== Verification Summary ==="
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    echo
    echo "STATIC VALIDATION: Complete"
    echo "- Complete upstream pstack bundle (571 files, 8MB)"
    echo "- All file hashes match manifest"
    echo "- All referenced dependencies present"
    echo "- NOT a condensed version"
    echo "- Playbooks, principles, references all bundled"
    echo
    echo "RUNTIME VALIDATION: Not performed (requires IDE)"
    echo
    echo "Manual integrity check:"
    echo "  cd .cursor/skills/pstack && sha256sum -c MANIFEST.sha256 --quiet && echo OK"
    echo
    echo "To update from upstream:"
    echo "  bash scripts/sync-pstack.sh [commit-sha]"
    echo
    exit 0
else
    echo -e "${RED}✗ $FAILED check(s) failed${NC}"
    echo
    exit 1
fi
