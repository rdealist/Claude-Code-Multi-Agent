# Changelog

> **Format**: Follow `.claude/output-styles/bullet-points.md`
> **Commits**: Follow commitlint convention (type(scope): subject)

## [2026-01-17]
### Changed
- refactor(docs): Rewrite core documents in English for token efficiency
  - CLAUDE.md: Simplified from 92 to 68 lines
  - output-styles/*.md: Condensed templates
  - project_document/*.md: Converted to English
- refactor(mcp): Restructure .mcp.json for cross-platform compatibility
  - Remove Windows command wrappers (`cmd /c`)
  - Lock MCP server versions
  - Use environment variables for credentials
- feat(config): Extend .env.example with MCP credentials
  - MySQL/Redis/Magic API templates
  - Filesystem path configuration

## [2026-01-13]
### Added
- feat(github): Add complete GitHub repository management
  - Issue templates: bug_report.yml, feature_request.yml, skill_request.yml, question.yml
  - PR template: PULL_REQUEST_TEMPLATE.md
  - Contribution guides: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
  - Automated Workflows:
    - ci.yml - CI pipeline (lint, test, validate)
    - stale.yml - Auto-cleanup stale Issues/PRs
    - welcome.yml - Welcome new contributors
    - auto-label.yml - Auto-labeling
    - release.yml - Release automation
    - sync-upstream.yml - Upstream sync mechanism
  - Bot config: dependabot.yml
  - Label definitions: labels.yml
  - Sponsor config: FUNDING.yml

---
*Maintained by Claude Code*
