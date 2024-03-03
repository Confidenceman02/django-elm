import os
from glob import glob
from pathlib import Path
import shutil

from src.djelm.utils import get_app_path


def cleanup_theme_app_dir(app_name):
    theme_app_dir = get_app_path(app_name)
    if theme_app_dir.tag == "Success" and os.path.isdir(theme_app_dir.value):
        shutil.rmtree(theme_app_dir.value)


def cleanup_models(app_name):
    theme_app_dir = get_app_path(app_name)
    if theme_app_dir.tag == "Success":
        all_files = glob(
            os.path.join(theme_app_dir.value, "static_src", "src", "**", "*.elm"),
            recursive=True,
        )
        for file in all_files:
            Path(file).unlink(missing_ok=True)
