"""Git synchronization module for remote configuration repositories."""

from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError


@dataclass
class RemoteConfig:
    """Remote repository configuration."""

    name: str
    url: str
    branch: str = "main"


class GitSync:
    """Handles Git-based configuration synchronization."""

    REMOTES_FILE = ".claude-config-manager/remotes.json"

    def __init__(self, base_path: Path | None = None):
        """Initialize with base path for storing remote configs."""
        self.base_path = base_path or Path.home()
        self.config_dir = self.base_path / ".claude-config-manager"
        self.remotes_path = self.config_dir / "remotes.json"

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def list_remotes(self) -> list[RemoteConfig]:
        """List all configured remote repositories."""
        if not self.remotes_path.exists():
            return []

        with open(self.remotes_path, encoding="utf-8") as f:
            data = json.load(f)

        return [RemoteConfig(**r) for r in data.get("remotes", [])]

    def add_remote(self, name: str, url: str, branch: str = "main") -> None:
        """Add a new remote repository."""
        self._ensure_config_dir()

        remotes = self.list_remotes()

        # Check for duplicate names
        if any(r.name == name for r in remotes):
            raise ValueError(f"Remote '{name}' already exists")

        remotes.append(RemoteConfig(name=name, url=url, branch=branch))

        self._save_remotes(remotes)

    def remove_remote(self, name: str) -> bool:
        """Remove a remote repository by name."""
        remotes = self.list_remotes()
        original_count = len(remotes)

        remotes = [r for r in remotes if r.name != name]

        if len(remotes) == original_count:
            return False

        self._save_remotes(remotes)
        return True

    def _save_remotes(self, remotes: list[RemoteConfig]) -> None:
        """Save remotes to configuration file."""
        self._ensure_config_dir()

        data = {"remotes": [{"name": r.name, "url": r.url, "branch": r.branch} for r in remotes]}

        with open(self.remotes_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    def clone_config(self, remote_name: str, dest: Path) -> Path:
        """
        Clone configuration from remote repository.

        Args:
            remote_name: Name of configured remote
            dest: Destination directory

        Returns:
            Path to cloned configuration
        """
        remotes = self.list_remotes()
        remote = next((r for r in remotes if r.name == remote_name), None)

        if not remote:
            raise ValueError(f"Remote '{remote_name}' not found")

        return self._clone_from_url(remote.url, remote.branch, dest)

    def _clone_from_url(self, url: str, branch: str, dest: Path) -> Path:
        """Clone from URL to destination."""
        if dest.exists():
            shutil.rmtree(dest)

        try:
            Repo.clone_from(url, dest, branch=branch, depth=1)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to clone repository: {e}") from e

        return dest

    def pull_config(self, remote_name: str) -> Path:
        """
        Pull latest configuration from remote.

        Returns path to temporary directory with configuration.
        """
        remotes = self.list_remotes()
        remote = next((r for r in remotes if r.name == remote_name), None)

        if not remote:
            raise ValueError(f"Remote '{remote_name}' not found")

        # Clone to temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="claude-config-"))
        return self._clone_from_url(remote.url, remote.branch, temp_dir)

    def push_config(
        self,
        source: Path,
        remote_name: str,
        commit_message: str = "Update Claude Code configuration",
    ) -> None:
        """
        Push local configuration to remote repository.

        Args:
            source: Source configuration directory
            remote_name: Name of remote repository
            commit_message: Git commit message
        """
        remotes = self.list_remotes()
        remote = next((r for r in remotes if r.name == remote_name), None)

        if not remote:
            raise ValueError(f"Remote '{remote_name}' not found")

        # Clone to temp, copy config, commit and push
        temp_dir = Path(tempfile.mkdtemp(prefix="claude-config-push-"))

        try:
            # Clone existing repo
            repo = Repo.clone_from(remote.url, temp_dir, branch=remote.branch)

            # Copy configuration files
            self._copy_config_files(source, temp_dir)

            # Stage all changes
            repo.git.add(A=True)

            # Check if there are changes
            if repo.is_dirty() or repo.untracked_files:
                repo.index.commit(commit_message)
                repo.remote("origin").push()

        except GitCommandError as e:
            raise RuntimeError(f"Failed to push configuration: {e}") from e
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _copy_config_files(self, source: Path, dest: Path) -> None:
        """Copy Claude Code configuration files to destination."""
        # .mcp.json
        mcp_source = source / ".mcp.json"
        if mcp_source.exists():
            shutil.copy2(mcp_source, dest / ".mcp.json")

        # .claude directory
        claude_source = source / ".claude"
        if claude_source.exists():
            claude_dest = dest / ".claude"
            if claude_dest.exists():
                shutil.rmtree(claude_dest)
            shutil.copytree(claude_source, claude_dest)

        # .env.example
        env_source = source / ".env.example"
        if env_source.exists():
            shutil.copy2(env_source, dest / ".env.example")

        # profiles.json
        profiles_source = source / "config" / "profiles.json"
        if profiles_source.exists():
            (dest / "config").mkdir(exist_ok=True)
            shutil.copy2(profiles_source, dest / "config" / "profiles.json")

    def list_remote_profiles(self, remote_name: str) -> list[str]:
        """List available profiles from a remote repository."""
        temp_dir = None
        try:
            temp_dir = self.pull_config(remote_name)

            profiles_path = temp_dir / "config" / "profiles.json"
            if not profiles_path.exists():
                return []

            with open(profiles_path, encoding="utf-8") as f:
                data = json.load(f)

            return list(data.get("profiles", {}).keys())

        finally:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def is_git_repo(self, path: Path) -> bool:
        """Check if path is a git repository."""
        try:
            Repo(path)
            return True
        except InvalidGitRepositoryError:
            return False
