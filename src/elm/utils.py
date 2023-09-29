from django.apps import apps


def get_app_path(app_name):
    app_label = app_name.split(".")[-1]
    return apps.get_app_config(app_label).path


def install_pip_package(pkg_name: str):
    from pip._internal import main
    main(["install", pkg_name])
