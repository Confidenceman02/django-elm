from src.elm.validate import Validations
from unittest import TestCase
from src.elm.effect import ExitFailure, ExitSuccess


def test_validate_fails_with_invalid_command_verb():
    TestCase().assertIsInstance(Validations().acceptable_command(["nonsense", "my_app"]), ExitFailure)


def test_validate_fails_with_single_command_verb():
    TestCase().assertIsInstance(Validations().acceptable_command(["init"]), ExitFailure)
    TestCase().assertIsInstance(Validations().acceptable_command(["create"]), ExitFailure)


def test_validate_fails_with_too_many_args():
    TestCase().assertIsInstance(Validations().acceptable_command(["list", "nonsense"]), ExitFailure)


def test_validate_command_verb_combo_succeeds():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["init", "my_app"]),
        ExitSuccess
    )


def test_validate_single_command_verb_succeeds():
    TestCase().assertIsInstance(
        Validations().acceptable_command(["list"]),
        ExitSuccess
    )
