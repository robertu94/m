import enum
import pprint

def get_class_name(cls):
    """returns the name of the most derived class"""
    return cls.__class__.__name__


class NotProvidedError(Exception):
    """Thrown when the class does not provide the desired method"""

    def __str__(self, method, cls):
        return "{method} not provided on {cls}".format(method=method, cls=get_class_name(cls))

class Setting:

    LOW = 0
    DEFAULT = 1
    URGENT = 2

    def __init__(self, value, description, source, priority=DEFAULT):
        self.value = value
        self.description = description
        self.priority = priority
        self.source = source

    def __str__(self):
        return "{description} : {value}".format(
            description=self.description,
            value=pprint.pformat(self.value)
        )

class PluginSupport(enum.Enum):
    """
    Modes for supporting functions

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
    NOT_SUPPORTED = -2
    NOT_ENABLED_BY_REPOSITORY = -1
    NOT_ENABLED_BY_DEFAULT = 0
    NOT_NEEDED = 1
    DEFAULT_BEFORE_MAIN = 2
    DEFAULT_MAIN = 3
    DEFAULT_AFTER_MAIN = 4

    REQUESTED_SETTINGS_BEFORE_MAIN = 5
    REQUESTED_SETTINGS_MAIN = 6
    REQUESTED_SETTINGS_AFTER_MAIN = 7
    REQUESTED_CMD_BEFORE_MAIN = 8
    REQUESTED_CMD_MAIN = 9
    REQUESTED_CMD_AFTER_MAIN = 10

class BasePlugin:
    """this class provides the default behaivor for and methods for a plugin"""

    def compile(self, settings):
        """compiles the source code or a subset thereof"""
        raise NotProvidedError("compile", self)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        raise NotProvidedError("compile", self)

    def clean(self, settings):
        """cleans source code or a subset there of"""
        raise NotProvidedError("compile", self)

    def get_settings_factory(self, cls=None, priority=Setting.DEFAULT):
        """returns a helper function that fills in commmon arguments on the Settings object"""
        if cls is None:
            cls = self
        def factory(value, description):
            return Setting(value, description, get_class_name(self), priority)
        return factory


    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        return {
            "settings": PluginSupport.DEFAULT_BEFORE_MAIN
        }

    def check(self, method: str, settings) -> int:
        """returns integer priority representing if an operation is supported,
        higher values are preferred.

        Users: please call this method rather than checking _supported() or checking for exceptions
        Plugin Developers: please override _supported instead().
        """
        cls_name = get_class_name(self)

        
        return self._supported(settings).get(method, PluginSupport.NOT_SUPPORTED)

        

    def settings(self):
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

    def __init__(self):
        self.settings = []


    def _find_plugin(self, method: str):
        """finds the plugin that should conduct the given call"""
        for _plugin in ALL_PLUGINS:
            _plugin.check(method, self.settings)


    def compile(self):
        """delgates to the right compile function"""
        _plugin = self._find_plugin("compile")
        _plugin.compile(self.settings)

    def test(self):
        """delgates to the right test function"""
        _plugin = self._find_plugin("test")
        _plugin.test(self.settings)

    def clean(self):
        """delegates to the right clean function"""
        _plugin = self._find_plugin("clean")
        _plugin.test(self.settings)




