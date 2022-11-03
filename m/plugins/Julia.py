from os import chdir, execvp
from subprocess import run, DEVNULL
from .Base import plugin, BasePlugin, PluginSupport


@plugin
class JuliaPlugin(BasePlugin):
    def build(self, settings):
        """compiles the source code or a subset thereof"""
        run(
            [
                "julia",
                "--project",
                "-e",
                "using Pkg; Pkg.instantiate(); Pkg.precompile()",
                *settings["cmdline_build"].value,
            ],
            cwd=settings["repo_base"].value,
        )

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        run(
            [
                "julia",
                "--project",
                "-e",
                "using Pkg; Pkg.test()",
                *settings["cmdline_test"].value,
            ],
            cwd=settings["repo_base"].value,
        )

    def repl(self, settings):
        chdir(settings["repo_base"].value)
        args = ["julia", "--project"]
        execvp(args[0], args)

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "Project.toml").exists()
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "repl": state,
            "build": state,
            "test": state,
        }
