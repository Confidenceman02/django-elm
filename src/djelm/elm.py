import subprocess
import sys

from djelm import get_config
from djelm.subprocess import SubProcess

from .effect import ExitFailure, ExitSuccess


class ElmError(Exception):
    pass


class Elm:
    elm_bin_path: str

    def __init__(self):
        binary = self.elm_binary()
        if get_config("ELM_BIN_PATH"):
            self.elm_bin_path = get_config("ELM_BIN_PATH")
        elif binary.tag == "Success":
            self.elm_bin_path = binary.value
        else:
            raise binary.err

    def command(
        self, args: list[str], target_dir: str
    ) -> ExitSuccess[str] | ExitFailure[None, ElmError | SystemExit]:
        try:
            process = SubProcess([self.elm_bin_path, *list(args)], target_dir, True)
            process.open()
            return ExitSuccess(f"cmd: {args}")
        except subprocess.CalledProcessError:
            sys.exit(1)
        except OSError as err:
            return ExitFailure(
                None,
                ElmError(_elm_binary_log(err)),
            )

    @staticmethod
    def elm_binary() -> ExitSuccess[str] | ExitFailure:
        try:
            # TODO: make platform specific 'platform.system() for Windows'
            p = subprocess.check_output(["which", "elm"])
            return ExitSuccess(p.decode("utf-8"))
        except subprocess.CalledProcessError as err:
            return ExitFailure[None, ElmError](None, ElmError(_elm_binary_log(err)))


def _elm_binary_log(err):
    return (
        f"I can't find an 'elm' binary in your PATH.\n Go to https://guide.elm-lang.org/install/elm.html for "
        f"instructions"
        f"on how to install elm.\n {err}"
    )
