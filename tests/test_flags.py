import pytest
from pydantic import ValidationError

from djelm.flags.main import (
    BoolFlag,
    Flags,
    FloatFlag,
    IntFlag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    StringFlag,
)


class TestStringFlags:
    def test_with_object_parser(self):
        d = ObjectFlag({"hello": StringFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 1})

    def test_parser(self):
        SUT = Flags(StringFlag())

        assert SUT.parse("hello world") == '"hello world"'
        with pytest.raises(ValidationError):
            SUT.parse(2)

    def test_to_elm_parser(self):
        SUT = Flags(StringFlag())

        assert SUT.to_elm_parser_data() == {
            "alias_type": "String",
            "decoder_body": "Decode.string",
        }

    def test_with_object_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": StringFlag(), "world": StringFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : String
    , world : String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" Decode.string
        |>  required "world" Decode.string""",
        }


class TestIntFlags:
    def test_with_object_parser(self):
        d = ObjectFlag({"hello": IntFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": 1}) == '{"hello":1}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_int_parser(self):
        SUT = Flags(IntFlag())

        assert SUT.parse(242) == "242"
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_to_elm_parser(self):
        SUT = Flags(IntFlag())

        assert SUT.to_elm_parser_data() == {
            "alias_type": "Int",
            "decoder_body": "Decode.int",
        }

    def test_with_object_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": IntFlag(), "world": IntFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Int
    , world : Int
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" Decode.int
        |>  required "world" Decode.int""",
        }


class TestFloatFlags:
    def test_with_object_parser(self):
        d = ObjectFlag({"hello": FloatFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": 1.0}) == '{"hello":1.0}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_parser(self):
        SUT = Flags(FloatFlag())

        assert SUT.parse(242.1) == "242.1"
        assert SUT.parse(22) == "22.0"
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_to_elm_parser(self):
        SUT = Flags(FloatFlag())

        assert SUT.to_elm_parser_data() == {
            "alias_type": "Float",
            "decoder_body": "Decode.float",
        }

    def test_with_object_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": FloatFlag(), "world": FloatFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Float
    , world : Float
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" Decode.float
        |>  required "world" Decode.float""",
        }


class TestNullableFlags:
    def test_with_string_parser(self):
        d = NullableFlag(StringFlag())
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse("Hello") == '"Hello"'
        with pytest.raises(ValidationError):
            SUT.parse(22)

    def test_with_int_parser(self):
        d = NullableFlag(IntFlag())
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse(22) == "22"
        with pytest.raises(ValidationError):
            SUT.parse("22")

    def test_with_float_parser(self):
        d = NullableFlag(FloatFlag())
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse(22.2) == "22.2"
        with pytest.raises(ValidationError):
            SUT.parse("22.2")

    def test_with_bool_parser(self):
        d = NullableFlag(BoolFlag())
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse(True) == "true"
        with pytest.raises(ValidationError):
            SUT.parse("True")

    def test_with_object_parser(self):
        d = NullableFlag(ObjectFlag({"hello": StringFlag()}))
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(ValidationError):
            SUT.parse({})

    def test_with_object_with_object_parser(self):
        d = NullableFlag(ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})}))
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse({"hello": {"world": "hi"}}) == '{"hello":{"world":"hi"}}'
        with pytest.raises(ValidationError):
            SUT.parse({})

    def test_with_list_with_object_parser(self):
        d = NullableFlag(ListFlag(ObjectFlag({"hello": StringFlag()})))
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse([{"hello": "world"}]) == '[{"hello":"world"}]'
        with pytest.raises(ValidationError):
            SUT.parse({})

    def test_with_list_with_string_parser(self):
        d = NullableFlag(ListFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert SUT.parse(["hello", "world"]) == '["hello","world"]'
        with pytest.raises(ValidationError):
            SUT.parse({})
        with pytest.raises(ValidationError):
            SUT.parse("[]")

    def test_with_string_to_elm_parser(self):
        d = NullableFlag(StringFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe String)""",
            "decoder_body": """(Decode.nullable Decode.string)""",
        }

    def test_with_int_to_elm_parser(self):
        d = NullableFlag(IntFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe Int)""",
            "decoder_body": """(Decode.nullable Decode.int)""",
        }

    def test_with_float_to_elm_parser(self):
        d = NullableFlag(FloatFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe Float)""",
            "decoder_body": """(Decode.nullable Decode.float)""",
        }

    def test_with_bool_to_elm_parser(self):
        d = NullableFlag(BoolFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe Bool)""",
            "decoder_body": """(Decode.nullable Decode.bool)""",
        }

    def test_with_list_with_string_to_elm_parser(self):
        d = NullableFlag(ListFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe (List String))""",
            "decoder_body": """(Decode.nullable (Decode.list Decode.string))""",
        }

    def test_with_object_with_string_to_elm_parser(self):
        d = NullableFlag(ObjectFlag({"hello": StringFlag()}))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe InlineToModel_)

type alias InlineToModel_ =
    { hello : String
    }""",
            "decoder_body": """(Decode.nullable inlineToModel_Decoder)

inlineToModel_Decoder : Decode.Decoder InlineToModel_
inlineToModel_Decoder =
    Decode.succeed InlineToModel_
        |>  required "hello" Decode.string""",
        }

    def test_with_object_with_object_to_elm_parser(self):
        d = NullableFlag(ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})}))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe InlineToModel_)

type alias InlineToModel_ =
    { hello : Hello__
    }

type alias Hello__ =
    { world : String
    }""",
            "decoder_body": """(Decode.nullable inlineToModel_Decoder)

inlineToModel_Decoder : Decode.Decoder InlineToModel_
inlineToModel_Decoder =
    Decode.succeed InlineToModel_
        |>  required "hello" hello__Decoder

hello__Decoder : Decode.Decoder Hello__
hello__Decoder =
    Decode.succeed Hello__
        |>  required "world" Decode.string""",
        }

    def test_with_nullable_with_string_to_elm_parser(self):
        d = NullableFlag(NullableFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe (Maybe String))""",
            "decoder_body": """(Decode.nullable (Decode.nullable Decode.string))""",
        }

    def test_with_nullable_with_int_to_elm_parser(self):
        d = NullableFlag(NullableFlag(IntFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe (Maybe Int))""",
            "decoder_body": """(Decode.nullable (Decode.nullable Decode.int))""",
        }

    def test_with_nullable_with_bool_to_elm_parser(self):
        d = NullableFlag(NullableFlag(BoolFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe (Maybe Bool))""",
            "decoder_body": """(Decode.nullable (Decode.nullable Decode.bool))""",
        }

    def test_with_nullable_with_float_tol_elm_parser(self):
        d = NullableFlag(NullableFlag(FloatFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe (Maybe Float))""",
            "decoder_body": """(Decode.nullable (Decode.nullable Decode.float))""",
        }

    def test_with_nullable_with_list_to_elm_parser(self):
        d = NullableFlag(NullableFlag(ListFlag(StringFlag())))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(Maybe (Maybe (List String)))""",
            "decoder_body": """(Decode.nullable (Decode.nullable (Decode.list Decode.string)))""",
        }


class TestListFlags:
    def test_with_object_parser(self):
        d = ObjectFlag({"hello": ListFlag(StringFlag())})
        SUT = Flags(d)

        assert SUT.parse({"hello": ["world"]}) == '{"hello":["world"]}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 1})

    def test_with_string_parser(self):
        d = ListFlag(StringFlag())
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse(["Hello"]) == '["Hello"]'
        with pytest.raises(ValidationError):
            SUT.parse(22)

    def test_with_int_parser(self):
        d = ListFlag(IntFlag())
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse([22]) == "[22]"
        with pytest.raises(ValidationError):
            SUT.parse(["22"])

    def test_with_float_parser(self):
        d = ListFlag(FloatFlag())
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse([22.2]) == "[22.2]"
        with pytest.raises(ValidationError):
            SUT.parse(["22.2"])

    def test_with_bool_parser(self):
        d = ListFlag(BoolFlag())
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse([True]) == "[true]"
        with pytest.raises(ValidationError):
            SUT.parse(["True"])

    def test_with_nullable_with_string_parser(self):
        d = ListFlag(NullableFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse([None, "hello"]) == '[null,"hello"]'
        with pytest.raises(ValidationError):
            SUT.parse([None, 123])

    def test_with_list_with_float_parser(self):
        d = ListFlag(ListFlag(FloatFlag()))
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse([[11.2]]) == "[[11.2]]"
        with pytest.raises(ValidationError):
            SUT.parse([["11.2"]])

    def test_with_object_with_string_parser(self):
        d = ListFlag(ObjectFlag({"hello": StringFlag()}))
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert SUT.parse([{"hello": "world"}]) == '[{"hello":"world"}]'
        with pytest.raises(ValidationError):
            SUT.parse([{}])

    def test_with_string_to_elm_parser(self):
        d = ListFlag(StringFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List String)""",
            "decoder_body": """(Decode.list Decode.string)""",
        }

    def test_with_int_to_elm_parser(self):
        d = ListFlag(IntFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List Int)""",
            "decoder_body": """(Decode.list Decode.int)""",
        }

    def test_with_float_to_elm_parser(self):
        d = ListFlag(FloatFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List Float)""",
            "decoder_body": """(Decode.list Decode.float)""",
        }

    def test_with_bool_to_elm_parser(self):
        d = ListFlag(BoolFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List Bool)""",
            "decoder_body": """(Decode.list Decode.bool)""",
        }

    def test_with_object_to_elm_parser(self):
        d = ListFlag(ObjectFlag({"hello": StringFlag()}))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List InlineToModel_)

type alias InlineToModel_ =
    { hello : String
    }""",
            "decoder_body": """(Decode.list inlineToModel_Decoder)

inlineToModel_Decoder : Decode.Decoder InlineToModel_
inlineToModel_Decoder =
    Decode.succeed InlineToModel_
        |>  required "hello" Decode.string""",
        }

    def test_with_nullable_with_string_to_elm_parser(self):
        d = ListFlag(NullableFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List (Maybe String))""",
            "decoder_body": """(Decode.list (Decode.nullable Decode.string))""",
        }

    def test_with_nullable_with_int_to_elm_parser(self):
        d = ListFlag(NullableFlag(IntFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List (Maybe Int))""",
            "decoder_body": """(Decode.list (Decode.nullable Decode.int))""",
        }

    def test_with_nullable_with_bool_to_elm_parser(self):
        d = ListFlag(NullableFlag(BoolFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List (Maybe Bool))""",
            "decoder_body": """(Decode.list (Decode.nullable Decode.bool))""",
        }

    def test_with_nullable_with_float_to_elm_parser(self):
        d = ListFlag(NullableFlag(FloatFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List (Maybe Float))""",
            "decoder_body": """(Decode.list (Decode.nullable Decode.float))""",
        }

    def test_with_nullable_with_list_to_elm_parser(self):
        d = ListFlag(NullableFlag(ListFlag(StringFlag())))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """(List (Maybe (List String)))""",
            "decoder_body": """(Decode.list (Decode.nullable (Decode.list Decode.string)))""",
        }


class TestBoolFlags:
    def test_with_object_parser(self):
        d = ObjectFlag({"hello": BoolFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": True}) == '{"hello":true}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_bool_parser(self):
        SUT = Flags(BoolFlag())

        assert SUT.parse(True) == "true"
        with pytest.raises(ValidationError):
            SUT.parse("hello world")

    def test_bool_to_elm_parser(self):
        SUT = Flags(BoolFlag())

        assert SUT.to_elm_parser_data() == {
            "alias_type": "Bool",
            "decoder_body": "Decode.bool",
        }

    def test_with_object_with_bool_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": BoolFlag(), "world": BoolFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Bool
    , world : Bool
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" Decode.bool
        |>  required "world" Decode.bool""",
        }


class TestObjectFlags:
    def test_with_mix_parser(self):
        d = ObjectFlag(
            {
                "hello": ObjectFlag({"world": StringFlag()}),
                "someList": ListFlag(StringFlag()),
            }
        )
        SUT = Flags(d)

        assert (
                SUT.parse({"hello": {"world": "I'm here"}, "someList": ["hello", "world"]})
                == '{"hello":{"world":"I\'m here"},"someList":["hello","world"]}'
        )
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 22})

    def test_with_string_parser(self):
        d = ObjectFlag({"hello": StringFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 22})

    def test_with_object_with_string_parser(self):
        d = ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})})
        SUT = Flags(d)

        assert (
                SUT.parse({"hello": {"world": "I have arrived"}})
                == '{"hello":{"world":"I have arrived"}}'
        )
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 22})

    def test_with_int_parser(self):
        d = ObjectFlag({"hello": IntFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": 22}) == '{"hello":22}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "22"})

    def test_with_object_with_int_parser(self):
        d = ObjectFlag({"hello": ObjectFlag({"world": IntFlag()})})
        SUT = Flags(d)

        assert SUT.parse({"hello": {"world": 22}}) == '{"hello":{"world":22}}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": {"world": "22"}})

    def test_with_float_parser(self):
        d = ObjectFlag({"hello": FloatFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": 22.22}) == '{"hello":22.22}'
        assert SUT.parse({"hello": 22}) == '{"hello":22}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "22.22"})

    def test_with_object_with_float_parser(self):
        d = ObjectFlag({"hello": ObjectFlag({"world": FloatFlag()})})
        SUT = Flags(d)

        assert SUT.parse({"hello": {"world": 22.22}}) == '{"hello":{"world":22.22}}'
        assert SUT.parse({"hello": {"world": 22}}) == '{"hello":{"world":22}}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": {"world": "22.22"}})

    def test_with_bool_parser(self):
        d = ObjectFlag({"hello": BoolFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": True}) == '{"hello":true}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "True"})

    def test_with_object_with_bool_parser(self):
        d = ObjectFlag({"hello": ObjectFlag({"world": BoolFlag()})})
        SUT = Flags(d)

        assert SUT.parse({"hello": {"world": True}}) == '{"hello":{"world":true}}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": {"world": "True"}})

    def test_with_nullable_parser(self):
        d = ObjectFlag({"hello": NullableFlag(StringFlag())})
        SUT = Flags(d)

        assert SUT.parse({"hello": None}) == '{"hello":null}'
        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(ValidationError):
            SUT.parse({})

    def test_with_nullable_with_nullable_with_string(self):
        d = ObjectFlag({"hello": NullableFlag(NullableFlag(StringFlag()))})
        SUT = Flags(d)

        assert SUT.parse({"hello": None}) == '{"hello":null}'
        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(ValidationError):
            SUT.parse(22)

    def test_with_list_with_object_with_string_parser(self):
        d = ObjectFlag({"hello": ListFlag(ObjectFlag({"world": StringFlag()}))})
        SUT = Flags(d)

        assert (
                SUT.parse({"hello": [{"world": "I have arrived"}]})
                == '{"hello":[{"world":"I have arrived"}]}'
        )
        with pytest.raises(ValidationError):
            SUT.parse({"hello": "world"})

    def test_with_list_with_list_with_string_parser(self):
        d = ObjectFlag({"hello": ListFlag(ListFlag(StringFlag()))})
        SUT = Flags(d)

        assert SUT.parse({"hello": [["world"]]}) == '{"hello":[["world"]]}'
        assert SUT.parse({"hello": []}) == '{"hello":[]}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": ["world"]})

    def test_with_list_with_nullable_with_string_parser(self):
        d = ObjectFlag({"hello": ListFlag(NullableFlag(StringFlag()))})
        SUT = Flags(d)

        assert SUT.parse({"hello": [None]}) == '{"hello":[null]}'
        assert SUT.parse({"hello": ["null"]}) == '{"hello":["null"]}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": [22]})

    def test_with_mix_to_elm_parser(self):
        d = ObjectFlag(
            {
                "hello": ObjectFlag({"world": StringFlag()}),
                "someList": ListFlag(StringFlag()),
            }
        )
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Hello_
    , someList : List String
    }

type alias Hello_ =
    { world : String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" hello_Decoder
        |>  required "someList" (Decode.list Decode.string)

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |>  required "world" Decode.string""",
        }

    def test_with_list_with_nullable_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": ListFlag(NullableFlag(StringFlag()))})
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : (List (Maybe String))
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.list (Decode.nullable Decode.string))""",
        }

    def test_with_list_with_list_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": ListFlag(ListFlag(StringFlag()))})
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : (List (List String))
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.list (Decode.list Decode.string))""",
        }

    def test_with_object_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})})
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Hello_
    }

type alias Hello_ =
    { world : String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" hello_Decoder

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |>  required "world" Decode.string""",
        }

    def test_with_list_with_object_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": ListFlag(ObjectFlag({"world": StringFlag()}))})
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : (List Hello_)
    }

type alias Hello_ =
    { world : String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.list hello_Decoder)

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |>  required "world" Decode.string""",
        }

    def test_with_list_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": ListFlag(StringFlag())})
        SUT = Flags(d)
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : (List String)
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.list Decode.string)""",
        }

    def test_with_nullable_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": NullableFlag(StringFlag())})
        SUT = Flags(d)
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Maybe String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.nullable Decode.string)""",
        }

    def test_with_nullable_with_int_to_elm_parser(self):
        d = ObjectFlag({"hello": NullableFlag(IntFlag())})
        SUT = Flags(d)
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Maybe Int
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.nullable Decode.int)""",
        }

    def test_with_nullable_with_nullable_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": NullableFlag(NullableFlag(StringFlag()))})
        SUT = Flags(d)
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Maybe (Maybe String)
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.nullable (Decode.nullable Decode.string))""",
        }

    def test_with_nullable_with_object_to_elm_parser(self):
        d = ObjectFlag({"hello": NullableFlag(ObjectFlag({"hello": StringFlag()}))})
        SUT = Flags(d)
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Maybe Hello_
    }

type alias Hello_ =
    { hello : String
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.nullable hello_Decoder)

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |>  required "hello" Decode.string""",
        }

    def test_with_nullable_with_list_with_string_to_elm_parser(self):
        d = ObjectFlag({"hello": NullableFlag(ListFlag(StringFlag()))})
        SUT = Flags(d)
        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Maybe (List String)
    }""",
            "decoder_body": """Decode.succeed ToModel
        |>  required "hello" (Decode.nullable (Decode.list Decode.string))""",
        }
