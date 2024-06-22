import os
import uuid

from django.core.management import call_command

from djelm.utils import get_app_path, get_app_src_path

from .conftest import cleanup_theme_app_dir


def test_after_create(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]
    assert os.path.isfile(
        os.path.join(get_app_path(app_name).value, "apps.py")  # type:ignore
    ), 'The "project" app has been generated'

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            "static_src",
            "package.json",  # type:ignore
        )
    ), "The project package.json has been generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            app_name + ".djelm",  # type:ignore
        )
    ), "The project package.json has been generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            "static_src",
            ".gitignore",  # type:ignore
        )
    ), "The project .gitignore has been generated"

    assert os.path.isdir(app_name), "The project directory has been generated"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "templatetags")  # type:ignore
    ), "The elm templatetags directory has been created"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "static")  # type:ignore
    ), "The elm templates static directory has been created"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "elm.json",  # type:ignore
        )
    ), "The project elm.json file has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_src_path(app_name).value,
            "djelm_src",  # type:ignore
        )
    ), "The djelm source directory has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_src_path(app_name).value,
            "src",  # type:ignore
        )
    ), "The elm program src directory has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_src_path(app_name).value,
            "src",
            "Models",  # type:ignore
        )
    ), "The elm program Models directory has been generated"

    assert os.path.isdir(
        os.path.join(
            get_app_path(app_name).value,
            "flags",  # type:ignore
        )
    ), "The elm program flags directory has been generated"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_after_addprogram(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

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


def test_after_addwidget(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("djelm", "addwidget", app_name, "ModelChoiceField", "--no-deps")
    call_command(
        "djelm", "addwidget", app_name, "ModelMultipleChoiceField", "--no-deps"
    )

    assert os.path.isdir(
        os.path.join(get_app_src_path(app_name).value, "elm-stuff")
    ), "elm-stuff directory gets created"

    assert os.path.isdir(
        os.path.join(get_app_src_path(app_name).value, "src", "Widgets")
    ), "Widgets directory gets created"

    assert os.path.isdir(
        os.path.join(get_app_src_path(app_name).value, "src", "Widgets", "Models")
    ), "Widgets.Models directory gets created"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "src",
            "Widgets",
            "Models",
            "ModelChoiceField.elm",
        )
    ), "The Widgets.Models.ModelChoiceField module gets generated"
    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "src",
            "Widgets",
            "Models",
            "ModelMultipleChoiceField.elm",
        )
    ), "The Widgets.Models.ModelMultipleChoiceField module gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "src",
            "Widgets",
            "ModelChoiceField.elm",
        )
    ), "The Widgets.ModelChoiceField  module gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "src",
            "Widgets",
            "ModelMultipleChoiceField.elm",
        )
    ), "The Widgets.ModelMultipleChoiceField  module gets generated"

    assert os.path.isdir(
        os.path.join(get_app_path(app_name).value, "flags", "widgets")
    ), "The flags.widgets directory gets created"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            "flags",
            "widgets",
            "modelChoiceField.py",
        )
    ), "The flags.widgets.modelChoiceField module gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            "flags",
            "widgets",
            "modelMultipleChoiceField.py",
        )
    ), "The flags.widgets.modelMultipleChoiceField module gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            "templatetags",
            "modelChoiceField_widget_tags.py",
        )
    ), "The templatetags.modelChoiceField__widget_tags module gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_path(app_name).value,
            "templatetags",
            "modelMultipleChoiceField_widget_tags.py",
        )
    ), "The templatetags.modelMultipleChoiceField__widget_tags module gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "djelm_src",
            "Widgets.ModelChoiceField.ts",
        )
    ), "The Widgets.ModelChoiceField ts file gets generated"

    assert os.path.isfile(
        os.path.join(
            get_app_src_path(app_name).value,
            "djelm_src",
            "Widgets.ModelMultipleChoiceField.ts",
        )
    ), "The Widgets.ModelMultipleChoiceField ts file gets generated"

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)
