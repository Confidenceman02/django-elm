import subprocess
import sys

from elm import get_config


class ElmException(Exception):
    pass


class Elm:
    elm_bin_path: str | None = None
    target_dir: str | None = None

    def __init__(self, elm_bin_path: str | None = None, target_dir: str | None = None):
        self.elm_bin_path: str = elm_bin_path if elm_bin_path else get_config("ELM_BIN_PATH")
        self.target_dir = target_dir

    def command(self, *args: tuple[str]):
        try:
            subprocess.check_output([self.elm_bin_path] + list(args), cwd=self.target_dir)
        except subprocess.CalledProcessError:
            sys.exit(1)
        except OSError:
            raise ElmException(
                "\nI can't find an 'elm' binary.\nGo to https://guide.elm-lang.org/install/elm.html for instructions "
                "on how to install elm.\n"
            )
