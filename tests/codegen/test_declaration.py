import djelm.codegen.elm as Elm
import djelm.codegen.annotation as Anno
import djelm.codegen.writer as Writer


class TestExpressions:
    def test_alias_expression(self):
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
