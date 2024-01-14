import subprocess
import sys
from dataclasses import dataclass

from djelm import get_config
from djelm.effect import ExitFailure, ExitSuccess
from djelm.subprocess import SubProcess


class NPMError(Exception):
    pass


@dataclass(slots=True)
class NPM:
    raise_err: bool = True

    def command(
        self, cwd: str, args: list[str]
    ) -> ExitSuccess[None] | ExitFailure[None, NPMError]:
        npm_bin_path = get_config("NODE_PACKAGE_MANAGER")
        try:
            process = SubProcess([npm_bin_path, *args], cwd, self.raise_err)
            process.open()
            return ExitSuccess(None)
        except subprocess.CalledProcessError:
            sys.exit(1)
        except OSError:
            return ExitFailure(
                None,
                NPMError(
                    f"\nIt looks like node.js and/or {npm_bin_path} is not installed or cannot be found.\n\n"
                    "Visit https://nodejs.org to download and install node.js for your system.\n\n"
                    "If you have npm installed and are still getting this error message, "
                    "set NODE_PACKAGE_MANAGER variable in settings.py to match the path of a node package manager executable in your system.\n\n"
                    "Example:\n"
                    'NODE_PACKAGE_MANAGER = "/usr/local/bin/pnpm"'
                ),
            )
