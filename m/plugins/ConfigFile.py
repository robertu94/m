import typing
import json
import os
from pathlib import Path
from .Base import plugin, BasePlugin, PluginSupport, Setting
from .Settings import Settings


def expandvars(value: str) -> str:
    """expands variables in a similar way to how bash expands variables

    it supports the following syntax:

    ${foo} - replaces with the value of foo from the environment, or an empty string if one does not exist
    ${foo:-bar} - replaces with the value of foo from the environment, or bar is used
    """
    expanded = []
    last_var_start = 0
    last_var_end = 0

    def translate(var: str) -> str:
        """preforms the actual expansion of the variable"""
        colon_pos = var.find(":")
        if colon_pos == -1:
            # treat as a normal variable
            return os.environ.get(var, "")
        else:
            # has an opcode
            name = var[:colon_pos]
            opcode = var[colon_pos + 1 : colon_pos + 2]
            argument = var[colon_pos + 2 :]
            if opcode == "-":
                return os.environ.get(name, argument)
            else:
                raise RuntimeError(f'invalid opcode {opcode} in "{var}"')

    while last_var_start != -1:
        next_var_start = value.find("${", last_var_end)
        next_var_end = value.find("}", last_var_end)
        if next_var_start == -1 and next_var_end == -1:
            break
        if next_var_start == -1:
            raise RuntimeError(f"extra '}}' at character {next_var_end} in \"{value}\"")
        if next_var_end == -1:
            raise RuntimeError(
                f"extra '${{' at character {next_var_start} in \"{value}\""
            )

        not_in_var = value[last_var_end:next_var_start]
        variable = value[next_var_start + 2 : next_var_end]

        expanded.append(not_in_var)
        expanded.append(translate(variable))

        last_var_start = next_var_start
        last_var_end = next_var_end + 1
    expanded.append(value[last_var_end:])
    return "".join(expanded)


@plugin
class ConfigFile(BasePlugin):
    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""

        if (Settings.find_repo_base() / ".mstop").exists():
            state = PluginSupport.DEFAULT_AFTER_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {"settings": state}

    def settings(self, current_settings) -> typing.List[Setting]:
        """returns settings that this plugin is authoritative for"""
        try:
            with open(Settings.find_repo_base() / ".mstop") as setting_file:
                settings_from_file = json.load(setting_file)

            make_setting = self.get_settings_factory()

            def make_typed_setting(key, value):
                if key.endswith(":path"):
                    key = key[: -len(":path")]
                    return make_setting(key, Path(value))
                else:
                    if isinstance(value, str):
                        return make_setting(key, expandvars(value))
                    if isinstance(value, list):
                        return make_setting(key, [expandvars(i) for i in value])
                    else:
                        return make_setting(key, value)

            return [
                make_typed_setting(key, value)
                for key, value in settings_from_file.items()
            ]
        except json.decoder.JSONDecodeError:
            return []
