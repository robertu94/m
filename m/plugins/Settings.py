import typing
from pathlib import Path
from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport, Setting


@plugin
class Settings(BasePlugin):
    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        return {
            "settings": PluginSupport.DEFAULT_MAIN,
        }

    @staticmethod
    def find_repo_base():
        repo_base = Path.cwd()
        dirs = [Path.cwd(), *Path.cwd().parents]
        for path in dirs:
            if (path / ".git").exists():
                repo_base = path
                break
            if (path / ".hg").exists():
                repo_base = path
                break
            if (path / ".mstop").exists():
                repo_base = path
                break
        return repo_base

    @staticmethod
    def find_build_dir():
        base = Settings.find_repo_base()
        if base is not None:
            return base / "build"
        else:
            return None

    def settings(self, current_settings) -> typing.List[Setting]:
        """returns settings that this plugin is authoritative for"""
        make_setting = self.get_settings_factory(priority=Setting.LOW)
        return [
            make_setting("repo_base", self.find_repo_base()),
            make_setting("build_dir", self.find_build_dir()),
            *super().settings(current_settings),
        ]
