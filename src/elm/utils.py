import os
from django.apps import apps


def get_app_path(app_name) -> str:
    app_label = app_name.split(".")[-1]
    try:
        path = apps.get_app_config(app_label).path
        return path
    except LookupError:
        pass


def get_app_src_path(app_name: str):
    return os.path.join(get_app_path(app_name), "static_src")


def install_pip_package(pkg_name: str):
    from pip._internal import main
    main(["install", pkg_name])


def walk_level(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
