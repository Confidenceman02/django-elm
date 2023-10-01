import os
from .validate import Validations, InitValidation
from .effect import ExitFailure, ExitSuccess
from .utils import install_pip_package
from dataclasses import dataclass


@dataclass
class InitStrategy:
    app_name: str

    def run(self, logger, style):
        # TODO implement init
        pass


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
    def create(self, *labels) -> InitStrategy | CreateStrategy:
        e = Validations().acceptable_command(list(labels))
        match e:
            case ExitFailure(err):
                raise err
            case ExitSuccess(value={'command': 'init', 'app_name': app_name}):
                return InitStrategy(app_name)
            case ExitSuccess(value={'command': 'create', 'app_name': app_name}):
                return CreateStrategy(app_name)
