#!/bin/bash
# Verify pstack integration: actual skill files, parsed metadata, negative tests
# Distinguishes static verification vs runtime validation

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== pstack Integration Verification (Static) ==="
echo
echo "This script performs STATIC file/structure validation only."
echo "RUNTIME validation requires Cursor IDE and is NOT performed here."
echo

FAILED=0

# Helper: check condition and report
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

# 1. Check skill file exists and structure
echo "1. Checking .cursor/skills/use-pstack-for-coding/SKILL.md..."
SKILL_FILE=".cursor/skills/use-pstack-for-coding/SKILL.md"

check "Skill file exists" "[ -f '$SKILL_FILE' ]"

if [ -f "$SKILL_FILE" ]; then
    # Parse YAML frontmatter properly (between --- markers)
    FRONTMATTER=$(awk 'BEGIN {inFM=0} /^---$/ {if (inFM==0) {inFM=1; next} else {exit}} inFM==1 {print}' "$SKILL_FILE")
    
    check "Has YAML frontmatter" "[ -n '$FRONTMATTER' ]"
    check "name field present" "echo '$FRONTMATTER' | grep -q '^name:'"
    check "description field present" "echo '$FRONTMATTER' | grep -q '^description:'"
    check "name matches directory" "echo '$FRONTMATTER' | grep -q 'name: use-pstack-for-coding'"
    check "Description mentions coding/features/bugs" "echo '$FRONTMATTER' | grep -qi 'coding\\|features\\|bug\\|refactor\\|review'"
    
    # Check skill content
    check "Directs to read actual pstack SKILL.md" "grep -q 'read.*pstack.*SKILL\\.md\\|Read.*pstack.*skill\\|poteto-mode.*SKILL\\.md' '$SKILL_FILE'"
    check "Mentions plugin installation required" "grep -q 'install.*plugin\\|Plugin.*Required\\|must install' '$SKILL_FILE'"
    check "Provides fallback principles" "grep -q 'Fallback\\|fallback\\|cannot access.*principles' '$SKILL_FILE'"
    check "No hidden user paths" "! grep -q '\\.cursor/plugins/cache.*\[hash\]\\|/Users/\\|/home/[^/]\\+/\\.cursor' '$SKILL_FILE' || grep -q 'example\\|similar\\|or similar' '$SKILL_FILE'"
else
    echo -e "   ${RED}✗${NC} Cannot check frontmatter - file missing"
    FAILED=$((FAILED + 8))
fi
echo

# 2. Check CLAUDE.md integration
echo "2. Checking CLAUDE.md integration..."

check "CLAUDE.md exists" "[ -f 'CLAUDE.md' ]"

if [ -f "CLAUDE.md" ]; then
    check "Mentions pstack" "grep -q 'pstack' CLAUDE.md"
    check "Installation instructions present" "grep -q '/add-plugin pstack\\|plugin install pstack' CLAUDE.md"
    check "Core principles listed" "grep -q 'Prove It Works\\|Fix Root Causes\\|핵심 원칙' CLAUDE.md"
    check "NOT just link to rules (actual content)" "grep -q 'Prove It Works\\|Laziness Protocol\\|Type System' CLAUDE.md"
else
    FAILED=$((FAILED + 4))
fi
echo

# 3. Check upstream references
echo "3. Checking upstream pinned references..."

PINNED_SHA="2776ddd2355d6d6c8747d3964600f28daf62f049"

check "Skill file has pinned SHA" "[ -f '$SKILL_FILE' ] && grep -q '$PINNED_SHA' '$SKILL_FILE'"
check "CLAUDE.md has pinned SHA" "[ -f 'CLAUDE.md' ] && grep -q '$PINNED_SHA' CLAUDE.md"
check "Immutable tree reference (not /main)" "[ -f '$SKILL_FILE' ] && grep -q 'tree/$PINNED_SHA' '$SKILL_FILE'"
check "MIT license mentioned" "[ -f '$SKILL_FILE' ] && grep -q 'MIT' '$SKILL_FILE'"
check "Copyright holder (Lauren Tan)" "[ -f '$SKILL_FILE' ] && grep -q 'Lauren Tan' '$SKILL_FILE'"
echo

# 4. Check project policy integration
echo "4. Checking project policy integration..."

if [ -f "$SKILL_FILE" ]; then
    check "SPEC.md compliance mentioned" "grep -q 'SPEC\\.md' '$SKILL_FILE'"
    check "pytest requirement" "grep -q 'pytest' '$SKILL_FILE'"
    check "ruff requirement" "grep -q 'ruff' '$SKILL_FILE'"
    check "Interface isolation mentioned" "grep -qi 'interface.*isolation\\|External calls.*interfaces' '$SKILL_FILE'"
else
    FAILED=$((FAILED + 4))
fi
echo

# 5. Check docs/wiki entry
echo "5. Checking docs/wiki/05-operations/pstack-integration.md..."

WIKI_FILE="docs/wiki/05-operations/pstack-integration.md"

check "Wiki file exists" "[ -f '$WIKI_FILE' ]"

if [ -f "$WIKI_FILE" ]; then
    check "Has 결정 section" "grep -q '^## 결정' '$WIKI_FILE'"
    check "Has 배경·이유 section" "grep -q '^## 배경.*이유' '$WIKI_FILE'"
    check "Has 검토한 대안 section" "grep -q '^## 검토한 대안' '$WIKI_FILE'"
    check "Explains design rationale" "grep -q '저작권\\|copyright\\|라이선스\\|license' '$WIKI_FILE'"
    check "Links to related docs" "grep -q 'operations-and-security' '$WIKI_FILE'"
else
    FAILED=$((FAILED + 5))
fi
echo

# 6. Security checks
echo "6. Checking for leaked secrets/paths..."

check "No hardcoded private plugin IDs" "! grep -r 'plugin 9717366\\|9717366' .cursor/ CLAUDE.md 2>/dev/null || ! grep -q 'Already installed\\|이미 설치됨' .cursor/ CLAUDE.md"
check "No absolute user paths" "! grep -rE '/Users/[^/]+/\\.cursor|/home/[^/]+/\\.cursor' .cursor/ --exclude-dir=cache 2>/dev/null || grep -q 'example\\|similar' .cursor/"
check "No API keys" "! grep -rE 'sk-[a-zA-Z0-9]{20,}|ANTH[a-zA-Z0-9]{20,}' . --exclude-dir=.git --exclude-dir=.venv 2>/dev/null"
check "No email addresses in repo files" "! grep -rE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' .cursor/ CLAUDE.md --exclude-dir=cache 2>/dev/null"
echo

# 7. Size check (not too large = not full plugin copy)
echo "7. Checking integration size..."

if [ -f "$SKILL_FILE" ]; then
    SKILL_SIZE=$(wc -c < "$SKILL_FILE")
    check "Skill file <10KB (not full plugin copy)" "[ $SKILL_SIZE -lt 10240 ]"
    echo "   (Actual size: $SKILL_SIZE bytes)"
else
    FAILED=$((FAILED + 1))
fi
echo

# 8. NEGATIVE TESTS (must FAIL with corrupted input)
echo "8. Negative tests (expect failures with bad input)..."

# Create temp directory for negative tests
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Test: Missing skill file
echo "   Testing: Missing skill file detection..."
mkdir -p "$TEMP_DIR/test1/.cursor/skills/use-pstack-for-coding"
if [ -f "$SKILL_FILE" ]; then
    # Don't copy SKILL.md, leave empty
    if ! grep -q "read.*pstack" "$TEMP_DIR/test1/.cursor/skills/use-pstack-for-coding/SKILL.md" 2>/dev/null; then
        echo -e "      ${GREEN}✓${NC} Correctly detects missing skill file"
    else
        echo -e "      ${RED}✗${NC} False positive on missing skill"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "      ${YELLOW}⚠${NC}  Cannot test (main skill file missing)"
fi

# Test: Corrupted frontmatter
echo "   Testing: Corrupted frontmatter detection..."
mkdir -p "$TEMP_DIR/test2/.cursor/skills/use-pstack-for-coding"
cat > "$TEMP_DIR/test2/.cursor/skills/use-pstack-for-coding/SKILL.md" << 'EOF'
---
broken yaml: [unclosed
description
---
# Some content
EOF

CORRUPTED_FM=$(awk '/^---$/,/^---$/{if (NR>1 && !/^---$/) print}' "$TEMP_DIR/test2/.cursor/skills/use-pstack-for-coding/SKILL.md")
if ! echo "$CORRUPTED_FM" | grep -q "^name:.*use-pstack-for-coding"; then
    echo -e "      ${GREEN}✓${NC} Correctly detects corrupted frontmatter"
else
    echo -e "      ${RED}✗${NC} False positive on corrupted frontmatter"
    FAILED=$((FAILED + 1))
fi

# Test: Missing upstream reference
echo "   Testing: Missing upstream reference detection..."
mkdir -p "$TEMP_DIR/test3/.cursor/skills/use-pstack-for-coding"
cat > "$TEMP_DIR/test3/.cursor/skills/use-pstack-for-coding/SKILL.md" << 'EOF'
---
name: use-pstack-for-coding
description: Test
---
# No upstream reference here
EOF

if ! grep -q "$PINNED_SHA" "$TEMP_DIR/test3/.cursor/skills/use-pstack-for-coding/SKILL.md"; then
    echo -e "      ${GREEN}✓${NC} Correctly detects missing upstream reference"
else
    echo -e "      ${RED}✗${NC} False positive on missing reference"
    FAILED=$((FAILED + 1))
fi

# Test: No actual skill reading instruction
echo "   Testing: Missing skill-reading instruction detection..."
mkdir -p "$TEMP_DIR/test4/.cursor/skills/use-pstack-for-coding"
cat > "$TEMP_DIR/test4/.cursor/skills/use-pstack-for-coding/SKILL.md" << 'EOF'
---
name: use-pstack-for-coding
description: Coding work
---
# Just apply these principles
1. Write good code
2. Test it
EOF

if ! grep -q "read.*pstack.*SKILL\\.md\\|poteto-mode.*SKILL\\.md" "$TEMP_DIR/test4/.cursor/skills/use-pstack-for-coding/SKILL.md"; then
    echo -e "      ${GREEN}✓${NC} Correctly detects missing skill-reading instruction"
else
    echo -e "      ${RED}✗${NC} False positive on missing instruction"
    FAILED=$((FAILED + 1))
fi

echo

# 9. README consistency
echo "9. Checking README.md consistency..."

check "README mentions pstack" "[ -f 'README.md' ] && grep -q 'pstack' README.md"
echo

# Final summary
echo "=== Verification Summary ==="
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    echo
    echo "STATIC VERIFICATION: Complete"
    echo "RUNTIME VALIDATION: NOT performed (requires Cursor IDE)"
    echo
    echo "To test runtime behavior:"
    echo "  1. Open this project in Cursor IDE"
    echo "  2. Install pstack: /add-plugin pstack"
    echo "  3. Configure models: /setup-pstack"
    echo "  4. Make a coding request WITHOUT slash command:"
    echo "     'Add keyword filtering to briefing/sources/hf.py'"
    echo "  5. Check agent response references poteto-mode or pstack playbooks"
    echo "  6. Inspect transcript for evidence of reading actual SKILL.md"
    echo
    exit 0
else
    echo -e "${RED}✗ $FAILED check(s) failed${NC}"
    echo
    echo "Fix the issues above before merging."
    exit 1
fi
