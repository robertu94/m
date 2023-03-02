from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport
from os import execvp, chdir


@plugin
class PythonPoetryPlugin(BasePlugin):
    def build(self, settings):
        """compiles the source code or a subset thereof"""
        return run(
            ["poetry", "build", *settings["cmdline_build"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        return run(
            ["poetry", "run", "pytest", *settings["cmdline_test"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def format(self, settings):
        """runs fomatting on source code or a subset there of"""
        return run(
            ["poetry", "run", "black", *settings["cmdline_format"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    def tidy(self, settings):
        """runs checks on source code or a subset there of"""
        repo_base = settings["repo_base"].value
        package_dir = repo_base / repo_base.name
        c = run(["poetry", "check"], cwd=repo_base)
        m = run(
            ["poetry", "run", "mypy", package_dir, *settings["cmdline_tidy"].value],
            cwd=repo_base,
        )
        s = run(
            [
                "poetry",
                "run",
                "pycodestyle",
                package_dir,
                *settings["cmdline_tidy"].value,
            ],
            cwd=repo_base,
        )
        return c or m or s

    def install(self, settings):
        """cleans source code or a subset there of"""
        return run(
            [
                "python",
                "-m",
                "pip",
                "install",
                "--user",
                ".",
                *settings["cmdline_install"].value,
            ],
            cwd=settings["repo_base"].value,
        ).returncode

    def generate(self, settings):
        repo_base = settings["repo_base"].value
        return run(["poetry", "new", "."], cwd=repo_base).returncode

    def repl(self, settings):
        chdir(settings["repo_base"].value)
        args = ["poetry", "run", "python"]
        execvp(args[0], args)

    @staticmethod
    def should_enable(settings):
        def contains(path, contents):
            with open(path) as f:
                return contents in f.read()

        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "pyproject.toml").exists()
            and contains((settings["repo_base"].value / "pyproject.toml"), "poetry")
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
        return state

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        state = PythonPoetryPlugin.should_enable(settings)

        return {
            "build": state,
            "test": state,
            "repl": state,
            "tidy": state,
            "install": state,
            "format": state,
            "repl": state,
            "generate": state,
        }
