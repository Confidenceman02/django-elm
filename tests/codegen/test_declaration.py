import djelm.codegen.elm as Elm
import djelm.codegen.annotation as Anno
import djelm.codegen.writer as Writer
import djelm.codegen.op as Op
import djelm.codegen.expression as Exp
import djelm.codegen.module_name as Module
import djelm.codegen.range as Range
import djelm.codegen.compiler as Compiler


class TestExpressions:
    def test_alias_declaration(self):
        decl = Elm.alias(
            "Something",
            Anno.record([("hello", Anno.string()), ("world", Anno.string())]),
        )
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type alias Something =
    { hello : String
    , world : String
    }"""
        )

    def test_alias_declaration_with_lower(self):
        decl = Elm.alias(
            "something",
            Anno.record([("hello", Anno.string()), ("world", Anno.string())]),
        )
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type alias Something =
    { hello : String
    , world : String
    }"""
        )

    def test_custom_type_declaration(self):
        decl = Elm.customType("Something", [Elm.variant("Hello"), Elm.variant("World")])
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type Something
    = Hello
    | World
"""
        )

    def test_custom_type_single_string_variant(self):
        decl = Elm.customType("Something", [Elm.variant("A"), Elm.variant("B")])
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type Something
    = A
    | B
"""
        )

    def test_custom_type_single_string_lowercase_variant(self):
        decl = Elm.customType("Something", [Elm.variant("aa"), Elm.variant("bb")])
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type Something
    = Aa
    | Bb
"""
        )

    def test_custom_type_declaration_with_lower(self):
        decl = Elm.customType("something", [Elm.variant("Hello"), Elm.variant("World")])
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type Something
    = Hello
    | World
"""
        )

    def test_custom_type_declaration_with_annotated_variants(self):
        decl = Elm.customType(
            "Something",
            [
                Elm.variantWith("Hello", [Anno.string()]),
                Elm.variantWith("World", [Anno.maybe(Anno.string())]),
                Elm.variantWith("Is", [Anno.maybe(Anno.list(Anno.string()))]),
                Elm.variantWith(
                    "Classic",
                    [
                        Anno.alias(
                            "AnAlias", Anno.record([("something", Anno.string())])
                        )
                    ],
                ),
            ],
        )
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """type Something
    = Hello String
    | World (Maybe String)
    | Is (Maybe (List String))
    | Classic AnAlias
"""
        )

    def test_declaration_with_pipe_operator_expression(self):
        sig = Compiler.Signature(
            "options_Decoder",
            Compiler.Typed("Decode.Decoder", [Compiler.Typed("ToModel", [])]),
        )
        pipe = Op.pipe(
            Elm.apply(
                Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
                [
                    Elm.literal("someField01"),
                    Elm.apply(
                        Exp.FunctionOrValue(
                            Module.ModuleName(["Decode"]), "int", None, None
                        ),
                        [],
                    ),
                ],
                Range.Range(1, 0),
            ),
            Op.pipe(
                Elm.apply(
                    Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
                    [
                        Elm.literal("someField"),
                        Exp.Application(
                            [
                                Exp.FunctionOrValue(
                                    Module.ModuleName(["Decode"]),
                                    "string",
                                    None,
                                    None,
                                )
                            ],
                            None,
                            None,
                        ),
                    ],
                    Range.Range(1, 0),
                ),
                Elm.apply(
                    Exp.FunctionOrValue(
                        Module.ModuleName(["Decode"]), "succeed", None, None
                    ),
                    [
                        Elm.value("ToModel"),
                    ],
                ),
            ),
        )
        decl = Elm.declaration("options_Decoder", pipe, sig)
        SUT = Writer.writeDeclartion(decl)

        assert (
            SUT.write()
            == """options_Decoder : Decode.Decoder ToModel
options_Decoder =
    Decode.succeed ToModel
        |> required \"someField\" Decode.string
        |> required \"someField01\" Decode.int"""
        )
