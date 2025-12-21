import os
from django import forms
from djelm.effect import ExitSuccess
import pytest
from django.core.management.base import LabelCommand
from pydantic import ValidationError

from djelm.elm import Elm
from djelm.flags.form.primitives import (
    ModelChoiceFieldFlag,
    ModelMultipleChoiceFieldFlag,
)
from djelm.flags.primitives import (
    AliasFlag,
    BoolFlag,
    CustomTypeFlag,
    FloatFlag,
    IntFlag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    StringFlag,
)
from djelm.flags.main import Flags
from djelm.generators import ModelGenerator
from djelm.strategy import GenerateModelStrategy
from djelm.utils import get_app_src_path
from test_programs.models import (
    Blank,
    Extra,
    BlankM,
    Blanks,
    Car,
    Driver,
    Enthusiast,
    Extra01,
    Team,
)
from tests.conftest import cleanup_models
from tests.fuzz_flags import fuzz_flag


def elm_module_content(name: str) -> str:
    return f"""module {name} exposing (..)

import Browser
import Html exposing (Html, div, text)
import Json.Decode exposing (decodeValue)
import Json.Encode exposing (Value)
import Models.{name} exposing (ToModel, toModel)


type Msg
    = Increment
    | Decrement


type Model
    = Ready ToModel
    | Error


init : Value -> ( Model, Cmd Msg )
init f =
    case decodeValue toModel f of
        Ok m ->
            ( Ready m, Cmd.none )

        Err _ ->
            ( Error, Cmd.none )


main : Program Value Model Msg
main =
    Browser.element
        {{ init = init
        , update = update
        , view = view
        , subscriptions = subscriptions
        }}


subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none


update : Msg -> Model -> ( Model, Cmd Msg )
update _ model =
    ( model, Cmd.none )


view : Model -> Html Msg
view model =
    case model of
        Ready _ ->
            div []
                [ text "{name} test"
                ]

        _ ->
            text ""
"""


@pytest.fixture()
def basic_form():
    class UserForm(forms.ModelForm):
        car = forms.ModelChoiceField(
            queryset=Car.objects.all(),
            help_text="Do I detect.. Elm?",
        )

        extras = forms.ModelMultipleChoiceField(
            queryset=Extra.objects.all(),
            help_text="Do I detect.. Multiple Elm's?",
        )

        class Meta:  # type:ignore
            model = Enthusiast
            fields = ("username", "extras")

    return UserForm


@pytest.fixture()
def basic_form_no_empty_label():
    class UserForm(forms.ModelForm):
        car = forms.ModelChoiceField(
            queryset=Car.objects.all(), help_text="Do I detect.. Elm?", empty_label=None
        )
        extras = forms.ModelMultipleChoiceField(
            queryset=Extra.objects.all(),
            help_text="Do I detect.. Multiple Elm's?",
        )

        extras01 = forms.ModelMultipleChoiceField(
            queryset=Extra01.objects.all(),
            help_text="Do I detect.. Multiple Elm's?",
        )

        class Meta:  # type:ignore
            model = Enthusiast
            fields = ("username",)

    return UserForm


@pytest.fixture()
def basic_team_form():
    class UserForm(forms.ModelForm):
        driver = forms.ModelChoiceField(
            queryset=Driver.objects.all(),
            help_text="Do I detect.. Elm?",
            empty_label=None,
        )
        extras = forms.ModelMultipleChoiceField(
            queryset=Extra.objects.all(),
            help_text="Do I detect.. Multiple Elm's?",
        )

        class Meta:  # type:ignore
            model = Team
            fields = ("driver",)

    return UserForm


@pytest.fixture()
def blanks_form():
    class UserForm(forms.ModelForm):
        blank = forms.ModelChoiceField(
            queryset=Blank.objects.all(),
            help_text="SOS",
            empty_label=None,
        )
        blanks = forms.ModelMultipleChoiceField(
            queryset=BlankM.objects.all(),
            help_text="SOS Multi",
        )

        class Meta:  # type:ignore
            model = Blanks
            fields = ("blank", "blanks")

    return UserForm


def test_program_fuzzer():
    app_name = "test_programs"
    src_path = get_app_src_path(app_name).value  # type:ignore

    programs = []

    for i in range(1, 20):
        flags = fuzz_flag()

        class MockHandler(ModelGenerator):
            def load_flags(  # type:ignore
                self,
                app_path: str,
                program_name: str,
                from_source: bool,
                watch_mode: bool,
                logger,
            ):
                f = Flags(flags)
                return ExitSuccess(f)

        class MockGenerateModel(GenerateModelStrategy):
            def __init__(self, app_name, prog_name) -> None:
                super().__init__(app_name, prog_name, MockHandler(), False, False)

            def generate(self):
                self.run(LabelCommand().stdout)

        # Create files
        file = open(os.path.join(src_path, "src", "Models", f"Main{i}.elm"), "w")
        module = open(os.path.join(src_path, "src", f"Main{i}.elm"), "w")
        module.write(elm_module_content(f"Main{i}"))
        file.close()
        module.close()

        MockGenerateModel(app_name, f"Main{i}").generate()
        programs.append(f"src/Main{i}.elm")

    try:
        Elm().command(["make", *programs, "--output=/dev/null"], src_path)
    except Exception:
        pytest.fail("An elm program did not compile")

    assert True

    cleanup_models(app_name)


class TestFuzzExamplesGenerated:
    """This example was generated with a fuzz generator"""

    def test_fuzz_failure_01(self):
        d = ObjectFlag(
            {
                "yh": ObjectFlag(
                    {
                        "dFE3": NullableFlag(
                            NullableFlag(
                                ObjectFlag(
                                    {
                                        "k69xy": NullableFlag(NullableFlag(IntFlag())),
                                    }
                                )
                            )
                        ),
                    }
                )
            }
        )
        SUT = Flags(d)
        assert SUT.to_elm_parser_data()["alias_type"] == (
            """{ yh : Yh_
    }

type alias Yh_ =
    { dFE3 : Maybe (Maybe Yh_DFE3__) }

type alias Yh_DFE3__ =
    { k69xy : Maybe (Maybe Int) }"""
        )
        assert SUT.to_elm_parser_data()["decoder_body"] == (
            """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "yh" yh_Decoder

yh_Decoder : Decode.Decoder Yh_
yh_Decoder =
    Decode.succeed Yh_
        |> required "dFE3" (Decode.nullable (Decode.nullable yh_dFE3__Decoder))

yh_dFE3__Decoder : Decode.Decoder Yh_DFE3__
yh_dFE3__Decoder =
    Decode.succeed Yh_DFE3__
        |> required "k69xy" (Decode.nullable (Decode.nullable Decode.int))"""
        )

    def test_fuzz_failure_02(self):
        d = ObjectFlag(
            {
                "zJc": BoolFlag(),
                "dEB": ListFlag(
                    ListFlag(
                        NullableFlag(
                            ObjectFlag({"z": NullableFlag(ListFlag(BoolFlag()))})
                        )
                    )
                ),
                "dKfU": ListFlag(NullableFlag(BoolFlag())),
            }
        )
        SUT = Flags(d)

        assert SUT.to_elm_parser_data()["decoder_body"] == (
            """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "zJc" Decode.bool
        |> required "dEB" (Decode.list (Decode.list (Decode.nullable dEB_Decoder)))
        |> required "dKfU" (Decode.list (Decode.nullable Decode.bool))

dEB_Decoder : Decode.Decoder DEB_
dEB_Decoder =
    Decode.succeed DEB_
        |> required "z" (Decode.nullable (Decode.list Decode.bool))"""
        )

    def test_fuzz_failure_03(self):
        """Compiler error: NAME CLASH - This file defines multiple `Options__` types."""
        d = ObjectFlag(
            {
                "a": ObjectFlag({"options": ObjectFlag({"name": StringFlag()})}),
                "b": ListFlag(
                    ObjectFlag({"options": ObjectFlag({"name": StringFlag()})})
                ),
            }
        )
        SUT = Flags(d)

        # Alias type
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """{ a : A_
    , b : List B_
    }

type alias A_ =
    { options : A_Options__ }

type alias A_Options__ =
    { name : String }

type alias B_ =
    { options : B_Options__ }

type alias B_Options__ =
    { name : String }"""
        )

        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "a" a_Decoder
        |> required "b" (Decode.list b_Decoder)

a_Decoder : Decode.Decoder A_
a_Decoder =
    Decode.succeed A_
        |> required "options" a_options__Decoder

a_options__Decoder : Decode.Decoder A_Options__
a_options__Decoder =
    Decode.succeed A_Options__
        |> required "name" Decode.string

b_Decoder : Decode.Decoder B_
b_Decoder =
    Decode.succeed B_
        |> required "options" b_options__Decoder

b_options__Decoder : Decode.Decoder B_Options__
b_options__Decoder =
    Decode.succeed B_Options__
        |> required "name" Decode.string"""
        )

    def test_fuzz_failure_04(self):
        """Compiler error: RESERVED WORD - using keyword if."""
        d = ObjectFlag(
            {
                "if": StringFlag(),
            }
        )

        with pytest.raises(Exception):
            Flags(d)


class TestAliasFlags:
    @pytest.mark.parametrize(
        "flag,expected",
        [
            (
                AliasFlag("SomeAlias", ObjectFlag({"hello": StringFlag()})),
                {
                    "alias_type": """SomeAlias_

type alias SomeAlias_ =
    { hello : String }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    someAlias_Decoder

someAlias_Decoder : Decode.Decoder SomeAlias_
someAlias_Decoder =
    Decode.succeed SomeAlias_
        |> required "hello" Decode.string""",
                },
            ),
            (
                AliasFlag(
                    "SomeAlias",
                    ObjectFlag(
                        {"hello": CustomTypeFlag(variants=[("Hello", StringFlag())])}
                    ),
                ),
                {
                    "alias_type": """SomeAlias_

type alias SomeAlias_ =
    { hello : SomeAlias_Hello__ }

type SomeAlias_Hello__
    = Hello String
""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    someAlias_Decoder

someAlias_Decoder : Decode.Decoder SomeAlias_
someAlias_Decoder =
    Decode.succeed SomeAlias_
        |> required "hello" (Decode.oneOf [Decode.map Hello Decode.string])""",
                },
            ),
            (
                ObjectFlag(
                    {
                        "messages": AliasFlag(
                            "Status",
                            CustomTypeFlag(variants=[("Hello", StringFlag())]),
                        )
                    }
                ),
                {
                    "alias_type": """{ messages : Status_
    }

type Status_
    = Hello String
""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "messages" (Decode.oneOf [Decode.map Hello Decode.string])""",
                },
            ),
            (
                AliasFlag(
                    "SomeAlias",
                    CustomTypeFlag(variants=[("Hello", StringFlag())]),
                ),
                {
                    "alias_type": """SomeAlias_

type SomeAlias_
    = Hello String
""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Hello Decode.string])""",
                },
            ),
            (
                ObjectFlag(
                    {
                        "some_field": AliasFlag(
                            "Field",
                            ObjectFlag({"value": StringFlag(), "scope": StringFlag()}),
                        ),
                        "some_other_field": AliasFlag(
                            "Field",
                            ObjectFlag({"value": StringFlag(), "scope": StringFlag()}),
                        ),
                    }
                ),
                {
                    "alias_type": """{ some_field : Field_
    , some_other_field : Field_
    }

type alias Field_ =
    { value : String
    , scope : String
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "some_field" field_Decoder
        |> required "some_other_field" field_Decoder

field_Decoder : Decode.Decoder Field_
field_Decoder =
    Decode.succeed Field_
        |> required "value" Decode.string
        |> required "scope" Decode.string""",
                },
            ),
        ],
    )
    def test_to_elm_parser_data_success(self, flag, expected):
        SUT = Flags(flag)
        assert SUT.to_elm_parser_data() == expected


class TestStringFlags:
    def test_with_object_parser(self):
        d = ObjectFlag({"hello": StringFlag()})
        SUT = Flags(d)

        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(ValidationError):
            SUT.parse({"hello": 1})

    def test_with_object_parser_literal(self):
        d = ObjectFlag({"hello": StringFlag(literal="world")})
        SUT = Flags(d)

        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'
        with pytest.raises(Exception):
            SUT.parse({"hello": "World"})

    def test_parser(self):
        SUT = Flags(StringFlag())

        assert SUT.parse("hello world") == '"hello world"'
        with pytest.raises(ValidationError):
            SUT.parse(2)

    def test_parser_with_literal(self):
        SUT = Flags(StringFlag(literal="Hello"))

        assert SUT.parse("Hello") == '"Hello"'
        with pytest.raises(Exception):
            SUT.parse("hello")

    def test_to_elm_parser_with_literal(self):
        SUT = Flags(StringFlag(literal="hello"))

        assert SUT.to_elm_parser_data() == {
            "alias_type": "String",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.string |> Decode.andThen (\\lit -> if lit == "hello" then Decode.succeed "hello" else Decode.fail "Value did not match literal <hello>\"))"""
            "",
        }

    def test_to_elm_parser(self):
        SUT = Flags(StringFlag())

        assert SUT.to_elm_parser_data() == {
            "alias_type": "String",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.string""",
        }

    def test_with_object_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": StringFlag(), "world": StringFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : String
    , world : String
    }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" Decode.string
        |> required "world" Decode.string""",
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
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.int""",
        }

    def test_with_object_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": IntFlag(), "world": IntFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Int
    , world : Int
    }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" Decode.int
        |> required "world" Decode.int""",
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
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.float""",
        }

    def test_with_object_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": FloatFlag(), "world": FloatFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Float
    , world : Float
    }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" Decode.float
        |> required "world" Decode.float""",
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

    @pytest.mark.django_db
    def test_with_model_choice_field_parser(self, basic_form):
        prepared = basic_form()
        d = NullableFlag(ModelChoiceFieldFlag())
        SUT = Flags(d)

        assert SUT.parse(None) == "null"
        assert (
            SUT.parse(prepared["car"])
            == '{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"---------","value":"","selected":true}]}'
        )

        try:
            SUT.parse({})
        except Exception:
            assert True
            return
        pytest.fail("Illegal input should raise error")

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
            "alias_type": """Maybe String""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable Decode.string)""",
        }

    def test_with_int_to_elm_parser(self):
        d = NullableFlag(IntFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe Int""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable Decode.int)""",
        }

    def test_with_float_to_elm_parser(self):
        d = NullableFlag(FloatFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe Float""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable Decode.float)""",
        }

    def test_with_bool_to_elm_parser(self):
        d = NullableFlag(BoolFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe Bool""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable Decode.bool)""",
        }

    def test_with_list_with_string_to_elm_parser(self):
        d = NullableFlag(ListFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe (List String)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable (Decode.list Decode.string))""",
        }

    def test_with_object_with_string_to_elm_parser(self):
        d = NullableFlag(ObjectFlag({"hello": StringFlag()}))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe InlineToModel_

type alias InlineToModel_ =
    { hello : String }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable inlineToModel_Decoder)

inlineToModel_Decoder : Decode.Decoder InlineToModel_
inlineToModel_Decoder =
    Decode.succeed InlineToModel_
        |> required "hello" Decode.string""",
        }

    def test_with_object_with_object_to_elm_parser(self):
        d = NullableFlag(ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})}))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe InlineToModel_

type alias InlineToModel_ =
    { hello : Hello__ }

type alias Hello__ =
    { world : String }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable inlineToModel_Decoder)

inlineToModel_Decoder : Decode.Decoder InlineToModel_
inlineToModel_Decoder =
    Decode.succeed InlineToModel_
        |> required "hello" hello__Decoder

hello__Decoder : Decode.Decoder Hello__
hello__Decoder =
    Decode.succeed Hello__
        |> required "world" Decode.string""",
        }

    def test_with_nullable_with_string_to_elm_parser(self):
        d = NullableFlag(NullableFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe (Maybe String)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable (Decode.nullable Decode.string))""",
        }

    def test_with_nullable_with_int_to_elm_parser(self):
        d = NullableFlag(NullableFlag(IntFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe (Maybe Int)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable (Decode.nullable Decode.int))""",
        }

    def test_with_nullable_with_bool_to_elm_parser(self):
        d = NullableFlag(NullableFlag(BoolFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe (Maybe Bool)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable (Decode.nullable Decode.bool))""",
        }

    def test_with_nullable_with_float_tol_elm_parser(self):
        d = NullableFlag(NullableFlag(FloatFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe (Maybe Float)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable (Decode.nullable Decode.float))""",
        }

    def test_with_nullable_with_list_to_elm_parser(self):
        d = NullableFlag(NullableFlag(ListFlag(StringFlag())))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """Maybe (Maybe (List String))""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.nullable (Decode.nullable (Decode.list Decode.string)))""",
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

    @pytest.mark.django_db
    def test_with_model_choice_field_parser(self, basic_form):
        prepared = basic_form()
        d = ListFlag(ModelChoiceFieldFlag())
        SUT = Flags(d)

        assert SUT.parse([]) == "[]"
        assert (
            SUT.parse([prepared["car"]])
            == '[{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"---------","value":"","selected":true}]}]'
        )

        try:
            SUT.parse({})
        except Exception:
            assert True
            return
        pytest.fail("Illegal input should raise error")

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
            "alias_type": """List String""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list Decode.string)""",
        }

    def test_with_int_to_elm_parser(self):
        d = ListFlag(IntFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List Int""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list Decode.int)""",
        }

    def test_with_float_to_elm_parser(self):
        d = ListFlag(FloatFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List Float""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list Decode.float)""",
        }

    def test_with_bool_to_elm_parser(self):
        d = ListFlag(BoolFlag())
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List Bool""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list Decode.bool)""",
        }

    def test_with_object_to_elm_parser(self):
        d = ListFlag(ObjectFlag({"hello": StringFlag()}))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List InlineToModel_

type alias InlineToModel_ =
    { hello : String }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list inlineToModel_Decoder)

inlineToModel_Decoder : Decode.Decoder InlineToModel_
inlineToModel_Decoder =
    Decode.succeed InlineToModel_
        |> required "hello" Decode.string""",
        }

    def test_with_nullable_with_string_to_elm_parser(self):
        d = ListFlag(NullableFlag(StringFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List (Maybe String)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list (Decode.nullable Decode.string))""",
        }

    def test_with_nullable_with_int_to_elm_parser(self):
        d = ListFlag(NullableFlag(IntFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List (Maybe Int)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list (Decode.nullable Decode.int))""",
        }

    def test_with_nullable_with_bool_to_elm_parser(self):
        d = ListFlag(NullableFlag(BoolFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List (Maybe Bool)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list (Decode.nullable Decode.bool))""",
        }

    def test_with_nullable_with_float_to_elm_parser(self):
        d = ListFlag(NullableFlag(FloatFlag()))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List (Maybe Float)""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list (Decode.nullable Decode.float))""",
        }

    def test_with_nullable_with_list_to_elm_parser(self):
        d = ListFlag(NullableFlag(ListFlag(StringFlag())))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List (Maybe (List String))""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list (Decode.nullable (Decode.list Decode.string)))""",
        }

    def test_with_custom_type_flag_to_elm_parser(self):
        d = ListFlag(CustomTypeFlag(variants=[("Car", StringFlag())]))
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """List InlineToModel_

type InlineToModel_
    = Car String
""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    (Decode.list (Decode.oneOf [Decode.map Car Decode.string]))""",
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
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.bool""",
        }

    def test_with_object_with_bool_to_elm_parser(self):
        SUT = Flags(ObjectFlag({"hello": BoolFlag(), "world": BoolFlag()}))

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ hello : Bool
    , world : Bool
    }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" Decode.bool
        |> required "world" Decode.bool""",
        }


class TestObjectFlags:
    @pytest.mark.parametrize("flag", [(ObjectFlag({"hello$": StringFlag()}))])
    def test_instance_errors(self, flag):
        with pytest.raises(ValidationError):
            Flags(flag)

    @pytest.mark.parametrize(
        "flag,value,error_value,expected",
        [
            (
                ObjectFlag({"hello\n": StringFlag()}),
                {"hello": "world"},
                {"hello": 2},
                '{"hello":"world"}',
            ),
            (
                ObjectFlag(
                    {
                        "hello": ObjectFlag({"world": StringFlag()}),
                        "someList": ListFlag(StringFlag()),
                    }
                ),
                {"hello": {"world": "I'm here"}, "someList": ["hello", "world"]},
                {"hello": 2},
                '{"hello":{"world":"I\'m here"},"someList":["hello","world"]}',
            ),
            (
                ObjectFlag({"hello": StringFlag()}),
                {"hello": "world"},
                {"hello": 2},
                '{"hello":"world"}',
            ),
            (
                ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})}),
                {"hello": {"world": "I have arrived"}},
                {"hello": 22},
                '{"hello":{"world":"I have arrived"}}',
            ),
            (
                ObjectFlag({"hello": IntFlag()}),
                {"hello": 22},
                {"hello": "22"},
                '{"hello":22}',
            ),
            (
                ObjectFlag({"hello": ObjectFlag({"world": IntFlag()})}),
                {"hello": {"world": 22}},
                {"hello": {"world": "22"}},
                '{"hello":{"world":22}}',
            ),
            (
                ObjectFlag({"hello": FloatFlag()}),
                {"hello": 22.22},
                {"hello": {"world": "22.22"}},
                '{"hello":22.22}',
            ),
            (
                ObjectFlag({"hello": FloatFlag()}),
                {"hello": 22},
                {"hello": {"world": "22.22"}},
                '{"hello":22.0}',
            ),
            (
                ObjectFlag({"hello": ObjectFlag({"world": FloatFlag()})}),
                {"hello": {"world": 22.22}},
                {"hello": {"world": "22.22"}},
                '{"hello":{"world":22.22}}',
            ),
            (
                ObjectFlag({"hello": ObjectFlag({"world": FloatFlag()})}),
                {"hello": {"world": 22}},
                {"hello": {"world": "22.22"}},
                '{"hello":{"world":22.0}}',
            ),
            (
                ObjectFlag({"hello": BoolFlag()}),
                {"hello": True},
                {"hello": "True"},
                '{"hello":true}',
            ),
            (
                ObjectFlag({"hello": ObjectFlag({"world": BoolFlag()})}),
                {"hello": {"world": True}},
                {"hello": {"world": "True"}},
                '{"hello":{"world":true}}',
            ),
            (
                ObjectFlag({"hello": NullableFlag(StringFlag())}),
                {"hello": None},
                22,
                '{"hello":null}',
            ),
            (
                ObjectFlag({"hello": NullableFlag(StringFlag())}),
                {"hello": "world"},
                {},
                '{"hello":"world"}',
            ),
            (
                ObjectFlag({"hello": NullableFlag(NullableFlag(StringFlag()))}),
                {"hello": None},
                22,
                '{"hello":null}',
            ),
            (
                ObjectFlag({"hello": ListFlag(ObjectFlag({"world": StringFlag()}))}),
                {"hello": [{"world": "I have arrived"}]},
                {"hello": "world"},
                '{"hello":[{"world":"I have arrived"}]}',
            ),
            (
                ObjectFlag({"hello": ListFlag(ListFlag(StringFlag()))}),
                {"hello": [["world"]]},
                {"hello": ["world"]},
                '{"hello":[["world"]]}',
            ),
            (
                ObjectFlag({"hello": ListFlag(ListFlag(StringFlag()))}),
                {"hello": []},
                {"hello": ["world"]},
                '{"hello":[]}',
            ),
            (
                ObjectFlag({"hello": ListFlag(NullableFlag(StringFlag()))}),
                {"hello": [None]},
                {"hello": [22]},
                '{"hello":[null]}',
            ),
            (
                ObjectFlag({"hello": ListFlag(NullableFlag(StringFlag()))}),
                {"hello": ["null"]},
                {"hello": [22]},
                '{"hello":["null"]}',
            ),
        ],
    )
    def test_parse_success_err(self, flag, value, error_value, expected):
        SUT = Flags(flag)

        assert SUT.parse(value) == expected

        with pytest.raises(ValidationError):
            SUT.parse(error_value)

    @pytest.mark.parametrize(
        "flag,expected",
        [
            (
                ObjectFlag({"hello": StringFlag(literal="world")}),
                {
                    "alias_type": """{ hello : String
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.string |> Decode.andThen (\\lit -> if lit == "world" then Decode.succeed "world" else Decode.fail "Value did not match literal <world>"))""",
                },
            ),
            (
                ObjectFlag({"hello": StringFlag(literal="world")}),
                {
                    "alias_type": """{ hello : String
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.string |> Decode.andThen (\\lit -> if lit == "world" then Decode.succeed "world" else Decode.fail "Value did not match literal <world>"))""",
                },
            ),
        ],
    )
    def test_to_elm_parser_success(self, flag, expected):
        SUT = Flags(flag)

        assert SUT.to_elm_parser_data() == expected

    @pytest.mark.parametrize(
        "flag,expected",
        [
            (
                ObjectFlag(
                    {"hello": CustomTypeFlag(variants=[("Custom1", StringFlag())])}
                ),
                """{ hello : Hello_
    }

type Hello_
    = Custom1 String
""",
            ),
            (
                ObjectFlag(
                    {"hello": CustomTypeFlag(variants=[("Custom1", StringFlag())])}
                ),
                """{ hello : Hello_
    }

type Hello_
    = Custom1 String
""",
            ),
        ],
    )
    def test_alias_type_success(self, flag, expected):
        SUT = Flags(flag)

        assert SUT.to_elm_parser_data()["alias_type"] == expected

    @pytest.mark.parametrize(
        "flag,expected",
        [
            (
                ObjectFlag(
                    {
                        "hello": CustomTypeFlag(
                            variants=[
                                (
                                    "Custom1",
                                    ObjectFlag(
                                        {"hello": StringFlag(), "world": StringFlag()}
                                    ),
                                )
                            ]
                        )
                    }
                ),
                {
                    "alias_type": """{ hello : Hello_
    }

type Hello_
    = Custom1 Hello_Custom1__


type alias Hello_Custom1__ =
    { hello : String
    , world : String
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.oneOf [Decode.map Custom1 hello_Custom1__Decoder])

hello_Custom1__Decoder : Decode.Decoder Hello_Custom1__
hello_Custom1__Decoder =
    Decode.succeed Hello_Custom1__
        |> required "hello" Decode.string
        |> required "world" Decode.string""",
                },
            ),
            (
                ObjectFlag(
                    {
                        "hello": NullableFlag(
                            CustomTypeFlag(
                                variants=[
                                    (
                                        "Custom1",
                                        StringFlag(),
                                    )
                                ]
                            )
                        )
                    }
                ),
                {
                    "alias_type": """{ hello : Maybe Hello_
    }

type Hello_
    = Custom1 String
""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.nullable (Decode.oneOf [Decode.map Custom1 Decode.string]))""",
                },
            ),
            (
                ObjectFlag(
                    {
                        "hello": ListFlag(
                            CustomTypeFlag(
                                variants=[
                                    (
                                        "Custom1",
                                        StringFlag(),
                                    )
                                ]
                            )
                        )
                    }
                ),
                {
                    "alias_type": """{ hello : List Hello_
    }

type Hello_
    = Custom1 String
""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.list (Decode.oneOf [Decode.map Custom1 Decode.string]))""",
                },
            ),
            (
                ObjectFlag(
                    {
                        "hello": ObjectFlag({"world": StringFlag()}),
                        "someList": ListFlag(StringFlag()),
                    }
                ),
                {
                    "alias_type": """{ hello : Hello_
    , someList : List String
    }

type alias Hello_ =
    { world : String }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" hello_Decoder
        |> required "someList" (Decode.list Decode.string)

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |> required "world" Decode.string""",
                },
            ),
            (
                ObjectFlag({"hello": ListFlag(NullableFlag(StringFlag()))}),
                {
                    "alias_type": """{ hello : List (Maybe String)
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.list (Decode.nullable Decode.string))""",
                },
            ),
            (
                ObjectFlag({"hello": ListFlag(ListFlag(StringFlag()))}),
                {
                    "alias_type": """{ hello : List (List String)
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.list (Decode.list Decode.string))""",
                },
            ),
            (
                ObjectFlag({"hello": ObjectFlag({"world": StringFlag()})}),
                {
                    "alias_type": """{ hello : Hello_
    }

type alias Hello_ =
    { world : String }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" hello_Decoder

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |> required "world" Decode.string""",
                },
            ),
            (
                ObjectFlag({"hello": ListFlag(ObjectFlag({"world": StringFlag()}))}),
                {
                    "alias_type": """{ hello : List Hello_
    }

type alias Hello_ =
    { world : String }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.list hello_Decoder)

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |> required "world" Decode.string""",
                },
            ),
            (
                ObjectFlag({"hello": ListFlag(StringFlag())}),
                {
                    "alias_type": """{ hello : List String
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.list Decode.string)""",
                },
            ),
            (
                ObjectFlag({"hello": NullableFlag(StringFlag())}),
                {
                    "alias_type": """{ hello : Maybe String
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.nullable Decode.string)""",
                },
            ),
            (
                ObjectFlag({"hello": NullableFlag(IntFlag())}),
                {
                    "alias_type": """{ hello : Maybe Int
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.nullable Decode.int)""",
                },
            ),
            (
                ObjectFlag({"hello": NullableFlag(NullableFlag(StringFlag()))}),
                {
                    "alias_type": """{ hello : Maybe (Maybe String)
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.nullable (Decode.nullable Decode.string))""",
                },
            ),
            (
                ObjectFlag(
                    {"hello": NullableFlag(ObjectFlag({"hello": StringFlag()}))}
                ),
                {
                    "alias_type": """{ hello : Maybe Hello_
    }

type alias Hello_ =
    { hello : String }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.nullable hello_Decoder)

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |> required "hello" Decode.string""",
                },
            ),
            (
                ObjectFlag({"hello": NullableFlag(ListFlag(StringFlag()))}),
                {
                    "alias_type": """{ hello : Maybe (List String)
    }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" (Decode.nullable (Decode.list Decode.string))""",
                },
            ),
            (
                ObjectFlag(
                    {"hello": ObjectFlag({"world": ObjectFlag({"it": StringFlag()})})}
                ),
                {
                    "alias_type": """{ hello : Hello_
    }

type alias Hello_ =
    { world : Hello_World__ }

type alias Hello_World__ =
    { it : String }""",
                    "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "hello" hello_Decoder

hello_Decoder : Decode.Decoder Hello_
hello_Decoder =
    Decode.succeed Hello_
        |> required "world" hello_world__Decoder

hello_world__Decoder : Decode.Decoder Hello_World__
hello_world__Decoder =
    Decode.succeed Hello_World__
        |> required "it" Decode.string""",
                },
            ),
        ],
    )
    def test_to_parser_data_success(self, flag, expected):
        SUT = Flags(flag)

        assert SUT.to_elm_parser_data() == expected


class TestCustomTypeFlags:
    def test_root_string_flag_custom_type_parser(self):
        """Handles StringFlag"""
        d = CustomTypeFlag(variants=[("Custom1", StringFlag())])

        SUT = Flags(d)
        assert SUT.parse("2") == '"2"'

        with pytest.raises(ValidationError):
            assert SUT.parse(2)

    def test_root_multi_string_flag_custom_type_parser(self):
        """Resolved correct literal"""
        d = CustomTypeFlag(
            variants=[
                ("Custom1", StringFlag(literal="1")),
                ("Custom2", StringFlag(literal="2")),
            ]
        )
        SUT = Flags(d)
        assert SUT.parse("2") == '"2"'

        with pytest.raises(ValidationError):
            assert SUT.parse(2)

    def test_root_int_flag_custom_type_parser(self):
        """Handles IntFlag"""
        d = CustomTypeFlag(variants=[("Custom1", IntFlag())])

        SUT = Flags(d)
        assert SUT.parse(2) == "2"

        with pytest.raises(ValidationError):
            assert SUT.parse(2.0)

    def test_root_float_flag_custom_type_parser(self):
        """Handles FloatFlag"""
        d = CustomTypeFlag(variants=[("Custom1", FloatFlag())])

        SUT = Flags(d)
        assert SUT.parse(2.0) == "2.0"
        assert SUT.parse(2) == "2.0"

    def test_root_bool_flag_custom_type_parser(self):
        """Handles BoolFlag"""
        d = CustomTypeFlag(variants=[("Custom1", BoolFlag())])

        SUT = Flags(d)
        assert SUT.parse(True) == "true"
        assert SUT.parse(False) == "false"

    def test_root_nullable_with_string_flag_custom_type_parser(self):
        """Handles NullableFlag"""
        d = CustomTypeFlag(variants=[("Custom1", NullableFlag(StringFlag()))])

        SUT = Flags(d)
        assert SUT.parse(None) == "null"
        assert SUT.parse("hello") == '"hello"'

    def test_root_list_with_string_flag_custom_type_parser(self):
        """Handles ListFlag"""
        d = CustomTypeFlag(variants=[("Custom1", ListFlag(StringFlag()))])

        SUT = Flags(d)
        assert SUT.parse([]) == "[]"
        assert SUT.parse(["hello"]) == '["hello"]'

    def test_root_object_flag_with_string_field_custom_type_parser(self):
        """Handles ObjectFlag"""
        d = CustomTypeFlag(variants=[("Custom1", ObjectFlag({"hello": StringFlag()}))])

        SUT = Flags(d)
        assert SUT.parse({"hello": "world"}) == '{"hello":"world"}'

    @pytest.mark.django_db
    def test_root_mcf_flag_custom_type_parser(self, basic_form):
        """Handles a ModelChoiceFieldFlag"""
        prepare_form = basic_form()
        d = ModelChoiceFieldFlag()

        SUT = Flags(d)
        d = CustomTypeFlag(variants=[("Custom1", ModelChoiceFieldFlag())])

        assert (
            SUT.parse(prepare_form["car"])
            == '{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"---------","value":"","selected":true}]}'
        )

    def test_inline_custom_type_with_no_variants_raises(self):
        d = CustomTypeFlag(variants=[])

        with pytest.raises(Exception):
            Flags(d)

    def test_inline_custom_type_with_lowercase_variant(self):
        d = CustomTypeFlag(variants=[("custom1", ObjectFlag({"hello": StringFlag()}))])

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 InlineToModel_Custom1__


type alias InlineToModel_Custom1__ =
    { hello : String }"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 inlinetomodel_Custom1__Decoder])

inlinetomodel_Custom1__Decoder : Decode.Decoder InlineToModel_Custom1__
inlinetomodel_Custom1__Decoder =
    Decode.succeed InlineToModel_Custom1__
        |> required "hello" Decode.string"""
        )

    def test_root_custom_type_with_string_codegen(self):
        """Generates String custom type"""
        d = CustomTypeFlag(variants=[("Custom1", StringFlag())])

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 String
"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 Decode.string])"""
        )

    def test_root_custom_type_with_multi_string_literal_codegen(self):
        """Generates String literal custom type"""
        d = CustomTypeFlag(variants=[("Custom1", StringFlag(literal="1"))])

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 String
"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 (Decode.string |> Decode.andThen (\\lit -> if lit == "1" then Decode.succeed "1" else Decode.fail "Value did not match literal <1>"))])"""
        )

    def test_root_custom_type_with_nullable_codegen(self):
        """Generates String custom type"""
        d = CustomTypeFlag(variants=[("Custom1", NullableFlag(StringFlag()))])

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 (Maybe String)
"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 (Decode.nullable Decode.string)])"""
        )

    def test_root_custom_type_with_list_codegen(self):
        """Generates String custom type"""
        d = CustomTypeFlag(variants=[("Custom1", ListFlag(StringFlag()))])

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 (List String)
"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 (Decode.list Decode.string)])"""
        )

    def test_root_custom_type_with_list_nullable_codegen(self):
        """Generates String custom type"""
        d = CustomTypeFlag(variants=[("Custom1", ListFlag(NullableFlag(StringFlag())))])

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 (List (Maybe String))
"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 (Decode.list (Decode.nullable Decode.string))])"""
        )

    def test_root_custom_flag_custom_type_codegen(self):
        d = CustomTypeFlag(
            variants=[
                ("Custom1", CustomTypeFlag(variants=[("InnerCustom", StringFlag())])),
            ]
        )

        SUT = Flags(d)

        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 InlineToModel_Custom1__


type InlineToModel_Custom1__
    = InnerCustom String
"""
        )

        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 (Decode.oneOf [Decode.map InnerCustom Decode.string])])"""
        )

    def test_root_object_flag_custom_type_codegen(self):
        """Generates String custom type"""
        d = CustomTypeFlag(
            variants=[
                ("Custom1", ObjectFlag({"hello": StringFlag(), "world": StringFlag()})),
                ("Custom2", ObjectFlag({"ive": StringFlag(), "arrived": StringFlag()})),
                ("Custom3", StringFlag()),
            ]
        )

        SUT = Flags(d)
        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """InlineToModel_

type InlineToModel_
    = Custom1 InlineToModel_Custom1__
    | Custom2 InlineToModel_Custom2__
    | Custom3 String


type alias InlineToModel_Custom1__ =
    { hello : String
    , world : String
    }

type alias InlineToModel_Custom2__ =
    { ive : String
    , arrived : String
    }"""
        )
        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    (Decode.oneOf [Decode.map Custom1 inlinetomodel_Custom1__Decoder, Decode.map Custom2 inlinetomodel_Custom2__Decoder, Decode.map Custom3 Decode.string])

inlinetomodel_Custom1__Decoder : Decode.Decoder InlineToModel_Custom1__
inlinetomodel_Custom1__Decoder =
    Decode.succeed InlineToModel_Custom1__
        |> required "hello" Decode.string
        |> required "world" Decode.string

inlinetomodel_Custom2__Decoder : Decode.Decoder InlineToModel_Custom2__
inlinetomodel_Custom2__Decoder =
    Decode.succeed InlineToModel_Custom2__
        |> required "ive" Decode.string
        |> required "arrived" Decode.string"""
        )


class TestModelMultipleChoiceFieldFlags:
    @pytest.mark.django_db
    def test_inline_model_multiple_choice_field_flag_parser(self, basic_form):
        prepare_form = basic_form()
        d = ModelMultipleChoiceFieldFlag()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["extras"])
            == '{"help_text":"Do I detect.. Multiple Elm\'s?","auto_id":"id_extras","id_for_label":"id_extras","label":"Extras","name":"extras","widget_type":"selectmultiple","options":[]}'
        )

    @pytest.mark.django_db
    def test_inline_model_multiple_choice_field_flag_parser_with_selections_on_model(
        self, basic_form
    ):
        extra = Extra(name="Something")
        extra.save()

        enth = Enthusiast()
        enth.save()
        enth.extras.add(extra)

        prepare_form = basic_form(instance=enth)
        d = ModelMultipleChoiceFieldFlag()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["extras"])
            == '{"help_text":"Do I detect.. Multiple Elm\'s?","auto_id":"id_extras","id_for_label":"id_extras","label":"Extras","name":"extras","widget_type":"selectmultiple","options":[{"choice_label":"Extra object (1)","value":"1","selected":true}]}'
        )

    @pytest.mark.django_db
    def test_root_value_model_multiple_choice_field_parser(self, basic_form):
        prepare_form = basic_form()
        d = ObjectFlag({"mmcf": ModelMultipleChoiceFieldFlag()})

        SUT = Flags(d)

        assert (
            SUT.parse({"mmcf": prepare_form["extras"]})
            == '{"mmcf":{"help_text":"Do I detect.. Multiple Elm\'s?","auto_id":"id_extras","id_for_label":"id_extras","label":"Extras","name":"extras","widget_type":"selectmultiple","options":[]}}'
        )

    @pytest.mark.django_db
    def test_inline_model_multiple_choice_field_flag_with_mixed_fields(
        self,
        blanks_form: type[forms.ModelForm],
    ):
        blanks = BlankM(third=False, fourth=122, fifth=5.55)
        blanks.save()
        d = ModelMultipleChoiceFieldFlag(variants=[BlankM])
        prepare_form = blanks_form()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["blanks"])
            == '{"help_text":"SOS Multi","auto_id":"id_blanks","id_for_label":"id_blanks","label":"Blanks","name":"blanks","widget_type":"selectmultiple","options":[{"choice_label":"BlankM object (1)","value":"1","selected":false,"instance":{"id":1,"first":null,"second":null,"third":false,"fourth":122,"fifth":5.55}}]}'
        )

        blanks.first = "first"
        blanks.save()
        prepare_form = blanks_form()

        assert (
            SUT.parse(prepare_form["blanks"])
            == '{"help_text":"SOS Multi","auto_id":"id_blanks","id_for_label":"id_blanks","label":"Blanks","name":"blanks","widget_type":"selectmultiple","options":[{"choice_label":"BlankM object (1)","value":"1","selected":false,"instance":{"id":1,"first":"first","second":null,"third":false,"fourth":122,"fifth":5.55}}]}'
        )

        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """{ help_text : String
    , auto_id : String
    , id_for_label : String
    , label : Maybe String
    , name : String
    , widget_type : String
    , options : List Options_
    }

type Options_
    = BlankM Options_BlankM__


type alias Options_BlankM__ =
    { choice_label : String
    , value : String
    , selected : Bool
    , instance : Options_BlankM__Instance__
    }

type alias Options_BlankM__Instance__ =
    { id : Int
    , first : Maybe String
    , second : Maybe String
    , third : Bool
    , fourth : Int
    , fifth : Float
    }"""
        )

    @pytest.mark.django_db
    def test_inline_model_multiple_choice_field_flag_with_single_variant(
        self,
        basic_form_no_empty_label: type[forms.ModelForm],
    ):
        extra = Extra(name="Something")
        extra.save()
        d = ModelMultipleChoiceFieldFlag(variants=[Extra])
        prepare_form = basic_form_no_empty_label()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["extras"])
            == '{"help_text":"Do I detect.. Multiple Elm\'s?","auto_id":"id_extras","id_for_label":"id_extras","label":"Extras","name":"extras","widget_type":"selectmultiple","options":[{"choice_label":"Extra object (1)","value":"1","selected":false,"instance":{"id":1,"name":"Something"}}]}'
        )

    @pytest.mark.django_db
    def test_inline_model_multiple_choice_field_flag_with_multiple_variants(
        self,
        basic_form_no_empty_label: type[forms.ModelForm],
    ):
        extras = Extra(name="Extra")
        extras.save()
        extra01 = Extra01(name="Extra01")
        extra01.save()
        d = ModelMultipleChoiceFieldFlag(variants=[Extra, Extra01])
        prepare_extra_form = basic_form_no_empty_label()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_extra_form["extras"])
            == '{"help_text":"Do I detect.. Multiple Elm\'s?","auto_id":"id_extras","id_for_label":"id_extras","label":"Extras","name":"extras","widget_type":"selectmultiple","options":[{"choice_label":"Extra object (1)","value":"1","selected":false,"instance":{"id":1,"name":"Extra"}}]}'
        )
        assert (
            SUT.parse(prepare_extra_form["extras01"])
            == '{"help_text":"Do I detect.. Multiple Elm\'s?","auto_id":"id_extras01","id_for_label":"id_extras01","label":"Extras01","name":"extras01","widget_type":"selectmultiple","options":[{"choice_label":"Extra01 object (1)","value":"1","selected":false,"instance":{"id":1,"name":"Extra01"}}]}'
        )

    @pytest.mark.django_db
    def test_inline_model_multiple_choice_field_flag_with_incorrect_model_variant(
        self,
        basic_team_form: type[forms.ModelForm],
    ):
        driver = Driver(name="Jdawg")
        driver.save()
        d = ModelMultipleChoiceFieldFlag(variants=[Extra])
        prepare_form = basic_team_form()

        SUT = Flags(d)

        with pytest.raises(ValidationError):
            SUT.parse(prepare_form["driver"])

    def test_inline_model_multiple_choice_field_flag(self):
        d = ModelChoiceFieldFlag()
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ help_text : String
    , auto_id : String
    , id_for_label : String
    , label : Maybe String
    , name : String
    , widget_type : String
    , options : List Options_
    }

type alias Options_ =
    { choice_label : String
    , value : String
    , selected : Bool
    }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "help_text" Decode.string
        |> required "auto_id" Decode.string
        |> required "id_for_label" Decode.string
        |> required "label" (Decode.nullable Decode.string)
        |> required "name" Decode.string
        |> required "widget_type" Decode.string
        |> required "options" (Decode.list options_Decoder)

options_Decoder : Decode.Decoder Options_
options_Decoder =
    Decode.succeed Options_
        |> required "choice_label" Decode.string
        |> required "value" Decode.string
        |> required "selected" Decode.bool""",
        }

    def test_inline_model_multiple_choice_field_flag_with_variant(self):
        d = ModelMultipleChoiceFieldFlag(variants=[Extra])
        SUT = Flags(d)

        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """{ help_text : String
    , auto_id : String
    , id_for_label : String
    , label : Maybe String
    , name : String
    , widget_type : String
    , options : List Options_
    }

type Options_
    = Extra Options_Extra__


type alias Options_Extra__ =
    { choice_label : String
    , value : String
    , selected : Bool
    , instance : Options_Extra__Instance__
    }

type alias Options_Extra__Instance__ =
    { id : Int
    , name : String
    }"""
        )

        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "help_text" Decode.string
        |> required "auto_id" Decode.string
        |> required "id_for_label" Decode.string
        |> required "label" (Decode.nullable Decode.string)
        |> required "name" Decode.string
        |> required "widget_type" Decode.string
        |> required "options" (Decode.list (Decode.oneOf [Decode.map Extra options_Extra__Decoder]))

options_Extra__Decoder : Decode.Decoder Options_Extra__
options_Extra__Decoder =
    Decode.succeed Options_Extra__
        |> required "choice_label" Decode.string
        |> required "value" Decode.string
        |> required "selected" Decode.bool
        |> required "instance" options_extra__instance__Decoder

options_extra__instance__Decoder : Decode.Decoder Options_Extra__Instance__
options_extra__instance__Decoder =
    Decode.succeed Options_Extra__Instance__
        |> required "id" Decode.int
        |> required "name" Decode.string"""
        )


class TestModelChoiceFieldFlags:
    @pytest.mark.django_db
    def test_inline_model_choice_field_flag_parser(self, basic_form):
        prepare_form = basic_form()
        d = ModelChoiceFieldFlag()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["car"])
            == '{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"---------","value":"","selected":true}]}'
        )

        try:
            SUT.parse({"something": "wrong"})
        except Exception:
            assert True
            return

        pytest.fail("Passing wrong shape should fail validation")

    @pytest.mark.django_db
    def test_root_value_model_choice_field_parser(self, basic_form):
        prepare_form = basic_form()
        d = ObjectFlag({"mcf": ModelChoiceFieldFlag()})

        SUT = Flags(d)

        assert (
            SUT.parse({"mcf": prepare_form["car"]})
            == '{"mcf":{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"---------","value":"","selected":true}]}}'
        )

    @pytest.mark.django_db
    def test_inline_model_choice_field_flag_with_mixed_fields(
        self,
        blanks_form: type[forms.ModelForm],
    ):
        blank = Blank(third=False, fourth=122, fifth=5.55)
        blank.save()
        d = ModelChoiceFieldFlag(variants=[Blank])
        prepare_form = blanks_form()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["blank"])
            == '{"help_text":"SOS","auto_id":"id_blank","id_for_label":"id_blank","label":"Blank","name":"blank","widget_type":"select","options":[{"choice_label":"Blank object (1)","value":"1","selected":false,"instance":{"id":1,"first":null,"second":null,"third":false,"fourth":122,"fifth":5.55}}]}'
        )

        blank.first = "first"
        blank.save()
        prepare_form = blanks_form()

        assert (
            SUT.parse(prepare_form["blank"])
            == '{"help_text":"SOS","auto_id":"id_blank","id_for_label":"id_blank","label":"Blank","name":"blank","widget_type":"select","options":[{"choice_label":"Blank object (1)","value":"1","selected":false,"instance":{"id":1,"first":"first","second":null,"third":false,"fourth":122,"fifth":5.55}}]}'
        )

        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """{ help_text : String
    , auto_id : String
    , id_for_label : String
    , label : Maybe String
    , name : String
    , widget_type : String
    , options : List Options_
    }

type Options_
    = Blank Options_Blank__


type alias Options_Blank__ =
    { choice_label : String
    , value : String
    , selected : Bool
    , instance : Options_Blank__Instance__
    }

type alias Options_Blank__Instance__ =
    { id : Int
    , first : Maybe String
    , second : Maybe String
    , third : Bool
    , fourth : Int
    , fifth : Float
    }"""
        )

    @pytest.mark.django_db
    def test_inline_model_choice_field_flag_with_single_variant(
        self,
        basic_form_no_empty_label: type[forms.ModelForm],
    ):
        car = Car(manufacturer="Mazda", country="Japan")
        car.save()
        d = ModelChoiceFieldFlag(variants=[Car])
        prepare_form = basic_form_no_empty_label()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_form["car"])
            == '{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"Mazda","value":"1","selected":false,"instance":{"id":1,"manufacturer":"Mazda","country":"Japan"}}]}'
        )

    @pytest.mark.django_db
    def test_inline_model_choice_field_flag_with_multiple_variants(
        self,
        basic_form_no_empty_label: type[forms.ModelForm],
        basic_team_form: type[forms.ModelForm],
    ):
        car = Car(manufacturer="Mazda", country="Japan")
        car.save()
        driver = Driver(name="Jdawg")
        driver.save()
        d = ModelChoiceFieldFlag(variants=[Car, Driver])
        prepare_car_form = basic_form_no_empty_label()
        prepare_team_form = basic_team_form()

        SUT = Flags(d)

        assert (
            SUT.parse(prepare_car_form["car"])
            == '{"help_text":"Do I detect.. Elm?","auto_id":"id_car","id_for_label":"id_car","label":"Car","name":"car","widget_type":"select","options":[{"choice_label":"Mazda","value":"1","selected":false,"instance":{"id":1,"manufacturer":"Mazda","country":"Japan"}}]}'
        )
        assert (
            SUT.parse(prepare_team_form["driver"])
            == '{"help_text":"Do I detect.. Elm?","auto_id":"id_driver","id_for_label":"id_driver","label":"Driver","name":"driver","widget_type":"select","options":[{"choice_label":"Jdawg","value":"1","selected":false,"instance":{"id":1,"name":"Jdawg"}}]}'
        )

    @pytest.mark.django_db
    def test_inline_model_choice_field_flag_with_incorrect_model_variant(
        self,
        basic_team_form: type[forms.ModelForm],
    ):
        driver = Driver(name="Jdawg")
        driver.save()
        d = ModelChoiceFieldFlag(variants=[Car])
        prepare_form = basic_team_form()

        SUT = Flags(d)

        with pytest.raises(ValidationError):
            SUT.parse(prepare_form["driver"])

    def test_inline_model_choice_field_flag(self):
        d = ModelChoiceFieldFlag()
        SUT = Flags(d)

        assert SUT.to_elm_parser_data() == {
            "alias_type": """{ help_text : String
    , auto_id : String
    , id_for_label : String
    , label : Maybe String
    , name : String
    , widget_type : String
    , options : List Options_
    }

type alias Options_ =
    { choice_label : String
    , value : String
    , selected : Bool
    }""",
            "decoder_body": """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "help_text" Decode.string
        |> required "auto_id" Decode.string
        |> required "id_for_label" Decode.string
        |> required "label" (Decode.nullable Decode.string)
        |> required "name" Decode.string
        |> required "widget_type" Decode.string
        |> required "options" (Decode.list options_Decoder)

options_Decoder : Decode.Decoder Options_
options_Decoder =
    Decode.succeed Options_
        |> required "choice_label" Decode.string
        |> required "value" Decode.string
        |> required "selected" Decode.bool""",
        }

    def test_inline_model_choice_field_flag_with_variant(self):
        d = ModelChoiceFieldFlag(variants=[Car])
        SUT = Flags(d)

        assert (
            SUT.to_elm_parser_data()["alias_type"]
            == """{ help_text : String
    , auto_id : String
    , id_for_label : String
    , label : Maybe String
    , name : String
    , widget_type : String
    , options : List Options_
    }

type Options_
    = Car Options_Car__


type alias Options_Car__ =
    { choice_label : String
    , value : String
    , selected : Bool
    , instance : Options_Car__Instance__
    }

type alias Options_Car__Instance__ =
    { id : Int
    , manufacturer : String
    , country : String
    }"""
        )

        assert (
            SUT.to_elm_parser_data()["decoder_body"]
            == """toModel : Decode.Decoder ToModel
toModel =
    Decode.succeed ToModel
        |> required "help_text" Decode.string
        |> required "auto_id" Decode.string
        |> required "id_for_label" Decode.string
        |> required "label" (Decode.nullable Decode.string)
        |> required "name" Decode.string
        |> required "widget_type" Decode.string
        |> required "options" (Decode.list (Decode.oneOf [Decode.map Car options_Car__Decoder]))

options_Car__Decoder : Decode.Decoder Options_Car__
options_Car__Decoder =
    Decode.succeed Options_Car__
        |> required "choice_label" Decode.string
        |> required "value" Decode.string
        |> required "selected" Decode.bool
        |> required "instance" options_car__instance__Decoder

options_car__instance__Decoder : Decode.Decoder Options_Car__Instance__
options_car__instance__Decoder =
    Decode.succeed Options_Car__Instance__
        |> required "id" Decode.int
        |> required "manufacturer" Decode.string
        |> required "country" Decode.string"""
        )
