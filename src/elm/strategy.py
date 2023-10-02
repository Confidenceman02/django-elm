import os
from .validate import Validations
from .effect import ExitFailure, ExitSuccess
from .utils import (
    install_pip_package,
    get_app_path,
    walk_level,
    get_app_src_path,
    is_django_elm
)
from .elm import Elm
from dataclasses import dataclass
from django.conf import settings
from itertools import filterfalse


class StrategyError(Exception):
    pass


@dataclass
class InitStrategy:
    app_name: str
    elm: Elm = Elm()

    def run(self, logger, style):
        src_path = get_app_src_path(self.app_name)
        # TODO implement init
        pass


class ListStrategy:
    _apps: list[str] = []

    def __init__(self):
        self._apps = settings.INSTALLED_APPS

    def run(self, logger, style) -> list[str]:
        app_paths = filterfalse(
            lambda x: x is None,
            map(get_app_path, self._apps)
        )

        dir_data = map(
            next,
            map(
                walk_level,
                app_paths
            ))

        django_elm_apps = [os.path.basename(r) for r, _, f in dir_data if is_django_elm(f)]

        logger.write(style.SUCCESS("Here are all your installed django-elm apps:"))
        for app in django_elm_apps:
            logger.write(
                style.SUCCESS(f"{app}")
            )
        logger.write(
            style.WARNING(
                "If you don't see all your django-elm apps make sure they are installed in your 'settings.py'."))
        return django_elm_apps


@dataclass
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


class Strategy:
    def create(self, *labels) -> InitStrategy | CreateStrategy | ListStrategy:
        e = Validations().acceptable_command(list(labels))
        match e:
            case ExitFailure(err):
                raise err
            case ExitSuccess(value={'command': 'init', 'app_name': app_name}):
                return InitStrategy(app_name)
            case ExitSuccess(value={'command': 'create', 'app_name': app_name}):
                return CreateStrategy(app_name)
            case ExitSuccess(value={'command': 'list'}):
                return ListStrategy()
            case _ as x:
                raise StrategyError(f"Unable to handle {x}")
