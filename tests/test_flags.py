import pytest
from pydantic import ValidationError

from djelm.flags.main import BoolFlag, Flags, FloatFlag, IntFlag, StringFlag


class TestStringFlags:
    def test_dict_flag_succeeds(self):
        d = {"hello": StringFlag}
        SUT = Flags(d)
        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'

    def test_dict_flag_fails(self):
        """
        Values match the flag types
        """
        d = {"hello": StringFlag}
        SUT = Flags(d)
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 12})

    def test_string_flag_passes(self):
        SUT = Flags(StringFlag)
        assert SUT.parse("hello world") == '"hello world"'

    def test_string_flag_fails(self):
        SUT = Flags(StringFlag)
        with pytest.raises(ValidationError):
            SUT.parse(2)

    def test_string_to_elm_data(self):
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
    def test_dict_flag_succeeds(self):
        d = {"hello": IntFlag}
        SUT = Flags(d)
        assert SUT.parse({"hello": 1}) == '{"hello":1}'

    def test_dict_flag_fails(self):
        """
        Values match the flag types
        """
        d = {"hello": IntFlag}
        SUT = Flags(d)
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_int_flag_success(self):
        SUT = Flags(IntFlag)
        assert SUT.parse(242) == "242"

    def test_string_flag_fails(self):
        SUT = Flags(IntFlag)
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_int_to_elm_data(self):
        SUT = Flags(IntFlag)
        assert SUT.to_elm_parser_data() == {
            "alias_type": "Int",
            "decoder_body": "Decode.int",
        }

class TestFloatFlags:
    def test_dict_flag_succeeds(self):
        d = {"hello": FloatFlag}
        SUT = Flags(d)
        assert SUT.parse({"hello": 1.0}) == '{"hello":1}'

    def test_dict_flag_fails(self):
        """
        Values match the flag types
        """
        d = {"hello": FloatFlag}
        SUT = Flags(d)
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_float_flag_success(self):
        SUT = Flags(FloatFlag)
        assert SUT.parse(242.1) == "242.1"

    def test_float_flag_fails(self):
        SUT = Flags(FloatFlag)
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_float_to_elm_data(self):
        SUT = Flags(FloatFlag)
        assert SUT.to_elm_parser_data() == {
            "alias_type": "Float",
            "decoder_body": "Decode.float",
        }

class TestBoolFlags:
    def test_dict_flag_succeeds(self):
        d = {"hello": BoolFlag}
        SUT = Flags(d)
        assert SUT.parse({"hello": True}) == '{"hello":true}'

    def test_dict_flag_fails(self):
        """
        Values match the flag types
        """
        d = {"hello": BoolFlag}
        SUT = Flags(d)
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_bool_flag_success(self):
        SUT = Flags(BoolFlag)
        assert SUT.parse(True) == "true"

    def test_bool_flag_fails(self):
        SUT = Flags(BoolFlag)
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_bool_to_elm_data(self):
        SUT = Flags(BoolFlag)
        assert SUT.to_elm_parser_data() == {
            "alias_type": "Bool",
            "decoder_body": "Decode.bool",
        }
