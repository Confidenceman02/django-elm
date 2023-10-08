import os
import shutil

from src.elm.utils import get_app_path


def cleanup_theme_app_dir(app_name):
    theme_app_dir = get_app_path(app_name)
    if theme_app_dir.tag == "Success" and os.path.isdir(theme_app_dir.value):
        shutil.rmtree(theme_app_dir.value)
