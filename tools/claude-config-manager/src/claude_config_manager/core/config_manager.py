"""Configuration manager for reading, writing, and merging configurations."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .models import ExportedConfig, ExportMetadata, MCPConfig

if TYPE_CHECKING:
    pass


class ConfigManager:
    """Manages Claude Code configuration files."""

    def __init__(self, project_path: Path | None = None):
        """Initialize with optional project path."""
        self.project_path = project_path or Path.cwd()
        self.mcp_config_path = self.project_path / ".mcp.json"
        self.claude_dir = self.project_path / ".claude"
        self.skills_dir = self.claude_dir / "skills"
        self.hooks_dir = self.claude_dir / "hooks"
        self.output_styles_dir = self.claude_dir / "output-styles"
        self.env_example_path = self.project_path / ".env.example"

    def has_config(self) -> bool:
        """Check if project has Claude Code configuration."""
        return self.mcp_config_path.exists() or self.claude_dir.exists()

    def read_mcp_config(self) -> MCPConfig:
        """Read MCP configuration from project."""
        return MCPConfig.from_file(self.mcp_config_path)

    def write_mcp_config(self, config: MCPConfig) -> None:
        """Write MCP configuration to project."""
        config.to_file(self.mcp_config_path)

    def list_skills(self) -> list[str]:
        """List all installed skills."""
        if not self.skills_dir.exists():
            return []
        return [
            d.name
            for d in self.skills_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    def list_hooks(self) -> list[str]:
        """List all hooks."""
        if not self.hooks_dir.exists():
            return []
        return [f.name for f in self.hooks_dir.iterdir() if f.is_file()]

    def list_output_styles(self) -> list[str]:
        """List all output styles."""
        if not self.output_styles_dir.exists():
            return []
        return [f.name for f in self.output_styles_dir.iterdir() if f.is_file()]

    def backup(self, suffix: str | None = None) -> Path:
        """Create backup of current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = suffix or timestamp
        backup_dir = self.project_path / f".backup-claude-{suffix}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup .mcp.json
        if self.mcp_config_path.exists():
            shutil.copy2(self.mcp_config_path, backup_dir / ".mcp.json")

        # Backup .claude directory
        if self.claude_dir.exists():
            shutil.copytree(
                self.claude_dir,
                backup_dir / ".claude",
                dirs_exist_ok=True,
            )

        # Backup .env.example
        if self.env_example_path.exists():
            shutil.copy2(self.env_example_path, backup_dir / ".env.example")

        return backup_dir

    def restore_from_backup(self, backup_dir: Path) -> None:
        """Restore configuration from backup."""
        mcp_backup = backup_dir / ".mcp.json"
        claude_backup = backup_dir / ".claude"
        env_backup = backup_dir / ".env.example"

        if mcp_backup.exists():
            shutil.copy2(mcp_backup, self.mcp_config_path)

        if claude_backup.exists():
            if self.claude_dir.exists():
                shutil.rmtree(self.claude_dir)
            shutil.copytree(claude_backup, self.claude_dir)

        if env_backup.exists():
            shutil.copy2(env_backup, self.env_example_path)

    def merge_config(
        self,
        source: ConfigManager,
        strategy: str = "overwrite",
        mcp_servers: list[str] | None = None,
        skills: list[str] | None = None,
    ) -> None:
        """
        Merge configuration from source into this project.

        Args:
            source: Source configuration manager
            strategy: 'overwrite' (backup and replace) or 'merge' (combine)
            mcp_servers: Specific MCP servers to include (None = all)
            skills: Specific skills to include (None = all)
        """
        # Always backup first
        self.backup()

        # Handle MCP config
        source_mcp = source.read_mcp_config()
        if mcp_servers:
            source_mcp = source_mcp.filter_servers(mcp_servers)

        if strategy == "merge" and self.mcp_config_path.exists():
            current_mcp = self.read_mcp_config()
            merged_mcp = current_mcp.merge(source_mcp)
            self.write_mcp_config(merged_mcp)
        else:
            self.write_mcp_config(source_mcp)

        # Handle skills
        source_skills = skills or source.list_skills()
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        for skill in source_skills:
            source_skill_dir = source.skills_dir / skill
            if source_skill_dir.exists():
                target_skill_dir = self.skills_dir / skill
                if target_skill_dir.exists():
                    shutil.rmtree(target_skill_dir)
                shutil.copytree(source_skill_dir, target_skill_dir)

        # Copy hooks if not exists
        if source.hooks_dir.exists() and not self.hooks_dir.exists():
            shutil.copytree(source.hooks_dir, self.hooks_dir)

        # Copy output styles if not exists
        if source.output_styles_dir.exists() and not self.output_styles_dir.exists():
            shutil.copytree(source.output_styles_dir, self.output_styles_dir)

        # Copy .env.example if not exists
        if source.env_example_path.exists() and not self.env_example_path.exists():
            shutil.copy2(source.env_example_path, self.env_example_path)

    def export_config(
        self,
        output_path: Path,
        profile_name: str | None = None,
        mcp_servers: list[str] | None = None,
        skills: list[str] | None = None,
    ) -> ExportedConfig:
        """Export configuration to a single file."""
        mcp_config = self.read_mcp_config()
        if mcp_servers:
            mcp_config = mcp_config.filter_servers(mcp_servers)

        selected_skills = skills or self.list_skills()

        # Read env template
        env_template = {}
        if self.env_example_path.exists():
            with open(self.env_example_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_template[key.strip()] = value.strip()

        exported = ExportedConfig(
            metadata=ExportMetadata(
                profile=profile_name,
                source_path=str(self.project_path),
            ),
            mcp_config=mcp_config.model_dump(exclude_none=True),
            skills=selected_skills,
            env_template=env_template,
            hooks=self.list_hooks(),
            output_styles=self.list_output_styles(),
        )

        exported.to_file(output_path)
        return exported

    def import_config(self, config_path: Path, strategy: str = "overwrite") -> None:
        """Import configuration from exported file."""
        exported = ExportedConfig.from_file(config_path)

        # Backup first
        self.backup()

        # Write MCP config
        mcp_config = MCPConfig.model_validate(exported.mcp_config)
        if strategy == "merge" and self.mcp_config_path.exists():
            current = self.read_mcp_config()
            mcp_config = current.merge(mcp_config)
        self.write_mcp_config(mcp_config)

        # Update .env.example
        if exported.env_template:
            self._update_env_example(exported.env_template)

    def _update_env_example(self, template: dict[str, str]) -> None:
        """Update .env.example with template values."""
        existing = {}
        if self.env_example_path.exists():
            with open(self.env_example_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        existing[key.strip()] = value.strip()

        merged = {**existing, **template}

        with open(self.env_example_path, "w", encoding="utf-8") as f:
            f.write("# Claude Code Configuration Environment Variables\n\n")
            for key, value in sorted(merged.items()):
                f.write(f"{key}={value}\n")
