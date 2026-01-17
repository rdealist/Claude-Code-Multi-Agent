"""CLI entry point for Claude Config Manager."""

from __future__ import annotations

from pathlib import Path

import click


@click.group(invoke_without_command=True)
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Source configuration directory (default: current directory)",
)
@click.pass_context
def main(ctx: click.Context, source: Path | None) -> None:
    """Claude Config Manager - TUI tool for managing Claude Code configurations."""
    ctx.ensure_object(dict)
    ctx.obj["source"] = source or Path.cwd()

    if ctx.invoked_subcommand is None:
        # Launch TUI if no subcommand
        from .ui.app import run_app

        # Use the resolved source path, not the raw argument
        run_app(ctx.obj["source"])


@main.command()
@click.option(
    "--target",
    "-t",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Target directory for new project",
)
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["full", "frontend", "backend", "algorithm"]),
    default="full",
    help="Configuration profile to use",
)
@click.option(
    "--git/--no-git",
    default=False,
    help="Initialize git repository",
)
@click.pass_context
def create(ctx: click.Context, target: Path, profile: str, git: bool) -> None:
    """Create a new project with Claude Code configuration."""
    from .core import ConfigManager, ProfileManager

    source = ctx.obj["source"]
    config_manager = ConfigManager(source)
    profile_manager = ProfileManager()

    click.echo(f"Creating new project at {target} with profile '{profile}'...")

    try:
        profile_manager.create_project(
            target_path=target,
            source=config_manager,
            profile_name=profile,
            init_git=git,
        )
        click.echo(click.style("✓ Project created successfully!", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Failed to create project: {e}", fg="red"))
        raise click.Abort()


@main.command()
@click.option(
    "--target",
    "-t",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Target project directory",
)
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["full", "frontend", "backend", "algorithm"]),
    default="full",
    help="Configuration profile to use",
)
@click.option(
    "--strategy",
    type=click.Choice(["overwrite", "merge"]),
    default="overwrite",
    help="Merge strategy for existing configuration",
)
@click.pass_context
def import_config(
    ctx: click.Context, target: Path, profile: str, strategy: str
) -> None:
    """Import configuration to an existing project."""
    from .core import ConfigManager, ProfileManager

    source = ctx.obj["source"]
    source_config = ConfigManager(source)
    target_config = ConfigManager(target)
    profile_manager = ProfileManager()

    profile_info = profile_manager.get_profile(profile)
    if not profile_info:
        click.echo(click.style(f"Unknown profile: {profile}", fg="red"))
        raise click.Abort()

    # Check if target has existing config
    if target_config.has_config():
        click.echo(f"Target project already has configuration at {target}")
        click.echo(f"Strategy: {strategy} (backup will be created)")
        if not click.confirm("Continue?"):
            raise click.Abort()

    click.echo(f"Importing '{profile}' configuration to {target}...")

    try:
        target_config.merge_config(
            source=source_config,
            strategy=strategy,
            mcp_servers=profile_info.mcpServers,
            skills=profile_info.skills,
        )
        click.echo(click.style("✓ Configuration imported successfully!", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Import failed: {e}", fg="red"))
        raise click.Abort()


@main.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Output file path",
)
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["full", "frontend", "backend", "algorithm"]),
    default=None,
    help="Filter to specific profile",
)
@click.pass_context
def export(ctx: click.Context, output: Path | None, profile: str | None) -> None:
    """Export configuration to a single file."""
    from .core import ConfigManager, ProfileManager

    source = ctx.obj["source"]
    config_manager = ConfigManager(source)

    output = output or source / "claude-config-export.json"

    mcp_servers = None
    skills = None

    if profile:
        profile_manager = ProfileManager()
        profile_info = profile_manager.get_profile(profile)
        if profile_info:
            mcp_servers = profile_info.mcpServers
            skills = profile_info.skills

    click.echo(f"Exporting configuration to {output}...")

    try:
        config_manager.export_config(
            output_path=output,
            profile_name=profile,
            mcp_servers=mcp_servers,
            skills=skills,
        )
        click.echo(click.style(f"✓ Exported to {output}", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Export failed: {e}", fg="red"))
        raise click.Abort()


@main.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate project configuration integrity."""
    from .core import ConfigManager, ProfileManager, Validator

    source = ctx.obj["source"]
    config_manager = ConfigManager(source)
    profile_manager = ProfileManager()
    validator = Validator(config_manager, profile_manager)

    click.echo(f"Validating configuration at {source}...\n")

    report = validator.validate_all()

    for result in report.results:
        status = "✓" if result.passed else "✗"
        color = "green" if result.passed else "red"
        click.echo(click.style(f"[{status}] {result.category}", fg=color))
        click.echo(f"    {result.message}")

        if result.details and not result.passed:
            for detail in result.details[:5]:
                click.echo(click.style(f"      - {detail}", fg="yellow"))
            if len(result.details) > 5:
                click.echo(f"      ... and {len(result.details) - 5} more")

    click.echo()
    if report.passed:
        click.echo(click.style("✓ All validations passed!", fg="green"))
    else:
        click.echo(
            click.style(
                f"✗ {report.error_count} validation(s) failed", fg="red"
            )
        )


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show current configuration information."""
    from .core import ConfigManager

    source = ctx.obj["source"]
    config_manager = ConfigManager(source)

    click.echo(f"Project: {source}\n")

    if not config_manager.has_config():
        click.echo(click.style("No Claude Code configuration found.", fg="yellow"))
        return

    # MCP Servers
    mcp = config_manager.read_mcp_config()
    click.echo(click.style(f"MCP Servers ({len(mcp.mcpServers)}):", fg="blue", bold=True))
    for name in mcp.mcpServers:
        click.echo(f"  • {name}")

    # Skills
    skills = config_manager.list_skills()
    click.echo(click.style(f"\nSkills ({len(skills)}):", fg="blue", bold=True))
    for skill in skills:
        click.echo(f"  • {skill}")

    # Hooks
    hooks = config_manager.list_hooks()
    click.echo(click.style(f"\nHooks ({len(hooks)}):", fg="blue", bold=True))
    for hook in hooks:
        click.echo(f"  • {hook}")


@main.group()
def git() -> None:
    """Git remote configuration management."""
    pass


@git.command("add")
@click.argument("name")
@click.argument("url")
@click.option("--branch", "-b", default="main", help="Remote branch")
def git_add(name: str, url: str, branch: str) -> None:
    """Add a remote configuration repository."""
    from .core import GitSync

    git_sync = GitSync()

    try:
        git_sync.add_remote(name, url, branch)
        click.echo(click.style(f"✓ Added remote '{name}'", fg="green"))
    except ValueError as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
        raise click.Abort()


@git.command("list")
def git_list() -> None:
    """List configured remote repositories."""
    from .core import GitSync

    git_sync = GitSync()
    remotes = git_sync.list_remotes()

    if not remotes:
        click.echo("No remote repositories configured.")
        return

    click.echo("Configured remotes:\n")
    for remote in remotes:
        click.echo(f"  {remote.name}")
        click.echo(f"    URL: {remote.url}")
        click.echo(f"    Branch: {remote.branch}")
        click.echo()


@git.command("remove")
@click.argument("name")
def git_remove(name: str) -> None:
    """Remove a remote configuration repository."""
    from .core import GitSync

    git_sync = GitSync()

    if git_sync.remove_remote(name):
        click.echo(click.style(f"✓ Removed remote '{name}'", fg="green"))
    else:
        click.echo(click.style(f"✗ Remote '{name}' not found", fg="red"))


@git.command("pull")
@click.argument("name")
@click.option(
    "--target",
    "-t",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Target directory to pull into",
)
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["full", "frontend", "backend", "algorithm"]),
    default="full",
    help="Profile to pull",
)
def git_pull(name: str, target: Path | None, profile: str) -> None:
    """Pull configuration from a remote repository."""
    from .core import ConfigManager, GitSync, ProfileManager

    git_sync = GitSync()
    target = target or Path.cwd()

    click.echo(f"Pulling configuration from '{name}'...")

    try:
        temp_dir = git_sync.pull_config(name)

        # Apply to target
        source_config = ConfigManager(temp_dir)
        target_config = ConfigManager(target)
        profile_manager = ProfileManager(temp_dir / "config" / "profiles.json")

        profile_info = profile_manager.get_profile(profile)
        if profile_info:
            target_config.merge_config(
                source=source_config,
                strategy="overwrite",
                mcp_servers=profile_info.mcpServers,
                skills=profile_info.skills,
            )

        click.echo(click.style(f"✓ Pulled '{profile}' configuration", fg="green"))

    except Exception as e:
        click.echo(click.style(f"✗ Pull failed: {e}", fg="red"))
        raise click.Abort()


@git.command("push")
@click.argument("name")
@click.option(
    "--message",
    "-m",
    default="Update Claude Code configuration",
    help="Commit message",
)
@click.pass_context
def git_push(ctx: click.Context, name: str, message: str) -> None:
    """Push configuration to a remote repository."""
    from .core import GitSync

    source = ctx.obj["source"]
    git_sync = GitSync()

    click.echo(f"Pushing configuration to '{name}'...")

    try:
        git_sync.push_config(source, name, message)
        click.echo(click.style("✓ Configuration pushed successfully!", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Push failed: {e}", fg="red"))
        raise click.Abort()


if __name__ == "__main__":
    main()
