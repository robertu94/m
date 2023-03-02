from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport


@plugin
class RustPlugin(BasePlugin):
    def build(self, settings):
        """compiles the source code or a subset thereof"""
        return run(
            ["cargo", "build", *settings["cmdline_build"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        return run(
            ["cargo", "test", *settings["cmdline_test"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def clean(self, settings):
        """cleans source code or a subset there of"""
        return run(["cargo", "clean"], cwd=settings["repo_base"].value).returncode

    def install(self, settings):
        """compiles the source code or a subset thereof"""
        return run(
            ["cargo", "install", "--path", ".", *settings["cmdline_install"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def run(self, settings):
        """runs the binary"""
        return run(
            ["cargo", "run", *settings["cmdline_run"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def format(self, settings):
        """runs the binary"""
        return run(
            ["cargo", "fmt", *settings["cmdline_format"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def tidy(self, settings):
        """runs the binary"""
        return run(
            ["cargo", "check", *settings["cmdline_tidy"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def bench(self, settings):
        """runs the binary"""
        return run(
            ["cargo", "bench", *settings["cmdline_bench"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def generate(self, settings):
        return run(
            ["cargo", "init", *settings["cmdline_generate"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "Cargo.toml").exists()
        ):
            state = PluginSupport.DEFAULT_MAIN
            install_state = PluginSupport.NOT_ENABLED_BY_DEFAULT
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
            install_state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": install_state,
            "run": state,
            "format": state,
            "tidy": state,
            "bench": state,
            "generate": PluginSupport.NOT_ENABLED_BY_DEFAULT,
        }
