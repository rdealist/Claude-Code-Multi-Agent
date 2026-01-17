# Project Knowledge Base

> **Format**: Follow `.claude/output-styles/markdown-focused.md`

## Code Patterns

### MCP Configuration Pattern
- **Cross-platform**: Use `npx`/`uvx` directly, no shell wrappers
- **Version strategy**: Use `@latest` for flexibility; branch-based configs for domain separation
- **Credentials**: Reference env vars via `${ENV_VAR:-default}` syntax

### Branch-Based Configuration Pattern
- **master**: Full configuration with all MCP servers
- **frontend**: UI-focused tools (playwright, magic-ui, chrome-devtools)
- **backend**: Server-focused tools (mysql, redis-mcp, docker)
- **algorithm**: AI/reasoning tools (Context7, Sequential Thinking, Shrimp Task Manager)
- **Rationale**: Reduces context overhead; each branch loads only relevant tools

### Document Optimization Pattern
- **Language**: Write prompts/docs in English for token efficiency
- **Conciseness**: Minimize redundancy while preserving semantics
- **Structure**: Use tables and lists over prose

### Documentation Architecture Pattern
- **Main README**: Quick start focused (~300-400 lines), no deep details
- **Modular docs/**: Separate detailed guides (SKILLS, INSTALLATION, MCP_TOOLS, HOOKS, TROUBLESHOOTING)
- **Skills organization**: Group by technical domain (Frontend, Backend, Data, Security, etc.)
- **Cross-referencing**: Link related sections across documents
- **Target audience**: Experienced developers, actionable content

## FAQ

### Q: How to choose the right branch?
A: Use `frontend` for UI development, `backend` for server/database work, `algorithm` for AI/reasoning tasks. Use `master` for full-stack or when unsure.

### Q: MCP server won't start on different platforms?
A: Check if `.mcp.json` uses platform-specific commands (e.g., `cmd /c`). Use cross-platform `npx` or `uvx` instead.

### Q: How to manage database passwords securely?
A: Store sensitive info in `.env` file. Reference in `.mcp.json` via `${MYSQL_PASS}` syntax.

### Q: Why write documents in English?
A: English uses fewer tokens than CJK characters, reducing prompt size and improving context efficiency.

### Q: How to organize Skills for better usability?
A: Group Skills by technical domain (Frontend, Backend, Data, Security, etc.) rather than alphabetically. This helps users quickly find relevant capabilities for their task type.

## Technical Decision Records

### Branch-Based MCP Configuration
- **Context**: Single `.mcp.json` loaded all 13 MCP servers regardless of task type
- **Decision**: Create domain-specific branches (frontend, backend, algorithm)
- **Reason**:
  - Reduce context overhead by loading only relevant tools
  - Faster startup for specialized workflows
  - Easier maintenance of domain-specific configurations

### MCP Version Strategy Change
- **Context**: Previously locked versions for stability
- **Decision**: Switch to `@latest` for all MCP servers
- **Reason**: User preference for latest features; branch separation reduces breaking change impact

### MCP Version Locking
- **Context**: `@latest` versions may cause unexpected breaking updates
- **Decision**: Lock major MCP servers to specific versions
- **Reason**: Ensure workflow stability; manual upgrade with compatibility testing

### Credential Environment Variables
- **Context**: `.mcp.json` stored database passwords in plaintext
- **Decision**: Move sensitive info to `.env`, reference via environment variables
- **Reason**: Prevent credential exposure in version control

### Document Language Standardization
- **Context**: Documents injected as prompts were in Chinese
- **Decision**: Rewrite core docs in English
- **Reason**: Token efficiency, broader compatibility, clearer semantics

### Modular Documentation Structure
- **Context**: Original README was 1000+ lines, difficult to navigate
- **Decision**: Split into main README (~350 lines) + separate detailed guides in docs/
- **Reason**: 
  - Improve discoverability: users can jump directly to relevant section
  - Reduce cognitive load: main README provides quick overview
  - Better maintainability: each guide can be updated independently
  - Progressive disclosure: beginners get quick start, experts get deep dives

### Skills Domain Classification
- **Context**: 22 Skills were presented in alphabetical order
- **Decision**: Organize into 9 technical domains (Frontend, Backend, Data, Security, Architecture, Project Management, Testing & Quality, Documentation & Tools, Other)
- **Reason**:
  - Task-oriented discovery: users think "I need backend help" not "I need backend-specialist"
  - Faster navigation: domain categories reduce search space
  - Better learning: grouping reveals related capabilities

## Resources
- [MCP Protocol Docs](https://modelcontextprotocol.io/)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)

---
*Maintained by Claude Code*
