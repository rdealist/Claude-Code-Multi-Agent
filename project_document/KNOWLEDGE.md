# Project Knowledge Base

> **Format**: Follow `.claude/output-styles/markdown-focused.md`

## Code Patterns

### MCP Configuration Pattern
- **Cross-platform**: Use `npx`/`uvx` directly, no shell wrappers
- **Version locking**: Pin versions to avoid `@latest` instability
- **Credentials**: Reference env vars via `${ENV_VAR:-default}` syntax

### Document Optimization Pattern
- **Language**: Write prompts/docs in English for token efficiency
- **Conciseness**: Minimize redundancy while preserving semantics
- **Structure**: Use tables and lists over prose

## FAQ

### Q: MCP server won't start on different platforms?
A: Check if `.mcp.json` uses platform-specific commands (e.g., `cmd /c`). Use cross-platform `npx` or `uvx` instead.

### Q: How to manage database passwords securely?
A: Store sensitive info in `.env` file. Reference in `.mcp.json` via `${MYSQL_PASS}` syntax.

### Q: Why write documents in English?
A: English uses fewer tokens than CJK characters, reducing prompt size and improving context efficiency.

## Technical Decision Records

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

## Resources
- [MCP Protocol Docs](https://modelcontextprotocol.io/)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)

---
*Maintained by Claude Code*
