import pytest

from src.elm.validate import ValidationError, Validations


def test_validate_fails():
    with pytest.raises(ValidationError):
        Validations.acceptable_label("nonsense")


def test_validate_passes():
    assert Validations.acceptable_label("init"), "Passes with init label"


def test_has_elm_binary():
    assert Validations.has_elm_binary()
