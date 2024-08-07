import asyncio
import re
import aiofiles
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from itertools import filterfalse
from typing import Iterable, cast

from django.conf import settings
from importlib.metadata import version
from typing_extensions import TypedDict
from djelm.forms.widgets.main import WIDGET_NAMES, WIDGET_NAMES_T
from djelm.generators import (
    ModelGenerator,
    ModelBuilder,
    ModelChoiceFieldWidgetGenerator,
    ProgramBuilder,
    ProgramGenerator,
    WidgetModelGenerator,
)
from watchfiles import awatch

from djelm.cookiecutter import CookieCutter
from djelm.subprocess import SubProcess

from .effect import ExitFailure, ExitSuccess
from .elm import Elm
from .npm import NPM
from .utils import (
    STUFF_NAMESPACE,
    get_app_path,
    get_app_src_path,
    is_djelm,
    module_name,
    program_file,
    to_program_namespace,
    walk_level,
)
from .validate import Validations

CreateCookieExtra = TypedDict("CreateCookieExtra", {"app_name": str})
AddProgramCookieExtra = TypedDict(
    "AddProgramCookieExtra",
    {
        "program_name": str,
        "view_name": str,
        "tmp_dir": str,
        "tag_file": str,
        "scope": str,
        "app_name": str,
    },
)

FlagsCookieExtra = TypedDict(
    "FlagsCookieExtra",
    {
        "program_name": str,
        "alias_type": str,
        "decoder_body": str,
        "tmp_dir": str,
    },
)


class StrategyError(Exception):
    pass


@dataclass(slots=True)
class FindPrograms:
    app_name: str

    def run(self, logger) -> ExitSuccess[list[str]] | ExitFailure[None, StrategyError]:
        src_path = get_app_src_path(self.app_name)

        if src_path.tag != "Success":
            raise src_path.err
        if not os.path.isdir(os.path.join(src_path.value, "src")):
            logger.write("No programs found.")
            return ExitSuccess([])

        programs_home = os.path.join(src_path.value, "src")

        dir_data: Iterable[tuple[str, list[str], list[str]]] = walk_level(programs_home)
        _, _, files = next(dir_data)
        elm_files = list(filter(lambda x: x.endswith(".elm"), files))
        parsed_file_results = asyncio.run(self.parsed_files(programs_home, elm_files))

        if parsed_file_results:
            logger.write("I found the following programs:\n")
            for f in parsed_file_results:
                if f.tag == "Success":
                    if f.value.endswith(".elm"):
                        logger.write(f"""    {f.value}""")
                else:
                    logger.write(str(f.err))

        return ExitSuccess(elm_files)

    async def parsed_files(self, programs_home: str, files: list[str]):
        parsed_file_exits = [self.parse_file(programs_home, f) for f in files]
        return await asyncio.gather(*parsed_file_exits)

    async def parse_file(
        self, programs_home: str, file: str
    ) -> ExitSuccess[str] | ExitFailure[None, Exception]:
        try:
            handle = await aiofiles.open(os.path.join(programs_home, file))
            content = await handle.read()
            await handle.close()
            if re.search(
                r"^(main : Program Value Model Msg)", content, flags=re.MULTILINE
            ):
                return ExitSuccess(file)
            else:
                return ExitFailure(
                    None, Exception("'main : Program Value Model Msg' not found")
                )

        except Exception as err:
            return ExitFailure(None, err)


@dataclass(slots=True)
class AddWidgetStrategy:
    """Add a djelm widget"""

    app_name: str
    widget_name: WIDGET_NAMES_T
    handler: ProgramBuilder
    no_deps: bool

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        src_path = get_app_src_path(self.app_name)
        app_path = get_app_path(self.app_name)
        djelm_version = version("djelm")

        if src_path.tag != "Success":
            raise src_path.err

        if app_path.tag != "Success":
            raise app_path.err

        if not self.no_deps:
            install_deps_effect = self.handler.install_elm_deps(src_path.value, logger)
            if install_deps_effect.tag != "Success":
                raise install_deps_effect.err

        # Make widgets dir in elm-stuff
        try:
            os.makedirs(os.path.join(src_path.value, *STUFF_NAMESPACE, "widgets"))
        except FileExistsError:
            pass

        # Make flags dirs
        try:
            os.makedirs(os.path.join(app_path.value, "flags", "widgets"))
        except FileExistsError:
            pass

        # Make Widgets dirs
        try:
            os.makedirs(os.path.join(src_path.value, "src", "Widgets", "Models"))
        except FileExistsError:
            pass

        cookie = self.handler.cookie_cutter(
            self.app_name, self.widget_name, src_path.value, djelm_version
        )

        # Cut cookie
        ck_result = cookie.cut(logger)

        if ck_result.tag != "Success":
            raise ck_result.err

        # Apply template applicators
        try:
            for applicator in self.handler.applicators(
                ck_result.value,
                src_path.value,
                app_path.value,
                self.widget_name,
                self.app_name,
                logger,
            ):
                applicator.apply(logger)

        except OSError as err:
            raise err

        # Generate model
        model_strat = GenerateModelStrategy(
            self.app_name,
            self.widget_name,
            WidgetModelGenerator(),
            from_source=True,
            watch_mode=False,
        )
        model_strat_effect = model_strat.run(logger)

        if model_strat_effect.tag != "Success":
            raise model_strat_effect.err

        return ExitSuccess(None)


@dataclass(slots=True)
class CompileStrategy:
    """
    Compiles all elm programs inside of a djelm app
    """

    app_name: str
    build: bool = False
    raise_error: bool = True

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        src_path = get_app_src_path(self.app_name)

        if src_path.tag == "Success":
            try:
                COMPILE_PROGRAM = f"""
                "use strict";
                const _core = require("@parcel/core");
                let bundler = new _core.Parcel({{
                  entries: "./djelm_src/*.ts",
                  defaultConfig: "@parcel/config-default",
                  mode: {"'production'" if self.build else "'development'"},
                  defaultTargetOptions: {{
                    distDir: "../static/dist",
                    outputFormat: "esmodule",
                  }},
                }});
                async function Main() {{
                  try {{
                    let {{ bundleGraph, buildTime }} = await bundler.run();
                    let bundles = bundleGraph.getBundles();
                    console.log(`✨ Built ${{bundles.length}} bundles in ${{buildTime}}ms!\n`);
                  }} catch (err) {{
                    if (Array.isArray(err.diagnostics)) {{
                      err.diagnostics.forEach((d) => console.error(d.message ? d.message : d));
                    }} else {{
                      console.error(err.diagnostics);
                    }}
                    process.exit(1);
                  }}
                }}
                Main().then(() => process.exit());
                """
                process = SubProcess(
                    ["node", "-e", COMPILE_PROGRAM],
                    os.path.join(src_path.value),
                    self.raise_error,
                )
                try:
                    process.open()
                except Exception as err:
                    if self.raise_error:
                        raise err
                    else:
                        return ExitSuccess(None)
                return ExitSuccess(None)
            except subprocess.CalledProcessError:
                sys.exit(1)
        return ExitFailure(None, StrategyError("Error"))


@dataclass(slots=True)
class WatchStrategy:
    """
    Sets up the file watcher for the given djelm app.
    When changes occur it will re-compile the elm programs.

    Modules in the flags directory are also monitored and models generated.
    """

    app_name: str

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        compile = CompileStrategy(self.app_name, raise_error=False)
        src_path = get_app_src_path(self.app_name)
        app_path = get_app_path(self.app_name)

        if src_path.tag != "Success":
            raise src_path.err

        if app_path.tag != "Success":
            raise app_path.err

        shutil.rmtree(os.path.join(src_path.value, ".parcel-cache"), ignore_errors=True)
        try:
            # first pass compile on start of watch
            compile.run(logger)
            return asyncio.run(
                self.watch(
                    app_path.value,
                    src_path.value,
                    [
                        os.path.join(src_path.value, "src"),
                        os.path.join(src_path.value, "djelm_src"),
                        os.path.join(app_path.value, "flags"),
                    ],
                    logger,
                )
            )
        except KeyboardInterrupt:
            return ExitSuccess(None)

    async def watch(
        self,
        app_path: str,
        src_path: str,
        dir: list[str],
        logger,
    ):
        compile = CompileStrategy(self.app_name, raise_error=False)
        async for changes in awatch(*dir):
            for change, f in changes:
                # VIM creates a file to check it can create a file, we want to ignore it
                if f.endswith("4913"):
                    continue
                # If flags change generate models
                # TODO Don't generate a model when a flags module is deleted
                # TODO Only generate a model when the flags output is different to what has already been generated.
                # TODO Validate if it's an actual flag file and not some other python file
                if os.path.join(app_path, "flags") in f and f.endswith(".py"):
                    dirname = os.path.basename(os.path.dirname(f))
                    target_dirs = ["widgets", "flags"]
                    # bail early
                    if dirname not in target_dirs:
                        continue
                    filename = os.path.splitext(os.path.basename(f))[0]
                    namespace = ["src"]
                    generator: ModelBuilder = ModelGenerator()
                    if "widgets" == dirname:
                        namespace.append("Widgets")
                        generator = WidgetModelGenerator()
                    program_name = program_file(filename)
                    # TODO validate if program is an actual Elm program and not some other Elm file
                    is_program = os.path.isfile(
                        os.path.join(src_path, *namespace, program_name)
                    )
                    if is_program:
                        logger.write(f"FLAGS CHANGED: {f}")
                        try:
                            GenerateModelStrategy(
                                self.app_name,
                                module_name(filename),
                                generator,
                                from_source=True,
                                watch_mode=True,
                            ).run(logger)
                        except Exception:
                            pass
                    continue
                # VIM for some reason triggers an ADDED(2) event when saving a buffer
                if change == 1:
                    logger.write(f"FILE ADDED: {f}")
                    # recompile
                    compile.run(logger)
                if change == 2:
                    logger.write(f"FILE MODIFIED: {f}")
                    # recompile
                    compile.run(logger)

        return ExitSuccess(None)


@dataclass(slots=True)
class NpmStrategy:
    """
    A helper class to call the node package manager binary on the given djelm app.

    The commands passed will execute in the directory of the djelm app that contains the package.json file.
    """

    app_name: str
    args: list[str]

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        npm = NPM()
        src_path = get_app_src_path(self.app_name)

        if src_path.tag != "Success":
            # TODO Better error
            raise src_path.err

        npm_exit = npm.command(src_path.value, self.args)

        if npm_exit.tag != "Success":
            # TODO Better error
            raise npm_exit.err

        logger.write("\033[92mCompleted successfully.\033[0m")
        return ExitSuccess(None)


@dataclass(slots=True)
class ElmStrategy:
    """
    A Helper class to call an elm binary on the given djelm app.

    The commands passed will execute in the directory of the djelm app that contains the elm.json file.
    """

    app_name: str
    args: list[str]

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        elm: Elm = Elm()
        src_path = get_app_src_path(self.app_name)
        if src_path.tag == "Success":
            elm_exit = elm.command(self.args, target_dir=src_path.value)

            if elm_exit.tag == "Success":
                return ExitSuccess(None)
            else:
                return ExitFailure(None, err=StrategyError(elm_exit.err))
        return ExitFailure(None, err=StrategyError())


class GenerateModelStrategy:
    """Generate a model and decoders for an Elm program"""

    def __init__(
        self,
        app_name,
        prog_name,
        handler: ModelBuilder,
        from_source: bool,
        watch_mode: bool,
    ) -> None:
        self.app_name = app_name
        self.prog_name = prog_name
        self.handler = handler
        self.from_source = from_source
        self.watch_mode = watch_mode

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        app_path = get_app_path(self.app_name)
        src_path = get_app_src_path(self.app_name)
        handler = self.handler

        if app_path.tag != "Success":
            raise app_path.err
        if src_path.tag != "Success":
            raise src_path.err

        flags_effect = handler.load_flags(
            app_path.value, self.prog_name, self.from_source, self.watch_mode, logger
        )

        if flags_effect.tag != "Success":
            raise flags_effect.err

        try:
            os.makedirs(os.path.join(src_path.value, *STUFF_NAMESPACE))
        except FileExistsError:
            pass
        except FileNotFoundError as err:
            raise err
        ck = handler.cookie_cutter(
            flags_effect.value, self.app_name, self.prog_name, src_path.value
        )
        try:
            cookie_effect = ck.cut(logger)

            if cookie_effect.tag != "Success":
                raise cookie_effect.err

            for applicator in handler.applicators(
                cookie_effect.value,
                src_path.value,
                app_path.value,
                self.prog_name,
                self.app_name,
                logger,
            ):
                applicator.apply(logger)

            return ExitSuccess(None)
        except OSError as err:
            raise err


@dataclass(slots=True)
class AddProgramStrategy:
    """Create a default elm program.

    The program model is static and get's generated from the ProgramBuilder.
    """

    app_name: str
    prog_name: str
    handler: ProgramBuilder

    def run(
        self, logger
    ) -> (
        ExitSuccess[None]
        | ExitFailure[None | str, StrategyError | FileNotFoundError | Exception]
    ):
        src_path = get_app_src_path(self.app_name)
        app_path = get_app_path(self.app_name)
        djelm_version = version("djelm")
        stuff_namespace = ("elm-stuff", f"djelm_{djelm_version}")

        if src_path.tag != "Success":
            raise src_path.err

        if app_path.tag != "Success":
            raise app_path.err

        try:
            os.makedirs(os.path.join(src_path.value, *stuff_namespace))
        except FileExistsError:
            pass
        except FileNotFoundError as err:
            raise err

        program_ck = self.handler.cookie_cutter(
            self.app_name, self.prog_name, src_path.value, djelm_version
        )

        program_ck_effect = program_ck.cut(logger)

        if program_ck_effect.tag != "Success":
            raise program_ck_effect.err

        # Apply program applicators
        try:
            for applicator in self.handler.applicators(
                program_ck_effect.value,
                src_path.value,
                app_path.value,
                self.prog_name,
                self.app_name,
                logger,
            ):
                applicator.apply(logger)
        except OSError as err:
            raise err

        # Generate model
        model_strat = GenerateModelStrategy(
            self.app_name,
            self.prog_name,
            ModelGenerator(),
            from_source=False,
            watch_mode=False,
        )

        model_strat_effect = model_strat.run(logger)

        if model_strat_effect.tag != "Success":
            raise model_strat_effect.err

        logger.write(
            f"""
I created the \033[92m{self.prog_name}.elm\033[0m program for you!

Right now it's just a default little program that you can change to your hearts content.

You can find it here:

\033[92m{os.path.join(src_path.value, 'src', program_file(self.prog_name))}\033[0m

Check out <https://github.com/Confidenceman02/django-elm/blob/main/README.md> to find out how to compile it and see it in the browser.

"""
        )
        return ExitSuccess(None)


class ListStrategy:
    apps: list[str] = settings.INSTALLED_APPS

    def run(self, logger) -> ExitSuccess[list[str]] | ExitFailure[None, StrategyError]:
        app_path_exits = filterfalse(
            lambda x: x.tag == "Failure", map(get_app_path, self.apps)
        )

        dir_data: Iterable[tuple[str, list[str], list[str]]] = map(
            next,
            map(lambda p: walk_level(p.value), app_path_exits),  # type:ignore
        )

        django_elm_apps = [os.path.basename(r) for r, _, f in dir_data if is_djelm(f)]

        apps = ""

        for app in django_elm_apps:
            apps += f"\033[93m{app}\033[0m\n\t"

        logger.write(
            f"""
Here are all the djelm apps I found:

        {apps}"""
        )
        return ExitSuccess(django_elm_apps)


class ListWidgetsStrategy:
    widgets = WIDGET_NAMES

    def run(
        self, logger
    ) -> ExitSuccess[list[WIDGET_NAMES_T]] | ExitFailure[None, StrategyError]:
        widgets = ""
        for w in self.widgets:
            widgets += f"\033[93m{w}\033[0m\n\t"

        logger.write(
            f"""
Here are all the widgets I support:

        {widgets}"""
        )
        return ExitSuccess(self.widgets)


@dataclass(slots=True)
class CreateStrategy:
    app_name: str

    def run(self, logger) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        ck = CookieCutter[CreateCookieExtra](
            file_dir=os.path.dirname(__file__),
            output_dir=os.getcwd(),
            cookie_dir_name="project_template",
            extra={
                "app_name": self.app_name.strip(),
            },
        )

        cut_cookie = ck.cut(logger)

        if cut_cookie.tag == "Success":
            app_name = os.path.basename(cut_cookie.value)
            logger.write(
                f"""

Hi there! I have created the \033[92m{f"{app_name}"}\033[0m djelm app for you. This is where all your Elm programs will live.

Now you may be wondering, what will be in this app? Where do I add Elm files?
How does it work with django so I can see it in the browser? How will my code grow? Do I need
more directories?

Check out <https://github.com/Confidenceman02/django-elm/blob/main/README.md> for all the answers!

For now, make sure you add \033[92m"{f"{app_name}"}"\033[0m to the \033[1mINSTALLED_APPS\033[0m variable in \033[1msettings.py\033[0m.
"""
            )
            return ExitSuccess(None)
        return ExitFailure(None, StrategyError(cut_cookie.err))


@dataclass(slots=True)
class Strategy:
    def create(
        self, labels, options: dict[str, bool]
    ) -> (
        ElmStrategy
        | CreateStrategy
        | ListStrategy
        | ListWidgetsStrategy
        | AddProgramStrategy
        | NpmStrategy
        | WatchStrategy
        | GenerateModelStrategy
        | CompileStrategy
        | AddWidgetStrategy
        | FindPrograms
    ):
        e = Validations().acceptable_command(labels)
        match e:
            case ExitFailure(err=err):
                raise err
            case ExitSuccess(value={"command": "create", "app_name": app_name}):
                return CreateStrategy(cast(str, app_name))
            case ExitSuccess(value={"command": "watch", "app_name": app_name}):
                return WatchStrategy(cast(str, app_name))
            case ExitSuccess(
                value={
                    "command": "addprogram",
                    "app_name": app_name,
                    "program_name": pn,
                }
            ):
                return AddProgramStrategy(
                    cast(str, app_name), cast(str, pn), handler=ProgramGenerator()
                )
            case ExitSuccess(
                value={
                    "command": "generatemodel",
                    "app_name": app_name,
                    "program_name": pn,
                }
            ):
                program_path, program_name = to_program_namespace(pn.split("."))
                return GenerateModelStrategy(
                    cast(str, app_name),
                    program_name,
                    handler=program_namespace_to_model_builder(
                        [*program_path, program_name]
                    ),
                    from_source=True,
                    watch_mode=False,
                )
            case ExitSuccess(value={"command": "list"}):
                return ListStrategy()
            case ExitSuccess(value={"command": "listwidgets"}):
                return ListWidgetsStrategy()
            case ExitSuccess(value={"command": "findprograms", "app_name": app_name}):
                return FindPrograms(app_name=app_name)
            case ExitSuccess(
                value={"command": "npm", "app_name": app_name, "args": args}
            ):
                return NpmStrategy(cast(str, app_name), cast(list[str], args))
            case ExitSuccess(
                value={"command": "elm", "app_name": app_name, "args": args}
            ):
                return ElmStrategy(cast(str, app_name), cast(list[str], args))
            case ExitSuccess(
                value={"command": "compile", "app_name": app_name, "build": build}
            ):
                return CompileStrategy(cast(str, app_name), cast(bool, build))
            case ExitSuccess(
                value={"command": "addwidget", "app_name": app_name, "widget": widget}
            ):
                return AddWidgetStrategy(
                    cast(str, app_name),
                    cast(WIDGET_NAMES_T, widget),
                    handler=widget_name_to_program_builder(widget),
                    no_deps=options.get("no_deps", False),
                )
            case _ as x:
                raise StrategyError(f"Unable to handle {x}")


def widget_name_to_program_builder(widget_name: WIDGET_NAMES_T) -> ProgramBuilder:
    match widget_name:
        case "ModelChoiceField":
            return ModelChoiceFieldWidgetGenerator()
        case "ModelMultipleChoiceField":
            return ModelChoiceFieldWidgetGenerator()
        case _:
            raise StrategyError(
                f"""The widget name {widget_name} is not supported.

\033[4m\033[1mHint\033[0m: Run \033[1mpython manage.py djelm listwidgets\033[0m to find out what type of widget programs I can add for you."""
            )


def program_namespace_to_model_builder(namespace: list[str]) -> ModelBuilder:
    match namespace:
        case [_]:
            return ModelGenerator()
        case ["Widgets", widget_name]:
            if widget_name in WIDGET_NAMES:
                return WidgetModelGenerator()
            else:
                raise StrategyError(
                    f"""

\033[91m-- UNKNOWN WIDGET ------------------------------------------------------------------------------------------------------------------------- command/generatemodel\033[0m

It looks like you are trying to generate a model for this widget:

    \033[93m{widget_name}\033[0m

But I don't recognize the \033[1m{widget_name}\033[0m widget name.

\033[4m\033[1mHint\033[0m: Run \033[1mpython manage.py djelm listwidgets\033[0m to find out what type of widget programs I can work with."""
                )

        case [head, *_]:
            raise StrategyError(
                f"""\033[91m-- INVALID PROGRAM NAMESPACE ------------------------------------------------------------------------------------------------------------------------- command/generatemodel\033[0m

I can't generate a model for programs in the {head} namespace.

\033[4m\033[1mHint\033[0m: Make sure the program you are trying to generate a model for exists in one of the following directories.

\033[1msrc\033[0m - python manage.py djelm generatemodel <app> <program_name>
\033[1mWidgets\033[0m  - python manage.py djelm generatemodel <app> Widgets.<widget_program>
"""
            )
        case _:
            raise StrategyError(f"I can't resolve a ModelBuilder for {namespace}")
