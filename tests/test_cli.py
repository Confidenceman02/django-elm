import os
import uuid

from django.core.management import call_command

from src.elm.utils import get_app_path

from .conftest import cleanup_theme_app_dir


def test_elm_create_directory(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]
    assert os.path.isfile(
        os.path.join(get_app_path(app_name).value, "apps.py")  # type:ignore
    ), 'The "project" app has been generated'

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value, "static_src", "package.json"  # type:ignore
        )
    ), "The project package.json has been generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value, app_name + ".djelm"  # type:ignore
        )
    ), "The project package.json has been generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value, "static_src", ".gitignore"  # type:ignore
        )
    ), "The project .gitignore has been generated"

    assert os.path.isdir(app_name), "The project directory has been generated"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "templatetags")  # type:ignore
    ), "The elm templatetags directory has been created"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "templates")  # type:ignore
    ), "The elm templates directory has been created"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_elm_init(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("elm", "init", app_name)

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value, "static_src", "elm.json"  # type:ignore
        )
    ), "The app elm.json has been generated"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "static_src", "src")  # type:ignore
    ), "The elm starter src has been created"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_elm_addprogram(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("elm", "init", app_name)
    call_command("elm", "addprogram", app_name, "Main")

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "static_src",
            "src",
            "Main.elm",
        )
    ), "The elm program has been created"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)
