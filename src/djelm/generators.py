import os
import shutil
from typing import Protocol, Sequence
import types
from typing_extensions import TypedDict

from djelm.cookiecutter import CookieCutter
from djelm.effect import ExitFailure, ExitSuccess
from djelm.flags import Flags
from djelm.flags.form.primitives import ModelChoiceFieldFlag
from djelm.flags.primitives import IntFlag
from djelm.npm import NPM, NPMError
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
    def apply(self, logger) -> None:
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
        """
        Load the flag config.

        Is is either going to be from a djelm app or a pre-built one.
        """
        ...


class SupportsProgramCookieCutter(Protocol):
    def cookie_cutter(
        self, app_name: str, program_name: str, src_path: str
    ) -> CookieCutter:
        """Generate a cookie cutter config"""
        ...


class SupportsModelCookieCutter(Protocol):
    def cookie_cutter(
        self,
        flags: Flags,
        app_name: str,
        program_name: str,
        src_path: str,
    ) -> CookieCutter:
        """Generate a cookie cutter config"""
        ...


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
        """Move the template files to their respective targets."""
        ...


class SupportsElmDependencies(Protocol):
    def install_elm_deps(
        self, working_dir: str, logger
    ) -> ExitSuccess[None] | ExitFailure[None, NPMError]:
        """Install Elm packages for the program needs"""
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


WidgetProgramCookieExtra = TypedDict(
    "WidgetProgramCookieExtra",
    {
        "tmp_dir": str,
        "program_name": str,
        "tag_file": str,
        "app_name": str,
        "scope": str,
        "view_name": str,
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
    },
)


def widget_cookie_cutter(
    app_name: str, src_path: str, program_name: str
) -> CookieCutter:
    return CookieCutter[WidgetProgramCookieExtra](
        file_dir=os.path.dirname(__file__),
        output_dir=os.path.join(src_path, *STUFF_NAMESPACE),
        cookie_dir_name="widget_templates",
        extra={
            "tmp_dir": "widgets",
            "program_name": program_name,
            "tag_file": tag_file_name(program_name),
            "app_name": app_name,
            "scope": widget_scope_name(app_name, program_name),
            "view_name": view_name(program_name),
        },
        overwrite=True,
    )


def model_cookie_cutter(
    flags: Flags, program_name: str, tmp_dir: str, output_dir: str, module_path: str
):
    return CookieCutter[ModelCookieExtra](
        file_dir=os.path.dirname(__file__),
        output_dir=(output_dir),
        cookie_dir_name="model_template",
        extra={
            "program_name": module_name(program_name),
            "tmp_dir": tmp_dir,
            "alias_type": flags.to_elm_parser_data()["alias_type"],
            "decoder_body": flags.to_elm_parser_data()["decoder_body"],
            "module_path": module_path,
        },
        overwrite=True,
    )


class WidgetModelGenerator(ModelBuilder):
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
        # TODO load flags from source flag module
        return ExitSuccess(Flags(ModelChoiceFieldFlag()))  # type:ignore

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
            f"""\n-- GENERATING WIDGET MODEL ---------------------------------------------- widget/{module_name(program_name)}"""
        )
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


class ModelChoiceFieldWidgetGenerator(ProgramBuilder):
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
            f"""\n-- INSTALLING WIDGET DEPENDENCIES ---------------------------------------------- widget/ModelChoiceField
{dep_string}"""
        )
        args = ["elm-json", "install", "--yes"]
        args.extend(deps)
        effect = NPM(raise_err=True).command(working_dir, args)

        if effect.tag != "Success":
            return ExitFailure(None, effect.err)
        return ExitSuccess(None)

    def cookie_cutter(
        self, app_name: str, program_name: str, src_path: str
    ) -> CookieCutter:
        return widget_cookie_cutter(app_name, src_path, program_name)

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
            """\n-- GENERATING TEMPLATES -------------------------------------------------------- widget/ModelChoiceField"""
        )
        return [
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elmw"),
                os.path.join(
                    src_dir, "src", "Widgets", module_name(program_name) + ".elm"
                ),
            ),
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + ".pyf"),
                os.path.join(
                    app_dir,
                    "flags",
                    "widgets",
                    tag_file_name(program_name) + ".py",
                ),
            ),
            TemplateCopyer(
                os.path.join(template_dir, f"{tag_file_name(program_name)}_tags.py"),
                os.path.join(
                    app_dir,
                    "templatetags",
                    f"{tag_file_name(program_name)}_widget_tags.py",
                ),
            ),
            TemplateCopyer(
                os.path.join(template_dir, f"{tag_file_name(program_name)}.html"),
                os.path.join(app_dir, "templates", app_name, "widgets"),
            ),
            TemplateCopyer(
                os.path.join(template_dir, f"Widgets.{module_name(program_name)}.ts"),
                os.path.join(
                    src_dir,
                    "djelm_src",
                ),
            ),
        ]


class ProgramGenerator(ProgramBuilder):
    def install_elm_deps(
        self, working_dir: str, logger
    ) -> ExitSuccess[None] | ExitFailure[None, NPMError]:
        return ExitSuccess(None)

    def cookie_cutter(
        self, app_name: str, program_name: str, src_path: str
    ) -> CookieCutter:
        return CookieCutter[ProgramCookieExtra](
            file_dir=os.path.dirname(__file__),
            output_dir=os.path.join(src_path, "elm-stuff"),
            cookie_dir_name="program_template",
            extra={
                "program_name": module_name(program_name),
                "view_name": view_name(program_name),
                "tmp_dir": STUFF_NAMESPACE[1],
                "tag_file": tag_file_name(program_name),
                "scope": scope_name(app_name, program_name),
                "app_name": app_name,
            },
            overwrite=True,
        )

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
            f"""\n-- GENERATING TEMPLATES -------------------------------------------------------- widget/{module_name(program_name)}"""
        )
        return [
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elm"),
                os.path.join(src_dir, "src"),
            ),
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + "_tags.py"),
                os.path.join(app_dir, "templatetags"),
            ),
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + ".pyf"),
                os.path.join(app_dir, "flags", tag_file_name(program_name) + ".py"),
            ),
            TemplateCopyer(
                os.path.join(template_dir, tag_file_name(program_name) + ".html"),
                os.path.join(app_dir, "templates", app_name),
            ),
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".ts"),
                os.path.join(src_dir, "djelm_src"),
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
            # If load source is True, we want to load the flags from the programs flags.
            import importlib.machinery

            loader = importlib.machinery.SourceFileLoader(
                tag_file_name(program_name),
                os.path.join(app_path, "flags", tag_file_name(program_name) + ".py"),
            )
            mod = types.ModuleType(loader.name)

            try:
                loader.exec_module(mod)
            except Exception as err:
                error_hint = ""
                if watch_mode:
                    error_hint = "\033[4m\033[1mNote\033[0m: I'll keep watching this module and will generate the model once the errors are fixed."
                logger.write(
                    f"""
    \033[91m-- FLAG MODULE ERROR ----------------------------------------------------------------------------------------------------- command/generatemodel\033[0m

    I was trying to generate a model from this flags module:

        \033[93m{os.path.join(app_path, "flags", tag_file_name(program_name) + ".py")}\033[0m

    But got the following error type:

        \033[93m{err.args[0]}\033[0m

    Make sure you fix the errors in \033[1m{os.path.join(app_path, "flags", tag_file_name(program_name) + ".py")}\033[0m.

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
            f"""\n-- GENERATING MODEL -------------------------------------------------------- model/{module_name(program_name)}"""
        )
        return [
            TemplateCopyer(
                os.path.join(template_dir, module_name(program_name) + ".elmf"),
                os.path.join(
                    src_dir, "src", "Models", module_name(program_name) + ".elm"
                ),
            )
        ]


class TemplateCopyer(TemplateApplicator):
    def __init__(self, src, destination) -> None:
        self.src = src
        self.destination = destination

    def apply(self, logger) -> None:
        shutil.copy(self.src, self.destination)
        logger.write(f"\t\033[93m{self.destination}\033[0m")
