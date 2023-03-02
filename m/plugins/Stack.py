from subprocess import run
from pathlib import Path
from .Base import plugin, BasePlugin, PluginSupport
from os import execvp, chdir
import re


@plugin
class HaskellStackPlugin(BasePlugin):
    def build(self, settings):
        """compiles the source code or a subset thereof"""
        return run(
            ["stack-bin", "build", *settings["cmdline_build"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        return run(
            ["stack-bin", "test", *settings["cmdline_test"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def clean(self, settings):
        """cleans source code or a subset there of"""
        return run(
            ["stack-bin", "clean", *settings["cmdline_clean"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def install(self, settings):
        """compiles the source code or a subset thereof"""
        return run(
            ["stack-bin", "install", *settings["cmdline_install"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def run(self, settings):
        """runs the binary"""
        return run(
            ["stack-bin", "run", *settings["cmdline_run"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def repl(self, settings):
        chdir(settings["repo_base"].value)
        args = ["stack-bin", "repl"]
        execvp(args[0], args)

    @staticmethod
    def haskellize(path):
        return re.sub("_", "-", str(path))

    def generate(self, settings):
        g_settings = settings["cmdline_generate"].value or ["simple-library"]
        args = [
            "stack-bin",
            "new",
            "--bare",
            self.haskellize(settings["repo_base"].value.stem),
            *g_settings,
        ]
        print(args)
        run(args, cwd=settings["repo_base"].value)

    def bench(self, settings):
        """runs the binary"""
        return run(
            ["stack-bin", "bench", *settings["cmdline_run"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "stack.yaml").exists()
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "build": state,
            "test": state,
            "run": state,
            "repl": state,
            "clean": state,
            "install": state,
            "generate": PluginSupport.NOT_ENABLED_BY_DEFAULT,
        }
