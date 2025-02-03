import subprocess
import sys
import threading
from dataclasses import dataclass
from typing import IO


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
            text=True,
        )

        stderr_data = []

        def read_stream(stream: IO[str], buffer: list[str]):
            while True:
                char = stream.read(1)
                if not char:
                    break
                sys.stdout.write(char)
                sys.stdout.flush()
                if stream == process.stderr:
                    buffer.append(char)

        stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, []))
        stderr_thread = threading.Thread(
            target=read_stream, args=(process.stderr, stderr_data)
        )

        stdout_thread.start()
        stderr_thread.start()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()

        if process.returncode != 0 or (self.raise_error and stderr_data):
            error_message = "".join(stderr_data).strip()
            raise subprocess.CalledProcessError(
                process.returncode, self.command, output=None, stderr=error_message
            )
