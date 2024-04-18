import uuid
from unittest import TestCase

from django.core.management import call_command

from djelm.effect import ExitFailure, ExitSuccess
from djelm.validate import Validations

from .conftest import cleanup_theme_app_dir


def test_validate_failure_with_invalid_command_verb():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["nonsense", "my_app"]), ExitFailure
    )


def test_validate_failure_when_single_command():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["create"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["generatemodel"]), ExitFailure
    )
    TestCase().assertIsInstance(Validations().acceptable_command(["npm"]), ExitFailure)
    TestCase().assertIsInstance(Validations().acceptable_command(["elm"]), ExitFailure)
    TestCase().assertIsInstance(
        Validations().acceptable_command(["watch"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["compile"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["compilebuild"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addwidget"]), ExitFailure
    )


def test_validate_failure_when_too_many_args():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["list", "nonsense"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["listwidgets", "nonsense"]), ExitFailure
    )


def test_validate_failure_when_not_app():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", "my_app", "Main"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["generatemodel", "my_app", "Main"]),
        ExitFailure,
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", "my_app"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["elm", "my_app"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["watch", "my_app"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["compile", "my_app"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["compilebuild", "my_app"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addwidget", "my_app", "ModelChoiceField"]),
        ExitFailure,
    )


def test_after_create_validate_failure(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    # Too few args
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", app_name]), ExitFailure
    )

    # Too few args
    TestCase().assertIsInstance(
        Validations().acceptable_command(["generatemodel", app_name]), ExitFailure
    )

    # App doesn't exist
    TestCase().assertIsInstance(
        Validations().acceptable_command(["generatemodel", "random", "Main"]),
        ExitFailure,
    )

    # Too few args
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addwidget", app_name]), ExitFailure
    )

    # Unsuppoerted widget name
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addwidget", "SomeWidget"]), ExitFailure
    )

    TestCase().assertIsInstance(
        Validations().acceptable_command(["create", app_name]), ExitFailure
    )

    # App already exists
    TestCase().assertIsInstance(
        Validations().acceptable_command(["create", "djelm"]), ExitFailure
    )

    # App doesn't exists
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", "random", "install"]), ExitFailure
    )

    # App doesn't exists
    TestCase().assertIsInstance(
        Validations().acceptable_command(["elm", "random", "install", "elm/json"]),
        ExitFailure,
    )

    # App doesn't exists
    TestCase().assertIsInstance(
        Validations().acceptable_command(["watch", "random"]), ExitFailure
    )

    # App doesn't exists
    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_after_create_validate_success(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name, "install"]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name, "install", "-D", "elm"]),
        ExitSuccess,
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["elm", app_name, "init"]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["elm", app_name]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["elm", app_name, "install", "elm/json"]),
        ExitSuccess,
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["watch", app_name]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", app_name, "Main"]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["compile", app_name]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["compilebuild", app_name]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addwidget", app_name, "ModelChoiceField"]),
        ExitSuccess,
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_success_when_addprogram_sequence(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]
    call_command("djelm", "addprogram", app_name, "Main")
    call_command("djelm", "addwidget", app_name, "ModelChoiceField", "--no-deps")

    TestCase().assertIsInstance(
        Validations().acceptable_command(["generatemodel", app_name, "Main"]),
        ExitSuccess,
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(
            ["generatemodel", app_name, "Widgets.ModelChoiceField"]
        ),
        ExitSuccess,
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_failure_when_app_external():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", "djelm", "install"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["elm", "djelm", "install", "elm/json"]),
        ExitFailure,
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["watch", "djelm"]), ExitFailure
    )


def test_validate_single_command_verb_succeeds():
    TestCase().assertIsInstance(Validations().acceptable_command(["list"]), ExitSuccess)
    TestCase().assertIsInstance(
        Validations().acceptable_command(["listwidgets"]), ExitSuccess
    )
