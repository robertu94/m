from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport


@plugin
class MesonPlugin(BasePlugin):
    def configure(self, settings):
        """configure the build directory"""
        if not self.is_configured(settings):
            settings["build_dir"].value.mkdir(exist_ok=True)
            return run(
                [
                    "meson",
                    str(settings["build_dir"].value),
                    *settings["cmdline_configure"].value,
                ],
                cwd=settings["repo_base"].value,
            ).returncode

    def is_configured(self, settings):
        """test if the build directory is configured"""
        return settings["build_dir"].value.exists() and (
            (settings["build_dir"].value / "build.ninja").exists()
        )

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings["build_dir"].value))
            return run(
                [
                    "ninja",
                    "-C",
                    str(settings["build_dir"].value),
                    *settings["cmdline_build"].value,
                ],
                cwd=settings["repo_base"].value,
            ).returncode
        else:
            print("failed to configure")
            return 1

    def tidy(self, settings):
        """runs static analysis"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings["build_dir"].value))
            return run(
                [
                    "ninja",
                    "-C",
                    str(settings["build_dir"].value),
                    "scan-build",
                    *settings["cmdline_tidy"].value,
                ],
                cwd=settings["repo_base"].value,
            ).returncode
        else:
            print("failed to configure")
            return 1

    def bench(self, settings):
        """run benchmarks"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings["build_dir"].value))
            return run(
                [
                    "ninja",
                    "-C",
                    str(settings["build_dir"].value),
                    "benchmark",
                    *settings["cmdline_bench"].value,
                ],
                cwd=settings["repo_base"].value,
            ).returncode
        else:
            print("failed to configure")
            return 1

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings["build_dir"].value))
            return run(
                ["meson", "test", *settings["cmdline_test"].value],
                cwd=settings["build_dir"].value,
            ).returncode
        else:
            print("failed to configure")
            return 1

    def clean(self, settings):
        """cleans source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings["build_dir"].value))
            return run(["ninja", "clean"], cwd=settings["build_dir"].value).returncode
        else:
            print("failed to configure")
            return 1

    def install(self, settings):
        """cleans source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings["build_dir"].value))
            return run(["ninja", "install"], cwd=settings["build_dir"].value).returncode
        else:
            print("failed to configure")
            return 1

    def generate(self, settings):
        """generates a blank project"""
        return run(
            ["meson", "init", *settings["cmdline_generate"].value],
            cwd=settings["repo_base"].value,
        ).returncode

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "meson.build").exists()
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": state,
            "tidy": state,
            "bench": state,
            "generate": PluginSupport.NOT_ENABLED_BY_DEFAULT,
        }
