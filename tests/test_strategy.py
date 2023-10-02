import uuid
from django.core.management.base import LabelCommand
from src.elm.strategy import Strategy, CreateStrategy, InitStrategy, ListStrategy
from unittest import TestCase
from django.core.management import call_command
from .conftest import cleanup_theme_app_dir


def test_strategy_create_create():
    TestCase().assertIsInstance(
        Strategy().create("create", "my_app"),
        CreateStrategy
    )


def test_strategy_create_init():
    TestCase().assertIsInstance(
        Strategy().create("init", "my_app"),
        InitStrategy
    )


def test_strategy_list(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("elm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertListEqual(ListStrategy().run(LabelCommand().stdout, LabelCommand().style), [app_name])
    cleanup_theme_app_dir(app_name)
