from multiprocessing import cpu_count
from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport

@plugin
class PythonSetupToolsPlugin(BasePlugin):

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        run(["python", "setup.py", "build", *settings['cmdline_build'].value], cwd=settings['repo_base'].value)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        run(["python", "setup.py", "test", *settings['cmdline_test'].value], cwd=settings['repo_base'].value)

    def clean(self, settings):
        """cleans source code or a subset there of"""
        run(["python", "setup.py", "clean", *settings['cmdline_clean'].value], cwd=settings['repo_base'].value)

    def install(self, settings):
        """cleans source code or a subset there of"""
        run(["python", "setup.py", "install", *settings['cmdline_install'].value], cwd=settings['repo_base'].value)


    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if 'repo_base' in  settings and (settings['repo_base'].value / "setup.py").exists():
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
            
        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": state
        }


