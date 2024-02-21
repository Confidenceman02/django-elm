import subprocess
import sys
from dataclasses import dataclass


@dataclass(slots=True)
class SubProcess:
    command: list[str]
    cwd: str
    raise_error: bool = False

    def open(self):
        process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if process.stdout is None:
            raise Exception("stdout not available")
        for c in iter(lambda: process.stdout.read(1), ""):  # type:ignore
            sys.stdout.write(c.decode("utf-8", "ignore"))
            sys.stdout.flush()
            if process.poll() is not None:
                break
        for c in iter(lambda: process.stderr.read(), ""):  # type:ignore
            if c.decode("utf-8", "ignore") != "":
                if self.raise_error:
                    raise Exception(c.decode("utf-8", "ignore"))
                else:
                    sys.stdout.write(c.decode("utf-8", "ignore"))
            break
