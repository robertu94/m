from multiprocessing import cpu_count
from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport

@plugin
class AutotoolsPlugin(BasePlugin):

    def build(self, settings):
        """compiles the source code or a subset thereof"""

        if not (settings['repo_base'].value / "configure").exists() and (settings['repo_base'].value / "autogen.sh").exists():
            run(["./autogen.sh"], cwd=settings['repo_base'].value)

        if not (settings['repo_base'].value / "configure").exists() and (settings['repo_base'].value / "configure").exists():
            run(["./configure"], cwd=settings['repo_base'].value)

        run(["make", "-j", str(cpu_count())], cwd=settings['repo_base'].value)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        run(["make", "-j", str(cpu_count()), "check"], cwd=settings['repo_base'].value)

    def clean(self, settings):
        """cleans source code or a subset there of"""
        run(["make", "-j", str(cpu_count()), "clean"], cwd=settings['repo_base'].value)

    def install(self, settings):
        """cleans source code or a subset there of"""
        run(["make", "-j", str(cpu_count()), "install"], cwd=settings['repo_base'].value)


    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if 'repo_base' in  settings and (
                (settings['repo_base'].value / "autogen.sh").exists() or
                (settings['repo_base'].value / "configure").exists() or
                (settings['repo_base'].value / "Makefile").exists() or
                (settings['repo_base'].value / "makefile").exists()
                ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
            

        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": state
        }

