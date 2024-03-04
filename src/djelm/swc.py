from dataclasses import dataclass
from os.path import isdir, isfile
from urllib.request import urlretrieve
from pathlib import Path
import os
import stat

SWC_LINUX_X64_NIGHTLY = (
    "https://github.com/swc-project/swc/releases/download/v1.4.3-nightly-20240222.2/swc-linux-x64-gnu",
    "v1.4.3-nightly",
)


@dataclass(slots=True)
class Swc:
    def download_binary(self):
        home_dir = Path.home()
        os.access
        djelm_home = os.path.join(home_dir, ".djelm")
        swc_x = os.path.join(djelm_home, "swc")
        tmp_swc_path = ""
        if not isdir(djelm_home):
            os.mkdir(djelm_home)
        if not isfile(swc_x):
            try:
                tmp_swc_path = self.request()
                os.rename(tmp_swc_path, swc_x)
                os.chmod(swc_x, mode=stat.S_IXUSR)
            except Exception as err:
                raise err
        if not os.access(swc_x, os.X_OK):
            raise Exception(
                "Looks like I can't execute swc, make sure you have executable permissions on it."
            )

    def request(self):
        tmp_path, _ = urlretrieve(SWC_LINUX_X64_NIGHTLY[0])
        return tmp_path
