import typing
import json
from pathlib import Path
from .Base import plugin, BasePlugin, PluginSupport, Setting
from .Settings import Settings


@plugin
class ConfigFile(BasePlugin):

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        
        if (Settings.find_repo_base() / ".mstop").exists():
            state = PluginSupport.DEFAULT_AFTER_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "settings": state
        }

    def settings(self, current_settings) -> typing.List[Setting]:
        """returns settings that this plugin is authoritative for"""
        try:
            with open(Settings.find_repo_base() / ".mstop") as setting_file:
                settings_from_file = json.load(setting_file)

            make_setting = self.get_settings_factory()

            def make_typed_setting(key, value):
                if key.endswith(":path"):
                    key = key[:-len(":path")]
                    return make_setting(key, Path(value))
                else:
                    return make_setting(key, value)

            return [
               make_typed_setting(key, value)
               for key, value in settings_from_file.items()
             ]
        except json.decoder.JSONDecodeError:
            return []

