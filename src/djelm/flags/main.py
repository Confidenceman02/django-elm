from collections import deque
import typing
from dataclasses import dataclass

from pydantic import BaseModel, TypeAdapter, validate_call
from typing_extensions import Annotated

import djelm.codegen.annotation as Anno
import djelm.codegen.compiler as Compiler
import djelm.codegen.elm as Elm
import djelm.codegen.expression as Exp
import djelm.codegen.format as Format
import djelm.codegen.module_name as Module
import djelm.codegen.op as Op
import djelm.codegen.range as Range
import djelm.codegen.writer as Writer
from djelm.codegen.pattern import VarPattern
from djelm.flags.form.primitives import ModelChoiceFieldFlag

from .adapters import (
    BoolAdapter,
    FloatAdapter,
    IntAdapter,
    StringAdapter,
    annotated_alias_key,
    annotated_bool,
    annotated_float,
    annotated_int,
    annotated_string,
    annotated_string_literal,
    string_literal_adapter,
)
from .primitives import (
    AliasFlag,
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

RESERVED_KEYWORDS = ["if", "in"]

PreparedElm = typing.TypedDict("PreparedElm", {"alias_type": str, "decoder_body": str})


@dataclass(slots=True)
class _DeclarationMetaBasic:
    """The standard declaration type"""

    declaration: Compiler.Declaration


@dataclass(slots=True)
class _DeclarationMetaStatic:
    """
    The static declaration type

    Static declarations only appear once in the generated Elm code.
    The main use is to create top level reusable types.

    When generating code, this type tags all the inner declarations
    as being part of a static declaration.
    """

    static_name: str
    declarations: list[_DeclarationMetaBasic | typing.Self]


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

    def alias(self, key: str):
        return f"""{key} : {self._to_annotation()}"""

    def nested_alias(self, key: str):
        return f""", {key} : {self._to_annotation()}"""

    def _to_annotation(self) -> str:
        anno = self._compiler_annotation(
            Anno.record([]),
        )
        return Anno.toString(anno)

    def _to_decoder_name(self):
        if self.parent_alias:
            prefix = f"{self.parent_alias.lower()}{self.value}"
        else:
            prefix = self.value[0].lower() + self.value[1:]
        return f"""{prefix + self._depth_markers()}Decoder"""

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

    def pipeline_expression(self, key: str) -> Compiler.Expression:
        return Elm.apply(
            Exp.FunctionOrValue(Module.ModuleName([]), "required", None, None),
            [Elm.literal(key), self.decoder_expression()],
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

    def _to_declaration(self) -> Compiler.Declaration:
        return self._compiler_declaration()

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


PipelineReturn = typing.TypedDict(
    "PipelineReturn",
    {
        "adapter": TypeAdapter,
        "anno": typing.Dict[str, PrimitiveObjectFlagType],
        "alias_type": str,
        "field_annotations": list[tuple[str, Compiler.Annotation]],
        "type_declarations": list[_DeclarationMetaBasic | _DeclarationMetaStatic],
        "decoder_declarations": list[_DeclarationMetaBasic | _DeclarationMetaStatic],
    },
)
InlineReturn = typing.TypedDict(
    "InlineReturn",
    {
        "adapter": TypeAdapter,
        "anno": PrimitiveObjectFlagType,
        "alias_type": str,
        "compiler_annotation": Compiler.Annotation,
        "decoder_expression": Compiler.Expression,
        "type_declarations": list[_DeclarationMetaBasic | _DeclarationMetaStatic],
        "decoder_declarations": list[_DeclarationMetaBasic | _DeclarationMetaStatic],
    },
)


class FlagMetaClass(type):
    def __new__(cls, class_name, bases, attrs):
        return type(class_name, bases, attrs)


class BaseFlag(metaclass=FlagMetaClass):
    def __new__(cls, flag):
        assert isinstance(flag, Flag)

        prepared_flags: PipelineReturn | InlineReturn | None = None
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

        match flag:
            case ObjectFlag(obj=_):
                prepared_flags = _prepare_pipeline_flags(flag, decoder_sig)
            case ModelChoiceFieldFlag(variants=_) as mcf:
                prepared_flags = _prepare_pipeline_flags(
                    mcf.obj(), decoder_sig=decoder_sig
                )
                prepared_flags["adapter"] = mcf.adapter()
            case _:
                prepared_flags = _prepare_inline_flags(
                    flag, ObjectDecoder("inlineToModel", 1), decoder_sig=decoder_sig
                )

        assert prepared_flags is not None

        class Prepared:
            """Validator and Elm values builder"""

            @staticmethod
            def parse(input) -> str:
                match flag:
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
                """
                Organises and prepares all declarations for code generation.
                """
                prepared_type_declarations = []
                prepared_decoder_declarations = []
                processed_static_types: list[str] = []
                processed_static_decoders: list[str] = []

                type_declarations_to_process = deque(
                    prepared_flags["type_declarations"]
                )
                decoder_declarations_to_process = deque(
                    prepared_flags["decoder_declarations"]
                )

                while type_declarations_to_process:
                    current = type_declarations_to_process.popleft()

                    match current:
                        case _DeclarationMetaBasic():
                            prepared_type_declarations.append(
                                f"\n\n{Writer.writeDeclartion(current.declaration).write()}"
                            )
                        case _DeclarationMetaStatic():
                            if current.static_name in processed_static_types:
                                continue
                            else:
                                type_declarations_to_process.extendleft(
                                    reversed(current.declarations)
                                )
                                processed_static_types.append(current.static_name)

                while decoder_declarations_to_process:
                    current = decoder_declarations_to_process.popleft()
                    match current:
                        case _DeclarationMetaBasic():
                            prepared_decoder_declarations.append(
                                f"{Writer.writeDeclartion(current.declaration).write()}"
                            )
                        case _DeclarationMetaStatic():
                            if current.static_name in processed_static_decoders:
                                continue
                            else:
                                decoder_declarations_to_process.extendleft(
                                    reversed(current.declarations)
                                )
                                processed_static_decoders.append(current.static_name)

                return {
                    "alias_type": prepared_flags["alias_type"]
                    + "".join(prepared_type_declarations),
                    "decoder_body": "\n\n".join(prepared_decoder_declarations),
                }

        return Prepared


def _prepare_inline_flags(
    flag: Flag,
    object_decoder: ObjectDecoder | None = None,
    depth: int = 1,
    decoder_sig: tuple[Compiler.Signature, Compiler.Expression] | None = None,
) -> InlineReturn:
    adapter: TypeAdapter
    anno: PrimitiveObjectFlagType
    alias_type: str = ""
    compiler_annotation = None
    decoder_expression: Compiler.Expression | None = None
    type_declarations: list[_DeclarationMetaBasic | _DeclarationMetaStatic] = []
    decoder_declarations: list[_DeclarationMetaBasic | _DeclarationMetaStatic] = []
    match flag:
        case AliasFlag(name=alias_name, obj=alias_flag):
            alias_object_decoder = ObjectDecoder(alias_name, 1)
            object_inline = _prepare_inline_flags(alias_flag, alias_object_decoder)
            adapter = object_inline["adapter"]
            anno = object_inline["anno"]
            alias_type = object_inline["alias_type"]
            compiler_annotation = object_inline["compiler_annotation"]
            decoder_expression = object_inline["decoder_expression"]
            type_declarations.append(
                _DeclarationMetaStatic(
                    static_name=alias_name,
                    declarations=object_inline["type_declarations"],
                )
            )
            decoder_declarations.append(
                _DeclarationMetaStatic(
                    static_name=alias_name,
                    declarations=object_inline["decoder_declarations"],
                )
            )
        case StringFlag():
            adapter = StringAdapter
            decoder_expression = StringDecoder.decoder_expression()
            anno = annotated_string  # type:ignore
            if flag.literal is not None:
                adapter = string_literal_adapter(flag.literal)
                decoder_expression = StringDecoder.decoder_literal_expression(
                    flag.literal
                )
                anno = annotated_string_literal(flag.literal)  # type:ignore
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
            object_inline = _prepare_inline_flags(obj, object_decoder)
            t = object_inline["anno"]
            adapter = TypeAdapter(Annotated[typing.Optional[t], None])
            anno = typing.Optional[t]  # type:ignore
            alias_type = NullableDecoder._annotation(
                object_inline["compiler_annotation"]
            )

            type_declarations.extend(object_inline["type_declarations"])
            decoder_declarations.extend(object_inline["decoder_declarations"])

            compiler_annotation = NullableDecoder._compiler_annotation(
                object_inline["compiler_annotation"]
            )
            decoder_expression = NullableDecoder.decoder_expression(
                object_inline["decoder_expression"]
            )
        case ListFlag(obj=obj):
            object_inline = _prepare_inline_flags(obj, object_decoder)
            t = object_inline["anno"]
            adapter = TypeAdapter(Annotated[list[t], None])  # type:ignore
            anno = list[t]  # type:ignore
            alias_type = ListDecoder._annotation(object_inline["compiler_annotation"])

            type_declarations.extend(object_inline["type_declarations"])
            decoder_declarations.extend(object_inline["decoder_declarations"])
            compiler_annotation = ListDecoder._compiler_annotation(
                object_inline["compiler_annotation"]
            )
            decoder_expression = ListDecoder.decoder_expression(
                object_inline["decoder_expression"]
            )
        case CustomTypeFlag(variants=v):
            if object_decoder is None:
                raise Exception(
                    "Missing an ObjectDecoder argument for CustomTypeDecoder"
                )
            assert 0 < len(v)

            annos = []
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
                object_inline = _prepare_inline_flags(var[1], next_object_decoder)
                variant_decoder_expressions.append(
                    (formatted_constructor, object_inline["decoder_expression"])
                )
                annos.append(object_inline["anno"])
                type_declarations.extend(object_inline["type_declarations"])
                decoder_declarations.extend(object_inline["decoder_declarations"])
                if object_inline["compiler_annotation"]:
                    variants.append(
                        (
                            Elm.variantWith(
                                formatted_constructor,
                                [object_inline["compiler_annotation"]],
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

            alias_type = custom_type_decoder._to_annotation()
            type_declarations = [
                _DeclarationMetaBasic(
                    declaration=custom_type_decoder._to_declaration()
                ),
                *type_declarations,
            ]
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

            object_pipeline = _prepare_pipeline_flags(
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
            compiler_annotation = object_decoder._compiler_annotation(
                Anno.record(object_pipeline["field_annotations"])
            )

            alias_type = object_decoder._to_annotation()

            type_declaration = Elm.alias(
                object_decoder._to_annotation(),
                Anno.record(object_pipeline["field_annotations"]),
            )
            type_declarations.extend(
                [
                    _DeclarationMetaBasic(declaration=type_declaration),
                    *object_pipeline["type_declarations"],
                ]
            )
            decoder_declarations.extend(object_pipeline["decoder_declarations"])
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
            object_pipeline = _prepare_pipeline_flags(
                flag,
                (
                    object_decoder.pipeline_signature(),
                    object_decoder.pipeline_starter_expression(),
                ),
                depth + 1,
                parent_key,
            )
            t = object_pipeline["anno"]  # type:ignore
            type_declaration = Elm.alias(
                object_decoder._to_annotation(),
                Anno.record(object_pipeline["field_annotations"]),
            )
            compiler_annotation = object_decoder._compiler_annotation(
                Anno.record(object_pipeline["field_annotations"])
            )

            adapter = object_pipeline["adapter"]
            anno = t  # type:ignore

            alias_type = Anno.toString(compiler_annotation)
            type_declarations.extend(
                [
                    _DeclarationMetaBasic(declaration=type_declaration),
                    *object_pipeline["type_declarations"],
                ]
            )
            decoder_declarations.extend(object_pipeline["decoder_declarations"])
            decoder_expression = object_decoder.decoder_expression()
        case _:
            raise Exception(f"Can't resolve core_schema type for: {flag}")

    decoder_body = ""

    if decoder_sig:
        sig, _ = decoder_sig
        decoder_body = Elm.declaration(sig.name, decoder_expression, sig)

    return {
        "adapter": adapter,
        "anno": anno,
        "alias_type": alias_type,
        "compiler_annotation": compiler_annotation,
        "decoder_expression": decoder_expression,
        "type_declarations": type_declarations,
        "decoder_declarations": [
            _DeclarationMetaBasic(declaration=decoder_body),
            *decoder_declarations,
        ]
        if decoder_body
        else decoder_declarations,
    }


def _prepare_pipeline_flags(
    flag: ObjectFlag,
    decoder_sig: tuple[Compiler.Signature, Compiler.Expression],
    depth: int = 1,
    parent_key: str | None = None,
) -> PipelineReturn:
    anno: typing.Dict[str, PrimitiveObjectFlagType] = {}
    alias_values: str = ""
    field_annotations: list[tuple[str, Compiler.Annotation]] = []
    pipeline_expressions: list[Compiler.Expression] = []
    type_declarations: list[_DeclarationMetaBasic | _DeclarationMetaStatic] = []
    decoder_declarations: list[_DeclarationMetaBasic | _DeclarationMetaStatic] = []

    for idx, (key, value_flag) in enumerate(flag.obj.items()):
        try:
            assert key not in RESERVED_KEYWORDS
            key = key.replace("\n", "")
            valid_alias_key(key)
            match value_flag:
                case AliasFlag(name=alias_name, obj=alias_obj):
                    object_decoder = ObjectDecoder(alias_name, 1)
                    object_inline = _prepare_inline_flags(alias_obj, object_decoder)
                    type_declarations.append(
                        _DeclarationMetaStatic(
                            static_name=alias_name,
                            declarations=object_inline["type_declarations"],
                        )
                    )
                    decoder_declarations.append(
                        _DeclarationMetaStatic(
                            static_name=alias_name,
                            declarations=object_inline["decoder_declarations"],
                        )
                    )
                    anno[key] = object_inline["anno"]
                    field_annotations.append(
                        (key, object_inline["compiler_annotation"])
                    )
                    match alias_obj:
                        case CustomTypeFlag():
                            pipeline_expressions.append(
                                CustomTypeDecoder.pipeline_expression(
                                    key, object_inline["decoder_expression"]
                                )
                            )
                        case ObjectFlag():
                            pipeline_expressions.append(
                                object_decoder.pipeline_expression(key)
                            )
                    if idx == 0:
                        alias_values += f" {object_decoder.alias(key)}"
                    else:
                        alias_values += f"\n    {object_decoder.nested_alias(key)}"
                case ModelChoiceFieldFlag() as mcf:
                    decoder = ObjectDecoder(key, depth, parent_key)
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
                    anno[key] = mcf.anno()
                    field_annotations.append(
                        (
                            key,
                            Anno.alias(
                                decoder._to_annotation(),
                                Anno.record(
                                    prepared_object_recursive["field_annotations"]
                                ),
                            ),
                        )
                    )
                    type_declaration = Elm.alias(
                        decoder._to_annotation(),
                        Anno.record(prepared_object_recursive["field_annotations"]),
                    )
                    type_declaration = Elm.alias(
                        decoder._to_annotation(),
                        Anno.record(prepared_object_recursive["field_annotations"]),
                    )
                    type_declarations.extend(
                        [
                            _DeclarationMetaBasic(declaration=type_declaration),
                            *prepared_object_recursive["type_declarations"],
                        ]
                    )
                    decoder_declarations.extend(
                        prepared_object_recursive["decoder_declarations"]
                    )
                    pipeline_expressions.append(decoder.pipeline_expression(key))
                    if idx == 0:
                        alias_values += f" {decoder.alias(key)}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias(key)}"

                case ObjectFlag(obj=obj):
                    decoder = ObjectDecoder(key, depth, parent_key)
                    prepared_object_recursive = _prepare_pipeline_flags(
                        ObjectFlag(obj),
                        (
                            decoder.pipeline_signature(),
                            decoder.pipeline_starter_expression(),
                        ),
                        depth + 1,
                        parent_key=decoder._to_annotation(),
                    )
                    anno[key] = type(
                        "K",
                        (BaseModel,),
                        {
                            "__annotations__": prepared_object_recursive[
                                "anno"
                            ].__origin__.__annotations__  # type:ignore
                        },
                    )
                    field_annotations.append(
                        (
                            key,
                            Anno.alias(
                                decoder._to_annotation(),
                                Anno.record(
                                    prepared_object_recursive["field_annotations"]
                                ),
                            ),
                        )
                    )

                    type_declaration = Elm.alias(
                        decoder._to_annotation(),
                        Anno.record(prepared_object_recursive["field_annotations"]),
                    )
                    type_declarations.extend(
                        [
                            _DeclarationMetaBasic(declaration=type_declaration),
                            *prepared_object_recursive["type_declarations"],
                        ]
                    )
                    decoder_declarations.extend(
                        prepared_object_recursive["decoder_declarations"]
                    )
                    pipeline_expressions.append(decoder.pipeline_expression(key))
                    if idx == 0:
                        alias_values += f" {decoder.alias(key)}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias(key)}"

                case ListFlag(obj=obj):
                    decoder = ObjectDecoder(key, depth, parent_key)
                    object_inline = _prepare_inline_flags(obj, decoder)
                    list_decoder = ListDecoder(
                        key,
                        object_inline["compiler_annotation"],
                    )
                    type_declarations.extend(object_inline["type_declarations"])
                    decoder_declarations.extend(object_inline["decoder_declarations"])
                    anno[key] = list[object_inline["anno"]]  # type:ignore
                    field_annotations.append(
                        (key, Anno.list(object_inline["compiler_annotation"]))
                    )
                    pipeline_expressions.append(
                        list_decoder.pipeline_expression(
                            object_inline["decoder_expression"]
                        )
                    )
                    if idx == 0:
                        alias_values += f" {list_decoder.alias()}"
                    else:
                        alias_values += f"\n    {list_decoder.nested_alias()}"

                case CustomTypeFlag(variants=_) as ctf:
                    decoder = ObjectDecoder(key, depth, parent_key)
                    object_inline = _prepare_inline_flags(ctf, decoder)
                    anno[key] = typing.Optional[object_inline["anno"]]  # type:ignore
                    field_annotations.append(
                        (key, object_inline["compiler_annotation"])
                    )

                    type_declarations.extend(object_inline["type_declarations"])
                    decoder_declarations.extend(object_inline["decoder_declarations"])

                    pipeline_expressions.append(
                        CustomTypeDecoder.pipeline_expression(
                            key, object_inline["decoder_expression"]
                        )
                    )
                    if idx == 0:
                        alias_values += f" {decoder.alias(key)}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias(key)}"
                    pass

                case NullableFlag(obj=obj1):
                    object_inline = _prepare_inline_flags(
                        obj1, ObjectDecoder(key, depth, parent_key)
                    )
                    nullable_decoder = NullableDecoder(
                        key,
                        object_inline["compiler_annotation"],
                    )
                    type_declarations.extend(object_inline["type_declarations"])
                    decoder_declarations.extend(object_inline["decoder_declarations"])
                    anno[key] = typing.Optional[object_inline["anno"]]  # type:ignore
                    field_annotations.append(
                        (key, Anno.maybe(object_inline["compiler_annotation"]))
                    )

                    pipeline_expressions.append(
                        nullable_decoder.pipeline_expression(
                            object_inline["decoder_expression"]
                        )
                    )

                    if idx == 0:
                        alias_values += f" {nullable_decoder.alias()}"
                    else:
                        alias_values += f"\n    {nullable_decoder.nested_alias()}"
                case StringFlag():
                    string_decoder = StringDecoder(key)
                    single_prepared = _prepare_inline_flags(value_flag)
                    anno[key] = single_prepared["anno"]
                    field_annotations.append(
                        (key, single_prepared["compiler_annotation"])
                    )

                    if value_flag.literal:
                        pipeline_expressions.append(
                            string_decoder.pipeline_literal_expression(
                                value_flag.literal
                            )
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
                    int_decoder = IntDecoder(key)
                    single_prepared = _prepare_inline_flags(value_flag)
                    anno[key] = single_prepared["anno"]
                    field_annotations.append(
                        (key, single_prepared["compiler_annotation"])
                    )
                    pipeline_expressions.append(int_decoder.pipeline_expression())

                    if idx == 0:
                        alias_values += f" {int_decoder.alias()}"
                    else:
                        alias_values += f"\n    {int_decoder.nested_alias()}"

                case FloatFlag():
                    float_decoder = FloatDecoder(key)
                    single_prepared = _prepare_inline_flags(value_flag)
                    anno[key] = single_prepared["anno"]
                    field_annotations.append(
                        (key, single_prepared["compiler_annotation"])
                    )
                    pipeline_expressions.append(float_decoder.pipeline_expression())

                    if idx == 0:
                        alias_values += f" {float_decoder.alias()}"
                    else:
                        alias_values += f"\n    {float_decoder.nested_alias()}"

                case BoolFlag():
                    bool_decoder = BoolDecoder(key)
                    single_prepared = _prepare_inline_flags(value_flag)
                    anno[key] = single_prepared["anno"]
                    field_annotations.append(
                        (key, single_prepared["compiler_annotation"])
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

    pipeline_decoder = Elm.declaration(
        sig.name,
        Op.pipes(top_pipe, reversed(pipeline_expressions)),
        sig,
    )

    return {
        "adapter": TypeAdapter(
            Annotated[type("K", (BaseModel,), {"__annotations__": anno}), None]
        ),  # type:ignore
        "anno": Annotated[type("K", (BaseModel,), {"__annotations__": anno}), None],  # type:ignore
        "alias_type": "{" + alias_values + "\n    }",
        "alias_extra": "",
        "decoder_extra": "",
        "field_annotations": field_annotations,
        "type_declarations": type_declarations,
        "decoder_declarations": [
            _DeclarationMetaBasic(declaration=pipeline_decoder),
            *decoder_declarations,
        ],
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
