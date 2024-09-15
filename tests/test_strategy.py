import uuid
import pytest
from unittest import TestCase

from django.core.management import call_command
from django.core.management.base import LabelCommand
from djelm.generators import (
    ModelGenerator,
    ProgramGenerator,
    WidgetModelGenerator,
)

from djelm.effect import ExitSuccess
from djelm.strategy import (
    AddProgramStrategy,
    AddWidgetStrategy,
    CreateStrategy,
    FindPrograms,
    GenerateModelStrategy,
    ListStrategy,
    NpmStrategy,
    Strategy,
    StrategyError,
    WatchStrategy,
    program_namespace_to_model_builder,
)

from .conftest import cleanup_theme_app_dir


def test_strategy_create_when_no_create():
    TestCase().assertIsInstance(
        Strategy().create(["create", "my_app"], {}), CreateStrategy
    )


def test_findprograms_strategy(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]
    call_command("djelm", "addprogram", app_name, "Main1")
    call_command("djelm", "addprogram", app_name, "Main2")
    call_command("djelm", "addprogram", app_name, "Main3")
    call_command("djelm", "addprogram", app_name, "Main4")
    call_command("djelm", "addwidget", app_name, "ModelChoiceField", "--no-deps")
    call_command(
        "djelm", "addprogram", app_name, "ModelMultipleChoiceField", "--no-deps"
    )

    TestCase().assertIsInstance(
        FindPrograms(app_name).run(LabelCommand().stdout), ExitSuccess
    )

    programs = FindPrograms(app_name).run(LabelCommand().stdout).value

    SUT = [p["file"] for p in programs]

    TestCase().assertEqual(
        set(
            [
                "Main1.elm",
                "Main2.elm",
                "Main3.elm",
                "Main4.elm",
                "ModelChoiceField.elm",
                "ModelMultipleChoiceField.elm",
            ]
        ),
        set(SUT),
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_after_create_strategy_success(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]

    TestCase().assertIsInstance(
        Strategy().create(["watch", app_name], {}), WatchStrategy
    )
    TestCase().assertIsInstance(ListStrategy().run(LabelCommand().stdout), ExitSuccess)
    TestCase().assertEqual(
        ListStrategy().run(LabelCommand().stdout).value,  # type: ignore
        ["test_programs", app_name],
    )
    TestCase().assertIsInstance(
        Strategy().create(["npm", app_name, "install"], {}), NpmStrategy
    )
    TestCase().assertIsInstance(
        AddProgramStrategy(app_name, "Main", ProgramGenerator()).run(
            LabelCommand().stdout
        ),
        ExitSuccess,
    )
    TestCase().assertIsInstance(
        Strategy().create(["watch", app_name], {}), WatchStrategy
    )
    TestCase().assertIsInstance(
        Strategy().create(["addprogram", app_name, "Main"], {}), AddProgramStrategy
    )
    TestCase().assertIsInstance(
        Strategy().create(["addwidget", app_name, "ModelChoiceField"], {}),
        AddWidgetStrategy,
    )
    TestCase().assertIsInstance(
        Strategy().create(["addwidget", app_name, "ModelMultipleChoiceField"], {}),
        AddWidgetStrategy,
    )
    TestCase().assertIsInstance(
        Strategy().create(["findprograms", app_name], {}),
        FindPrograms,
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_after_addprogram_strategy_success(settings):
    app_name = f'test_project_{str(uuid.uuid1()).replace("-", "_")}'
    call_command("djelm", "create", app_name)
    settings.INSTALLED_APPS += [app_name]
    call_command("djelm", "addprogram", app_name, "Main")

    TestCase().assertIsInstance(
        Strategy().create(["generatemodel", app_name, "Main"], {}),
        GenerateModelStrategy,
    )

    settings.INSTALLED_APPS.remove(app_name)
    cleanup_theme_app_dir(app_name)


def test_program_namespace_to_model_builder():
    SUT1 = program_namespace_to_model_builder(["Main"])

    assert isinstance(SUT1, ModelGenerator)

    SUT2 = program_namespace_to_model_builder(["Widgets", "ModelChoiceField"])

    assert isinstance(SUT2, WidgetModelGenerator)

    with pytest.raises(StrategyError):
        program_namespace_to_model_builder(["Widgets", "NonsenseWidget"])

    with pytest.raises(StrategyError):
        program_namespace_to_model_builder(["Some", "Program"])
