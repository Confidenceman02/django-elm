import pytest
from subprocess import CalledProcessError
from djelm.subprocess import SubProcess


def test_subprocess_raises_error():
    process = SubProcess(command=["sh", "-c", "exit 1"], cwd="/", raise_error=True)

    with pytest.raises(CalledProcessError):
        process.open()
