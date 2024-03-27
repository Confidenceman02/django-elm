import djelm.codegen.elm as Elm
import djelm.codegen.annotation as Anno
import djelm.codegen.writer as Writer


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
