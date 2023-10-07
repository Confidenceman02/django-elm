import subprocess
import sys
from elm import get_config
from .effect import ExitSuccess, ExitFailure


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
        self, *args, target_dir: str
    ) -> ExitSuccess[None] | ExitFailure[None, ElmError | SystemExit]:
        try:
            subprocess.check_output(
                [self.elm_bin_path] + list(args), cwd=target_dir, input=b"y"
            )
            return ExitSuccess(None)
        except subprocess.CalledProcessError:
            return ExitFailure(None, sys.exit(1))
        except SystemExit as err:
            return ExitFailure(None, ElmError(_elm_binary_log(err)))
        except OSError as err:
            return ExitFailure(None, ElmError(_elm_binary_log(err)))

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
