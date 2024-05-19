import djelm.codegen.expression as Exp
import djelm.codegen.elm as Elm
from djelm.codegen.pattern import VarPattern
import djelm.codegen.writer as Writer
import djelm.codegen.range as Range
import djelm.codegen.module_name as Module
import djelm.codegen.op as Op


class TestExpressions:
    def test_if_block(self):
        SUT = Writer.writeExpression(
            Exp.IfBlock(
                Op.equals(Elm.int(2), Elm.int(2)),
                Elm.apply(
                    Exp.FunctionOrValue(
                        Module.ModuleName(["Decode"]), "succeed", None, None
                    ),
                    [Elm.literal("foo")],
                ),
                Elm.apply(
                    Exp.FunctionOrValue(
                        Module.ModuleName(["Decode"]), "fail", None, None
                    ),
                    [Elm.literal("some fail message")],
                ),
            )
        )

        assert (
            SUT.write()
            == 'if 2 == 2 then Decode.succeed "foo" else Decode.fail "some fail message"'
        )

    def test_lambda(self):
        SUT = Writer.writeExpression(
            Exp.Lambda(
                [VarPattern("one")],
                Elm.apply(
                    Exp.FunctionOrValue(
                        Module.ModuleName(["Decode"]), "succeed", None, None
                    ),
                    [Elm.literal("foo")],
                ),
            )
        )

        assert SUT.write() == '\\one -> Decode.succeed "foo"'

    def test_pipe(self):
        SUT = Writer.writeExpression(
            Op.pipe(
                Elm.apply(
                    Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
                    [
                        Exp.Literal("someField01", None),
                        Exp.Parenthesized(
                            Elm.apply(
                                Exp.FunctionOrValue(
                                    Module.ModuleName(["Decode"]),
                                    "nullable",
                                    None,
                                    None,
                                ),
                                [Elm.value("Decode.string")],
                            ),
                            None,
                        ),
                    ],
                    Range.Range(1, 0),
                ),
                Op.pipe(
                    Elm.apply(
                        Exp.FunctionOrValue(
                            Module.ModuleName([]), "required", None, None
                        ),
                        [
                            Exp.Literal("someField", None),
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
            ),
        )
        assert (
            SUT.write()
            == """Decode.succeed ToModel
    |> required \"someField\" Decode.string
    |> required \"someField01\" (Decode.nullable Decode.string)"""
        )

    def test_pipes(self):
        top_pipe = Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "succeed", None, None),
            [
                Elm.value("ToModel"),
            ],
        )
        SUT = Writer.writeExpression(
            Op.pipes(
                top_pipe,
                iter(
                    [
                        Elm.apply(
                            Exp.FunctionOrValue(
                                Module.ModuleName([]), "required", None, None
                            ),
                            [
                                Exp.Literal("someField01", None),
                                Exp.Parenthesized(
                                    Elm.apply(
                                        Exp.FunctionOrValue(
                                            Module.ModuleName(["Decode"]),
                                            "nullable",
                                            None,
                                            None,
                                        ),
                                        [Elm.value("Decode.string")],
                                    ),
                                    None,
                                ),
                            ],
                            Range.Range(1, 0),
                        ),
                        Elm.apply(
                            Exp.FunctionOrValue(
                                Module.ModuleName([]), "required", None, None
                            ),
                            [
                                Exp.Literal("someField", None),
                                Exp.Parenthesized(
                                    Elm.apply(
                                        Exp.FunctionOrValue(
                                            Module.ModuleName(["Decode"]),
                                            "nullable",
                                            None,
                                            None,
                                        ),
                                        [Elm.value("Decode.string")],
                                    ),
                                    None,
                                ),
                            ],
                            Range.Range(1, 0),
                        ),
                    ]
                ),
            )
        )

        assert (
            SUT.write()
            == """Decode.succeed ToModel
    |> required \"someField\" (Decode.nullable Decode.string)
    |> required \"someField01\" (Decode.nullable Decode.string)"""
        )

    def test_plus_expression(self):
        SUT = Writer.writeExpression(
            Op.plus(
                Elm.int(2),
                Elm.int(2),
            )
        )

        assert SUT.write() == """2 + 2"""

    def test_equals_expression(self):
        SUT = Writer.writeExpression(
            Op.equals(
                Elm.int(2),
                Elm.int(2),
            )
        )

        assert SUT.write() == """2 == 2"""

    def test_list_expression(self):
        SUT = Writer.writeExpression(Elm.list([Elm.literal("someVar")]))

        assert SUT.write() == '["someVar"]'
