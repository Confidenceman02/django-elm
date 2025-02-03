from dataclasses import dataclass
from django.conf import settings
import sys
from typing import Generic, TypeVar

from djelm.effect import ExitFailure, ExitSuccess
from djelm.subprocess import SubProcess


T = TypeVar("T")


@dataclass(slots=True)
class CookieCutter(Generic[T]):
    file_dir: str
    output_dir: str
    cookie_template_name: str
    extra: T
    overwrite: bool = False

    def cut(self, logger) -> ExitSuccess[str] | ExitFailure[None, Exception]:
        try:
            from cookiecutter.main import cookiecutter
        except (ImportError, ModuleNotFoundError):
            logger.write("Couldn't find cookie cutter, installing...")
            SubProcess(
                [sys.executable, "-m", "pip", "install", "cookiecutter"],
                settings.BASE_DIR,
            ).open()
            from cookiecutter.main import cookiecutter
        try:
            app_path = cookiecutter(
                self.file_dir,
                output_dir=self.output_dir,
                directory=self.cookie_template_name,
                no_input=True,
                overwrite_if_exists=self.overwrite,
                extra_context=self.extra,
            )
            return ExitSuccess(app_path)
        except Exception as err:
            return ExitFailure(None, err)
