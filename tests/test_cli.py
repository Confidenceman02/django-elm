import os
import uuid

from django.core.management import call_command

from src.djelm.utils import get_app_path, get_app_src_path

from .conftest import cleanup_theme_app_dir


def test_elm_create_directory(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

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

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "static")  # type:ignore
    ), "The elm templates static directory has been created"

    assert os.path.isdir(
        os.path.join(get_app_src_path(app_name).value, ".djelm")  # type:ignore
    ), "The elm templates static directory has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value, ".djelm", "compile.js"  # type:ignore
        )
    ), "The project .gitignore has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_src_path(app_name).value, "djelm_src"  # type:ignore
        )
    ), "The djelm source directory has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_src_path(app_name).value, "src"  # type:ignore
        )
    ), "The elm program src directory has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_src_path(app_name).value, "src", "Models"  # type:ignore
        )
    ), "The elm program Models directory has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_path(app_name).value, "flags"  # type:ignore
        )
    ), "The elm program flags directory has been generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "templates",
            "include.html",
        )
    ), "The elm program template has been created"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_elm_init(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("djelm", "init", app_name)

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
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("djelm", "init", app_name)
    call_command("djelm", "addprogram", app_name, "Main")

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "static_src",
            "src",
            "Main.elm",
        )
    ), "The elm program has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "static_src",
            "src",
            "Models",
            "Main.elm",
        )
    ), "The elm program flags have been generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "templates",
            "main.html",
        )
    ), "The elm program template has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "templatetags",
            "main_tags.py",
        )
    ), "The elm program custom template tag has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,  # type:ignore
            "djelm_src",
            "Main.ts",
        )
    ), "The elm program custom template tag has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,  # type:ignore
            "flags",
            "main.py",
        )
    ), "The elm program flag file has been created"

    assert any(
        f == "Main.ts"
        for f in os.listdir(
            os.path.join(get_app_src_path(app_name).value, "djelm_src")  # type:ignore
        )
    ), "The elm program typescript glue code has been generated"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)
