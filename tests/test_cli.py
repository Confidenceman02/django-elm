import os
import uuid
from .conftest import cleanup_theme_app_dir
from django.core.management import call_command
from src.elm.utils import get_app_path


def test_elm_create_directory(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]
    assert os.path.isfile(os.path.join(get_app_path(app_name), "apps.py")), 'The "project" app has been generated'

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name),
            "static_src",
            "package.json")), 'The project package.json has been generated'

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name),
            app_name + ".django_elm"
        )), 'The project package.json has been generated'

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name),
            "static_src",
            ".gitignore")), 'The project .gitignore has been generated'

    assert os.path.isdir(app_name), 'The project directory has been generated'

    cleanup_theme_app_dir(app_name)
