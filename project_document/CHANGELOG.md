# Changelog

> **Format**: Follow `.claude/output-styles/bullet-points.md`
> **Commits**: Follow commitlint convention (type(scope): subject)

## [2026-01-18]
### Added
- feat(branch): Create domain-specific configuration branches
  - `frontend`: playwright, magic-ui, chrome-devtools, magic
  - `backend`: mysql, redis-mcp, docker
  - `algorithm`: Context7, Sequential Thinking, Shrimp Task Manager

### Changed
- chore(mcp): Restore @latest versions for all MCP servers
- docs(readme): Add branch strategy documentation

## [2026-01-17]
### Changed
- refactor(docs): Restructure README and documentation for better usability
  - README.md: Reduced from 1000+ to ~350 lines, quick start focused
  - Created modular docs/ structure with 5 detailed guides
  - docs/SKILLS.md: Comprehensive reference for all 22 Skills
  - docs/INSTALLATION.md: Detailed installation and configuration guide
  - docs/MCP_TOOLS.md: Complete MCP servers documentation (13 servers)
  - docs/HOOKS.md: Hooks system guide with practical examples
  - docs/TROUBLESHOOTING.md: Common issues and solutions
  - Organized Skills into 9 technical domain categories
  - Target audience: experienced developers, actionable content
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
