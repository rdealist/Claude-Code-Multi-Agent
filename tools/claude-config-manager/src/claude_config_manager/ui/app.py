"""Main Textual application for Claude Config Manager."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from ..core import ConfigManager, ProfileManager


class MainMenu(Static):
    """Main menu widget."""

    def __init__(self, source_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_path = source_path

    def compose(self) -> ComposeResult:
        """Create menu buttons."""
        yield Label("Claude Code 项目配置管理器", classes="title")
        yield Label(f"源配置: {self.source_path}", classes="info")
        yield Label("", classes="spacer")

        with Vertical(classes="menu-container"):
            yield Button("1. 创建新项目", id="btn-create", variant="primary")
            yield Button("2. 导入配置到现有项目", id="btn-import", variant="primary")
            yield Button("3. 验证项目完整性", id="btn-validate", variant="success")
            yield Button("4. 导出配置文件", id="btn-export", variant="default")
            yield Button("5. 查看当前配置", id="btn-view", variant="default")
            yield Label("", classes="spacer")
            yield Button("Q. 退出", id="btn-quit", variant="error")


class ConfigViewScreen(Screen):
    """Screen for viewing current configuration."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "返回"),
        Binding("q", "app.pop_screen", "返回"),
    ]

    def __init__(self, config_manager: ConfigManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager

    def compose(self) -> ComposeResult:
        """Create the view layout."""
        yield Header()

        with Container(classes="screen-container"):
            yield Label("当前项目配置", classes="screen-title")
            yield Label(f"路径: {self.config_manager.project_path}", classes="info")
            yield Label("", classes="spacer")

            mcp = self.config_manager.read_mcp_config()
            yield Label(f"MCP 服务器 ({len(mcp.mcpServers)}个):", classes="section-title")
            for name in mcp.mcpServers:
                yield Label(f"  • {name}", classes="list-item")

            yield Label("", classes="spacer")

            skills = self.config_manager.list_skills()
            yield Label(f"Skills ({len(skills)}个):", classes="section-title")
            for skill in skills[:10]:
                yield Label(f"  • {skill}", classes="list-item")
            if len(skills) > 10:
                yield Label(f"  ... 还有 {len(skills) - 10} 个", classes="list-item-more")

            yield Label("", classes="spacer")

            hooks = self.config_manager.list_hooks()
            yield Label(f"Hooks ({len(hooks)}个):", classes="section-title")
            for hook in hooks:
                yield Label(f"  • {hook}", classes="list-item")

        yield Footer()


class ValidationScreen(Screen):
    """Screen for validation results."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "返回"),
        Binding("q", "app.pop_screen", "返回"),
    ]

    def __init__(self, config_manager: ConfigManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager

    def compose(self) -> ComposeResult:
        """Create the validation view."""
        from ..core import ProfileManager, Validator

        yield Header()

        with Container(classes="screen-container"):
            yield Label("配置完整性验证", classes="screen-title")
            yield Label("", classes="spacer")

            validator = Validator(self.config_manager, ProfileManager())
            report = validator.validate_all()

            for result in report.results:
                status = "✓" if result.passed else "✗"
                status_class = "success" if result.passed else "error"
                yield Label(
                    f"[{status}] {result.category}: {result.message}",
                    classes=f"validation-{status_class}",
                )
                if result.details and not result.passed:
                    for detail in result.details[:5]:
                        yield Label(f"    - {detail}", classes="detail")

            yield Label("", classes="spacer")
            yield Label(report.summary(), classes="summary")

        yield Footer()


class CreateProjectScreen(Screen):
    """Screen for creating a new project."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "返回"),
    ]

    def __init__(
        self,
        config_manager: ConfigManager,
        profile_manager: ProfileManager,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager
        self.profile_manager = profile_manager
        self.selected_profile = "full"

    def compose(self) -> ComposeResult:
        """Create the project creation view."""
        yield Header()

        with Container(classes="screen-container"):
            yield Label("创建新项目", classes="screen-title")
            yield Label("", classes="spacer")

            yield Label("目标路径:", classes="input-label")
            yield Input(
                placeholder="输入目标项目路径，例如: ~/my-new-project",
                id="target-path",
            )

            yield Label("", classes="spacer")
            yield Label("选择配置模板 (点击选择):", classes="input-label")

            for profile_name in self.profile_manager.list_profiles():
                summary = self.profile_manager.get_profile_summary(profile_name)
                variant = "primary" if profile_name == "full" else "default"
                yield Button(
                    f"{summary['name']} ({summary['mcp_count']} MCP, {summary['skill_count']} Skills)",
                    id=f"create-profile-{profile_name}",
                    variant=variant,
                    classes="profile-button",
                )

            yield Label("", classes="spacer")
            yield Label("当前选择: full (完整配置)", id="status-label", classes="status")
            yield Button("✓ 确认创建项目", id="create-confirm", variant="success", classes="confirm-button")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in this screen."""
        button_id = event.button.id

        if button_id and button_id.startswith("create-profile-"):
            # Update selected profile
            self.selected_profile = button_id.replace("create-profile-", "")
            # Update button styles
            for btn in self.query(".profile-button"):
                btn.variant = "default"
            event.button.variant = "primary"
            # Update status
            profile = self.profile_manager.get_profile(self.selected_profile)
            if profile:
                self.query_one("#status-label", Label).update(
                    f"当前选择: {self.selected_profile} ({profile.name})"
                )
            event.stop()

        elif button_id == "create-confirm":
            self._create_project()
            event.stop()

    def _create_project(self) -> None:
        """Create the project."""
        target_input = self.query_one("#target-path", Input)
        target_path_str = target_input.value.strip()

        if not target_path_str:
            self.notify("请输入目标路径", severity="error")
            return

        target_path = Path(target_path_str).expanduser().resolve()

        try:
            self.profile_manager.create_project(
                target_path=target_path,
                source=self.config_manager,
                profile_name=self.selected_profile,
                init_git=True,
            )
            self.notify(f"✓ 项目创建成功: {target_path}", severity="information")
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"创建失败: {e}", severity="error")


class ImportConfigScreen(Screen):
    """Screen for importing configuration to existing project."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "返回"),
    ]

    def __init__(
        self,
        config_manager: ConfigManager,
        profile_manager: ProfileManager,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager
        self.profile_manager = profile_manager
        self.selected_profile = "full"

    def compose(self) -> ComposeResult:
        """Create the import view."""
        yield Header()

        with Container(classes="screen-container"):
            yield Label("导入配置到现有项目", classes="screen-title")
            yield Label("", classes="spacer")

            yield Label("目标项目路径:", classes="input-label")
            yield Input(
                placeholder="输入已有项目的路径，例如: ~/existing-project",
                id="target-path",
            )

            yield Label("", classes="spacer")
            yield Label("选择配置模板 (点击选择):", classes="input-label")

            for profile_name in self.profile_manager.list_profiles():
                summary = self.profile_manager.get_profile_summary(profile_name)
                variant = "primary" if profile_name == "full" else "default"
                yield Button(
                    f"{summary['name']} ({summary['mcp_count']} MCP, {summary['skill_count']} Skills)",
                    id=f"import-profile-{profile_name}",
                    variant=variant,
                    classes="profile-button",
                )

            yield Label("", classes="spacer")
            yield Label("当前选择: full (完整配置)", id="status-label", classes="status")
            yield Button("✓ 确认导入配置", id="import-confirm", variant="success", classes="confirm-button")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in this screen."""
        button_id = event.button.id

        if button_id and button_id.startswith("import-profile-"):
            self.selected_profile = button_id.replace("import-profile-", "")
            for btn in self.query(".profile-button"):
                btn.variant = "default"
            event.button.variant = "primary"
            profile = self.profile_manager.get_profile(self.selected_profile)
            if profile:
                self.query_one("#status-label", Label).update(
                    f"当前选择: {self.selected_profile} ({profile.name})"
                )
            event.stop()

        elif button_id == "import-confirm":
            self._import_config()
            event.stop()

    def _import_config(self) -> None:
        """Import configuration."""
        target_input = self.query_one("#target-path", Input)
        target_path_str = target_input.value.strip()

        if not target_path_str:
            self.notify("请输入目标路径", severity="error")
            return

        target_path = Path(target_path_str).expanduser().resolve()

        if not target_path.exists():
            self.notify("目标路径不存在", severity="error")
            return

        profile = self.profile_manager.get_profile(self.selected_profile)
        if not profile:
            self.notify("无效的配置模板", severity="error")
            return

        try:
            target_config = ConfigManager(target_path)
            target_config.merge_config(
                source=self.config_manager,
                strategy="overwrite",
                mcp_servers=profile.mcpServers,
                skills=profile.skills,
            )
            self.notify(f"✓ 配置导入成功: {target_path}", severity="information")
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"导入失败: {e}", severity="error")


class ClaudeConfigManagerApp(App):
    """Main TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }

    .title {
        text-align: center;
        text-style: bold;
        color: $primary;
        padding: 1 2;
        width: 100%;
    }

    .screen-title {
        text-style: bold;
        color: $primary;
        padding: 1 0;
    }

    .section-title {
        text-style: bold;
        color: $secondary;
        padding: 0 0 0 1;
    }

    .menu-container {
        align: center middle;
        padding: 1 2;
    }

    .menu-container Button {
        width: 40;
        margin: 0 0 1 0;
    }

    .screen-container {
        padding: 1 2;
        overflow-y: auto;
    }

    .info {
        color: $text-muted;
    }

    .list-item {
        padding: 0 0 0 2;
    }

    .list-item-more {
        color: $text-muted;
        padding: 0 0 0 2;
    }

    .validation-success {
        color: $success;
    }

    .validation-error {
        color: $error;
    }

    .detail {
        color: $warning;
        padding: 0 0 0 4;
    }

    .summary {
        text-style: bold;
        padding: 1 0;
    }

    .spacer {
        height: 1;
    }

    .profile-button {
        width: 70;
        margin: 0 0 1 0;
    }

    .input-label {
        padding: 0 0 0 0;
        text-style: bold;
    }

    .status {
        color: $success;
        text-style: italic;
        padding: 0 0 1 0;
    }

    .confirm-button {
        width: 30;
        margin: 1 0 0 0;
    }

    Input {
        width: 70;
        margin: 0 0 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("escape", "back", "返回"),
    ]

    def __init__(self, source_path: Path | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_path = source_path or Path.cwd()
        self.config_manager = ConfigManager(self.source_path)
        self.profile_manager = ProfileManager()

    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()
        yield Container(MainMenu(self.source_path), id="main-content")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events from main menu only."""
        button_id = event.button.id

        # Only handle main menu buttons
        if button_id == "btn-quit":
            self.exit()
        elif button_id == "btn-view":
            self.push_screen(ConfigViewScreen(self.config_manager))
        elif button_id == "btn-validate":
            self.push_screen(ValidationScreen(self.config_manager))
        elif button_id == "btn-create":
            self.push_screen(
                CreateProjectScreen(self.config_manager, self.profile_manager)
            )
        elif button_id == "btn-import":
            self.push_screen(
                ImportConfigScreen(self.config_manager, self.profile_manager)
            )
        elif button_id == "btn-export":
            self._export_config()

    def _export_config(self) -> None:
        """Export current configuration."""
        output_path = self.source_path / "claude-config-export.json"
        try:
            self.config_manager.export_config(output_path)
            self.notify(f"配置已导出到 {output_path}", severity="information")
        except Exception as e:
            self.notify(f"导出失败: {e}", severity="error")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()


def run_app(source_path: Path | None = None) -> None:
    """Run the TUI application."""
    app = ClaudeConfigManagerApp(source_path)
    app.run()
