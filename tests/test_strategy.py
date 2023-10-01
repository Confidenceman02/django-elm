from src.elm.strategy import Strategy, CreateStrategy, InitStrategy
from unittest import TestCase


def test_strategy_create():
    TestCase().assertIsInstance(
        Strategy().create("create", "my_app"),
        CreateStrategy
    )


def test_strategy_init():
    TestCase().assertIsInstance(
        Strategy().create("init", "my_app"),
        InitStrategy
    )
