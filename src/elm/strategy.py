import os
import shutil
import uuid
from dataclasses import dataclass
from itertools import filterfalse
from typing import Iterable, cast

from django.conf import settings
from typing_extensions import TypedDict

from elm.cookiecutter import CookieCutter

from .effect import ExitFailure, ExitSuccess
from .elm import Elm
from .utils import (
    get_app_path,
    get_app_src_path,
    is_djelm,
    module_name,
    program_file,
    tag_file_name,
    walk_level,
)
from .validate import Validations

CreateCookieExtra = TypedDict("CreateCookieExtra", {"app_name": str})
AddProgramCookieExtra = TypedDict(
    "AddProgramCookieExtra",
    {"program_name": str, "tmp_dir": str, "tag_file": str, "scope": str},
)


class StrategyError(Exception):
    pass


@dataclass(slots=True)
class AddProgramStrategy:
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
        if src_path.tag == "Success" and app_path.tag == "Success":
            try:
                os.mkdir(os.path.join(src_path.value, "elm-stuff"))
            except FileExistsError as err:
                pass
            except FileNotFoundError as err:
                return ExitFailure(meta="Path to 'elm-stuff invalid'", err=err)
            try:
                temp_dir_name = (
                    f'temp_program_djelm_{str(uuid.uuid1()).replace("-", "_")}'
                )
                scope_name = (
                    self.app_name.lower() + self.prog_name.lower().replace("_", "")
                ).replace("_", "")
                ck = CookieCutter[AddProgramCookieExtra](
                    file_dir=os.path.dirname(__file__),
                    output_dir=os.path.join(src_path.value, "elm-stuff"),
                    cookie_dir_name="program_template",
                    extra={
                        "program_name": module_name(self.prog_name),
                        "tmp_dir": temp_dir_name,
                        "tag_file": tag_file_name(self.prog_name),
                        "scope": scope_name,
                    },
                )
                temp_dir_path = ck.cut(logger)

                if temp_dir_path.tag == "Success":
                    # Move elm program
                    shutil.copy(
                        os.path.join(
                            temp_dir_path.value, module_name(self.prog_name) + ".elm"
                        ),
                        os.path.join(src_path.value, "src"),
                    )
                    # Move template tag
                    shutil.copy(
                        os.path.join(
                            temp_dir_path.value,
                            tag_file_name(self.prog_name) + "_tag.py",
                        ),
                        os.path.join(app_path.value, "templatetags"),
                    )
                    # Move template html
                    shutil.copy(
                        os.path.join(
                            temp_dir_path.value, tag_file_name(self.prog_name) + ".html"
                        ),
                        os.path.join(app_path.value, "templates"),
                    )

                    # Move template html
                    shutil.copy(
                        os.path.join(
                            temp_dir_path.value, module_name(self.prog_name) + ".ts"
                        ),
                        os.path.join(src_path.value, "djelm_src"),
                    )

                    logger.write(
                        style.SUCCESS(
                            f"I created an elm program at {os.path.join(src_path.value, 'src', program_file(self.app_name))}\n"
                            f"I created a template at {os.path.join(app_path.value, 'templates', tag_file_name(self.prog_name) + '.html')}\n"
                            f"I created a template tag at {os.path.join(app_path.value, 'templatetags', tag_file_name(self.prog_name) + '_tag.py')}"
                            f"I created a typescript starter at {os.path.join(src_path.value, 'djelm_src', module_name(self.prog_name) + '.ts')}"
                        )
                    )
                    return ExitSuccess(None)
                return ExitFailure(None, err=temp_dir_path.err)
            except OSError as err:
                return ExitFailure(None, err=StrategyError(err))
        else:
            return ExitFailure(
                None,
                Exception(
                    f"Something went wrong: Make sure the app exists and you have run 'python manage.py elm init {self.app_name}'"
                ),
            )


@dataclass(slots=True)
class InitStrategy:
    app_name: str
    elm: Elm = Elm()

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        src_path = get_app_src_path(self.app_name)
        if src_path.tag == "Success":
            init_exit = self.elm.command("init", target_dir=src_path.value)

            if init_exit.tag == "Success":
                return ExitSuccess(None)
            else:
                return ExitFailure(None, err=StrategyError(init_exit.err))
        return ExitFailure(None, err=StrategyError())


class ListStrategy:
    _apps: list[str] = settings.INSTALLED_APPS

    def run(
        self, logger, style
    ) -> ExitSuccess[list[str]] | ExitFailure[None, StrategyError]:
        app_path_exits = filterfalse(
            lambda x: x.tag == "Failure", map(get_app_path, self._apps)
        )

        dir_data: Iterable[tuple[str, list[str], list[str]]] = map(
            next, map(lambda p: walk_level(p.value), app_path_exits)  # type:ignore
        )

        django_elm_apps = [os.path.basename(r) for r, _, f in dir_data if is_djelm(f)]

        logger.write(style.SUCCESS("Here are all your installed django-elm apps:"))
        for app in django_elm_apps:
            logger.write(style.SUCCESS(f"{app}"))
        logger.write(
            style.WARNING(
                "If you don't see all your django-elm apps make sure they are installed in your 'settings.py'."
            )
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
            extra={"app_name": self.app_name.strip()},
        )

        cut_cookie = ck.cut(logger)

        if cut_cookie.tag == "Success":
            app_name = os.path.basename(cut_cookie.value)
            logger.write(
                style.SUCCESS(
                    f"Elm project '{app_name}' "
                    f"has been successfully created. "
                    f"Please add '{app_name}' to INSTALLED_APPS in settings.py, "
                    f"then run the following command to install all packages "
                    f"dependencies: `python manage.py elm init`"
                )
            )
            return ExitSuccess(None)
        return ExitFailure(
            None, StrategyError(" Could not create project from template:")
        )


@dataclass(slots=True)
class Strategy:
    def create(
        self, *labels
    ) -> InitStrategy | CreateStrategy | ListStrategy | AddProgramStrategy:
        e = Validations().acceptable_command(list(labels))
        match e:
            case ExitFailure(err=err):
                raise err
            case ExitSuccess(value={"command": "init", "app_name": app_name}):
                return InitStrategy(cast(str, app_name))
            case ExitSuccess(value={"command": "create", "app_name": app_name}):
                return CreateStrategy(cast(str, app_name))
            case ExitSuccess(
                value={
                    "command": "addprogram",
                    "app_name": app_name,
                    "program_name": pn,
                }
            ):
                return AddProgramStrategy(cast(str, app_name), cast(str, pn))
            case ExitSuccess(value={"command": "list"}):
                return ListStrategy()
            case _ as x:
                raise StrategyError(f"Unable to handle {x}")
