from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport

@plugin
class CMakePlugin(BasePlugin):

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        run(["cmake",".."], cwd=settings['build_dir'].value)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        raise NotProvidedError("test", self)

    def clean(self, settings):
        """cleans source code or a subset there of"""
        raise NotProvidedError("clean", self)

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if 'repo_dir' in  settings and (settings['repo_dir'].value / "CMakeLists.txt").exists():
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
            

        return {
            "build": state,
            "test": state,
            "clean": state
        }

