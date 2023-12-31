import os
import signal
import subprocess
import sys
from dataclasses import dataclass

from djelm import get_config
from djelm.effect import ExitFailure, ExitSuccess


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
            process = subprocess.Popen(
                [npm_bin_path, *args],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if process.stdout is None:
                raise Exception("stdout not available")
            for c in iter(lambda: process.stdout.read(1), ""):  # type:ignore
                sys.stdout.write(c.decode("utf-8", "ignore"))
                if process.poll() is not None:
                    break
            for c in iter(lambda: process.stderr.read(), ""):  # type:ignore
                if c.decode("utf-8", "ignore") != "" and self.raise_err:
                    raise Exception(c.decode("utf-8", "ignore"))
                break

            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
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
