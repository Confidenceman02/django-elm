import os
from dataclasses import dataclass
from itertools import filterfalse
from typing import IO, Iterable, cast

from django.conf import settings

from .effect import ExitFailure, ExitSuccess
from .elm import Elm
from .utils import (
    get_app_path,
    get_app_src_path,
    install_pip_package,
    is_djelm,
    module_name,
    program_file,
    walk_level,
)
from .validate import Validations


class StrategyError(Exception):
    pass


@dataclass(slots=True)
class AddProgramStrategy:
    app_name: str
    prog_name: str

    def run(
        self, logger, style
    ) -> ExitSuccess[None] | ExitFailure[None, StrategyError]:
        src_path = get_app_src_path(self.app_name)
        if src_path.tag == "Success":
            try:
                f: IO[str] = open(
                    os.path.join(src_path.value, "src", program_file(self.app_name)),
                    "w",
                )
                f.write(self.__elm_module() + self.__starter_code())
                return ExitSuccess(None)
            except OSError as err:
                return ExitFailure(None, err=StrategyError(err))
        else:
            return ExitFailure(None, err=StrategyError(src_path.err))

    def __elm_module(self):
        return f"module {module_name(self.app_name)} exposing(..)\n"

    def __starter_code(self):
        return """
import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)

type Msg = Increment | Decrement

main : Program () Int Msg
main =
    Browser.sandbox { init = 0, update = update, view = view }

update : Msg -> Int -> Int
update msg model =
    case msg of
        Increment ->
            model + 1

        Decrement ->
            model - 1

view : Int -> Html Msg
view model =
    div []
        [ button [ onClick Decrement ] [ text "-" ]
        , div [] [ text (String.fromInt model) ]
        , button [ onClick Increment ] [ text "+" ]
        ]
    """


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
                try:
                    f: IO[str] = open(
                        os.path.join(src_path.value, "src", module_name(self.app_name)),
                        "wt",
                    )
                    f.close()
                    return ExitSuccess(None)
                except OSError as err:
                    return ExitFailure(None, err=StrategyError(err))
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

    def run(self, logger, style):
        try:
            from cookiecutter.main import cookiecutter
        except ImportError:
            logger.stdout.write("Couldn't find cookie cutter, installing...")
            install_pip_package("cookiecutter")
            from cookiecutter.main import cookiecutter
        try:
            app_path = cookiecutter(
                os.path.dirname(__file__),
                output_dir=os.getcwd(),
                directory="project_template",
                no_input=True,
                overwrite_if_exists=False,
                extra_context={"app_name": self.app_name.strip()},
            )

            app_name = os.path.basename(app_path)
            logger.write(
                style.SUCCESS(
                    f"Elm project '{app_name}' "
                    f"has been successfully created. "
                    f"Please add '{app_name}' to INSTALLED_APPS in settings.py, "
                    f"then run the following command to install all packages "
                    f"dependencies: `python manage.py elm init`"
                )
            )
        except Exception as err:
            raise err


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
