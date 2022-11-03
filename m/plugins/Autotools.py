from multiprocessing import cpu_count
from subprocess import run
from .Base import plugin, BasePlugin, PluginSupport
from jinja2 import Environment, PackageLoader, select_autoescape


@plugin
class AutotoolsPlugin(BasePlugin):
    def configure(self, settings):
        if (
            not (settings["repo_base"].value / "configure").exists()
            and (settings["repo_base"].value / "autogen.sh").exists()
        ):
            run(["./autogen.sh"], cwd=settings["repo_base"].value)

        if (
            not (settings["repo_base"].value / "configure").exists()
            and (settings["repo_base"].value / "configure").exists()
        ):
            args = ["./configure"]
            args.extend(settings["cmdline_configure"].value)
            run(args, cwd=settings["repo_base"].value)

    def build(self, settings):
        """compiles the source code or a subset thereof"""
        self.configure(settings)
        run(["make", "-j", str(cpu_count())], cwd=settings["repo_base"].value)

    def test(self, settings):
        """runs automated tests on source code or a subset there of"""
        run(["make", "-j", str(cpu_count()), "check"], cwd=settings["repo_base"].value)

    def bench(self, settings):
        """runs automated benchmarks on source code or a subset there of"""
        run(["make", "-j", str(cpu_count()), "bench"], cwd=settings["repo_base"].value)

    def clean(self, settings):
        """cleans source code or a subset there of"""
        run(["make", "-j", str(cpu_count()), "clean"], cwd=settings["repo_base"].value)

    def install(self, settings):
        """cleans source code or a subset there of"""
        run(
            ["make", "-j", str(cpu_count()), "install"], cwd=settings["repo_base"].value
        )

    def generate(self, settings):
        """generates a basic project"""
        g_settings = settings["cmdline_generate"].value
        if (not g_settings) or g_settings[0].startswith("m"):
            self._generate_makefile(settings)
        else:
            print("unknown options", *g_settings)

    def _prepare_template(self, settings):

        env = {"repo_name": settings["repo_base"].value.name}
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

    def _generate_makefile(self, settings):
        templater, env = self._prepare_template(settings)
        source = settings["repo_base"].value / (env["repo_name"] + ".cc")
        templater("cpp/example.j2", source)
        templater("cpp/Makefile.j2", settings["repo_base"].value / "Makefile")

    @staticmethod
    def _supported(settings):
        """returns a dictionary of supported functions"""
        if "repo_base" in settings and (
            (settings["repo_base"].value / "autogen.sh").exists()
            or (settings["repo_base"].value / "configure").exists()
            or (settings["repo_base"].value / "GNUmakefile").exists()
            or (settings["repo_base"].value / "Makefile").exists()
            or (settings["repo_base"].value / "makefile").exists()
        ):
            state = PluginSupport.DEFAULT_MAIN
        else:
            state = PluginSupport.NOT_ENABLED_BY_REPOSITORY

        return {
            "configure": state,
            "build": state,
            "test": state,
            "bench": state,
            "clean": state,
            "install": state,
            "generate": PluginSupport.NOT_ENABLED_BY_DEFAULT,
        }
