import typing
from dataclasses import dataclass

from pydantic import BaseModel, TypeAdapter, validate_call
from typing_extensions import Annotated
from djelm.flags.form.adapters import ModelChoiceFieldAdapter

from djelm.flags.form.primitives import ModelChoiceFieldFlag

from .primitives import (
    BoolFlag,
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
)


PreparedElm = typing.TypedDict("PreparedElm", {"alias_type": str, "decoder_body": str})


@validate_call
def valid_alias_key(k: annotated_alias_key):
    return k


@dataclass(slots=True)
class StringDecoder:
    """Decoder helper for the Elm String primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {StringDecoder._raw_decoder()}"""

    def alias(self) -> str:
        return f"""{self.value} : {StringDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {StringDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.string"

    @staticmethod
    def _raw_type():
        return "String"


@dataclass(slots=True)
class IntDecoder:
    """Decoder helper for the Elm Int primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {IntDecoder._raw_decoder()}"""

    def alias(self):
        return f"""{self.value} : {IntDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {IntDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.int"

    @staticmethod
    def _raw_type():
        return "Int"


@dataclass(slots=True)
class BoolDecoder:
    """Decoder helper for the Elm Bool primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {BoolDecoder._raw_decoder()}"""

    def alias(self):
        return f"""{self.value} : {BoolDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {BoolDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.bool"

    @staticmethod
    def _raw_type():
        return "Bool"


@dataclass(slots=True)
class FloatDecoder:
    """Decoder helper for the Elm Float primitive"""

    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {FloatDecoder._raw_decoder()}"""

    def alias(self):
        return f"""{self.value} : {FloatDecoder._raw_type()}"""

    def nested_alias(self):
        return f""", {self.value} : {FloatDecoder._raw_type()}"""

    @staticmethod
    def _raw_decoder():
        return "Decode.float"

    @staticmethod
    def _raw_type():
        return "Float"


@dataclass(slots=True)
class ListDecoder:
    """Decoder helper for the Elm List primitive"""

    value: str
    targetDecoderName: str
    targetTypeName: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {ListDecoder._raw_decoder(self.targetDecoderName)}"""

    def alias(self):
        return f"""{self.value} : {self._raw_type(self.targetTypeName)}"""

    def nested_alias(self):
        return f""", {self.value} : List {self.targetTypeName}"""

    @staticmethod
    def _raw_decoder(decoder_def: str):
        return f"(Decode.list {decoder_def})"

    @staticmethod
    def _raw_type(targetType: str):
        return f"(List {targetType})"


@dataclass(slots=True)
class NullableDecoder:
    """Decoder helper for the Elm Maybe monad"""

    value: str
    targetDecoderName: str
    targetTypeName: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {NullableDecoder._raw_decoder(self.targetDecoderName)}"""

    def alias(self):
        return f"""{self.value} : Maybe {self.targetTypeName}"""

    def nested_alias(self):
        return f""", {self.value} : Maybe {self.targetTypeName}"""

    @staticmethod
    def _raw_decoder(decoder_def: str):
        return f"(Decode.nullable {decoder_def})"

    @staticmethod
    def _raw_type(targetType: str):
        return f"(Maybe {targetType})"


@dataclass(slots=True)
class ObjectDecoder:
    """Decoder helper for the Elm {} primitive"""

    value: str
    depth: int
    parent_alias: str | None = None

    def pipeline(self):
        return f"""|>  required "{self.value}" {self._to_decoder_name()}"""

    def pipeline_starter(self):
        return f"""{self._to_decoder_annotation()}\n    {self._to_pipeline_succeed()}"""

    def alias(self):
        return f"""{self.value} : {self._to_alias()}"""

    def nested_alias(self):
        return f""", {self.value} : {self._to_alias()}"""

    def _to_alias(self) -> str:
        p = self.parent_alias if self.parent_alias else ""
        return f"{p}{self.value[0].upper()}{self.value[1:]}{self._depth_markers()}"

    def _to_decoder_annotation(self):
        return f"""{self._to_decoder_name()} : Decode.Decoder {self._to_alias()}\n{self._to_decoder_name()} ="""

    def _to_decoder_name(self):
        p = self.parent_alias if self.parent_alias else ""
        return f"""{p.lower() + self.value + self._depth_markers()}Decoder"""

    def _to_alias_definition(self, body: str):
        return f"""\n\ntype alias {self._to_alias()} =\n    {body}"""

    def _to_pipeline_succeed(self):
        return f"""Decode.succeed {self._to_alias()}"""

    def _depth_markers(self) -> str:
        marker = ""
        for _ in range(self.depth):
            marker += "_"
        return marker


ObjHelperReturn = typing.TypedDict(
    "ObjHelperReturn",
    {
        "adapter": TypeAdapter,
        "anno": typing.Dict[str, PrimitiveObjectFlagType],
        "elm_values": PreparedElm,
        "alias_extra": str,
        "decoder_extra": str,
    },
)
SingleHelperReturn = typing.TypedDict(
    "SingleHelperReturn",
    {
        "adapter": TypeAdapter,
        "anno": PrimitiveObjectFlagType,
        "elm_values": PreparedElm,
        "alias_extra": str,
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

        match d:
            case ObjectFlag(obj=_):
                prepared_flags = _prepare_pipeline_flags(d, "Decode.succeed ToModel")
            case ModelChoiceFieldFlag() as mcf:
                prepared_flags = _prepare_pipeline_flags(
                    mcf.obj(), "Decode.succeed ToModel"
                )
                prepared_flags["adapter"] = ModelChoiceFieldAdapter
            case _:
                prepared_flags = _prepare_inline_flags(
                    d, ObjectDecoder("inlineToModel", 1)
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
    d: Flag, object_decoder: ObjectDecoder | None = None, depth: int = 1
) -> SingleHelperReturn:
    adapter: TypeAdapter
    anno: PrimitiveObjectFlagType
    alias_type: str = ""
    decoder_body = ""
    decoder_extra: str = ""
    alias_extra: str = ""
    match d:
        case StringFlag():
            adapter = StringAdapter
            anno = annotated_string  # type:ignore
            alias_type = StringDecoder._raw_type()
            decoder_body = StringDecoder._raw_decoder()
        case IntFlag():
            adapter = IntAdapter
            anno = annotated_int  # type:ignore
            alias_type = IntDecoder._raw_type()
            decoder_body = IntDecoder._raw_decoder()
        case FloatFlag():
            adapter = FloatAdapter
            anno = annotated_float  # type:ignore
            alias_type = FloatDecoder._raw_type()
            decoder_body = FloatDecoder._raw_decoder()
        case BoolFlag():
            adapter = BoolAdapter
            anno = annotated_bool  # type:ignore
            alias_type = BoolDecoder._raw_type()
            decoder_body = BoolDecoder._raw_decoder()
        case NullableFlag(obj=obj):
            single_flag = _prepare_inline_flags(obj, object_decoder)
            t = single_flag["anno"]
            adapter = TypeAdapter(Annotated[typing.Optional[t], None])
            anno = typing.Optional[t]  # type:ignore
            alias_type = NullableDecoder._raw_type(
                single_flag["elm_values"]["alias_type"]
            )
            alias_extra += single_flag["alias_extra"]
            decoder_body = NullableDecoder._raw_decoder(
                single_flag["elm_values"]["decoder_body"]
            )
            decoder_extra += single_flag["decoder_extra"]
        case ListFlag(obj=obj):
            single_flag = _prepare_inline_flags(obj, object_decoder)
            t = single_flag["anno"]
            adapter = TypeAdapter(Annotated[list[t], None])  # type:ignore
            anno = list[t]  # type:ignore
            alias_type = ListDecoder._raw_type(single_flag["elm_values"]["alias_type"])
            alias_extra += single_flag["alias_extra"]
            decoder_body = ListDecoder._raw_decoder(
                single_flag["elm_values"]["decoder_body"]
            )
            decoder_extra += single_flag["decoder_extra"]
        case ModelChoiceFieldFlag() as mcf:
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
            if object_decoder._to_alias() != "InlineToModel_":
                parent_key = object_decoder._to_alias()

            object_flag = _prepare_pipeline_flags(
                mcf.obj(),
                object_decoder.pipeline_starter(),
                depth + 1,
                parent_key,
            )
            adapter = ModelChoiceFieldAdapter
            # Use internal annotation
            anno = mcf.anno()

            alias_type = object_decoder._to_alias()
            alias_extra = object_decoder._to_alias_definition(
                object_flag["elm_values"]["alias_type"]
            )
            decoder_body = object_decoder._to_decoder_name()
            decoder_extra = f"\n\n{object_flag['elm_values']['decoder_body']}"
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
            if object_decoder._to_alias() != "InlineToModel_":
                parent_key = object_decoder._to_alias()
            object_flag = _prepare_pipeline_flags(
                d,
                object_decoder.pipeline_starter(),
                depth + 1,
                parent_key,
            )
            t = object_flag["anno"]  # type:ignore

            adapter = object_flag["adapter"]
            anno = t  # type:ignore
            alias_type = object_decoder._to_alias()
            alias_extra = object_decoder._to_alias_definition(
                object_flag["elm_values"]["alias_type"]
            )
            decoder_body = object_decoder._to_decoder_name()
            decoder_extra = f"\n\n{object_flag['elm_values']['decoder_body']}"
        case _:
            raise Exception(f"Can't resolve core_schema type for: {d}")
    return {
        "adapter": adapter,
        "anno": anno,
        "elm_values": {
            "alias_type": alias_type,
            "decoder_body": decoder_body,
        },
        "alias_extra": alias_extra,
        "decoder_extra": decoder_extra,
    }


def _prepare_pipeline_flags(
    d: Flag, decoder_start: str, depth: int = 1, parent_key: str | None = None
) -> ObjHelperReturn:
    anno: typing.Dict[str, PrimitiveObjectFlagType] = {}
    pipeline_decoder: str = decoder_start
    alias_values: str = ""
    decoder_extra: str = ""
    alias_extra: str = ""

    assert isinstance(d, ObjectFlag)

    for idx, (k, v) in enumerate(d.obj.items()):
        try:
            k = k.replace("\n", "")
            valid_alias_key(k)
            match v:
                case ModelChoiceFieldFlag() as mcf:
                    decoder = ObjectDecoder(k, depth, parent_key)
                    prepared_object_recursive = _prepare_pipeline_flags(
                        # Use built in flags
                        mcf.obj(),
                        decoder.pipeline_starter(),
                        depth + 1,
                        decoder._to_alias(),
                    )

                    # Use built in annotations
                    anno[k] = mcf.anno()
                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['elm_values']['decoder_body']}"
                    )
                    alias_extra += decoder._to_alias_definition(
                        prepared_object_recursive["elm_values"]["alias_type"]
                    )
                    pipeline_decoder += f"""\n        {decoder.pipeline()}"""
                    if idx == 0:
                        alias_values += f" {decoder.alias()}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias()}"

                case ObjectFlag(obj=obj):
                    decoder = ObjectDecoder(k, depth, parent_key)
                    prepared_object_recursive = _prepare_pipeline_flags(
                        ObjectFlag(obj),
                        decoder.pipeline_starter(),
                        depth + 1,
                        decoder._to_alias(),
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

                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['elm_values']['decoder_body']}"
                    )
                    alias_extra += decoder._to_alias_definition(
                        prepared_object_recursive["elm_values"]["alias_type"]
                    )
                    pipeline_decoder += f"""\n        {decoder.pipeline()}"""
                    if idx == 0:
                        alias_values += f" {decoder.alias()}"
                    else:
                        alias_values += f"\n    {decoder.nested_alias()}"

                case ListFlag(obj=obj):
                    decoder = ObjectDecoder(k, depth, parent_key)
                    single_flag = _prepare_inline_flags(obj, decoder)
                    list_decoder = ListDecoder(
                        k,
                        single_flag["elm_values"]["decoder_body"],
                        single_flag["elm_values"]["alias_type"],
                    )
                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]
                    anno[k] = list[single_flag["anno"]]  # type:ignore

                    pipeline_decoder += f"""\n        {list_decoder.pipeline()}"""

                    if idx == 0:
                        alias_values += f" {list_decoder.alias()}"
                    else:
                        alias_values += f"\n    {list_decoder.nested_alias()}"
                case NullableFlag(obj=obj1):
                    single_flag = _prepare_inline_flags(
                        obj1, ObjectDecoder(k, depth, parent_key)
                    )
                    nullable_decoder = NullableDecoder(
                        k,
                        single_flag["elm_values"]["decoder_body"],
                        single_flag["elm_values"]["alias_type"],
                    )
                    alias_extra += single_flag["alias_extra"]
                    decoder_extra += single_flag["decoder_extra"]
                    anno[k] = typing.Optional[single_flag["anno"]]  # type:ignore

                    pipeline_decoder += f"""\n        {nullable_decoder.pipeline()}"""

                    if idx == 0:
                        alias_values += f" {nullable_decoder.alias()}"
                    else:
                        alias_values += f"\n    {nullable_decoder.nested_alias()}"
                case StringFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {StringDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {StringDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {StringDecoder(k).nested_alias()}"

                case IntFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {IntDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {IntDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {IntDecoder(k).nested_alias()}"

                case FloatFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {FloatDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {FloatDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {FloatDecoder(k).nested_alias()}"

                case BoolFlag():
                    single_prepared = _prepare_inline_flags(v)
                    anno[k] = single_prepared["anno"]
                    pipeline_decoder += f"""\n        {BoolDecoder(k).pipeline()}"""
                    if idx == 0:
                        alias_values += f" {BoolDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {BoolDecoder(k).nested_alias()}"

                case _:
                    raise Exception("Unsopported type")
        except Exception as err:
            raise err
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
