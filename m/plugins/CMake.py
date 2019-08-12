from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport

@plugin
class CMakePlugin(BasePlugin):

    def configure(self, settings):
        """configure the build directory"""
        if not self.is_configured(settings):
            settings['build_dir'].value.mkdir(exist_ok=True)
            run(["cmake","..","-G","Ninja"], cwd=settings['build_dir'].value)

    def is_configured(self, settings):
        """test if the build directory is configured"""
        return settings['build_dir'].value.exists() and (
                   (settings['build_dir'].value / "build.ninja").exists() or
                   (settings['build_dir'].value / "Makefile").exists()
               )

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["cmake","--build",".", *settings['cmdline'].value], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["ctest", *settings['cmdline'].value], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")

    def clean(self, settings):
        """cleans source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["cmake", "--build", ".", "--target", "clean"], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")

    def install(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)

        if self.is_configured(settings):
            print("m[1]: Entering directory", str(settings['build_dir'].value))
            run(["cmake","--install","."], cwd=settings['build_dir'].value)
        else:
            print("failed to configure")


    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if 'repo_base' in  settings and (settings['repo_base'].value / "CMakeLists.txt").exists():
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY
            

        return {
            "build": state,
            "test": state,
            "clean": state,
            "install": state
        }

