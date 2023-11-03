from dataclasses import dataclass
from typing import Generic, TypeVar

from djelm.effect import ExitFailure, ExitSuccess

from .utils import install_pip_package

T = TypeVar("T")


@dataclass(slots=True)
class CookieCutter(Generic[T]):
    file_dir: str
    output_dir: str
    cookie_dir_name: str
    extra: T

    def cut(self, logger) -> ExitSuccess[str] | ExitFailure[None, Exception]:
        try:
            from cookiecutter.main import cookiecutter
        except (ImportError, ModuleNotFoundError):
            logger.write("Couldn't find cookie cutter, installing...")
            install_pip_package("cookiecutter")
            from cookiecutter.main import cookiecutter
        try:
            app_path = cookiecutter(
                self.file_dir,
                output_dir=self.output_dir,
                directory=self.cookie_dir_name,
                no_input=True,
                overwrite_if_exists=False,
                extra_context=self.extra,
            )
            return ExitSuccess(app_path)
        except Exception as err:
            return ExitFailure(None, err)
