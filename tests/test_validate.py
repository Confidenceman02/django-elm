import pytest

from src.elm.validate import ValidationError, Validations
from unittest import TestCase


def test_validate_fails_with_invalid_command_verb():
    with pytest.raises(ValidationError):
        Validations().acceptable_command(["nonsense"])


def test_validate_fails_with_single_valid_command_verb():
    with pytest.raises(ValidationError):
        Validations().acceptable_command(["init"])
    with pytest.raises(ValidationError):
        Validations().acceptable_command(["create"])


def test_validate_something():
    TestCase().assertDictEqual(
        {'_tag': 'Success', 'value': {'command': 'init', 'app_name': 'my_app'}},
        Validations().acceptable_command(["init", "my_app"]))


def test_has_elm_binary():
    assert Validations.has_elm_binary()
