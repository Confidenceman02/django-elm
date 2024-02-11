import asyncio
import os
import shutil
import subprocess
import sys
import types
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import filterfalse
from typing import Iterable, cast

from django.conf import settings
from importlib.metadata import version
from typing_extensions import TypedDict
from watchfiles import awatch

from djelm.cookiecutter import CookieCutter
from djelm.flags.main import Flags
from djelm.subprocess import SubProcess

from .effect import ExitFailure, ExitSuccess
from .elm import Elm
from .npm import NPM
from .utils import (
    get_app_path,
    get_app_src_path,
    is_djelm,
    module_name,
    program_file,
    scope_name,
    tag_file_name,
    view_name,
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
class CompileStrategy:
    """
    Compiles all elm programs inside of a djelm app
    """

    app_name: str
    build: bool = False
    raise_error: bool = True

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
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
                except Exception as _:
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

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
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
            compile.run(logger, style)
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
                    style,
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
        style,
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
                if os.path.join(app_path, "flags") in f and f.endswith(".py"):
                    filename = os.path.basename(f).split(".")[0]
                    program_name = program_file(filename)
                    is_program = os.path.isfile(
                        os.path.join(src_path, "src", program_name)
                    )
                    if is_program:
                        logger.write(f"FLAGS CHANGED: {f}")
                        GenerateModelStrategy(self.app_name, module_name(filename)).run(
                            logger, style
                        )
                    continue
                # VIM for some reason triggers an ADDED(2) event when saving a buffer
                if change == 1:
                    logger.write(f"FILE ADDED: {f}")
                    # recompile
                    compile.run(logger, style)
                if change == 2:
                    logger.write(f"FILE MODIFIED: {f}")
                    # recompile
                    compile.run(logger, style)

        return ExitSuccess(None)


@dataclass(slots=True)
class NpmStrategy:
    """
    A helper class to call the node package manager binary on the given djelm app.

    The commands passed will execute in the directory of the djelm app that contains the package.json file.
    """

    app_name: str
    args: list[str]

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        npm = NPM()
        src_path = get_app_src_path(self.app_name)

        if src_path.tag != "Success":
            # TODO Better error
            raise src_path.err

        npm_exit = npm.command(src_path.value, self.args)

        if npm_exit.tag != "Success":
            # TODO Better error
            raise npm_exit.err

        logger.write(style.SUCCESS("Completed successfully."))
        return ExitSuccess(None)


@dataclass(slots=True)
class ElmStrategy:
    """
    A Helper class to call an elm binary on the given djelm app.

    The commands passed will execute in the directory of the djelm app that contains the elm.json file.
    """

    app_name: str
    args: list[str]

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        elm: Elm = Elm()
        src_path = get_app_src_path(self.app_name)
        if src_path.tag == "Success":
            elm_exit = elm.command(self.args, target_dir=src_path.value)

            if elm_exit.tag == "Success":
                logger.write(elm_exit.value)
                return ExitSuccess(None)
            else:
                return ExitFailure(None, err=StrategyError(elm_exit.err))
        return ExitFailure(None, err=StrategyError())


class BaseGenerateModelStrategy(ABC):
    @abstractmethod
    def flags(self) -> Flags:
        pass


class GenerateModelStrategy(BaseGenerateModelStrategy):
    """Generate a model and decoders for an Elm program"""

    def __init__(self, app_name, prog_name) -> None:
        self.app_name = app_name
        self.prog_name = prog_name

    def flags(self) -> Flags:
        app_path_exit = get_app_path(self.app_name)
        src_path = get_app_src_path(self.app_name)
        if app_path_exit.tag == "Success" and src_path.tag == "Success":
            import importlib.machinery

            loader = importlib.machinery.SourceFileLoader(
                tag_file_name(self.prog_name),
                os.path.join(
                    app_path_exit.value, "flags", tag_file_name(self.prog_name) + ".py"
                ),
            )
            mod = types.ModuleType(loader.name)

            try:
                loader.exec_module(mod)
            except Exception as err:
                raise err

            return getattr(mod, self.prog_name + "Flags")
        raise StrategyError("Unable to resolve app_path or src_path")

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        app_path_exit = get_app_path(self.app_name)
        src_path = get_app_src_path(self.app_name)

        djelm_version = version("djelm")
        stuff_namespace = ("elm-stuff", f"djelm_{djelm_version}")

        if app_path_exit.tag != "Success":
            raise app_path_exit.err
        if src_path.tag != "Success":
            raise src_path.err
        try:
            flags = self.flags()
        except Exception as err:
            logger.write(
                f"""
\033[91m-- FLAG MODULE ERROR ----------------------------------------------------------------------------------------------------- command/generatemodel\033[0m

I was trying to generate a model from this flags module:

    \033[93m{os.path.join(app_path_exit.value, "flags", tag_file_name(self.prog_name) + ".py")}\033[0m

But got the following error type:

    \033[93m{err.args[0]}\033[0m

Make sure you fix the errors in \033[1m{os.path.join(app_path_exit.value, "flags", tag_file_name(self.prog_name) + ".py")}\033[0m.

\033[4m\033[1mNote\033[0m: I'll keep watching this module and will generate the model once the errors are fixed.

"""
            )
            return ExitFailure(None, err=StrategyError(err))

        try:
            os.makedirs(os.path.join(src_path.value, *stuff_namespace))
        except FileExistsError:
            pass
        except FileNotFoundError as err:
            raise err
        try:
            ck = CookieCutter[FlagsCookieExtra](
                file_dir=os.path.dirname(__file__),
                output_dir=os.path.join(src_path.value, stuff_namespace[0]),
                cookie_dir_name="flags_template",
                extra={
                    "program_name": module_name(self.prog_name),
                    "tmp_dir": stuff_namespace[1],
                    "alias_type": flags.to_elm_parser_data()["alias_type"],
                    "decoder_body": flags.to_elm_parser_data()["decoder_body"],
                },
                overwrite=True,
            )
            temp_dir_path = ck.cut(logger)

            if temp_dir_path.tag != "Success":
                raise temp_dir_path.err

            # Move elm program flags
            shutil.copy(
                os.path.join(
                    temp_dir_path.value, module_name(self.prog_name) + ".elmf"
                ),
                os.path.join(
                    src_path.value,
                    "src",
                    "Models",
                    module_name(self.prog_name) + ".elm",
                ),
            )
            logger.write(
                self._log(
                    os.path.join(
                        src_path.value, "src", "Models", program_file(self.prog_name)
                    )
                )
            )
            return ExitSuccess(None)
        except OSError as err:
            raise err

    def _log(self, model_path):
        return f"""
Model generated for:

    \033[93m{model_path}\033[0m
    """


@dataclass(slots=True)
class AddProgramStrategy:
    """Create an elm program like SomeProgram.elm"""

    app_name: str
    prog_name: str

    def run(
        self, logger, style
    ) -> (
        ExitSuccess[None]
        | ExitFailure[None | str, StrategyError | FileNotFoundError | Exception]
    ):
        src_path = get_app_src_path(self.app_name)
        app_path = get_app_path(self.app_name)
        djelm_version = version("djelm")
        stuff_namespace = ("elm-stuff", f"djelm_{djelm_version}")
        tag_file = tag_file_name(self.prog_name)

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
        try:
            ck = CookieCutter[AddProgramCookieExtra](
                file_dir=os.path.dirname(__file__),
                output_dir=os.path.join(src_path.value, "elm-stuff"),
                cookie_dir_name="program_template",
                extra={
                    "program_name": module_name(self.prog_name),
                    "view_name": view_name(self.prog_name),
                    "tmp_dir": stuff_namespace[1],
                    "tag_file": tag_file,
                    "scope": scope_name(self.app_name, self.prog_name),
                    "app_name": self.app_name,
                },
                overwrite=True,
            )
            temp_dir_path = ck.cut(logger)

            ck_flags_path = CookieCutter[FlagsCookieExtra](
                file_dir=os.path.dirname(__file__),
                output_dir=os.path.join(src_path.value, "elm-stuff"),
                cookie_dir_name="flags_template",
                extra={
                    "program_name": module_name(self.prog_name),
                    "alias_type": "Int",
                    "decoder_body": "Decode.int",
                    "tmp_dir": stuff_namespace[1],
                },
                overwrite=True,
            ).cut(logger)
            if temp_dir_path.tag != "Success":
                raise temp_dir_path.err
            if ck_flags_path.tag != "Success":
                raise ck_flags_path.err

            # Move elm program
            shutil.copy(
                os.path.join(temp_dir_path.value, module_name(self.prog_name) + ".elm"),
                os.path.join(src_path.value, "src"),
            )
            # Move elm program flags
            shutil.copy(
                os.path.join(
                    ck_flags_path.value,
                    module_name(self.prog_name) + ".elmf",
                ),
                os.path.join(
                    src_path.value,
                    "src",
                    "Models",
                    module_name(self.prog_name) + ".elm",
                ),
            )
            # Move template tag
            shutil.copy(
                os.path.join(
                    temp_dir_path.value,
                    tag_file_name(self.prog_name) + "_tags.py",
                ),
                os.path.join(app_path.value, "templatetags"),
            )
            # Move flag file
            shutil.copy(
                os.path.join(
                    temp_dir_path.value,
                    tag_file_name(self.prog_name) + ".pyf",
                ),
                os.path.join(
                    app_path.value,
                    "flags",
                    tag_file_name(self.prog_name) + ".py",
                ),
            )
            # Move template html
            shutil.copy(
                os.path.join(
                    temp_dir_path.value, tag_file_name(self.prog_name) + ".html"
                ),
                os.path.join(app_path.value, "templates", self.app_name),
            )

            # Move typescript
            shutil.copy(
                os.path.join(temp_dir_path.value, module_name(self.prog_name) + ".ts"),
                os.path.join(src_path.value, "djelm_src"),
            )

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
        except OSError as err:
            raise err
        else:
            raise Exception(
                f"Something went wrong: Make sure the app exists and you have run 'python manage.py elm init {self.app_name}'"
            )


class ListStrategy:
    _apps: list[str] = settings.INSTALLED_APPS

    def run(
        self, logger, style
    ) -> ExitSuccess[list[str]] | ExitFailure[None, StrategyError]:
        app_path_exits = filterfalse(
            lambda x: x.tag == "Failure", map(get_app_path, self._apps)
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


@dataclass(slots=True)
class CreateStrategy:
    app_name: str

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
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
        self, *labels
    ) -> (
        ElmStrategy
        | CreateStrategy
        | ListStrategy
        | AddProgramStrategy
        | NpmStrategy
        | WatchStrategy
        | GenerateModelStrategy
        | CompileStrategy
    ):
        e = Validations().acceptable_command(list(labels))
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
                return AddProgramStrategy(cast(str, app_name), cast(str, pn))
            case ExitSuccess(
                value={
                    "command": "generatemodel",
                    "app_name": app_name,
                    "program_name": pn,
                }
            ):
                return GenerateModelStrategy(cast(str, app_name), cast(str, pn))
            case ExitSuccess(value={"command": "list"}):
                return ListStrategy()
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
            case _ as x:
                raise StrategyError(f"Unable to handle {x}")
