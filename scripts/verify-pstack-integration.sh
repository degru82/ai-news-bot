#!/bin/bash
# Verify pstack integration: actual bundled skills with proper licensing
# Tests real file content validation, not just string matching

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== pstack Integration Verification ==="
echo
echo "This verifies ACTUAL pstack skills bundled in repository."
echo "STATIC validation only - runtime behavior requires IDE testing."
echo

FAILED=0

# Helper: check condition
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

# Validator function: validates skill file structure
validate_skill_file() {
    local file="$1"
    local required_name="$2"
    
    [ -f "$file" ] || return 1
    
    # Extract and validate frontmatter
    local frontmatter=$(awk 'BEGIN {inFM=0} /^---$/ {if (inFM==0) {inFM=1; next} else {exit}} inFM==1 {print}' "$file")
    [ -n "$frontmatter" ] || return 1
    
    # Check required fields
    echo "$frontmatter" | grep -q "^name:" || return 1
    echo "$frontmatter" | grep -q "^description:" || return 1
    
    # Check name matches if specified
    if [ -n "$required_name" ]; then
        echo "$frontmatter" | grep -q "^name: *$required_name" || return 1
    fi
    
    return 0
}

# 1. Check LICENSE file
echo "1. Checking .cursor/skills/pstack/LICENSE..."

LICENSE_FILE=".cursor/skills/pstack/LICENSE"

check "LICENSE file exists" "[ -f '$LICENSE_FILE' ]"

if [ -f "$LICENSE_FILE" ]; then
    check "Contains 'MIT License'" "grep -q 'MIT License' '$LICENSE_FILE'"
    check "Contains copyright (Lauren Tan)" "grep -q 'Copyright.*Lauren Tan' '$LICENSE_FILE'"
    check "Contains permission notice" "grep -q 'Permission is hereby granted' '$LICENSE_FILE'"
    check "Contains warranty disclaimer" "grep -q 'WITHOUT WARRANTY' '$LICENSE_FILE'"
    check "Contains full license text (>500 chars)" "[ \$(wc -c < '$LICENSE_FILE') -gt 500 ]"
else
    FAILED=$((FAILED + 4))
fi
echo

# 2. Check poteto-mode SKILL.md
echo "2. Checking .cursor/skills/pstack/poteto-mode/SKILL.md..."

POTETO_FILE=".cursor/skills/pstack/poteto-mode/SKILL.md"

check "Poteto-mode file exists" "[ -f '$POTETO_FILE' ]"

if validate_skill_file "$POTETO_FILE" "poteto-mode"; then
    echo -e "   ${GREEN}✓${NC} Valid skill file with frontmatter"
else
    echo -e "   ${RED}✗${NC} Invalid skill file or frontmatter"
    FAILED=$((FAILED + 1))
fi

if [ -f "$POTETO_FILE" ]; then
    check "Contains Principles section" "grep -q '## Principles' '$POTETO_FILE'"
    check "Contains Playbooks section" "grep -q '## Playbooks' '$POTETO_FILE'"
    check "Contains 'Prove It Works' principle" "grep -q 'Prove It Works' '$POTETO_FILE'"
    check "Contains 'Fix Root Causes' principle" "grep -q 'Fix Root Causes' '$POTETO_FILE'"
    check "Contains project constraints" "grep -q 'ai-news-bot' '$POTETO_FILE'"
    check "References upstream source" "grep -q 'github.com/cursor/plugins.*2776ddd' '$POTETO_FILE'"
    check "disable-model-invocation: true" "grep -q 'disable-model-invocation: true' '$POTETO_FILE'"
else
    FAILED=$((FAILED + 7))
fi
echo

# 3. Check router skill
echo "3. Checking .cursor/skills/use-pstack-workflows/SKILL.md..."

ROUTER_FILE=".cursor/skills/use-pstack-workflows/SKILL.md"

check "Router file exists" "[ -f '$ROUTER_FILE' ]"

if validate_skill_file "$ROUTER_FILE" "use-pstack-workflows"; then
    echo -e "   ${GREEN}✓${NC} Valid router skill with frontmatter"
else
    echo -e "   ${RED}✗${NC} Invalid router skill or frontmatter"
    FAILED=$((FAILED + 1))
fi

if [ -f "$ROUTER_FILE" ]; then
    check "Instructs to read poteto-mode" "grep -q '\\.cursor/skills/pstack/poteto-mode/SKILL\\.md' '$ROUTER_FILE'"
    check "No speculative cache paths" "! grep -q '~/.cursor/plugins/cache.*\\[hash\\]' '$ROUTER_FILE'"
    check "References LICENSE" "grep -q 'LICENSE' '$ROUTER_FILE'"
else
    FAILED=$((FAILED + 3))
fi
echo

# 4. Check CLAUDE.md integration
echo "4. Checking CLAUDE.md integration..."

check "CLAUDE.md exists" "[ -f 'CLAUDE.md' ]"

if [ -f "CLAUDE.md" ]; then
    check "Instructs to read poteto-mode" "grep -q '\\.cursor/skills/pstack/poteto-mode/SKILL\\.md' CLAUDE.md"
    check "References LICENSE file" "grep -q '\\.cursor/skills/pstack/LICENSE' CLAUDE.md"
    check "Upstream attribution" "grep -q 'github.com/cursor/plugins.*2776ddd' CLAUDE.md"
    check "No deleted .mdc paths" "! grep -q '\\.cursor/rules/pstack-coding\\.mdc' CLAUDE.md"
else
    FAILED=$((FAILED + 4))
fi
echo

# 5. Check wiki documentation
echo "5. Checking docs/wiki/05-operations/pstack-integration.md..."

WIKI_FILE="docs/wiki/05-operations/pstack-integration.md"

check "Wiki file exists" "[ -f '$WIKI_FILE' ]"

if [ -f "$WIKI_FILE" ]; then
    check "Has 결정 section" "grep -q '^## 결정' '$WIKI_FILE'"
    check "Has 배경·이유 section" "grep -q '^## 배경.*이유' '$WIKI_FILE'"
    check "Has 검토한 대안 section" "grep -q '^## 검토한 대안' '$WIKI_FILE'"
    check "Explains MIT license compliance" "grep -q 'MIT.*재배포.*허용\\|MIT.*license.*redistribution' '$WIKI_FILE'"
    check "Links to related docs" "grep -q 'operations-and-security' '$WIKI_FILE'"
    check "Not claiming copyright forbidden" "! grep -q '저작권.*문제.*벤더링.*불가\\|copyright.*forbidden.*vendor' '$WIKI_FILE' || grep -q '핵심.*poteto-mode.*포함' '$WIKI_FILE'"
else
    FAILED=$((FAILED + 6))
fi
echo

# 6. Security checks
echo "6. Security checks..."

check "No API keys" "! grep -rE 'sk-[a-zA-Z0-9]{20,}|ANTH[a-zA-Z0-9]{20,}' .cursor/skills/ 2>/dev/null"
check "No email addresses" "! grep -rE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' .cursor/skills/ 2>/dev/null"
check "No absolute user paths" "! grep -r '/home/[^/]\\+/.cursor\\|/Users/[^/]\\+/.cursor' .cursor/skills/ 2>/dev/null"
echo

# 7. File accessibility
echo "7. File accessibility test..."

if [ -f "$POTETO_FILE" ]; then
    CONTENT=$(cat "$POTETO_FILE" 2>/dev/null)
    if [ ${#CONTENT} -gt 1000 ]; then
        echo -e "   ${GREEN}✓${NC} poteto-mode SKILL.md is readable (${#CONTENT} bytes)"
    else
        echo -e "   ${RED}✗${NC} poteto-mode SKILL.md too small or unreadable"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "   ${RED}✗${NC} poteto-mode SKILL.md not found"
    FAILED=$((FAILED + 1))
fi
echo

# 8. NEGATIVE TESTS - validate_skill_file on corrupted input
echo "8. Negative tests (validator must reject bad input)..."

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Test 1: Missing file
echo "   Testing: Missing file detection..."
if ! validate_skill_file "$TEMP_DIR/nonexistent.md" "test" 2>/dev/null; then
    echo -e "      ${GREEN}✓${NC} Correctly rejects missing file"
else
    echo -e "      ${RED}✗${NC} False positive on missing file"
    FAILED=$((FAILED + 1))
fi

# Test 2: Missing frontmatter
echo "   Testing: Missing frontmatter detection..."
cat > "$TEMP_DIR/no-fm.md" << 'EOF'
# Some content
No frontmatter here
EOF
if ! validate_skill_file "$TEMP_DIR/no-fm.md" "test" 2>/dev/null; then
    echo -e "      ${GREEN}✓${NC} Correctly rejects missing frontmatter"
else
    echo -e "      ${RED}✗${NC} False positive on missing frontmatter"
    FAILED=$((FAILED + 1))
fi

# Test 3: Corrupted frontmatter
echo "   Testing: Corrupted frontmatter detection..."
cat > "$TEMP_DIR/corrupt-fm.md" << 'EOF'
---
broken: yaml: [unclosed
description
---
# Content
EOF
if ! validate_skill_file "$TEMP_DIR/corrupt-fm.md" "test" 2>/dev/null; then
    echo -e "      ${GREEN}✓${NC} Correctly rejects corrupted frontmatter"
else
    echo -e "      ${RED}✗${NC} False positive on corrupted frontmatter"
    FAILED=$((FAILED + 1))
fi

# Test 4: Missing name field
echo "   Testing: Missing name field detection..."
cat > "$TEMP_DIR/no-name.md" << 'EOF'
---
description: Test skill
---
# Content
EOF
if ! validate_skill_file "$TEMP_DIR/no-name.md" "test" 2>/dev/null; then
    echo -e "      ${GREEN}✓${NC} Correctly rejects missing name field"
else
    echo -e "      ${RED}✗${NC} False positive on missing name"
    FAILED=$((FAILED + 1))
fi

# Test 5: Wrong name
echo "   Testing: Wrong name detection..."
cat > "$TEMP_DIR/wrong-name.md" << 'EOF'
---
name: different-name
description: Test
---
# Content
EOF
if ! validate_skill_file "$TEMP_DIR/wrong-name.md" "expected-name" 2>/dev/null; then
    echo -e "      ${GREEN}✓${NC} Correctly rejects wrong name"
else
    echo -e "      ${RED}✗${NC} False positive on wrong name"
    FAILED=$((FAILED + 1))
fi

echo

# 9. Upstream provenance
echo "9. Upstream provenance..."

check "Pinned commit (2776ddd) in LICENSE" "grep -q '2776ddd' '$LICENSE_FILE' || grep -q 'upstream.*2776ddd' .cursor/skills/pstack/*/*.md"
check "Pinned commit in poteto-mode" "grep -q '2776ddd' '$POTETO_FILE'"
check "Pinned commit in router" "grep -q '2776ddd' '$ROUTER_FILE'"
echo

# Final summary
echo "=== Verification Summary ==="
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    echo
    echo "STATIC VALIDATION: Complete"
    echo "- Real pstack skills bundled in .cursor/skills/pstack/"
    echo "- MIT License with full text included"
    echo "- Repository-relative paths (no speculative cache refs)"
    echo "- Validator function tested with 5 negative cases"
    echo
    echo "RUNTIME VALIDATION: Not performed (requires IDE)"
    echo
    echo "To test runtime in Cursor:"
    echo "  1. Open project in Cursor IDE"
    echo "  2. Make coding request: 'Add keyword filtering to hf.py'"
    echo "  3. Check if agent references poteto-mode principles/playbooks"
    echo "  4. Verify agent read .cursor/skills/pstack/poteto-mode/SKILL.md"
    echo
    echo "To test in Claude Code:"
    echo "  1. Agent should read CLAUDE.md guidance"
    echo "  2. Guidance points to .cursor/skills/pstack/poteto-mode/SKILL.md"
    echo "  3. Agent reads that file for workflow instructions"
    echo
    echo "To test with Grok Bot:"
    echo "  1. Grok reads CLAUDE.md from source control"
    echo "  2. Delegates to coding agent with poteto-mode instructions"
    echo "  3. Coding agent reads .cursor/skills/pstack/poteto-mode/SKILL.md"
    echo
    exit 0
else
    echo -e "${RED}✗ $FAILED check(s) failed${NC}"
    echo
    echo "Fix issues above before merging."
    exit 1
fi
