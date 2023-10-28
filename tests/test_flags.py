import pytest
from pydantic import ValidationError

from djelm.flags.main import Flags, IntFlag, StringFlag


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
        assert SUT.parse("hello world") == '"hello world"'

    def test_single_flag_fails(self):
        SUT = Flags(StringFlag)
        with pytest.raises(ValidationError):
            SUT.parse(2)

    def test_single_to_elm_data(self):
        SUT = Flags(StringFlag)
        assert SUT.to_elm_parser_data() == {
            "alias_type": "String",
            "decoder_body": "Decode.string",
        }

    def test_dict_to_elm_data(self):
        SUT = Flags({"hello": StringFlag, "world": StringFlag})
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : String
    , world : String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" Decode.string
        |>  required "world" Decode.string""",
        }


class TestIntFlags:
    def test_dict_passes(self):
        d = {"hello": IntFlag}
        SUT = Flags(d)
        assert SUT.parse({"hello": 1}) == '{"hello":1}'

    def test_dict_fails(self):
        """
        Values match the flag types
        """
        d = {"hello": IntFlag}
        SUT = Flags(d)
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_single_flag_passes(self):
        SUT = Flags(IntFlag)
        assert SUT.parse(242) == "242"

    def test_single_flag_fails(self):
        SUT = Flags(IntFlag)
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_single_to_elm_data(self):
        SUT = Flags(IntFlag)
        assert SUT.to_elm_parser_data() == {
            "alias_type": "Int",
            "decoder_body": "Decode.int",
        }
