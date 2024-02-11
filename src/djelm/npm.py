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
        except OSError as err:
            return ExitFailure(
                None,
                NPMError(_to_npm_error(err, " ".join([npm_bin_path, *args]))),
            )


def _to_npm_error(err: Exception, command: str):
    return f"""
\033[91m-- PACKAGE MANAGER ERROR ---------------------------------------------------------------------------------------------------------- command/npm\033[0m

Im trying to run this command:

    \033[93m{command}\033[0m

But it raised this error:

    \033[93m{err}\033[0m

\033[4m\033[1mHint\033[0m: If I don't see a \033[1mNODE_PACKAGE_MANAGER\033[0m variable in \033[1msettings.py\033[0m I will try to use \033[1mpnpm\033[0m by default.

Check out <https://github.com/Confidenceman02/django-elm?tab=readme-ov-file#npm-command> for more information."""
