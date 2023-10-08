import os

from django.apps import apps

from elm.effect import ExitFailure, ExitSuccess


def get_app_path(app_name) -> ExitSuccess[str] | ExitFailure[None, Exception]:
    app_label = app_name.split(".")[0]
    try:
        path = apps.get_app_config(app_label).path
        return ExitSuccess(path)
    except LookupError as err:
        return ExitFailure(meta=None, err=err)


def get_app_src_path(app_name: str) -> ExitSuccess[str] | ExitFailure[None, Exception]:
    path_exit = get_app_path(app_name)
    if path_exit.tag == "Success":
        return ExitSuccess(os.path.join(path_exit.value, "static_src"))
    return path_exit


def install_pip_package(pkg_name: str):
    from pip._internal import main

    main(["install", pkg_name])


def walk_level(some_dir: str, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def is_django_elm(files: list[str]) -> bool:
    test = ".django_elm"
    found = False
    for f in files:
        if test in f:
            found = True
            break
    return found
