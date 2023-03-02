import typing
from pathlib import Path
from subprocess import run, DEVNULL
from .Base import plugin, BasePlugin, PluginSupport, Setting


@plugin
class Spack(BasePlugin):
    def build(self, settings):
        return run(["spack", "install"]).returncode

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "spack.yaml").exists()
            and (
                run(["which", "spack"], stdout=DEVNULL, stderr=DEVNULL).returncode == 0
            )
            and (
                run(["which", "spack"], stdout=DEVNULL, stderr=DEVNULL).returncode == 0
            )
        ):
            state = PluginSupport.DEFAULT_BEFORE_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
        return {
            "build": state,
        }
