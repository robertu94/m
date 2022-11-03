import typing
from subprocess import run, PIPE
from .Base import plugin, BasePlugin, Setting


@plugin
class GitPlugin(BasePlugin):
    @staticmethod
    def find_author():
        p = run(["git", "config", "user.name"], stdout=PIPE, universal_newlines=True)
        return p.stdout.strip()

    @staticmethod
    def find_email():
        p = run(["git", "config", "user.email"], stdout=PIPE, universal_newlines=True)
        return p.stdout.strip()

    def settings(self, current_settings) -> typing.List[Setting]:
        """returns settings that this plugin is authoritative for"""
        make_setting = self.get_settings_factory(priority=Setting.LOW)
        return [
            make_setting("author", self.find_author()),
            make_setting("email", self.find_email()),
            *super().settings(current_settings),
        ]
