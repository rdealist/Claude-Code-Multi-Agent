"""Configuration data models using Pydantic."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class MCPServer(BaseModel):
    """MCP server configuration."""

    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    type: str | None = None
    timeout: int | None = None
    autoApprove: list[str] = Field(default_factory=list)


class MCPConfig(BaseModel):
    """MCP configuration file structure."""

    mcpServers: dict[str, MCPServer] = Field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> MCPConfig:
        """Load configuration from file."""
        if not path.exists():
            return cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    def to_file(self, path: Path) -> None:
        """Save configuration to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(exclude_none=True), f, indent=2, ensure_ascii=False)
            f.write("\n")

    def filter_servers(self, names: list[str]) -> MCPConfig:
        """Filter to only include specified servers."""
        return MCPConfig(
            mcpServers={k: v for k, v in self.mcpServers.items() if k in names}
        )

    def merge(self, other: MCPConfig) -> MCPConfig:
        """Merge with another config, other takes precedence."""
        merged = {**self.mcpServers, **other.mcpServers}
        return MCPConfig(mcpServers=merged)


class ProfileConfig(BaseModel):
    """Profile configuration for a specific use case."""

    name: str
    description: str
    mcpServers: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    requiredEnvVars: list[str] = Field(default_factory=list)


class SkillDependencies(BaseModel):
    """Skill to MCP server dependencies."""

    skills: dict[str, list[str]] = Field(default_factory=dict)


class ProfilesFile(BaseModel):
    """Complete profiles.json structure."""

    version: str
    description: str
    profiles: dict[str, ProfileConfig] = Field(default_factory=dict)
    dependencies: SkillDependencies = Field(default_factory=SkillDependencies)

    @classmethod
    def from_file(cls, path: Path) -> ProfilesFile:
        """Load profiles from file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)


class ExportMetadata(BaseModel):
    """Metadata for exported configurations."""

    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    source: str = "claude-config-manager"
    profile: str | None = None
    source_path: str | None = None


class ExportedConfig(BaseModel):
    """Complete exported configuration package."""

    metadata: ExportMetadata
    mcp_config: dict[str, Any]
    skills: list[str]
    env_template: dict[str, str] = Field(default_factory=dict)
    hooks: list[str] = Field(default_factory=list)
    output_styles: list[str] = Field(default_factory=list)

    def to_file(self, path: Path) -> None:
        """Save exported config to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                self.model_dump(mode="json"),
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )
            f.write("\n")

    @classmethod
    def from_file(cls, path: Path) -> ExportedConfig:
        """Load exported config from file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)
