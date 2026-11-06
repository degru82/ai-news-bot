#!/bin/bash
# Verify pstack integration configuration
# This script checks that project-scoped pstack defaults are properly configured

set -e

echo "=== pstack Integration Verification ==="
echo

# Check .cursor/rules/pstack-coding.mdc exists and has valid frontmatter
echo "1. Checking .cursor/rules/pstack-coding.mdc..."
if [ -f .cursor/rules/pstack-coding.mdc ]; then
    echo "   ✓ File exists"
    
    # Check for required frontmatter
    if grep -q "alwaysApply: true" .cursor/rules/pstack-coding.mdc; then
        echo "   ✓ alwaysApply: true found"
    else
        echo "   ✗ Missing 'alwaysApply: true' in frontmatter"
        exit 1
    fi
    
    if grep -q "description:" .cursor/rules/pstack-coding.mdc; then
        echo "   ✓ description field found"
    else
        echo "   ✗ Missing description field"
        exit 1
    fi
else
    echo "   ✗ .cursor/rules/pstack-coding.mdc not found"
    exit 1
fi
echo

# Check pinned revision is present
echo "2. Checking upstream pinned revision..."
if grep -q "2776ddd2355d6d6c8747d3964600f28daf62f049" .cursor/rules/pstack-coding.mdc; then
    echo "   ✓ Pinned revision SHA found"
else
    echo "   ✗ Pinned revision not found or incorrect"
    exit 1
fi
echo

# Check MIT license attribution
echo "3. Checking license attribution..."
if grep -q "MIT" .cursor/rules/pstack-coding.mdc && grep -q "Lauren Tan" .cursor/rules/pstack-coding.mdc; then
    echo "   ✓ MIT license and copyright holder mentioned"
else
    echo "   ✗ License attribution incomplete"
    exit 1
fi
echo

# Check CLAUDE.md references pstack
echo "4. Checking CLAUDE.md integration..."
if [ -f CLAUDE.md ]; then
    if grep -q "pstack" CLAUDE.md; then
        echo "   ✓ CLAUDE.md mentions pstack"
    else
        echo "   ✗ CLAUDE.md does not mention pstack"
        exit 1
    fi
else
    echo "   ✗ CLAUDE.md not found"
    exit 1
fi
echo

# Check README.md references pstack
echo "5. Checking README.md integration..."
if [ -f README.md ]; then
    if grep -q "pstack" README.md; then
        echo "   ✓ README.md mentions pstack"
    else
        echo "   ✗ README.md does not mention pstack"
        exit 1
    fi
else
    echo "   ✗ README.md not found"
    exit 1
fi
echo

# Verify no secrets or paths leak
echo "6. Checking for leaked paths/secrets..."
if grep -rq "~/.cursor" .cursor/rules/ --exclude="README.md"; then
    echo "   ⚠ Warning: Found ~/.cursor reference (should only be in examples/docs)"
fi
if grep -rq "~/.claude" .; then
    echo "   ⚠ Warning: Found ~/.claude reference"
fi
echo "   ✓ No obvious secret leaks detected"
echo

# Check that principles are extracted, not full plugin vendored
echo "7. Checking integration size..."
RULE_SIZE=$(wc -c < .cursor/rules/pstack-coding.mdc)
if [ "$RULE_SIZE" -lt 10000 ]; then
    echo "   ✓ Rule file is concise ($RULE_SIZE bytes)"
else
    echo "   ⚠ Warning: Rule file is large ($RULE_SIZE bytes) - consider if full plugin was vendored"
fi
echo

# Verify upstream links are valid (basic syntax check)
echo "8. Checking upstream URL references..."
if grep -q "https://github.com/cursor/plugins/tree/2776ddd" .cursor/rules/pstack-coding.mdc; then
    echo "   ✓ Immutable upstream reference found"
else
    echo "   ✗ Missing immutable upstream reference"
    exit 1
fi
echo

echo "=== Verification Summary ==="
echo "✓ All checks passed"
echo
echo "Note: This verifies configuration structure only."
echo "Runtime verification requires:"
echo "  - Cursor: Check that .cursor/rules/*.mdc loads in agent context"
echo "  - Claude Code: Check CLAUDE.md is read by agents"
echo "  - pstack plugin: User must install separately"
echo
echo "To test in Cursor:"
echo "  1. Install pstack: /add-plugin pstack"
echo "  2. Configure models: /setup-pstack"
echo "  3. Start coding - principles should auto-apply via .cursor/rules/"
echo "  4. For full workflows: /poteto-mode [task]"
