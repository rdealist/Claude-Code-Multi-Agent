# Claude Config Manager

TUI tool for managing Claude Code project configurations.

## Features

- **Create New Projects**: Initialize new projects with predefined profiles (full/frontend/backend/algorithm)
- **Import Configuration**: Import Claude Code config to existing projects with conflict handling
- **Custom Installation**: Select specific MCP servers and Skills to install
- **Validation**: Verify configuration integrity and dependencies
- **Git Sync**: Synchronize configurations with remote repositories
- **Export/Import**: Export configuration to single file for sharing

## Installation

```bash
cd tools/claude-config-manager
pip install -e .
```

## Usage

### TUI Mode (Interactive)

```bash
ccm
```

### CLI Commands

```bash
# Show current configuration
ccm info

# Validate configuration
ccm validate

# Create new project
ccm create --target /path/to/new/project --profile frontend

# Import to existing project
ccm import-config --target /path/to/project --profile backend

# Export configuration
ccm export --output my-config.json --profile full

# Git remote management
ccm git add company-configs https://github.com/org/claude-configs.git
ccm git list
ccm git pull company-configs --profile frontend
ccm git push company-configs -m "Update config"
```

## Profiles

| Profile | Description | MCP Servers | Skills |
|---------|-------------|-------------|--------|
| `full` | Complete configuration | 13 | 20 |
| `frontend` | UI/UX development | 9 | 8 |
| `backend` | Server/database development | 8 | 8 |
| `algorithm` | AI/reasoning tasks | 6 | 7 |

## Configuration Structure

```
project/
├── .mcp.json           # MCP server configuration
├── .env.example        # Environment variable template
└── .claude/
    ├── skills/         # Claude Code skills
    ├── hooks/          # Git hooks
    ├── output-styles/  # Output formatting templates
    └── settings.json   # Claude settings
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
