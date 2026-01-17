"""Profile manager for handling configuration profiles."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from .config_manager import ConfigManager
from .models import ProfileConfig, ProfilesFile


class ProfileManager:
    """Manages configuration profiles (full, frontend, backend, algorithm)."""

    def __init__(self, profiles_file: Path | None = None):
        """Initialize with optional custom profiles file."""
        if profiles_file and profiles_file.exists():
            self.profiles = ProfilesFile.from_file(profiles_file)
        else:
            # Load bundled profiles.json
            self.profiles = self._load_bundled_profiles()

    def _load_bundled_profiles(self) -> ProfilesFile:
        """Load the bundled profiles.json from package."""
        try:
            with resources.files("claude_config_manager").joinpath(
                "profiles.json"
            ).open("r") as f:
                import json

                data = json.load(f)
                return ProfilesFile.model_validate(data)
        except Exception:
            # Return empty profiles if bundled file not found
            return ProfilesFile(
                version="1.0.0",
                description="Default profiles",
                profiles={},
            )

    def list_profiles(self) -> list[str]:
        """List available profile names."""
        return list(self.profiles.profiles.keys())

    def get_profile(self, name: str) -> ProfileConfig | None:
        """Get profile configuration by name."""
        return self.profiles.profiles.get(name)

    def get_skill_dependencies(self, skill: str) -> list[str]:
        """Get MCP server dependencies for a skill."""
        return self.profiles.dependencies.skills.get(skill, [])

    def resolve_dependencies(self, skills: list[str]) -> list[str]:
        """Resolve all MCP server dependencies for given skills."""
        mcp_servers = set()
        for skill in skills:
            deps = self.get_skill_dependencies(skill)
            mcp_servers.update(deps)
        return list(mcp_servers)

    def validate_selection(
        self, mcp_servers: list[str], skills: list[str]
    ) -> list[str]:
        """
        Validate that all skill dependencies are satisfied.
        Returns list of missing MCP servers.
        """
        required = self.resolve_dependencies(skills)
        missing = [s for s in required if s not in mcp_servers]
        return missing

    def create_project(
        self,
        target_path: Path,
        source: ConfigManager,
        profile_name: str = "full",
        init_git: bool = False,
    ) -> None:
        """
        Create a new project with specified profile.

        Args:
            target_path: Path for new project
            source: Source configuration manager
            profile_name: Profile to use (full, frontend, backend, algorithm)
            init_git: Whether to initialize git repository
        """
        profile = self.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Unknown profile: {profile_name}")

        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)

        # Create target config manager
        target = ConfigManager(target_path)

        # Merge with profile filter
        target.merge_config(
            source=source,
            strategy="overwrite",
            mcp_servers=profile.mcpServers,
            skills=profile.skills,
        )

        # Generate README documentation
        self._generate_readme(target_path, profile_name, profile)

        # Initialize git if requested
        if init_git:
            import subprocess

            subprocess.run(
                ["git", "init"],
                cwd=target_path,
                capture_output=True,
                check=True,
            )

            # Create .gitignore
            gitignore_path = target_path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_path.write_text(
                    ".env\n.backup-*\n__pycache__/\n*.pyc\nnode_modules/\n"
                )

    def _generate_readme(
        self, target_path: Path, profile_name: str, profile: ProfileConfig
    ) -> None:
        """Generate CLAUDE-CONFIG.md documentation for the project."""
        mcp_list = "\n".join(f"- {s}" for s in profile.mcpServers)
        skills_list = "\n".join(f"- {s}" for s in profile.skills)
        env_vars_section = ""
        if profile.requiredEnvVars:
            env_examples = "\n".join(
                f"{var}=your_value_here" for var in profile.requiredEnvVars
            )
            env_vars_section = f"""
## Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
{env_examples}
```

**Important**: Never commit `.env` to version control. Use `.env.example` as a template.
"""

        readme_content = f"""# Claude Code Configuration

This project is configured with Claude Code using the **{profile_name}** profile.

## Directory Structure

```
.
├── .mcp.json           # MCP server configuration
├── .claude/
│   ├── skills/         # AI skill definitions ({len(profile.skills)} skills)
│   ├── hooks/          # Automation hooks
│   └── output-styles/  # Output formatting templates
├── .env.example        # Environment variable template
└── .gitignore          # Git ignore rules
```

## Installed MCP Servers ({len(profile.mcpServers)})

{mcp_list}

## Installed Skills ({len(profile.skills)})

{skills_list}
{env_vars_section}
## Customization Guide

### Modifying MCP Servers

Edit `.mcp.json` to add, remove, or configure MCP servers:

```json
{{
  "mcpServers": {{
    "server-name": {{
      "command": "npx",
      "args": ["-y", "package-name@latest"],
      "env": {{}}
    }}
  }}
}}
```

### Adding New Skills

1. Create a new directory under `.claude/skills/your-skill-name/`
2. Add a markdown file with the skill definition
3. Skills are automatically loaded by Claude Code

### Modifying Existing Skills

Edit files in `.claude/skills/` to customize AI behavior and workflows.

## Quick Start

1. Copy `.env.example` to `.env` and fill in required values
2. Open this project in Claude Code
3. Use `/skill-name` to invoke specific skills

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io)

---
*Generated by Claude Config Manager - Profile: {profile_name}*
"""
        readme_path = target_path / "CLAUDE-CONFIG.md"
        readme_path.write_text(readme_content)

    def get_profile_summary(self, name: str) -> dict:
        """Get summary of a profile for display."""
        profile = self.get_profile(name)
        if not profile:
            return {}

        return {
            "name": profile.name,
            "description": profile.description,
            "mcp_count": len(profile.mcpServers),
            "skill_count": len(profile.skills),
            "env_vars": profile.requiredEnvVars,
            "mcp_servers": profile.mcpServers,
            "skills": profile.skills,
        }
