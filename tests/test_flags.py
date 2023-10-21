import pytest
from pydantic import ValidationError

from djelm.flags.main import Flags, StringFlag


class TestStringFlags:
    def test_dict_passes(self):
        d = {"hello": StringFlag}
        SUT = Flags(d)
        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'

    def test_dict_fails(self):
        """
        Values match the flag types
        """
        d = {"hello": StringFlag}
        SUT = Flags(d)
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 12})

    def test_single_flag_passes(self):
        SUT = Flags(StringFlag)
        assert SUT.parse("hello world") == b'"hello world"'

    def test_single_flag_fails(self):
        SUT = Flags(StringFlag)
        with pytest.raises(ValidationError):
            SUT.parse(2)
