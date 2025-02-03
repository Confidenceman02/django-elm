import os

from django.apps import apps

from djelm.effect import ExitFailure, ExitSuccess
from importlib.metadata import version

DJELM_VERSION = version("djelm")
STUFF_NAMESPACE = ("elm-stuff", f"djelm_{DJELM_VERSION}")
STUFF_ENTRYPOINTS = (*STUFF_NAMESPACE, "entrypoints")


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


def is_djelm(files: list[str]) -> bool:
    test = ".djelm"
    found = False
    for f in files:
        if test in f:
            found = True
            break
    return found


def is_create(app_name: str) -> bool:
    path_exit = get_app_path(app_name)
    if path_exit.tag == "Success":
        tags = os.path.isdir(
            os.path.join(
                path_exit.value,
                "templatetags",
            )
        )
        if tags:
            return True
    return False


def is_init(app_name: str) -> bool:
    path_exit = get_app_path(app_name)
    if path_exit.tag == "Success":
        f = os.path.isfile(
            os.path.join(
                path_exit.value,
                "static_src",
                "elm.json",
            )
        )
        src = os.path.isdir(
            os.path.join(
                path_exit.value,
                "static_src",
                "src",
            )
        )
        return f and src
    return False


def is_program(app_name: str, namespace: tuple[list[str], str]) -> bool:
    namespace_path, prog_name = namespace
    path_exit = get_app_src_path(app_name)
    if path_exit.tag == "Success":
        f = os.path.isfile(
            os.path.join(
                path_exit.value,
                "src",
                *namespace_path,
                prog_name + ".elm",
            )
        )
        return f
    return False


def to_program_namespace(namespace: list[str]) -> tuple[list[str], str]:
    prog_name = namespace.pop()

    return (namespace, prog_name)


def module_name(app_name: str):
    return app_name[0].upper() + app_name[1:]


def view_name(prog_name: str):
    return prog_name[0].upper() + prog_name[1:].lower()


def tag_file_name(prog_name: str):
    return prog_name[0].lower() + prog_name[1:]


def program_file(app_name: str):
    return module_name(app_name) + ".elm"


def scope_name(app_name: str, prog_name: str) -> str:
    return (app_name.lower() + prog_name.lower().replace("_", "")).replace("_", "")


def widget_scope_name(app_name: str, prog_name: str) -> str:
    return ("widgets" + app_name.lower() + prog_name.lower().replace("_", "")).replace(
        "_", ""
    )


def is_elm_file_string(string_file: str) -> bool:
    return string_file.endswith(".elm")


def is_ts_file_string(string_file: str) -> bool:
    return string_file.endswith(".ts")


def supporting_ts_files(prog_name: str) -> list[str]:
    return [prog_name + ".handlers.ts"]
