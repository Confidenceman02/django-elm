import os
import shutil
from typing import Protocol, Sequence, cast
from typing_extensions import TypedDict

from djelm.cookiecutter import CookieCutter
from djelm.effect import ExitFailure, ExitSuccess
from djelm.flags import Flags
from djelm.flags.primitives import IntFlag
from djelm.forms.widgets.main import WIDGET_NAME_TO_DEFAULT_FLAG, WIDGET_NAMES_T
from djelm.npm import NPM, NPMError
import djelm.flag_loader as FlagLoader
from djelm.utils import (
    STUFF_NAMESPACE,
    module_name,
    scope_name,
    tag_file_name,
    view_name,
    widget_scope_name,
)

#  _____           _                  _
# |  __ \         | |                | |
# | |__) | __ ___ | |_ ___   ___ ___ | |___
# |  ___/ '__/ _ \| __/ _ \ / __/ _ \| / __|
# | |   | | | (_) | || (_) | (_| (_) | \__ \
# |_|   |_|  \___/ \__\___/ \___\___/|_|___/


class TemplateApplicator(Protocol):
    def apply(self, logger) -> None: ...


class SupportsApplyTemplates(Protocol):
    def applicators(
        self,
        template_dir: str,
        src_dir: str,
        app_dir: str,
        program_name,
        app_name: str,
        logger,
    ) -> Sequence[TemplateApplicator]:
        """Support moving template files to their respective targets."""
        ...


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
    def cookie_cutters(self, parent_dir: str, program_name: str) -> list[CookieCutter]:
        """Support adding a handlers JS module to a program"""
        ...


class SupportsModelCookieCutter(Protocol):
    def cookie_cutter(
        self,
        flags: Flags,
        app_name: str,
        program_name: str,
        src_path: str,
    ) -> CookieCutter:
        """Support generating a cookie cutter config for an Elm program Model"""
        ...


class SupportsProgramCookieCutter(Protocol):
    def cookie_cutters(
        self, app_name: str, program_name: str, src_path: str, version: str
    ) -> list[CookieCutter]:
        """Support generating a cookie cutter config for an Elm program"""
        ...


class ModelBuilder(
    SupportsModelCookieCutter, SupportsFlagLoader, SupportsApplyTemplates
):
    pass


class ProgramBuilder(
    SupportsProgramCookieCutter,
    SupportsApplyTemplates,
    SupportsElmDependencies,
):
    pass


class ProgramHandlersBuilder(
    SupportsProgramHandlersCookieCutter,
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
        "program_name": str,
        "view_name": str,
        "tmp_dir": str,
        "tag_file": str,
        "scope": str,
        "app_name": str,
        "version": str,
    },
)


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
    default_imports = ['import defo from "@icelab/defo";']
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
            "lists": {"imports": default_imports + imports, "extras": extras},
        },
        overwrite=True,
    )


def model_cookie_cutter(
    flags: Flags, program_name: str, tmp_dir: str, output_dir: str, module_path: str
):
    return CookieCutter[ModelCookieExtra](
        file_dir=os.path.dirname(__file__),
        output_dir=(output_dir),
        cookie_template_name="model_template",
        extra={
            "program_name": module_name(program_name),
            "tmp_dir": tmp_dir,
            "alias_type": flags.to_elm_parser_data()["alias_type"],
            "decoder_body": flags.to_elm_parser_data()["decoder_body"],
            "module_path": module_path,
        },
        overwrite=True,
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

    def cookie_cutters(
        self, app_name: str, program_name: str, src_path: str, version: str
    ) -> list[CookieCutter]:
        return [
            widget_cookie_cutter(
                app_name, src_path, cast(WIDGET_NAMES_T, program_name), version
            ),
            entrypoint_cookie_cutter(
                base_name="Widgets.",
                base_path=f"Widgets{os.path.sep}",
                src_path=src_path,
                program_name=module_name(program_name),
                scope=widget_scope_name(app_name, program_name),
                view_prefix="widget",
            ),
        ]

    def applicators(
        self,
        template_dir: str,
        src_dir: str,
        app_dir: str,
        program_name: str,
        app_name: str,
        logger,
    ) -> Sequence[TemplateApplicator]:
        """Apply all generated templates to their respective targets"""

        logger.write(
            """\n-- GENERATING TEMPLATES ------------------------------------------------ widget/ModelChoiceField"""
        )
        return [
            # Program file
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elmw"),
                os.path.join(
                    src_dir, "src", "Widgets", module_name(program_name) + ".elm"
                ),
            ),
            # Flags
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + ".pyf"),
                os.path.join(
                    app_dir,
                    "flags",
                    "widgets",
                    tag_file_name(program_name) + ".py",
                ),
            ),
            # Tags
            TemplateCopyer(
                os.path.join(template_dir, f"{tag_file_name(program_name)}_tags.py"),
                os.path.join(
                    app_dir,
                    "templatetags",
                    f"{tag_file_name(program_name)}_widget_tags.py",
                ),
            ),
        ]


class ModelGenerator(ModelBuilder):
    def cookie_cutter(
        self, flags: Flags, app_name: str, program_name: str, src_path: str
    ) -> CookieCutter:
        return model_cookie_cutter(
            flags,
            program_name,
            STUFF_NAMESPACE[1],
            os.path.join(src_path, STUFF_NAMESPACE[0]),
            "Models",
        )

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

    def applicators(
        self,
        template_dir: str,
        src_dir: str,
        app_dir: str,
        program_name: str,
        app_name: str,
        logger,
    ) -> Sequence[TemplateApplicator]:
        logger.write(
            f"""\n-- GENERATING MODEL ----------------------------------------------------- model/{module_name(program_name)}"""
        )
        return [
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elmf"),
                os.path.join(
                    src_dir, "src", "Models", module_name(program_name) + ".elm"
                ),
            )
        ]


class ProgramGenerator(ProgramBuilder):
    """Generate an Elm program"""

    def install_elm_deps(
        self, working_dir: str, logger
    ) -> ExitSuccess[None] | ExitFailure[None, NPMError]:
        return ExitSuccess(None)

    def cookie_cutters(
        self, app_name: str, program_name: str, src_path: str, version: str
    ) -> list[CookieCutter]:
        cutters = []
        cutters.extend(
            [
                CookieCutter[ProgramCookieExtra](
                    file_dir=os.path.dirname(__file__),
                    output_dir=os.path.join(src_path, "elm-stuff"),
                    cookie_template_name="program_template",
                    extra={
                        "program_name": module_name(program_name),
                        "view_name": view_name(program_name),
                        "tmp_dir": STUFF_NAMESPACE[1],
                        "tag_file": tag_file_name(program_name),
                        "scope": scope_name(app_name, program_name),
                        "app_name": app_name,
                        "version": version,
                    },
                    overwrite=True,
                ),
                CookieCutter[EntrypointCookieExtra](
                    file_dir=os.path.join(os.path.dirname(__file__), "cookiecutters"),
                    output_dir=os.path.join(src_path, *STUFF_NAMESPACE),
                    cookie_template_name="entrypoint_template",
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
                ),
            ]
        )
        return cutters

    def applicators(
        self,
        template_dir: str,
        src_dir: str,
        app_dir: str,
        program_name,
        app_name: str,
        logger,
    ) -> Sequence[TemplateApplicator]:
        logger.write(
            f"""\n-- GENERATING TEMPLATES -------------------------------------------------------- {module_name(program_name)}"""
        )
        return [
            # Program file
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elm"),
                os.path.join(src_dir, "src"),
            ),
            # Template tags
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + "_tags.py"),
                os.path.join(app_dir, "templatetags"),
            ),
            # Flags
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + ".pyf"),
                os.path.join(app_dir, "flags", tag_file_name(program_name) + ".py"),
            ),
        ]


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

    def cookie_cutters(self, parent_dir: str, program_name: str) -> list[CookieCutter]:
        """
        parent_dir: parent directory of the generated cookiecutters

            If the cookiecutter is creating a 'bar' directory inside a 'foo' directory (foo/bar), then
            the parent_dir is 'foo'.

        program_name: name of the program i.e. Main
        """
        return [
            CookieCutter[HandlersCookieExtra](
                file_dir=os.path.join(os.path.dirname(__file__), "cookiecutters"),
                output_dir=os.path.join(parent_dir, *self.base_path),
                cookie_template_name="handlers_template",
                extra=HandlersCookieExtra(
                    {"dir": self.target_dir, "program_name": program_name}
                ),
                overwrite=True,
            ),
        ]


class WidgetModelGenerator(ModelBuilder):
    """Generates models for widget programs"""

    def cookie_cutter(
        self, flags: Flags, app_name: str, program_name: str, src_path: str
    ) -> CookieCutter:
        return model_cookie_cutter(
            flags,
            program_name,
            "Models",
            os.path.join(src_path, *STUFF_NAMESPACE, "Widgets"),
            "Widgets.Models",
        )

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

    def applicators(
        self,
        template_dir: str,
        src_dir: str,
        app_dir: str,
        program_name,
        app_name: str,
        logger,
    ) -> Sequence[TemplateApplicator]:
        logger.write(
            f"""\n-- GENERATING WIDGET MODEL --------------------------------------------- widget/{module_name(program_name)}"""
        )
        """Move the generated Elm model to their target location"""
        return [
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elmf"),
                os.path.join(
                    src_dir,
                    "src",
                    "Widgets",
                    "Models",
                    module_name(program_name) + ".elm",
                ),
            )
        ]


class TemplateCopyer(TemplateApplicator):
    """Copy a template file to a given destination"""

    def __init__(self, src: str, destination: str, log: bool = True) -> None:
        self.src = src
        self.destination = destination
        self.log = log

    def apply(self, logger) -> None:
        shutil.copy(self.src, self.destination)
        if self.log:
            logger.write(f"\t\033[93m{self.destination}\033[0m")
