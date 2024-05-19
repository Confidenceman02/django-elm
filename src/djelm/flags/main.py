import typing
from dataclasses import dataclass
import djelm.codegen.annotation as Anno
import djelm.codegen.compiler as Compiler
import djelm.codegen.expression as Exp
import djelm.codegen.op as Op
import djelm.codegen.module_name as Module
from djelm.codegen.pattern import VarPattern
import djelm.codegen.range as Range
import djelm.codegen.format as Format
import djelm.codegen.writer as Writer
import djelm.codegen.elm as Elm
from pydantic import BaseModel, TypeAdapter, validate_call
from typing_extensions import Annotated

from djelm.flags.form.primitives import ModelChoiceFieldFlag

from .primitives import (
    BoolFlag,
    CustomTypeFlag,
    Flag,
    FloatFlag,
    IntFlag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    PrimitiveFlag,
    PrimitiveObjectFlagType,
    StringFlag,
)

from .adapters import (
    BoolAdapter,
    FloatAdapter,
    IntAdapter,
    StringAdapter,
    annotated_alias_key,
    annotated_string,
    annotated_int,
    annotated_bool,
    annotated_float,
    annotated_string_literal,
    string_literal_adapter,
)

RESERVED_KEYWORDS = ["if"]

PreparedElm = typing.TypedDict("PreparedElm", {"alias_type": str, "decoder_body": str})


@validate_call
def valid_alias_key(k: annotated_alias_key):
    return k


@dataclass(slots=True)
class StringDecoder:
    """Decoder helper for the Elm String primitive"""

    value: str

    def alias(self) -> str:
        return f"""{self.value} : {StringDecoder._annotation()}"""

    def nested_alias(self):
        return f""", {self.value} : {StringDecoder._annotation()}"""

    @staticmethod
    def _raw_literal_decoder(literal: str) -> str:
        return Writer.writeExpression(
            StringDecoder.decoder_literal_expression(literal)
        ).write()

    @staticmethod
    def _annotation():
        return Anno.toString(StringDecoder._compiler_annotation())

    @staticmethod
    def _compiler_annotation() -> Compiler.Annotation:
        return Anno.string()

    def pipeline_expression(self) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(self.value), self.decoder_expression()],
            Range.Range(1, 0),
        )

    def pipeline_literal_expression(self, literal: str) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [
                Elm.literal(self.value),
                self.decoder_literal_expression(literal),
            ],
            Range.Range(1, 0),
        )

    @staticmethod
    def decoder_expression() -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "string", None, None),
            [],
        )

    @staticmethod
    def decoder_literal_expression(literal: str) -> Compiler.Expression:
        return Exp.Parenthesized(
            Op.pipe(
                Elm.apply(
                    Exp.FunctionOrValue(
                        Module.ModuleName(["Decode"]), "andThen", None, None
                    ),
                    [
                        Exp.Parenthesized(
                            Exp.Lambda(
                                [VarPattern("lit")],
                                Exp.IfBlock(
                                    Op.equals(
                                        Exp.FunctionOrValue(
                                            Module.ModuleName([]), "lit", None, None
                                        ),
                                        Elm.literal(literal),
                                    ),
                                    Elm.apply(
                                        Exp.FunctionOrValue(
                                            Module.ModuleName(["Decode"]),
                                            "succeed",
                                            None,
                                            None,
                                        ),
                                        [Elm.literal(literal)],
                                    ),
                                    Elm.apply(
                                        Exp.FunctionOrValue(
                                            Module.ModuleName(["Decode"]),
                                            "fail",
                                            None,
                                            None,
                                        ),
                                        [
                                            Elm.literal(
                                                f"Value did not match literal <{literal}>"
                                            )
                                        ],
                                    ),
                                ),
                            ),
                            None,
                        )
                    ],
                ),
                StringDecoder.decoder_expression(),
            ),
            None,
        )


@dataclass(slots=True)
class IntDecoder:
    """Decoder helper for the Elm Int primitive"""

    value: str

    def alias(self):
        return f"""{self.value} : {IntDecoder._annotation()}"""

    def nested_alias(self):
        return f""", {self.value} : {IntDecoder._annotation()}"""

    @staticmethod
    def _annotation():
        return Anno.toString(IntDecoder._compiler_annotation())

    @staticmethod
    def _compiler_annotation() -> Compiler.Annotation:
        return Anno.int()

    def pipeline_expression(self) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(self.value), self.decoder_expression()],
            Range.Range(1, 0),
        )

    @staticmethod
    def decoder_expression() -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "int", None, None),
            [],
        )


@dataclass(slots=True)
class BoolDecoder:
    """Decoder helper for the Elm Bool primitive"""

    value: str

    def alias(self):
        return f"""{self.value} : {BoolDecoder._annotation()}"""

    def nested_alias(self):
        return f""", {self.value} : {BoolDecoder._annotation()}"""

    @staticmethod
    def _annotation():
        return Anno.toString(BoolDecoder._compiler_annotation())

    @staticmethod
    def _compiler_annotation() -> Compiler.Annotation:
        return Anno.bool()

    def pipeline_expression(self) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(self.value), self.decoder_expression()],
            Range.Range(1, 0),
        )

    @staticmethod
    def decoder_expression() -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "bool", None, None),
            [],
        )


@dataclass(slots=True)
class FloatDecoder:
    """Decoder helper for the Elm Float primitive"""

    value: str

    def alias(self):
        return f"""{self.value} : {FloatDecoder._annotation()}"""

    def nested_alias(self):
        return f""", {self.value} : {FloatDecoder._annotation()}"""

    @staticmethod
    def _annotation():
        return Anno.toString(FloatDecoder._compiler_annotation())

    @staticmethod
    def _compiler_annotation() -> Compiler.Annotation:
        return Anno.float()

    def pipeline_expression(self) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(self.value), self.decoder_expression()],
            Range.Range(1, 0),
        )

    @staticmethod
    def decoder_expression() -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "float", None, None),
            [],
        )


@dataclass(slots=True)
class ListDecoder:
    """Decoder helper for the Elm List primitive"""

    value: str
    target: Compiler.Annotation

    def alias(self):
        return f"""{self.value} : {self._annotation(self.target)}"""

    def nested_alias(self):
        return f""", {self.value} : {self._annotation(self.target)}"""

    @staticmethod
    def _annotation(annotation: Compiler.Annotation) -> str:
        return Anno.toString(ListDecoder._compiler_annotation(annotation))

    @staticmethod
    def _compiler_annotation(annotation: Compiler.Annotation) -> Compiler.Annotation:
        return Anno.list(annotation)

    def pipeline_expression(
        self, expression: Compiler.Expression
    ) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [
                Elm.literal(self.value),
                self.decoder_expression(expression),
            ],
            Range.Range(1, 0),
        )

    @staticmethod
    def decoder_expression(expression: Compiler.Expression) -> Compiler.Expression:
        return Exp.Parenthesized(
            Elm.apply(
                Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "list", None, None),
                [expression],
            ),
            None,
        )


@dataclass(slots=True)
class NullableDecoder:
    """Decoder helper for the Elm Maybe monad"""

    value: str
    target: Compiler.Annotation

    def alias(self):
        return f"""{self.value} : {self._annotation(self.target)}"""

    def nested_alias(self):
        return f""", {self.value} : {self._annotation(self.target)}"""

    @staticmethod
    def _annotation(annotation: Compiler.Annotation) -> str:
        return Anno.toString(NullableDecoder._compiler_annotation(annotation))

    @staticmethod
    def _compiler_annotation(annotation: Compiler.Annotation) -> Compiler.Annotation:
        return Anno.maybe(annotation)

    def pipeline_expression(
        self, expression: Compiler.Expression
    ) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [
                Elm.literal(self.value),
                self.decoder_expression(expression),
            ],
            Range.Range(1, 0),
        )

    @staticmethod
    def decoder_expression(expression: Compiler.Expression) -> Compiler.Expression:
        return Exp.Parenthesized(
            Elm.apply(
                Exp.FunctionOrValue(
                    Module.ModuleName(["Decode"]), "nullable", None, None
                ),
                [expression],
            ),
            None,
        )


@dataclass(slots=True)
class ObjectDecoder:
    """Decoder helper for the Elm {} primitive"""

    value: str
    depth: int
    parent_alias: str | None = None

    def pipeline_signature(self) -> Compiler.Signature:
        return Compiler.Signature(
            self._to_decoder_name(),
            Compiler.Typed(
                "Decode.Decoder",
                [self._compiler_annotation(Anno.record([])).annotation],
            ),
        )

    def alias(self):
        return f"""{self.value} : {self._to_annotation()}"""

    def nested_alias(self):
        return f""", {self.value} : {self._to_annotation()}"""

    def _to_annotation(self) -> str:
        anno = self._compiler_annotation(
            Anno.record([]),
        )
        return Anno.toString(anno)

    def _to_decoder_name(self):
        p = self.parent_alias if self.parent_alias else ""
        return f"""{p.lower() + self.value + self._depth_markers()}Decoder"""

    def _depth_markers(self) -> str:
        marker = ""
        for _ in range(self.depth):
            marker += "_"
        return marker

    def _compiler_annotation(
        self, annotation: Compiler.Annotation
    ) -> Compiler.Annotation:
        p = self.parent_alias if self.parent_alias else ""
        return Anno.alias(
            f"{p}{Format.alias_type(self.value)}{self._depth_markers()}", annotation
        )

    def pipeline_expression(self) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(self.value), self.decoder_expression()],
            Range.Range(1, 0),
        )

    def pipeline_starter_expression(self) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "succeed", None, None),
            [Elm.value(self._to_annotation())],
        )

    def decoder_expression(self) -> Compiler.Expression:
        return Elm.value(self._to_decoder_name())


@dataclass(slots=True)
class CustomTypeDecoder:
    """Decoder helper for the Elm custom type primitive"""

    name: str
    depth: int
    compiler_variants: list[Compiler.Variant]
    decoder_expressions: list[tuple[str, Compiler.Expression]]

    @staticmethod
    def pipeline_expression(
        field: str, expression: Compiler.Expression
    ) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(field), expression],
            Range.Range(1, 0),
        )

    def _to_annotation(self) -> str:
        return Anno.toString(self._compiler_annotation())

    def _to_declaration(self) -> str:
        return Writer.writeDeclartion(self._compiler_declaration()).write()

    def _compiler_annotation(self) -> Compiler.Annotation:
        return Compiler.Annotation(
            Compiler.Typed(
                Format.alias_type(
                    Compiler.get_declaration_name(self._compiler_declaration())
                ),
                [],
            ),
            {},
        )

    def _compiler_declaration(self) -> Compiler.Declaration:
        return Elm.customType(self.name, self.compiler_variants)

    def decoder_expression(self) -> Compiler.Expression:
        return Exp.Parenthesized(
            Elm.apply(
                Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "oneOf", None, None),
                [
                    Elm.list(
                        [
                            self.decoder_expression_helper(de)
                            for de in self.decoder_expressions
                        ]
                    )
                ],
            ),
            None,
        )

    def decoder_expression_helper(
        self,
        variant: tuple[str, Compiler.Expression],
    ) -> Compiler.Expression:
        variant_name = variant[0]
        variant_decoder_expression = variant[1]

        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName(["Decode"]), "map", None, None),
            [Elm.value(variant_name), variant_decoder_expression],
        )


ObjHelperReturn = typing.TypedDict(
    "ObjHelperReturn",
    {
        "adapter": TypeAdapter,
        "anno": typing.Dict[str, PrimitiveObjectFlagType],
        "elm_values": PreparedElm,
        "alias_extra": str,
        "decoder_extra": str,
        "field_annotations": list[tuple[str, Compiler.Annotation]],
    },
)
SingleHelperReturn = typing.TypedDict(
    "SingleHelperReturn",
    {
        "adapter": TypeAdapter,
        "anno": PrimitiveObjectFlagType,
        "elm_values": PreparedElm,
        "alias_extra": str,
        "compiler_annotation": Compiler.Annotation,
        "decoder_expression": Compiler.Expression,
        "decoder_extra": str,
    },
)


class FlagMetaClass(type):
    def __new__(cls, class_name, bases, attrs):
        return type(class_name, bases, attrs)


class BaseFlag(metaclass=FlagMetaClass):
    def __new__(cls, d):
        assert isinstance(d, Flag)

        prepared_flags: ObjHelperReturn | SingleHelperReturn | None = None
        decoder_sig = (
            Compiler.Signature(
                "toModel",
                Compiler.Typed("Decode.Decoder", [Compiler.Typed("ToModel", [])]),
            ),
            Elm.apply(
                Exp.FunctionOrValue(
                    Module.ModuleName(["Decode"]), "succeed", None, None
                ),
                [
                    Elm.value("ToModel"),
                ],
            ),
        )

        match d:
            case ObjectFlag(obj=_):
                prepared_flags = _prepare_pipeline_flags(d, decoder_sig)
            case ModelChoiceFieldFlag(variants=_) as mcf:
                prepared_flags = _prepare_pipeline_flags(
                    mcf.obj(), decoder_sig=decoder_sig
                )
                prepared_flags["adapter"] = mcf.adapter()
            case _:
                prepared_flags = _prepare_inline_flags(
                    d, ObjectDecoder("inlineToModel", 1), decoder_sig=decoder_sig
                )

        assert prepared_flags is not None

        class Prepared:
            """Validator and Elm values builder"""

            @staticmethod
            def parse(input) -> str:
                match d:
                    case ObjectFlag(obj=_):
                        return (
                            prepared_flags["adapter"]
                            .validate_python(input)
                            .model_dump_json()
                        )
                    case ModelChoiceFieldFlag():
                        adapter = prepared_flags["adapter"]
                        validated = adapter.validate_python(input)
                        return adapter.dump_json(validated).decode("utf-8")
                    case _:
                        adapter = prepared_flags["adapter"]
                        validated = adapter.validate_python(input)
                        return adapter.dump_json(validated).decode("utf-8")

            @staticmethod
            def to_elm_parser_data() -> PreparedElm:
                if isinstance(d, ObjectFlag) or isinstance(d, ModelChoiceFieldFlag):
                    return prepared_flags["elm_values"]
                else:
                    return {
                        "alias_type": prepared_flags["elm_values"]["alias_type"]
                        + prepared_flags["alias_extra"],
                        "decoder_body": prepared_flags["elm_values"]["decoder_body"]
                        + prepared_flags["decoder_extra"],
                    }

        return Prepared


def _prepare_inline_flags(
    d: Flag,
    object_decoder: ObjectDecoder | None = None,
    depth: int = 1,
    decoder_sig: tuple[Compiler.Signature, Compiler.Expression] | None = None,
) -> SingleHelperReturn:
    adapter: TypeAdapter
    anno: PrimitiveObjectFlagType
    alias_type: str = ""
    decoder_extra: str = ""
    alias_extra: str = ""
    compiler_annotation = None
    decoder_expression: Compiler.Expression | None = None
    match d:
        case StringFlag():
            adapter = StringAdapter
            decoder_expression = StringDecoder.decoder_expression()
            anno = annotated_string  # type:ignore
            if d.literal is not None:
                adapter = string_literal_adapter(d.literal)
                decoder_expression = StringDecoder.decoder_literal_expression(d.literal)
                anno = annotated_string_literal(d.literal)  # type:ignore
            alias_type = StringDecoder._annotation()
            compiler_annotation = StringDecoder._compiler_annotation()
        case IntFlag():
            adapter = IntAdapter
            anno = annotated_int  # type:ignore
            alias_type = IntDecoder._annotation()
            compiler_annotation = IntDecoder._compiler_annotation()
            decoder_expression = IntDecoder.decoder_expression()
        case FloatFlag():
            adapter = FloatAdapter
            anno = annotated_float  # type:ignore
            alias_type = FloatDecoder._annotation()
            compiler_annotation = FloatDecoder._compiler_annotation()
            decoder_expression = FloatDecoder.decoder_expression()
        case BoolFlag():
            adapter = BoolAdapter
            anno = annotated_bool  # type:ignore
            alias_type = BoolDecoder._annotation()
            compiler_annotation = BoolDecoder._compiler_annotation()
            decoder_expression = BoolDecoder.decoder_expression()
        case NullableFlag(obj=obj):
            single_flag = _prepare_inline_flags(obj, object_decoder)
            t = single_flag["anno"]
            adapter = TypeAdapter(Annotated[typing.Optional[t], None])
            anno = typing.Optional[t]  # type:ignore
            alias_type = NullableDecoder._annotation(single_flag["compiler_annotation"])
            alias_extra += single_flag["alias_extra"]
            decoder_extra += single_flag["decoder_extra"]
            compiler_annotation = NullableDecoder._compiler_annotation(
                single_flag["compiler_annotation"]
            )
            decoder_expression = NullableDecoder.decoder_expression(
                single_flag["decoder_expression"]
            )
        case ListFlag(obj=obj):
            single_flag = _prepare_inline_flags(obj, object_decoder)
            t = single_flag["anno"]
            adapter = TypeAdapter(Annotated[list[t], None])  # type:ignore
            anno = list[t]  # type:ignore
            alias_type = ListDecoder._annotation(single_flag["compiler_annotation"])
            alias_extra += single_flag["alias_extra"]
            decoder_extra += single_flag["decoder_extra"]
            compiler_annotation = ListDecoder._compiler_annotation(
                single_flag["compiler_annotation"]
            )
            decoder_expression = ListDecoder.decoder_expression(
                single_flag["decoder_expression"]
            )
        case CustomTypeFlag(variants=v):
            if object_decoder is None:
                raise Exception(
                    "Missing an ObjectDecoder argument for CustomTypeDecoder"
                )
            assert 0 < len(v)

            annos = []
            alias_extras: list[str] = []
            decoder_extras: list[str] = []
            variants: list[Compiler.Variant] = []
            next_object_decoder = ObjectDecoder(
                object_decoder.value, object_decoder.depth + 1
            )
            variant_decoder_expressions: list[tuple[str, Compiler.Expression]] = []
            for var in v:
                formatted_constructor = Format.safe_capitalize(var[0])
                next_object_decoder = ObjectDecoder(
                    formatted_constructor,
                    object_decoder.depth + 1,
                    object_decoder._to_annotation(),
                )
                prepared = _prepare_inline_flags(var[1], next_object_decoder)
                variant_decoder_expressions.append(
                    (formatted_constructor, prepared["decoder_expression"])
                )
                annos.append(prepared["anno"])
                alias_extras.append(prepared["alias_extra"])
                decoder_extras.append(prepared["decoder_extra"])
                if prepared["compiler_annotation"]:
                    variants.append(
                        (
                            Elm.variantWith(
                                formatted_constructor, [prepared["compiler_annotation"]]
                            )
                        )
                    )

            adapter = TypeAdapter(typing.Union[*annos])  # type:ignore
            anno = typing.Union[*annos]  # type:ignore

            custom_type_decoder = CustomTypeDecoder(
                object_decoder._to_annotation(),
                depth,
                variants,
                variant_decoder_expressions,
            )

            compiler_annotation = custom_type_decoder._compiler_annotation()

            decoder_extra = "".join(decoder_extras)
            alias_type = custom_type_decoder._to_annotation()
            alias_extra = "".join(
                ["\n\n" + custom_type_decoder._to_declaration(), *alias_extras]
            )
            decoder_expression = custom_type_decoder.decoder_expression()
        case ModelChoiceFieldFlag(variants=_) as mcf:
            if object_decoder is None:
                raise Exception(f"Missing an ObjectDecoder argument for {mcf.obj()}")
            parent_key = None
            """
            We want to make sure we don't mangle the alias name for the first ObjectFlag
            that is exists in an inline flag. i.e. InlineToModel_InlineToModel_

            InlineToModel_ is an alias that only exists as a root alias name, it never gets reproduced
            in deeper objects so if we see it, we can safely assume we are in the first level of an inline flag.

            Subsequent alias's will have their parent added to the start. i.e. type alias InlineToModel_A__
            """
            if object_decoder._to_annotation() != "InlineToModel_":
                parent_key = object_decoder._to_annotation()

            object_flag = _prepare_pipeline_flags(
                mcf.obj(),
                (
                    object_decoder.pipeline_signature(),
                    object_decoder.pipeline_starter_expression(),
                ),
                depth + 1,
                parent_key,
            )
            adapter = mcf.adapter()
            # Use internal annotation
            anno = mcf.anno()
            declaration = Elm.alias(
                object_decoder._to_annotation(),
                Anno.record(object_flag["field_annotations"]),
            )
            compiler_annotation = object_decoder._compiler_annotation(
                Anno.record(object_flag["field_annotations"])
            )

            alias_type = object_decoder._to_annotation()
            alias_extra = (
                "\n\n"
                + Writer.writeDeclartion(declaration).write()
                + object_flag["alias_extra"]
            )
            decoder_extra = f"\n\n{object_flag['elm_values']['decoder_body']}"
            decoder_expression = object_decoder.decoder_expression()
        case ObjectFlag(obj=obj):
            if object_decoder is None:
                raise Exception(f"Missing an ObjectDecoder argument for {obj}")
            parent_key = None
            """
            We want to make sure we don't mangle the alias name for the first ObjectFlag
            that is exists in an inline flag. i.e. InlineToModel_InlineToModel_

            InlineToModel_ is an alias that only exists as a root alias name, it never gets reproduced
            in deeper objects so if we see it, we can safely assume we are in the first level of an inline flag.

            Subsequent alias's will have their parent added to the start. i.e. type alias InlineToModel_A__
            """
            if object_decoder._to_annotation() != "InlineToModel_":
                parent_key = object_decoder._to_annotation()
            object_flag = _prepare_pipeline_flags(
                d,
                (
                    object_decoder.pipeline_signature(),
                    object_decoder.pipeline_starter_expression(),
                ),
                depth + 1,
                parent_key,
            )
            t = object_flag["anno"]  # type:ignore
            declaration = Elm.alias(
                object_decoder._to_annotation(),
                Anno.record(object_flag["field_annotations"]),
            )
            compiler_annotation = object_decoder._compiler_annotation(
                Anno.record(object_flag["field_annotations"])
            )

            adapter = object_flag["adapter"]
            anno = t  # type:ignore

            alias_type = Anno.toString(compiler_annotation)
            alias_extra = (
                "\n\n"
                + Writer.writeDeclartion(declaration).write()
                + object_flag["alias_extra"]
            )
            decoder_extra = f"\n\n{object_flag['elm_values']['decoder_body']}"
            decoder_expression = object_decoder.decoder_expression()
        case _:
            raise Exception(f"Can't resolve core_schema type for: {d}")

    decoder_body = ""

    if decoder_sig:
        sig, _ = decoder_sig
        decoder_body = Writer.writeDeclartion(
            Elm.declaration(sig.name, decoder_expression, sig)
        ).write()

    return {
        "adapter": adapter,
        "anno": anno,
        "elm_values": {
            "alias_type": alias_type,
            "decoder_body": decoder_body,
        },
        "alias_extra": alias_extra,
        "compiler_annotation": compiler_annotation,
        "decoder_expression": decoder_expression,
        "decoder_extra": decoder_extra,
    }


def _prepare_pipeline_flags(
    d: Flag,
    decoder_sig: tuple[Compiler.Signature, Compiler.Expression],
    depth: int = 1,
    parent_key: str | None = None,
) -> ObjHelperReturn:
    anno: typing.Dict[str, PrimitiveObjectFlagType] = {}
    alias_values: str = ""
    decoder_extra: str = ""
    alias_extra: str = ""
    field_annotations: list[tuple[str, Compiler.Annotation]] = []
    pipeline_expressions: list[Compiler.Expression] = []

    assert isinstance(d, ObjectFlag)

    for idx, (k, v) in enumerate(d.obj.items()):
        try:
            assert k not in RESERVED_KEYWORDS
            k = k.replace("\n", "")
            valid_alias_key(k)
            match v:
                case ModelChoiceFieldFlag() as mcf:
                    decoder = ObjectDecoder(k, depth, parent_key)
                    prepared_object_recursive = _prepare_pipeline_flags(
                        # Use built in flags
                        mcf.obj(),
                        (
                            decoder.pipeline_signature(),
                            decoder.pipeline_starter_expression(),
                        ),
                        depth + 1,
                        parent_key=decoder._to_annotation(),
                    )

                    # Use built in annotations
                    anno[k] = mcf.anno()
                    declaration = Elm.alias(
                        decoder._to_annotation(),
                        Anno.record(prepared_object_recursive["field_annotations"]),
                    )
                    field_annotations.append(
                        (
                            k,
                            Anno.alias(
                                decoder._to_annotation(),
                                Anno.record(
                                    prepared_object_recursive["field_annotations"]
                                ),
                            ),
                        )
                    )
                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['elm_values']['decoder_body']}"
                    )
                    alias_extra += (
                        "\n\n"
                        + Writer.writeDeclartion(declaration).write()
                        + prepared_object_recursive["alias_extra"]
                    )
                    pipeline_expressions.append(decoder.pipeline_expression())
                    if idx == 0:
                        alias_values += f" {decoder.alias()}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias()}"

                case ObjectFlag(obj=obj):
                    decoder = ObjectDecoder(k, depth, parent_key)
                    prepared_object_recursive = _prepare_pipeline_flags(
                        ObjectFlag(obj),
                        (
                            decoder.pipeline_signature(),
                            decoder.pipeline_starter_expression(),
                        ),
                        depth + 1,
                        parent_key=decoder._to_annotation(),
                    )
                    anno[k] = type(
                        "K",
                        (BaseModel,),
                        {
                            "__annotations__": prepared_object_recursive[
                                "anno"
                            ].__origin__.__annotations__  # type:ignore
                        },
                    )
                    declaration = Elm.alias(
                        decoder._to_annotation(),
                        Anno.record(prepared_object_recursive["field_annotations"]),
                    )
                    field_annotations.append(
                        (
                            k,
                            Anno.alias(
                                decoder._to_annotation(),
                                Anno.record(
                                    prepared_object_recursive["field_annotations"]
                                ),
                            ),
                        )
                    )

                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['elm_values']['decoder_body']}"
                    )
                    alias_extra += (
                        "\n\n"
                        + Writer.writeDeclartion(declaration).write()
                        + prepared_object_recursive["alias_extra"]
                    )
                    pipeline_expressions.append(decoder.pipeline_expression())
                    if idx == 0:
                        alias_values += f" {decoder.alias()}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias()}"

                case ListFlag(obj=obj):
                    decoder = ObjectDecoder(k, depth, parent_key)
                    single_flag = _prepare_inline_flags(obj, decoder)
                    list_decoder = ListDecoder(
                        k,
                        single_flag["compiler_annotation"],
                    )
                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]
                    anno[k] = list[single_flag["anno"]]  # type:ignore
                    field_annotations.append(
                        (k, Anno.list(single_flag["compiler_annotation"]))
                    )
                    pipeline_expressions.append(
                        list_decoder.pipeline_expression(
                            single_flag["decoder_expression"]
                        )
                    )
                    if idx == 0:
                        alias_values += f" {list_decoder.alias()}"
                    else:
                        alias_values += f"\n    {list_decoder.nested_alias()}"

                case CustomTypeFlag(variants=_) as ctf:
                    decoder = ObjectDecoder(k, depth, parent_key)
                    single_flag = _prepare_inline_flags(ctf, decoder)
                    anno[k] = typing.Optional[single_flag["anno"]]  # type:ignore
                    field_annotations.append((k, single_flag["compiler_annotation"]))

                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]

                    pipeline_expressions.append(
                        CustomTypeDecoder.pipeline_expression(
                            k, single_flag["decoder_expression"]
                        )
                    )
                    if idx == 0:
                        alias_values += f" {decoder.alias()}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias()}"
                    pass

                case NullableFlag(obj=obj1):
                    single_flag = _prepare_inline_flags(
                        obj1, ObjectDecoder(k, depth, parent_key)
                    )
                    nullable_decoder = NullableDecoder(
                        k,
                        single_flag["compiler_annotation"],
                    )
                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]
                    anno[k] = typing.Optional[single_flag["anno"]]  # type:ignore
                    field_annotations.append(
                        (k, Anno.maybe(single_flag["compiler_annotation"]))
                    )

                    pipeline_expressions.append(
                        nullable_decoder.pipeline_expression(
                            single_flag["decoder_expression"]
                        )
                    )

                    if idx == 0:
                        alias_values += f" {nullable_decoder.alias()}"
                    else:
                        alias_values += f"\n    {nullable_decoder.nested_alias()}"
                case StringFlag():
                    string_decoder = StringDecoder(k)
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    field_annotations.append(
                        (k, single_prepared["compiler_annotation"])
                    )

                    if v.literal:
                        pipeline_expressions.append(
                            string_decoder.pipeline_literal_expression(v.literal)
                        )
                    else:
                        pipeline_expressions.append(
                            string_decoder.pipeline_expression()
                        )

                    if idx == 0:
                        alias_values += f" {string_decoder.alias()}"
                    else:
                        alias_values += f"\n    {string_decoder.nested_alias()}"

                case IntFlag():
                    int_decoder = IntDecoder(k)
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    field_annotations.append(
                        (k, single_prepared["compiler_annotation"])
                    )
                    pipeline_expressions.append(int_decoder.pipeline_expression())

                    if idx == 0:
                        alias_values += f" {int_decoder.alias()}"
                    else:
                        alias_values += f"\n    {int_decoder.nested_alias()}"

                case FloatFlag():
                    float_decoder = FloatDecoder(k)
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    field_annotations.append(
                        (k, single_prepared["compiler_annotation"])
                    )
                    pipeline_expressions.append(float_decoder.pipeline_expression())

                    if idx == 0:
                        alias_values += f" {float_decoder.alias()}"
                    else:
                        alias_values += f"\n    {float_decoder.nested_alias()}"

                case BoolFlag():
                    bool_decoder = BoolDecoder(k)
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    field_annotations.append(
                        (k, single_prepared["compiler_annotation"])
                    )
                    pipeline_expressions.append(bool_decoder.pipeline_expression())
                    if idx == 0:
                        alias_values += f" {bool_decoder.alias()}"
                    else:
                        alias_values += f"\n    {bool_decoder.nested_alias()}"

                case _:
                    raise Exception("Unsopported type")
        except Exception as err:
            raise err

    sig, top_pipe = decoder_sig

    pipeline_decoder = Writer.writeDeclartion(
        Elm.declaration(
            sig.name,
            Op.pipes(top_pipe, reversed(pipeline_expressions)),
            sig,
        )
    ).write()

    return {
        "adapter": TypeAdapter(
            Annotated[type("K", (BaseModel,), {"__annotations__": anno}), None]
        ),  # type:ignore
        "anno": Annotated[type("K", (BaseModel,), {"__annotations__": anno}), None],  # type:ignore
        "elm_values": {
            "alias_type": "{" + alias_values + "\n    }" + alias_extra,
            "decoder_body": pipeline_decoder + decoder_extra,
        },
        "alias_extra": alias_extra,
        "decoder_extra": decoder_extra,
        "field_annotations": field_annotations,
    }


class Flags(BaseFlag):
    """
    A class for validating djelm flags that are used in Elm programs.

    f1 = Flags(ObjectFlag({"hello": StringFlag}))
    f1.parse({"hello": "world"}) -> '{"hello":"world"}'

    f2 = Flags(StringFlag())
    f2.parse("hello world") -> '"hello world"'
    """

    if typing.TYPE_CHECKING:
        parse: typing.Callable[[PrimitiveFlag], str]
        to_elm_parser_data: typing.Callable[[], dict[str, str]]
