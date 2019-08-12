from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport

@plugin
class MesonPlugin(BasePlugin):

    def configure(self, settings):
        """configure the build directory"""
        if not self.is_configured(settings):
            settings['build_dir'].value.mkdir(exist_ok=True)
            run(["meson", str(settings['build_dir'].value)], cwd=settings['repo_base'].value)

    def is_configured(self, settings):
        """test if the build directory is configured"""
        return settings['build_dir'].value.exists() and (
                   (settings['build_dir'].value / "build.ninja").exists()
               )

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["ninja","-C", str(settings['build_dir'].value), *settings['cmdline'].value], cwd=settings['repo_base'].value)
        else:
            print("failed to configure")

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["meson", "test", *settings['cmdline'].value], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")

    def clean(self, settings):
        """cleans source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["ninja", "clean"], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")

    def install(self, settings):
        """cleans source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["ninja", "install"], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")


    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if 'repo_base' in  settings and (settings['repo_base'].value / "meson.build").exists():
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
            

        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": state
        }

