import os
from enum import Enum
from typing import Protocol

from typing_extensions import TypedDict

import djelm.flag_loader as FlagLoader
from djelm.cookiecutter import CookieCutter
from djelm.effect import ExitFailure, ExitSuccess
from djelm.flags import Flags
from djelm.flags.primitives import IntFlag
from djelm.forms.widgets.main import WIDGET_NAME_TO_DEFAULT_FLAG, WIDGET_NAMES_T
from djelm.npm import NPM, NPMError
from djelm.utils import (
    STUFF_ENTRYPOINTS,
    STUFF_NAMESPACE,
    module_name,
    scope_name,
    tag_file_name,
    view_name,
    widget_scope_name,
)


class ProgramFileType(Enum):
    Entrypoint = "entrypoint"
    Flag = "flag"
    Program = "program"
    TemplateTag = "templatetag"
    Handler = "handler"
    Model = "model"


ProgramConfig = TypedDict(
    "ProgramConfig", {"file_type": ProgramFileType, "template_name": str, "path": str}
)


#  _____           _                  _
# |  __ \         | |                | |
# | |__) | __ ___ | |_ ___   ___ ___ | |___
# |  ___/ '__/ _ \| __/ _ \ / __/ _ \| / __|
# | |   | | | (_) | || (_) | (_| (_) | \__ \
# |_|   |_|  \___/ \__\___/ \___\___/|_|___/


class SupportsElmDependencies(Protocol):
    def install_elm_deps(
        self, working_dir: str, logger
    ) -> ExitSuccess[None] | ExitFailure[None, NPMError]:
        """Support installing an Elm package"""
        ...


class SupportsFlagLoader(Protocol):
    def load_flags(
        self,
        app_path: str,
        program_name: str,
        from_source: bool,
        watch_mode: bool,
        logger,
    ) -> ExitSuccess[Flags] | ExitFailure[None, Exception]:
        """Support loading a python flag module"""
        ...


class SupportsProgramHandlersCookieCutter(Protocol):
    def cookie_cutters(self, src_dir: str, program_name: str) -> list[CookieCutter]:
        """Support adding a handlers JS module to a program"""
        ...


class SupportsModelCookieCutter(Protocol):
    def cookie_cutters(
        self,
        flags: Flags,
        app_name: str,
        program_name: str,
        app_path: str,
        src_path: str,
    ) -> list[CookieCutter]:
        """Support generating a cookie cutter config for an Elm program Model"""
        ...


class SupportsProgramCookieCutter(Protocol):
    def cookie_cutters(
        self,
        app_name: str,
        program_name: str,
        app_path: str,
        src_path: str,
        version: str,
    ) -> list[CookieCutter]:
        """Support generating a cookie cutter config for an Elm program"""
        ...


class SupportsProgramFileTypeDetails(Protocol):
    def file_type_details(
        self, program_name: str, app_path: str
    ) -> list[ProgramConfig]:
        """All the file type information for a program"""
        ...


class ModelBuilder(
    SupportsModelCookieCutter, SupportsFlagLoader, SupportsProgramFileTypeDetails
):
    pass


class ProgramBuilder(
    SupportsProgramCookieCutter, SupportsElmDependencies, SupportsProgramFileTypeDetails
):
    pass


class ProgramHandlersBuilder(
    SupportsProgramHandlersCookieCutter, SupportsProgramFileTypeDetails
):
    pass


Lists = TypedDict("Lists", {"imports": list[str], "extras": list[str]})

EntrypointCookieExtra = TypedDict(
    "EntrypointCookieExtra",
    {
        "base_name": str,
        "base_path": str,
        "dir": str,
        "program_name": str,
        "scope": str,
        "view_name": str,
        "lists": Lists,
    },
)

HandlersCookieExtra = TypedDict(
    "HandlersCookieExtra",
    {
        "dir": str,
        "program_name": str,
    },
)


WidgetProgramCookieExtra = TypedDict(
    "WidgetProgramCookieExtra",
    {
        "tmp_dir": str,
        "program_name": str,
        "tag_file": str,
        "app_name": str,
        "scope": str,
        "view_name": str,
        "version": str,
    },
)
ModelCookieExtra = TypedDict(
    "ModelCookieExtra",
    {
        "program_name": str,
        "alias_type": str,
        "decoder_body": str,
        "tmp_dir": str,
        "module_path": str,
    },
)

ProgramCookieExtra = TypedDict(
    "ProgramCookieExtra",
    {
        "module_namespace": str,
        "module_model_namespace": str,
        "dir": str,
        "program_name": str,
    },
)

ProgramFlagsCookieExtra = TypedDict(
    "ProgramFlagsCookieExtra",
    {
        "dir": str,
        "flag_file": str,
        "program_name": str,
        "scope": str,
        "view_name": str,
        "version": str,
    },
)

ProgramTagsCookieExtra = TypedDict(
    "ProgramTagsCookieExtra",
    {
        "program_name": str,
        "tag_name": str,
    },
)

ProgramModelCookieExtra = TypedDict(
    "ProgramModelCookieExtra",
    {
        "alias_type": str,
        "decoder_body": str,
        "dir": str,
        "module_model_namespace": str,
        "program_name": str,
    },
)

ProgramInitCookieExtra = TypedDict(
    "ProgramInitCookieExtra",
    {
        "program_name": str,
        "view_name": str,
        "tmp_dir": str,
        "tag_file": str,
        "scope": str,
        "app_name": str,
        "version": str,
    },
)

DEFAULT_WIDGET_IMPORTS = ['import defo from "@icelab/defo";']


def widget_cookie_cutter(
    app_name: str, src_path: str, program_name: WIDGET_NAMES_T, version: str
) -> CookieCutter:
    return CookieCutter[WidgetProgramCookieExtra](
        file_dir=os.path.dirname(__file__),
        output_dir=os.path.join(src_path, *STUFF_NAMESPACE),
        cookie_template_name="widget_templates",
        extra={
            "tmp_dir": "widgets",
            "program_name": program_name,
            "tag_file": tag_file_name(program_name),
            "app_name": app_name,
            "scope": widget_scope_name(app_name, program_name),
            "view_name": view_name(program_name),
            "version": version,
        },
        overwrite=True,
    )


def entrypoint_cookie_cutter(
    base_name: str,
    base_path: str,
    src_path: str,
    program_name: str,
    scope: str,
    view_prefix: str,
    imports: list[str] = [],
    extras: list[str] = [],
) -> CookieCutter:
    return CookieCutter[EntrypointCookieExtra](
        file_dir=os.path.join(os.path.dirname(__file__), "cookiecutters"),
        output_dir=os.path.join(src_path, *STUFF_NAMESPACE),
        cookie_template_name="entrypoint_template",
        extra={
            "base_name": base_name,
            "base_path": base_path,
            "dir": "entrypoints",
            "program_name": program_name,
            "scope": scope,
            "view_name": view_prefix + view_name(program_name),
            "lists": {"imports": DEFAULT_WIDGET_IMPORTS + imports, "extras": extras},
        },
        overwrite=True,
    )


def model_cookie_cutter(
    flags: Flags,
    app_name: str,
    program_name: str,
    cookie_template_name: str,
    dir: str,
    output_dir: str,
    module_model_namespace: str,
):
    return CookieCutter[ProgramModelCookieExtra](
        file_dir=os.path.join((os.path.dirname(__file__)), "cookiecutters"),
        output_dir=(output_dir),
        cookie_template_name=cookie_template_name,
        extra={
            "program_name": module_name(program_name),
            "dir": dir,
            "alias_type": flags.to_elm_parser_data()["alias_type"],
            "decoder_body": flags.to_elm_parser_data()["decoder_body"],
            "module_model_namespace": module_model_namespace,
        },
        overwrite=True,
        log_lines=[
            f"""\n-- GENERATED MODEL --------------------------------------------- {module_model_namespace}.{program_name}.elm""",
            f"\t\033[93m{app_name}/static_src/src/{module_model_namespace.replace('.', os.path.sep)}/{program_name}.elm\033[0m",
        ],
    )


class ModelChoiceFieldWidgetGenerator(ProgramBuilder):
    """Generate all files for the ModelChoiceField widget"""

    def install_elm_deps(self, working_dir: str, logger):
        deps = [
            "elm-community/list-extra",
            "rtfeldman/elm-css",
            "Confidenceman02/elm-select",
        ]
        dep_string = ""
        for dep in deps:
            dep_string += f"\033[93m\t{dep}\033[0m\n"
        logger.write(
            f"""\n-- INSTALLING WIDGET DEPENDENCIES -------------------------------------- widget/ModelChoiceField
{dep_string}"""
        )
        args = ["elm-json", "install", "--yes"]
        args.extend(deps)
        effect = NPM(raise_err=True).command(working_dir, args)

        if effect.tag != "Success":
            return ExitFailure(None, effect.err)
        return ExitSuccess(None)

    def file_type_details(
        self, program_name: str, app_path: str
    ) -> list[ProgramConfig]:
        configs = []
        for pft in ProgramFileType:
            match pft:
                case ProgramFileType.Entrypoint:
                    configs.append(
                        {
                            "file_type": ProgramFileType.Entrypoint,
                            "template_name": "entrypoint_template",
                            "path": os.path.join(
                                app_path,
                                "static_src",
                                *STUFF_ENTRYPOINTS,
                                f"Widgets.{module_name(program_name)}.ts",
                            ),
                        }
                    )
                case ProgramFileType.Flag:
                    configs.append(
                        {
                            "file_type": ProgramFileType.Flag,
                            "template_name": f"program_widget_{program_name}_flags_template",
                            "path": os.path.join(
                                app_path,
                                "flags",
                                "widgets",
                                tag_file_name(program_name) + ".py",
                            ),
                        }
                    )
                case ProgramFileType.Program:
                    configs.append(
                        {
                            "file_type": ProgramFileType.Program,
                            "template_name": f"program_widget_{program_name}_template",
                            "path": os.path.join(
                                app_path,
                                "static_src",
                                "src",
                                "Widgets",
                                module_name(program_name) + ".elm",
                            ),
                        }
                    )
                case ProgramFileType.TemplateTag:
                    configs.append(
                        {
                            "file_type": ProgramFileType.TemplateTag,
                            "template_name": f"program_widget_{program_name}_tags_template",
                            "path": os.path.join(
                                app_path,
                                "templatetags",
                                f"{tag_file_name(program_name)}_widget_tags.py",
                            ),
                        }
                    )

        return configs

    def cookie_cutters(
        self,
        app_name: str,
        program_name: str,
        app_path: str,
        src_path: str,
        version: str,
    ) -> list[CookieCutter]:
        cookies: list[CookieCutter] = []
        for detail in self.file_type_details(program_name, app_path):
            match detail["file_type"]:
                case ProgramFileType.Program:
                    cookies.append(
                        CookieCutter[ProgramCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=os.path.join(src_path, "src"),
                            cookie_template_name=detail["template_name"],
                            extra={
                                "module_namespace": "Widgets.",
                                "module_model_namespace": "Widgets.Models",
                                "dir": "Widgets",
                                "program_name": program_name,
                            },
                            overwrite=True,
                            log_lines=[
                                f"""\n-- GENERATED WIDGET PROGRAM --------------------------------------------- Widgets.{program_name}.elm""",
                                f"\t\033[93m{app_name}/static_src/src/Widgets/{program_name}.elm\033[0m",
                            ],
                        )
                    )
                case ProgramFileType.TemplateTag:
                    cookies.append(
                        CookieCutter[ProgramTagsCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=app_path,
                            cookie_template_name=detail["template_name"],
                            extra={
                                "program_name": module_name(program_name),
                                "tag_name": tag_file_name(program_name),
                            },
                            overwrite=True,
                            log_lines=[
                                f"""\n-- GENERATED WIDGET TAGS --------------------------------------------- {tag_file_name(program_name)}_widget_tags.py""",
                                f"\t\033[93m{app_name}/templatetags/{tag_file_name(program_name)}_widget_tags.py\033[0m",
                            ],
                        )
                    )
                case ProgramFileType.Flag:
                    cookies.append(
                        CookieCutter[ProgramFlagsCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=os.path.join(app_path, "flags"),
                            cookie_template_name=detail["template_name"],
                            extra={
                                "dir": "widgets",
                                "flag_file": tag_file_name(program_name),
                                "program_name": program_name,
                                "scope": widget_scope_name(app_name, program_name),
                                "view_name": view_name(program_name),
                                "version": version,
                            },
                            overwrite=True,
                            log_lines=[
                                f"""\n-- GENERATED WIDGET FLAGS --------------------------------------------- {tag_file_name(program_name)}.py""",
                                f"\t\033[93m{app_name}/flags/widgets/{tag_file_name(program_name)}.py\033[0m",
                            ],
                        )
                    )
                case ProgramFileType.Entrypoint:
                    cookies.append(
                        CookieCutter[EntrypointCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=os.path.join(src_path, *STUFF_NAMESPACE),
                            cookie_template_name=detail["template_name"],
                            extra={
                                "base_name": "Widgets.",
                                "base_path": f"Widgets{os.path.sep}",
                                "dir": "entrypoints",
                                "program_name": module_name(program_name),
                                "scope": widget_scope_name(app_name, program_name),
                                "view_name": "widget" + view_name(program_name),
                                "lists": {
                                    "imports": DEFAULT_WIDGET_IMPORTS,
                                    "extras": [],
                                },
                            },
                            overwrite=True,
                        )
                    )
        return cookies


class ModelGenerator(ModelBuilder):
    def file_type_details(
        self, program_name: str, app_path: str
    ) -> list[ProgramConfig]:
        return [
            {
                "file_type": ProgramFileType.Model,
                "template_name": "program_model_template",
                "path": os.path.join(
                    app_path,
                    "static_src",
                    "src",
                    "Models",
                    module_name(program_name) + ".elm",
                ),
            }
        ]

    def cookie_cutters(
        self,
        flags: Flags,
        app_name: str,
        program_name: str,
        app_path: str,
        src_path: str,
    ) -> list[CookieCutter]:
        configs = []
        for detail in self.file_type_details(program_name, app_path):
            match detail["file_type"]:
                case ProgramFileType.Model:
                    configs.append(
                        model_cookie_cutter(
                            flags,
                            app_name,
                            program_name,
                            detail["template_name"],
                            "Models",
                            os.path.join(src_path, "src"),
                            "Models",
                        )
                    )
        return configs

    def load_flags(
        self,
        app_path: str,
        program_name: str,
        from_source: bool,
        watch_mode: bool,
        logger,
    ) -> ExitSuccess[Flags] | ExitFailure[None, Exception]:
        if from_source:
            module = tag_file_name(program_name)
            module_path = os.path.join(
                app_path, "flags", tag_file_name(program_name) + ".py"
            )

            try:
                mod = FlagLoader.loader(module, module_path)
            except Exception as err:
                error_hint = ""
                if watch_mode:
                    error_hint = "\033[4m\033[1mNote\033[0m: I'll keep watching this module and will generate the model once the errors are fixed."
                logger.write(
                    f"""
    \033[91m-- FLAG MODULE ERROR -------------------------------------------------- command/generatemodel\033[0m

    I was trying to generate a model from this flags module:

        \033[93m{module_path}\033[0m

    But got the following error type:

        \033[93m{err.args[0]}\033[0m

    Make sure you fix the errors in \033[1m{module_path}\033[0m.

    {error_hint}

    """
                )
                return ExitFailure(None, err=err)

            return ExitSuccess(getattr(mod, program_name + "Flags"))
        else:
            # Return default flags for a new program
            return ExitSuccess(Flags(IntFlag()))  # type:ignore


class ProgramGenerator(ProgramBuilder):
    """Generate an Elm program"""

    def file_type_details(
        self, program_name: str, app_path: str
    ) -> list[ProgramConfig]:
        configs: list[ProgramConfig] = []

        for pft in ProgramFileType:
            match pft:
                case ProgramFileType.Entrypoint:
                    configs.append(
                        {
                            "file_type": ProgramFileType.Entrypoint,
                            "template_name": "entrypoint_template",
                            "path": os.path.join(
                                app_path,
                                "static_src",
                                *STUFF_ENTRYPOINTS,
                                module_name(program_name) + ".ts",
                            ),
                        }
                    )
                case ProgramFileType.Flag:
                    configs.append(
                        {
                            "file_type": ProgramFileType.Flag,
                            "template_name": "program_flags_template",
                            "path": os.path.join(
                                app_path, "flags", tag_file_name(program_name) + ".py"
                            ),
                        }
                    )
                case ProgramFileType.Program:
                    configs.append(
                        {
                            "file_type": ProgramFileType.Program,
                            "template_name": "program_template",
                            "path": os.path.join(
                                app_path,
                                "static_src",
                                "src",
                                module_name(program_name) + ".elm",
                            ),
                        }
                    )
                case ProgramFileType.TemplateTag:
                    configs.append(
                        {
                            "file_type": ProgramFileType.TemplateTag,
                            "template_name": "program_tags_template",
                            "path": os.path.join(
                                app_path,
                                "templatetags",
                                f"{tag_file_name(program_name)}_tags.py",
                            ),
                        }
                    )

        return configs

    def install_elm_deps(
        self, working_dir: str, logger
    ) -> ExitSuccess[None] | ExitFailure[None, NPMError]:
        return ExitSuccess(None)

    def cookie_cutters(
        self,
        app_name: str,
        program_name: str,
        app_path: str,
        src_path: str,
        version: str,
    ) -> list[CookieCutter]:
        cookies: list[CookieCutter] = []
        for detail in self.file_type_details(program_name, app_path):
            match detail["file_type"]:
                case ProgramFileType.Program:
                    cookies.append(
                        CookieCutter[ProgramCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=src_path,
                            cookie_template_name=detail["template_name"],
                            extra={
                                "module_namespace": "",
                                "module_model_namespace": "Models",
                                "dir": "src",
                                "program_name": module_name(program_name),
                            },
                            overwrite=True,
                            log_lines=[
                                f"""\n-- GENERATED PROGRAM --------------------------------------------- {module_name(program_name)}.elm""",
                                f"\t\033[93m{app_name}/static_src/src/{module_name(program_name)}.elm\033[0m",
                            ],
                        )
                    )
                case ProgramFileType.TemplateTag:
                    cookies.append(
                        CookieCutter[ProgramTagsCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=app_path,
                            cookie_template_name=detail["template_name"],
                            extra={
                                "program_name": module_name(program_name),
                                "tag_name": tag_file_name(program_name),
                            },
                            overwrite=True,
                            log_lines=[
                                f"""\n-- GENERATED TAGS --------------------------------------------- {tag_file_name(program_name)}_tags.py""",
                                f"\t\033[93m{app_name}/templatetags/{tag_file_name(program_name)}_tags.py\033[0m",
                            ],
                        )
                    )
                case ProgramFileType.Flag:
                    cookies.append(
                        CookieCutter[ProgramFlagsCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=app_path,
                            cookie_template_name=detail["template_name"],
                            extra={
                                "dir": "flags",
                                "flag_file": tag_file_name(program_name),
                                "program_name": module_name(program_name),
                                "scope": scope_name(app_name, program_name),
                                "view_name": view_name(program_name),
                                "version": version,
                            },
                            overwrite=True,
                            log_lines=[
                                f"""\n-- GENERATED FLAGS --------------------------------------------- {tag_file_name(program_name)}.py""",
                                f"\t\033[93m{app_name}/flags/{tag_file_name(program_name)}.py\033[0m",
                            ],
                        )
                    )
                case ProgramFileType.Entrypoint:
                    cookies.append(
                        CookieCutter[EntrypointCookieExtra](
                            file_dir=os.path.join(
                                os.path.dirname(__file__), "cookiecutters"
                            ),
                            output_dir=os.path.join(src_path, *STUFF_NAMESPACE),
                            cookie_template_name=detail["template_name"],
                            extra={
                                "base_name": "",
                                "base_path": "",
                                "dir": "entrypoints",
                                "program_name": program_name,
                                "scope": scope_name(app_name, program_name),
                                "view_name": "",
                                "lists": {"imports": [], "extras": []},
                            },
                            overwrite=True,
                        )
                    )

        return cookies


class ProgramHandlersGenerator(ProgramHandlersBuilder):
    """
    Generates JS handlers for programs

    base_path: The base path from the 'static_src' directory not including the directory
    the handler file will be added to.

            If The handler is being created for a program in "src" then
            the base_path is [""]

            If the handler is being created for a program in src/Widgets then
            the base_path is ["src"]

    target_dir: The directory the handler will be added to

            If the handler is being added to the 'src' directory then
            the target_dir is 'src'

            If the handler is being added to the 'src/Widgets' directory then
            the target_dir is 'Widgets'
    """

    base_path: list[str]
    target_dir: str

    def __init__(self, base_path: list[str], target_dir: str) -> None:
        self.base_path = base_path
        self.target_dir = target_dir

    def file_type_details(
        self, program_name: str, app_path: str
    ) -> list[ProgramConfig]:
        resolved_base_path = []
        if self.base_path:
            resolved_base_path = [*self.base_path, self.target_dir]
        else:
            resolved_base_path = ["src"]

        return [
            {
                "file_type": ProgramFileType.Handler,
                "template_name": "handlers_template",
                "path": os.path.join(
                    app_path,
                    "static_src",
                    *resolved_base_path,
                    f"{module_name(program_name)}.handlers.ts",
                ),
            }
        ]

    def cookie_cutters(self, src_dir: str, program_name: str) -> list[CookieCutter]:
        """
        parent_dir: parent directory of the generated cookiecutters

            If the cookiecutter is creating a 'bar' directory inside a 'foo' directory (foo/bar), then
            the parent_dir is 'foo'.

        program_name: name of the program i.e. Main
        """
        return [
            CookieCutter[HandlersCookieExtra](
                file_dir=os.path.join(os.path.dirname(__file__), "cookiecutters"),
                output_dir=os.path.join(src_dir, *self.base_path),
                cookie_template_name="handlers_template",
                extra=HandlersCookieExtra(
                    {"dir": self.target_dir, "program_name": program_name}
                ),
                overwrite=True,
            ),
        ]


class WidgetModelGenerator(ModelBuilder):
    """Generates models for widget programs"""

    def file_type_details(
        self, program_name: str, app_path: str
    ) -> list[ProgramConfig]:
        return [
            {
                "file_type": ProgramFileType.Model,
                "template_name": "program_model_template",
                "path": os.path.join(
                    app_path,
                    "static_src",
                    "src",
                    "Widgets",
                    "Models",
                    module_name(program_name) + ".elm",
                ),
            }
        ]

    def cookie_cutters(
        self,
        flags: Flags,
        app_name: str,
        program_name: str,
        app_path: str,
        src_path: str,
    ) -> list[CookieCutter]:
        configs = []

        for detail in self.file_type_details(program_name, app_path):
            match detail["file_type"]:
                case ProgramFileType.Model:
                    configs.append(
                        model_cookie_cutter(
                            flags,
                            app_name,
                            program_name,
                            "program_model_template",
                            "Models",
                            os.path.join(src_path, "src", "Widgets"),
                            "Widgets.Models",
                        )
                    )
        return configs

    def load_flags(
        self,
        app_path: str,
        program_name: str,
        from_source: bool,
        watch_mode: bool,
        logger,
    ) -> ExitSuccess[Flags] | ExitFailure[None, Exception]:
        """
        Load a flag class for the given program

        app_path: The path of the djelm app
        program_name: The Elm program name
        from_source:
            True =  Load the flag class from a python module in the 'flags' directory
            False = Load a default flag class
        watch_mode:
            True = In a watch mode context
            False = Not in a watch mode context
        """
        if from_source:
            module = tag_file_name(program_name)
            module_path = os.path.join(
                app_path, "flags", "widgets", tag_file_name(program_name) + ".py"
            )

            try:
                mod = FlagLoader.loader(module, module_path)
            except Exception as err:
                error_hint = ""
                if watch_mode:
                    error_hint = "\033[4m\033[1mNote\033[0m: I'll keep watching this module and will generate the model once the errors are fixed."
                logger.write(
                    f"""
    \033[91m-- FLAG MODULE ERROR -------------------------------------------------- command/generatemodel\033[0m

    I was trying to generate a model from this flags module:

        \033[93m{module_path}\033[0m

    But got the following error type:

        \033[93m{err.args[0]}\033[0m

    Make sure you fix the errors in \033[1m{module_path}\033[0m.

    {error_hint}

    """
                )
                return ExitFailure(None, err=err)

            return ExitSuccess(getattr(mod, program_name + "Flags"))
        else:
            return ExitSuccess(Flags(WIDGET_NAME_TO_DEFAULT_FLAG[program_name]()))  # type:ignore
