import uuid
from unittest import TestCase

from django.core.management import call_command

from src.djelm.effect import ExitFailure, ExitSuccess
from src.djelm.validate import Validations

from .conftest import cleanup_theme_app_dir


def test_validate_fails_with_invalid_command_verb():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["nonsense", "my_app"]), ExitFailure
    )


def test_validate_failure_when_single_command():
    TestCase().assertIsInstance(Validations().acceptable_command(["init"]), ExitFailure)
    TestCase().assertIsInstance(
        Validations().acceptable_command(["create"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram"]), ExitFailure
    )
    TestCase().assertIsInstance(Validations().acceptable_command(["npm"]), ExitFailure)


def test_validate_failure_when_combo_command():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["list", "nonsense"]), ExitFailure
    )


def test_validate_failure_when_no_create_sequence():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", "my_app"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", "my_app", "Main"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", "my_app"]), ExitFailure
    )


def test_validate_failure_when_not_enough_args_with_create_sequence(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", app_name]), ExitFailure
    )

    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name]), ExitFailure
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_success_when_create_sequence(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", app_name]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name, "install"]), ExitSuccess
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name, "install", "-D", "elm"]),
        ExitSuccess,
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_success_when_init_sequence(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    call_command("djelm", "init", app_name)

    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", app_name, "Main"]), ExitSuccess
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_failure_when_app_external():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", "djelm"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", "djelm"]), ExitFailure
    )


def test_validate_single_command_verb_succeeds():
    TestCase().assertIsInstance(Validations().acceptable_command(["list"]), ExitSuccess)


def test_validate_failure_when_init_sequence(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    call_command("djelm", "init", app_name)

    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", "djelm"]), ExitFailure
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_failure_when_create_sequence(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["create", app_name]), ExitFailure
    )

    TestCase().assertIsInstance(
        Validations().acceptable_command(["create", "djelm"]), ExitFailure
    )

    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", app_name, "Main"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name]), ExitFailure
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_failure_when_create_sequence_app_not_in_settings(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)

    TestCase().assertIsInstance(
        Validations().acceptable_command(["npm", app_name, "install"]), ExitFailure
    )

    # Hack to remove generated directory
    settings.INSTALLED_APPS += [app_name]
    cleanup_theme_app_dir(app_name)
