import typing
from pathlib import Path
from subprocess import run, DEVNULL
from .Base import plugin, BasePlugin, PluginSupport, Setting


@plugin
class Docker(BasePlugin):
    def build(self, settings):
        return run(["docker", "build", "."]).returncode

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "Dockerfile").exists()
            and (
                (
                    run(["which", "docker"], stdout=DEVNULL, stderr=DEVNULL).returncode
                    == 0
                )
            )
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
        return {
            "build": state,
        }
