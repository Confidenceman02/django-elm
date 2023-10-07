import os
import uuid
from .conftest import cleanup_theme_app_dir
from django.core.management import call_command
from src.elm.utils import get_app_path


def test_elm_create_directory(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]
    assert os.path.isfile(
        os.path.join(get_app_path(app_name), "apps.py")
    ), 'The "project" app has been generated'

    assert os.path.isfile(
        os.path.join(get_app_path(app_name), "static_src", "package.json")
    ), "The project package.json has been generated"

    assert os.path.isfile(
        os.path.join(get_app_path(app_name), app_name + ".django_elm")
    ), "The project package.json has been generated"

    assert os.path.isfile(
        os.path.join(get_app_path(app_name), "static_src", ".gitignore")
    ), "The project .gitignore has been generated"

    assert os.path.isdir(app_name), "The project directory has been generated"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_elm_init(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("elm", "init", app_name)

    assert os.path.isfile(
        os.path.join(get_app_path(app_name), "static_src", "elm.json")
    ), "The app elm.json has been generated"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name), "static_src", "src")
    ), "The elm starter src has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name),
            "static_src",
            "src",
            app_name[0].upper() + app_name[1:] + ".elm",
        )
    ), "The elm starter module has been created"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)
