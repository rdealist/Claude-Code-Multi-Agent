# Development Work Document

> **Format**: Follow `.claude/output-styles/bullet-points.md`

## Current Tasks
- [x] GitHub repository management setup
- [ ] Claude Code workflow optimization
  - [x] Fix .mcp.json cross-platform compatibility
  - [x] Create secure credentials management
  - [x] Optimize documents (simplify, English)

## Task Details
- Claude Code workflow optimization
  - Status: In progress
  - Files: `.mcp.json`, `.env.example`, `project_document/`, `CLAUDE.md`
  - Description: Cross-platform compat, secure credentials, doc optimization

## Recently Completed
- [2026-01-17] Document optimization
  - Rewrote CLAUDE.md in English, reduced from 92 to 68 lines
  - Simplified output-styles templates
  - Converted project_document to English
- [2026-01-17] Secure credentials management
  - Updated .env.example with MCP credentials template
  - MySQL/Redis/Magic API configuration
- [2026-01-17] Fixed .mcp.json cross-platform compatibility
  - Removed Windows commands (`cmd /c`) for direct npx/uvx
  - Locked MCP server versions (avoid @latest)
  - Sensitive credentials via environment variables
- [2026-01-13] GitHub repository management setup
  - Issue templates (Bug, Feature, Skill, Question)
  - PR template and contribution guidelines
  - Automated Workflows (CI, Stale, Welcome, Auto-label, Release, Sync-upstream)

## Issues Encountered
- None

## Technical Decisions
- Use GitHub Actions for CI/CD and automation
- Use YAML format for Issue templates for better form experience
- Upstream sync via PR instead of direct merge to avoid conflicts
- Lock MCP versions for stability
- Use environment variables for sensitive credentials

---
*Maintained by Claude Code*
