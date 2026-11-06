# Cursor Rules

This directory contains always-applied rules for Cursor agents.

## Files

- **pstack-coding.mdc**: Applies pstack principles and workflows to substantive coding tasks

## How Rules Work

Cursor automatically loads `.mdc` files from this directory and applies them to agent context when `alwaysApply: true` is set in frontmatter.

These rules are project-scoped and committed to the repository, so all contributors benefit from the same coding standards.

For user-specific rules (not committed), use `~/.cursor/rules/` on your local machine.

## Documentation

- Cursor rules: https://cursor.com/docs/context/rules-for-ai
- pstack integration: See CLAUDE.md for setup instructions
