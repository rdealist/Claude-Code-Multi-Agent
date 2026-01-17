"""Validator module for checking configuration integrity."""

from __future__ import annotations

import os
import stat
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .config_manager import ConfigManager
from .profile_manager import ProfileManager


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    category: str
    message: str
    details: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Complete validation report."""

    project_path: Path
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Check if all validations passed."""
        return all(r.passed for r in self.results)

    @property
    def error_count(self) -> int:
        """Count failed validations."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def success_count(self) -> int:
        """Count passed validations."""
        return sum(1 for r in self.results if r.passed)

    def summary(self) -> str:
        """Generate summary string."""
        return f"Validation: {self.success_count} passed, {self.error_count} failed"


class Validator:
    """Validates Claude Code configuration integrity."""

    def __init__(
        self,
        config_manager: ConfigManager,
        profile_manager: ProfileManager | None = None,
    ):
        """Initialize with configuration manager."""
        self.config = config_manager
        self.profiles = profile_manager or ProfileManager()

    def validate_all(self) -> ValidationReport:
        """Run all validation checks."""
        report = ValidationReport(project_path=self.config.project_path)

        # Check MCP configuration
        report.results.append(self._validate_mcp_config())

        # Check environment variables
        report.results.append(self._validate_env_vars())

        # Check skills directory
        report.results.append(self._validate_skills())

        # Check hooks
        report.results.append(self._validate_hooks())

        # Check skill dependencies
        report.results.append(self._validate_skill_dependencies())

        return report

    def _validate_mcp_config(self) -> ValidationResult:
        """Validate .mcp.json exists and is valid."""
        if not self.config.mcp_config_path.exists():
            return ValidationResult(
                passed=False,
                category="MCP Configuration",
                message=".mcp.json not found",
            )

        try:
            mcp = self.config.read_mcp_config()
            server_count = len(mcp.mcpServers)
            return ValidationResult(
                passed=True,
                category="MCP Configuration",
                message=f"Valid configuration with {server_count} MCP servers",
                details=list(mcp.mcpServers.keys()),
            )
        except Exception as e:
            return ValidationResult(
                passed=False,
                category="MCP Configuration",
                message=f"Invalid .mcp.json: {e}",
            )

    def _validate_env_vars(self) -> ValidationResult:
        """Validate required environment variables are set."""
        mcp = self.config.read_mcp_config()

        # Collect all env vars referenced in config
        required_vars = set()
        for server in mcp.mcpServers.values():
            for value in server.env.values():
                # Extract ${VAR_NAME} or ${VAR_NAME:-default}
                if value.startswith("${") and "}" in value:
                    var_name = value[2:].split(":")[0].split("}")[0]
                    # Skip vars with defaults
                    if ":-" not in value:
                        required_vars.add(var_name)

            # Also check args for env var references
            for arg in server.args:
                if arg.startswith("${") and "}" in arg:
                    var_name = arg[2:].split(":")[0].split("}")[0]
                    if ":-" not in arg:
                        required_vars.add(var_name)

        # Check which are set
        missing = [v for v in required_vars if not os.environ.get(v)]
        set_vars = [v for v in required_vars if os.environ.get(v)]

        if missing:
            return ValidationResult(
                passed=True,  # Warning, not failure
                category="Environment Variables",
                message=f"{len(missing)} optional environment variables not set (configure in .env)",
                details=missing,
            )

        return ValidationResult(
            passed=True,
            category="Environment Variables",
            message=f"All {len(set_vars)} required environment variables are set",
            details=set_vars,
        )

    def _validate_skills(self) -> ValidationResult:
        """Validate skills directory structure."""
        if not self.config.skills_dir.exists():
            return ValidationResult(
                passed=False,
                category="Skills",
                message="Skills directory not found",
            )

        skills = self.config.list_skills()
        if not skills:
            return ValidationResult(
                passed=True,
                category="Skills",
                message="No skills installed",
            )

        # Check each skill has required files
        valid_skills = []
        invalid_skills = []

        for skill in skills:
            skill_dir = self.config.skills_dir / skill
            # A skill should have at least a markdown file or instruction file
            # Check direct files first
            has_content = any(
                f.suffix in [".md", ".txt", ".yaml", ".yml", ".json"]
                for f in skill_dir.iterdir()
                if f.is_file()
            )
            # Also check subdirectories (nested skill structure)
            if not has_content:
                has_content = any(
                    d.is_dir() and any(
                        f.suffix in [".md", ".txt", ".yaml", ".yml", ".json"]
                        for f in d.iterdir()
                        if f.is_file()
                    )
                    for d in skill_dir.iterdir()
                    if d.is_dir()
                )
            if has_content:
                valid_skills.append(skill)
            else:
                invalid_skills.append(skill)

        if invalid_skills:
            return ValidationResult(
                passed=False,
                category="Skills",
                message=f"{len(invalid_skills)} skills missing content",
                details=invalid_skills,
            )

        return ValidationResult(
            passed=True,
            category="Skills",
            message=f"{len(valid_skills)} skills configured correctly",
            details=valid_skills,
        )

    def _validate_hooks(self) -> ValidationResult:
        """Validate hooks are executable."""
        if not self.config.hooks_dir.exists():
            return ValidationResult(
                passed=True,
                category="Hooks",
                message="No hooks directory (optional)",
            )

        hooks = self.config.list_hooks()
        if not hooks:
            return ValidationResult(
                passed=True,
                category="Hooks",
                message="No hooks configured",
            )

        # Check executability for shell scripts
        non_executable = []
        for hook in hooks:
            hook_path = self.config.hooks_dir / hook
            if hook_path.suffix in ["", ".sh", ".bash"]:
                mode = hook_path.stat().st_mode
                if not (mode & stat.S_IXUSR):
                    non_executable.append(hook)

        if non_executable:
            return ValidationResult(
                passed=False,
                category="Hooks",
                message=f"{len(non_executable)} hooks are not executable",
                details=non_executable,
            )

        return ValidationResult(
            passed=True,
            category="Hooks",
            message=f"{len(hooks)} hooks configured correctly",
            details=hooks,
        )

    def _validate_skill_dependencies(self) -> ValidationResult:
        """Validate that all skill dependencies are satisfied."""
        skills = self.config.list_skills()
        mcp = self.config.read_mcp_config()
        installed_servers = set(mcp.mcpServers.keys())

        missing_deps = []
        for skill in skills:
            deps = self.profiles.get_skill_dependencies(skill)
            for dep in deps:
                if dep not in installed_servers:
                    missing_deps.append(f"{skill} -> {dep}")

        if missing_deps:
            return ValidationResult(
                passed=False,
                category="Skill Dependencies",
                message=f"{len(missing_deps)} missing MCP server dependencies",
                details=missing_deps,
            )

        return ValidationResult(
            passed=True,
            category="Skill Dependencies",
            message="All skill dependencies satisfied",
        )

    def test_mcp_connectivity(self, server_name: str) -> bool:
        """Test if an MCP server can be started."""
        mcp = self.config.read_mcp_config()
        server = mcp.mcpServers.get(server_name)

        if not server:
            return False

        # Try to run the command with --version or --help
        try:
            cmd = [server.command] + server.args[:2]  # Just first few args
            result = subprocess.run(
                cmd + ["--version"],
                capture_output=True,
                timeout=5,
                env={**os.environ, **server.env},
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
