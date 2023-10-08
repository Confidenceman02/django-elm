import uuid
from unittest import TestCase

import pytest
from django.core.management import call_command

from src.elm.effect import ExitFailure, ExitSuccess
from src.elm.validate import Validations

from .conftest import cleanup_theme_app_dir


def test_validate_fails_with_invalid_command_verb():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["nonsense", "my_app"]), ExitFailure
    )


def test_validate_combo_command_fails_with_no_args():
    TestCase().assertIsInstance(Validations().acceptable_command(["init"]), ExitFailure)
    TestCase().assertIsInstance(
        Validations().acceptable_command(["create"]), ExitFailure
    )
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram"]), ExitFailure
    )


def test_validate_single_command_fails_with_args():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["list", "nonsense"]), ExitFailure
    )


def test_validate_init_fails_when_no_app_exists():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", "my_app"]), ExitFailure
    )


def test_validate_addprogram_fails_when_no_app_exists():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", "my_app"]), ExitFailure
    )


def test_validate_init_succeeds_when_app_exists(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", app_name]), ExitSuccess
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


@pytest.mark.skip(reason="Yet to implement")
def test_validate_addprogram_fails_when_init_not_run(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)

    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["addprogram", app_name]), ExitFailure
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_validate_init_fails_when_app_external():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", "elm"]), ExitFailure
    )


def test_validate_single_command_verb_succeeds():
    TestCase().assertIsInstance(Validations().acceptable_command(["list"]), ExitSuccess)


def test_validate_app_exists(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Validations().acceptable_command(["create", app_name]), ExitFailure
    )

    TestCase().assertIsInstance(
        Validations().acceptable_command(["create", "elm"]), ExitFailure
    )

    cleanup_theme_app_dir(app_name)
