from subprocess import run, DEVNULL, PIPE
from .Base import plugin, BasePlugin, PluginSupport
import json
from jinja2 import Environment, PackageLoader, select_autoescape


@plugin
class CMakePlugin(BasePlugin):
    def configure(self, settings):
        """configure the build directory"""
        if not self.is_configured(settings):
            settings["build_dir"].value.mkdir(exist_ok=True)
            args = ["cmake", ".."]
            if self.has_ninja():
                args.extend(["-G", "Ninja"])
            if self.has_lld():
                args.extend(
                    [
                        "-DCMAKE_LINKER=lld",
                        "-DCMAKE_C_FLAGS=-fuse-ld=lld",
                        "-DCMAKE_CXX_FLAGS=-fuse-ld=lld",
                    ]
                )

            if self.has_sccache():
                args.extend(
                    [
                        "-DCMAKE_CXX_COMPILER_LAUNCHER=sccache",
                        "-DCMAKE_C_COMPILER_LAUNCHER=sccache",
                        "-DCMAKE_CUDA_COMPILER_LAUNCHER=sccache",
                    ]
                )
            elif self.has_ccache():
                args.extend(
                    [
                        "-DCMAKE_CXX_COMPILER_LAUNCHER=ccache",
                        "-DCMAKE_C_COMPILER_LAUNCHER=ccache",
                        "-DCMAKE_CUDA_COMPILER_LAUNCHER=ccache",
                    ]
                )
            args.extend(settings["cmdline_configure"].value)
            return run(args, cwd=settings["build_dir"].value).returncode

    def is_configured(self, settings):
        """test if the build directory is configured"""
        return settings["build_dir"].value.exists() and (
            (settings["build_dir"].value / "build.ninja").exists()
            or (settings["build_dir"].value / "Makefile").exists()
        )

    @staticmethod
    def has_lld() -> bool:
        """returns if the system has lld on the path"""
        result = run(["ld.lld", "-V"], stdout=DEVNULL, stderr=DEVNULL)
        return result.returncode == 0

    @staticmethod
    def has_sccache() -> bool:
        """returns if the system has sccache on the path"""
        result = run(["sccache", "-V"], stdout=DEVNULL, stderr=DEVNULL)
        return result.returncode == 0

    @staticmethod
    def has_ccache() -> bool:
        """returns if the system has ccache on the path"""
        result = run(["ccache", "-V"], stdout=DEVNULL, stderr=DEVNULL)
        return result.returncode == 0

    @staticmethod
    def has_ninja() -> bool:
        """returns if the system has ninja on the path"""
        result = run(["ninja", "--version"])
        return result.returncode == 0

    @staticmethod
    def print_builddir(settings):
        print(f"m: Entering directory '{settings['build_dir'].value!s}'", flush=True)

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)

        if self.is_configured(settings):
            self.print_builddir(settings)
            return run(
                ["cmake", "--build", ".", *settings["cmdline_build"].value],
                cwd=settings["build_dir"].value,
            ).returncode
        else:
            print("failed to configure")
            return -1

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        self.configure(settings)
        self.build(settings)

        if self.is_configured(settings):
            self.print_builddir(settings)
            ctest_args = settings["cmdline_test"].value or ["--output-on-failure"]
            return run(
                ["ctest", *ctest_args],
                cwd=settings["build_dir"].value,
            ).returncode
        else:
            print("failed to configure")
            return -1

    def clean(self, settings):
        """cleans source code or a subset there of"""
        self.configure(settings)

        if self.is_configured(settings):
            self.print_builddir(settings)
            return run(
                ["cmake", "--build", ".", "--target", "clean"],
                cwd=settings["build_dir"].value,
            ).returncode
        else:
            print("failed to configure")
            return -1

    def install(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)

        if self.is_configured(settings):
            self.print_builddir(settings)
            return run(
                ["cmake", "--install", "."], cwd=settings["build_dir"].value
            ).returncode
        else:
            print("failed to configure")
            return -1

    def generate(self, settings):
        g_settings = settings["cmdline_generate"].value
        if (not g_settings) or g_settings[0].startswith("l"):
            return self._generate_library(settings)
        elif g_settings[0].startswith("b"):
            return self._generate_binary(settings)
        else:
            print("unknown options", *g_settings)
            return -1

    def _prepare_template(self, settings):
        cmake_version_p = run(["cmake", "-E", "capabilities"], stdout=PIPE, stderr=PIPE)
        cmake_version = json.loads(cmake_version_p.stdout)["version"]["string"]

        env = {
            "cmake_version_str": cmake_version,
            "repo_name": settings["repo_base"].value.name,
        }
        template_env = Environment(
            loader=PackageLoader("m", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        def templater(template_name, template_dest):
            template = template_env.get_template(template_name)
            render = template.render(**env)
            with open(template_dest, "w") as outfile:
                outfile.write(render)

        return templater, env

    def _generate_library(self, settings):
        templater, env = self._prepare_template(settings)
        (settings["repo_base"].value / "test").mkdir(exist_ok=True, parents=True)
        (settings["repo_base"].value / "include").mkdir(exist_ok=True, parents=True)
        (settings["repo_base"].value / "src").mkdir(exist_ok=True, parents=True)
        (settings["repo_base"].value / "src" / (env["repo_name"] + ".cc")).touch()
        (settings["repo_base"].value / "include" / (env["repo_name"] + ".h")).touch()
        templater(
            "cpp/CMakeListsLibrary.txt.j2",
            settings["repo_base"].value / "CMakeLists.txt",
        )
        templater(
            "cpp/VersionConfig.cmake.in.j2",
            settings["repo_base"].value / (env["repo_name"] + "Config.cmake.in"),
        )
        templater(
            "cpp/library_name.pc.in.j2",
            settings["repo_base"].value / (env["repo_name"] + ".pc.in"),
        )
        templater(
            "cpp/repo_name_version.h.in.j2",
            settings["repo_base"].value / "src" / (env["repo_name"] + "_version.h.in"),
        )
        templater(
            "cpp/CMakeListsTests.txt.j2",
            settings["repo_base"].value / "test" / "CMakeLists.txt",
        )
        templater(
            "cpp/GTestCMakeLists.txt.in.j2",
            settings["repo_base"].value / "test" / "GTestCMakeLists.txt.in",
        )
        templater(
            "cpp/test.cc.j2",
            settings["repo_base"].value / "test" / ("test_" + env["repo_name"] + ".cc"),
        )
        return 0

    def _generate_binary(self, settings):
        templater, env = self._prepare_template(settings)
        (settings["repo_base"].value / "test").mkdir(exist_ok=True, parents=True)
        (settings["repo_base"].value / "include").mkdir(exist_ok=True, parents=True)
        (settings["repo_base"].value / "src").mkdir(exist_ok=True, parents=True)
        (settings["repo_base"].value / "include" / (env["repo_name"] + ".h")).touch()
        templater(
            "cpp/binary_name.cc.j2",
            settings["repo_base"].value / "src" / (env["repo_name"] + ".cc"),
        )
        templater(
            "cpp/CMakeListsBinary.txt.j2",
            settings["repo_base"].value / "CMakeLists.txt",
        )
        templater(
            "cpp/repo_name_version.h.in.j2",
            settings["repo_base"].value / "src" / (env["repo_name"] + "_version.h.in"),
        )
        templater(
            "cpp/CMakeListsTests.txt.j2",
            settings["repo_base"].value / "test" / "CMakeLists.txt",
        )
        templater(
            "cpp/GTestCMakeLists.txt.in.j2",
            settings["repo_base"].value / "test" / "GTestCMakeLists.txt.in",
        )
        templater(
            "cpp/test.cc.j2",
            settings["repo_base"].value / "test" / ("test_" + env["repo_name"] + ".cc"),
        )
        return 0

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if (
            "repo_base" in settings
            and (settings["repo_base"].value / "CMakeLists.txt").exists()
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "configure": state,
            "build": state,
            "test": state,
            "clean": state,
            "install": state,
            "generate": PluginSupport.NOT_ENABLED_BY_DEFAULT,
        }
