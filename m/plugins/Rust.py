from subprocess import run, DEVNULL
from .Base import plugin, BasePlugin, PluginSupport

@plugin
class RustPlugin(BasePlugin):

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        run(["cargo", "build",  *settings['cmdline_build'].value], cwd=settings['repo_base'].value)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        run(["cargo", "test", *settings['cmdline_test'].value], cwd=settings['repo_base'].value)
        

    def clean(self, settings):
        """cleans source code or a subset there of"""
        run(["cargo", "clean"], cwd=settings['repo_base'].value)

    def install(self, settings):
        """compiles the source code or a subset thereof"""
        run(["cargo", "install", *settings['cmdline_install'].value], cwd=settings['repo_base'].value)

    def run(self, settings):
        """runs the binary"""
        run(["cargo", "run", *settings['cmdline_run'].value], cwd=settings['repo_base'].value)

    def format(self, settings):
        """runs the binary"""
        run(["cargo", "fmt", *settings['cmdline_format'].value], cwd=settings['repo_base'].value)

    def tidy(self, settings):
        """runs the binary"""
        run(["cargo", "check", *settings['cmdline_tidy'].value], cwd=settings['repo_base'].value)


    def bench(self, settings):
        """runs the binary"""
        run(["cargo", "bench", *settings['cmdline_bench'].value], cwd=settings['repo_base'].value)

    def generate(self, settings):
        run(["cargo", "init", *settings['cmdline_generate'].value], cwd=settings['repo_base'].value)

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if 'repo_base' in settings and \
                (settings['repo_base'].value / "Cargo.toml").exists():
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": state,
            "run": state,
            "format": state,
            "tidy": state,
            "bench": state,
            "generate": PluginSupport.NOT_ENABLED_BY_DEFAULT,
        }

