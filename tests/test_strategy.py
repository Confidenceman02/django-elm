import uuid
from unittest import TestCase

from django.core.management import call_command
from django.core.management.base import LabelCommand

from src.elm.effect import ExitSuccess
from src.elm.strategy import (
    AddProgramStrategy,
    CreateStrategy,
    InitStrategy,
    ListStrategy,
    NpmStrategy,
    Strategy,
)

from .conftest import cleanup_theme_app_dir


def test_strategy_create_create():
    TestCase().assertIsInstance(Strategy().create("create", "my_app"), CreateStrategy)


def test_strategy_init(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(Strategy().create("init", app_name), InitStrategy)

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_strategy_list(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        ListStrategy().run(LabelCommand().stdout, LabelCommand().style), ExitSuccess
    )
    TestCase().assertEqual(
        ListStrategy().run(LabelCommand().stdout, LabelCommand().style).value, [app_name]  # type: ignore
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_strategy_addprogram(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    call_command("elm", "init", app_name)

    TestCase().assertIsInstance(
        AddProgramStrategy(app_name, "Main").run(
            LabelCommand().stdout, LabelCommand().style
        ),
        ExitSuccess,
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_strategy_npm(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(Strategy().create("npm", app_name), NpmStrategy)
