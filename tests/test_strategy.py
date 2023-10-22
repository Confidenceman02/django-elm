import uuid
from unittest import TestCase

from django.core.management import call_command
from django.core.management.base import LabelCommand

from src.djelm.effect import ExitSuccess
from src.djelm.strategy import (
    AddProgramStrategy,
    CreateStrategy,
    ListStrategy,
    NpmStrategy,
    Strategy,
    WatchStrategy,
)

from .conftest import cleanup_theme_app_dir


def test_strategy_create_when_no_create():
    TestCase().assertIsInstance(Strategy().create("create", "my_app"), CreateStrategy)


def test_strategy_when_create(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(Strategy().create("watch", app_name), WatchStrategy)
    TestCase().assertIsInstance(
        ListStrategy().run(LabelCommand().stdout, LabelCommand().style), ExitSuccess
    )
    TestCase().assertEqual(
        ListStrategy().run(LabelCommand().stdout, LabelCommand().style).value, [app_name]  # type: ignore
    )
    TestCase().assertIsInstance(
        Strategy().create("npm", app_name, "install"), NpmStrategy
    )
    TestCase().assertIsInstance(
        AddProgramStrategy(app_name, "Main").run(
            LabelCommand().stdout, LabelCommand().style
        ),
        ExitSuccess,
    )
    TestCase().assertIsInstance(Strategy().create("watch", app_name), WatchStrategy)

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)
