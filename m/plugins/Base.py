from collections import defaultdict
from pathlib import Path
import itertools
import enum
import pprint
import typing
import logging

LOGGER = logging.getLogger(__name__)

def get_class_name(cls):
    """returns the name of the most derived class"""
    return cls.__class__.__name__


class NotProvidedError(Exception):
    """Thrown when the class does not provide the desired method"""

    def __str__(self, method, cls):
        return "{method} not provided on {cls}".format(method=method, cls=get_class_name(cls))

class Setting:

    UNSET = -100 # used only by cmdline for unset arguments
    LOW = 0
    DEFAULT = 100
    URGENT = 200

    def __init__(self, name, value, source, priority=DEFAULT):
        self.name = name
        self.value = value
        self.priority = priority
        self.source = source

    def __str__(self):
        return "{name} : {value}".format(
            name=self.name,
            value=pprint.pformat(self.value)
        )
    def __repr__(self):
        return "{source}[{priority}]:{name} : {value}".format(
            source=self.source,
            priority=self.priority,
            name=self.name,
            value=pprint.pformat(self.value),
        )


class PluginSupport(enum.IntEnum):
    """
    Modes for supporting functions

    SETTINGS_DISABLED -- the plugin is disabled by the settings file
    CMD_DISABLED -- the plugin is disabled on the command line
    NOT_SUPPORTED -- do not call this method on this plugin, it may not be
                     implemented
    NOT_ENABLED_BY_DEFAULT -- plugin supports this method, but does not act on default,
                              may be overwritten on cmdline
    NOT_ENABLED_BY_REPOSITORY -- plugin supports this method, but is not detected to work
                                 for this repository (i.e. missing a needed config file)
    NOT_NEEDED --  the plugin has determined that this action is unnecessary,
                   i.e. the cache is up to date or code is compiled

    DEFAULT_BEFORE_MAIN -- run this method after the main method by default
                          before main. (I.E. package configure steps)
    DEFAULT_MAIN -- run this method if it is the only main, else throw an
                    error. For things like running compiles.
    DEFAULT_AFTER_MAIN -- run this method after the main method by default
                          after main.  For things like release making release tarballs

    REQUESTED_SETTINGS_AFTER -- this module was specifically requested in the
                                settings database to run before main
    REQUESTED_SETTINGS_MAIN -- this module was specifically requested in the
                               settings database to run as main
    REQUESTED_SETTINGS_BEFORE -- this module was specifically requested in the
                                 settings database

    REQUESTED_CMD_BEFORE -- this module was specifically requested on the
                            command line, before the main mode
    REQUESTED_CMD_MAIN -- this module was specifically requested on the command
                          line, as the main mode
    REQUESTED_CMD_AFTER -- this module was specifically requested on the
                           command line, after the main mode
    """
    SETTINGS_DISABLED = -4
    CMD_DISABLED = -3
    NOT_SUPPORTED = -2
    NOT_ENABLED_BY_REPOSITORY = -1
    NOT_ENABLED_BY_DEFAULT = 0
    NOT_NEEDED = 1

    DEFAULT_BEFORE_MAIN = 2
    DEFAULT_MAIN = 3
    DEFAULT_AFTER_MAIN = 4

    REQUESTED_SETTINGS_BEFORE = 5
    REQUESTED_SETTINGS_MAIN = 6
    REQUESTED_SETTINGS_AFTER = 7
    REQUESTED_CMD_BEFORE = 8
    REQUESTED_CMD_MAIN = 9
    REQUESTED_CMD_AFTER = 10

class BasePlugin:
    """this class provides the default behaivor for and methods for a plugin"""

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        raise NotProvidedError("build", self)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        raise NotProvidedError("test", self)

    def clean(self, settings):
        """cleans source code or a subset there of"""
        raise NotProvidedError("clean", self)

    def install(self, settings):
        """cleans source code or a subset there of"""
        raise NotProvidedError("install", self)

    def run(self, settings):
        """runs the provided target"""
        raise NotProvidedError("run", self)

    def tidy(self, settings):
        """runs the provided target"""
        raise NotProvidedError("tidy", self)

    def bench(self, settings):
        """runs the provided target"""
        raise NotProvidedError("bench", self)

    def generate(self, settings):
        """runs the provided target"""
        raise NotProvidedError("generate", self)

    def get_settings_factory(self, cls=None, priority=Setting.DEFAULT):
        """returns a helper function that fills in commmon arguments on the Setting object"""
        if cls is None:
            cls = self
        def factory(name, value):
            return Setting(name, value, get_class_name(self), priority)
        return factory


    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        return {
            "settings": PluginSupport.DEFAULT_BEFORE_MAIN
        }

    @staticmethod
    def _is_in_ignorecase(item, list):
        item_lowered = item.lower()
        for list_lowered in (i.lower() for i in list):
            if item_lowered.startswith(list_lowered):
                return True
        return False



    def check(self, method: str, settings: typing.List[Setting]) -> int:
        """returns integer priority representing if an operation is supported,
        higher values are preferred.

        Users: please call this method rather than checking _supported() or checking for exceptions
        Plugin Developers: please override _supported instead().
        """
        cls_name = get_class_name(self).lower()

        is_supported = self._supported(settings).get(method, PluginSupport.NOT_SUPPORTED) 
        if is_supported is not PluginSupport.NOT_SUPPORTED:
            for setting in settings.values():
                if setting.name == "cmd_enable" and self._is_in_ignorecase(cls_name, setting.value):
                    is_supported = PluginSupport.REQUESTED_CMD_MAIN
                if setting.name == "cmd_disable" and self._is_in_ignorecase(cls_name, setting.value):
                    is_supported = PluginSupport.CMD_DISABLED
                if setting.name == "settings_enable" and self._is_in_ignorecase(cls_name, setting.value):
                    is_supported = PluginSupport.REQUESTED_SETTINGS_MAIN
                if setting.name == "settings_disable" and self._is_in_ignorecase(cls_name, setting.value):
                    is_supported = PluginSupport.SETTINGS_DISABLED
        return is_supported


        

    def settings(self, current_settings) -> typing.List[Setting]:
        """returns settings that this plugin is authoritative for"""
        make_setting = self.get_settings_factory()
        return [
            make_setting("version", "1.0.0"),
        ]

ALL_PLUGINS = []
def plugin(cls):
    """registers a plugin for use with the system"""
    ALL_PLUGINS.append(cls())
    return cls

class MBuildTool:

    def __init__(self, args):
        self._settings = self._args_to_settings(args)
        self._actions_run = 0

    def _args_to_settings(self, args):
        return {
                key: Setting(
                    key,
                    value,
                    "CmdlineArguments",
                    priority=Setting.URGENT if value else Setting.UNSET,
                    )
                for key, value
                in vars(args).items()
                if any(isinstance(value, cls) for cls in (int,str,list,Path))
        }

    def _active_plugin_loglevel(self, status):
        if status >= PluginSupport.DEFAULT_BEFORE_MAIN and self._actions_run > 0:
            return logging.INFO
        else:
            return logging.DEBUG

    def _find_active_plugins(self, method: str):
        """finds the plugin that should conduct the given call"""
        active_plugins = defaultdict(list)
        for plugin in ALL_PLUGINS:
            status = plugin.check(method, self._settings)
            LOGGER.log(self._active_plugin_loglevel(status),"plugin %s is %s for %s", get_class_name(plugin), status.name, method)
            if status in (PluginSupport.DEFAULT_BEFORE_MAIN, PluginSupport.REQUESTED_SETTINGS_BEFORE, PluginSupport.REQUESTED_CMD_BEFORE):
                active_plugins['before'].append(plugin)
            elif status in (PluginSupport.DEFAULT_MAIN, PluginSupport.REQUESTED_SETTINGS_MAIN, PluginSupport.REQUESTED_CMD_MAIN):
                active_plugins['main'].append(plugin)
            elif status in (PluginSupport.DEFAULT_AFTER_MAIN, PluginSupport.REQUESTED_SETTINGS_AFTER, PluginSupport.REQUESTED_CMD_AFTER):
                active_plugins['after'].append(plugin)
        return active_plugins


    def _run_action(self, method: str):
        """implmementation of the plugin calling logic"""
        LOGGER.info("running %s", method)
        plugins = self._find_active_plugins(method)
        results = []
        for before_plugin in plugins['before']:
            LOGGER.debug("%s: %s", method, get_class_name(before_plugin))
            results.append(getattr(before_plugin, method)(self._settings))
        for main_plugin in plugins['main']:
            LOGGER.debug("%s: %s", method, get_class_name(main_plugin))
            results.append(getattr(main_plugin, method)(self._settings))
        for after_plugin in plugins['after']:
            LOGGER.debug("%s: %s", method, get_class_name(after_plugin))
            results.append(getattr(after_plugin, method)(self._settings))
        
        self._actions_run += 1
        if method == "settings":
            self._update_settings(results)

    def _update_settings(self, new_settings):
        for new_setting in itertools.chain(*new_settings):
            current_setting = self._settings.get(new_setting.name, None)
            if current_setting is not None:
                if new_setting.priority > current_setting.priority:
                    self._settings[current_setting.name] = new_setting
                elif new_setting.priority == current_setting.priority and self._actions_run > 0:
                    LOGGER.debug("ignoring duplicate priority setting %s from %s and %s",
                            new_setting.name,
                            current_setting.source,
                            new_setting.source
                            )
            else:
                self._settings[new_setting.name] = new_setting

    def build(self):
        """delgates to the right compile function"""
        self._run_action("settings")
        self._run_action("build")

    def configure(self):
        """delgates to the right configure function"""
        self._run_action("settings")
        self._run_action("configure")

    def test(self):
        """delgates to the right test function"""
        self._run_action("settings")
        self._run_action("test")

    def clean(self):
        """delegates to the right clean function"""
        self._run_action("settings")
        self._run_action("clean")

    def install(self):
        """delegates to the right clean function"""
        self._run_action("settings")
        self._run_action("install")

    def format(self):
        """delegates to the right format function"""
        self._run_action("settings")
        self._run_action("format")

    def tidy(self):
        """delegates to the right tidy function"""
        self._run_action("settings")
        self._run_action("tidy")

    def bench(self):
        """delegates to the right bench function"""
        self._run_action("settings")
        self._run_action("bench")

    def run(self):
        """delgates to the right run function"""
        self._run_action("settings")
        self._run_action("run")

    def settings(self):
        """delegates to the right clean function"""
        self._run_action("settings")
        for value in self._settings.values():
            print(value)

    def generate(self):
        """delgates to the right run function"""
        self._run_action("settings")
        self._run_action("generate")




