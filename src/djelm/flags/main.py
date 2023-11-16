import typing
from dataclasses import dataclass

from pydantic import BaseModel, Strict, TypeAdapter
from typing_extensions import Annotated


_annotated_string = Annotated[str, Strict()]
_annotated_int = Annotated[int, Strict()]
_annotated_float = Annotated[float, Strict()]
_annotated_bool = Annotated[bool, Strict()]


_StringAdapter = TypeAdapter(_annotated_string)
_IntAdapter = TypeAdapter(_annotated_int)
_FloatAdapter = TypeAdapter(_annotated_float)
_BoolAdapter = TypeAdapter(_annotated_bool)


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
        return f"""{self.value} : List {self.targetTypeName}"""

    def nested_alias(self):
        return f""", {self.value} : List {self.targetTypeName}"""

    @staticmethod
    def _raw_decoder(decoder_def: str):
        return f"(Decode.list {decoder_def})"


@dataclass(slots=True)
class ObjectDecoder:
    """Decoder helper for the Elm {} primitive"""

    value: str
    depth: int

    def pipeline(self):
        return f"""|>  required "{self.value}" {self.value + self._depth_markers()}Decoder"""

    def pipeline_starter(self):
        return f"""{self._to_decoder_annotation()}\n    {self._to_pipeline_succeed()}"""

    def alias(self):
        return f"""{self.value} : {self._to_alias()}"""

    def nested_alias(self):
        return f""", {self.value} : {self._to_alias()}"""

    def _to_alias(self) -> str:
        return self.value[0].upper() + self.value[1:] + self._depth_markers()

    def _to_decoder_annotation(self):
        return f"""{self.value + self._depth_markers()}Decoder : Decode.Decoder {self._to_alias()}\n{self._to_decoder_name()} ="""

    def _to_decoder_name(self):
        return f"""{self.value + self._depth_markers()}Decoder"""

    def _to_alias_definition(self, body: str):
        return f"""\n\ntype alias {self._to_alias()} =\n    {body}"""

    def _to_pipeline_succeed(self):
        return f"""Decode.succeed {self._to_alias()}"""

    def _depth_markers(self) -> str:
        marker = ""
        for _ in range(self.depth):
            marker += "_"
        return marker


@dataclass(slots=True)
class StringFlag:
    """Flag for the Elm String primitive"""

    adapter = _StringAdapter
    t = str
    elm_t = StringDecoder._raw_type()
    decoder = StringDecoder._raw_decoder()


@dataclass(slots=True)
class IntFlag:
    """Flag for the Elm Int primitive"""

    adapter = _IntAdapter
    t = int
    elm_t = IntDecoder._raw_type()
    decoder = IntDecoder._raw_decoder()


@dataclass(slots=True)
class FloatFlag:
    """Flag for the Elm Float primitive"""

    adapter = _FloatAdapter
    t = float
    elm_t = FloatDecoder._raw_type()
    decoder = FloatDecoder._raw_decoder()


@dataclass(slots=True)
class BoolFlag:
    """Flag for the Elm Bool primitive"""

    adapter = _BoolAdapter
    t = bool
    elm_t = BoolDecoder._raw_type()
    decoder = BoolDecoder._raw_decoder()


@dataclass(slots=True)
class ListFlag:
    """Flag for the Elm List primitive"""

    obj: "Primitive"


@dataclass(slots=True)
class ObjectFlag:
    """Flag for the Elm {} primitive"""

    obj: typing.Dict[str, "Primitive"]


Primitive = StringFlag | IntFlag | FloatFlag | BoolFlag | ListFlag | ObjectFlag
FlagsObject = dict[str, "PrimitiveFlag"]
FlagsList = list["PrimitiveFlag"]
PrimitiveFlagType = (
    type[str] | type[int] | type[float] | type[bool] | type[BaseModel] | type[list]
)
PrimitiveFlag = str | int | float | bool | FlagsObject | FlagsList

ObjHelperReturn = typing.TypedDict(
    "ObjHelperReturn",
    {
        "anno": typing.Dict[str, PrimitiveFlagType],
        "pipeline_decoder": str,
        "alias_values": str,
    },
)


class FlagMetaClass(type):
    def __new__(cls, class_name, bases, attrs):
        return type(class_name, bases, attrs)


class BaseFlag(metaclass=FlagMetaClass):
    def __new__(cls, d):
        if isinstance(d, ObjectFlag):
            prepared_object = _prepare_object_helper(d, "Decode.succeed ToModel")

            K = type("K", (BaseModel,), {"__annotations__": prepared_object["anno"]})

            class VD:
                """
                Validates ObjectFlag input.
                """

                @staticmethod
                def parse(input) -> str:
                    return K.model_validate(input).model_dump_json()

                @staticmethod
                def to_elm_parser_data() -> dict[str, str]:
                    alias_type = prepared_object["alias_values"]
                    return {
                        "alias_type": alias_type,
                        "decoder_body": prepared_object["pipeline_decoder"],
                    }

            return VD

        class VS:
            """Validates a single flag input"""

            @staticmethod
            def parse(input) -> str:
                d.adapter.validate_python(input)
                return d.adapter.dump_json(input).decode("utf-8")

            @staticmethod
            def to_elm_parser_data() -> dict[str, str]:
                match d:
                    case StringFlag():
                        return {
                            "alias_type": "String",
                            "decoder_body": StringDecoder._raw_decoder(),
                        }
                    case IntFlag():
                        return {
                            "alias_type": "Int",
                            "decoder_body": IntDecoder._raw_decoder(),
                        }
                    case FloatFlag():
                        return {
                            "alias_type": "Float",
                            "decoder_body": FloatDecoder._raw_decoder(),
                        }
                    case BoolFlag():
                        return {
                            "alias_type": "Bool",
                            "decoder_body": BoolDecoder._raw_decoder(),
                        }
                    case _:
                        raise Exception(
                            f"Can't resolve core_schema type: {d.adapter.core_schema['type']}"
                        )

        assert isinstance(d, (StringFlag, IntFlag, FloatFlag, BoolFlag))

        return VS


def _prepare_object_helper(
    d: ObjectFlag, decoder_start: str, depth: int = 1
) -> ObjHelperReturn:
    anno: typing.Dict[str, PrimitiveFlagType] = {}
    pipeline_decoder: str = decoder_start
    alias_values: str = ""
    decoder_extra: str = ""
    alias_extra: str = ""
    for idx, (k, v) in enumerate(d.obj.items()):
        try:
            match v:
                case StringFlag():
                    anno[k] = str
                    pipeline_decoder += f"""\n        {StringDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {StringDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {StringDecoder(k).nested_alias()}"

                case IntFlag():
                    anno[k] = int
                    pipeline_decoder += f"""\n        {IntDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {IntDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {IntDecoder(k).nested_alias()}"

                case FloatFlag():
                    anno[k] = int
                    pipeline_decoder += f"""\n        {FloatDecoder(k).pipeline()}"""

                    if idx == 0:
                        alias_values += f" {FloatDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {FloatDecoder(k).nested_alias()}"

                case BoolFlag():
                    anno[k] = bool
                    pipeline_decoder += f"""\n        {BoolDecoder(k).pipeline()}"""
                    if idx == 0:
                        alias_values += f" {BoolDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {BoolDecoder(k).nested_alias()}"
                case ObjectFlag(obj=obj):
                    prepared_object_recursive = _prepare_object_helper(
                        ObjectFlag(obj),
                        ObjectDecoder(k, depth).pipeline_starter(),
                        depth + 1,
                    )
                    anno[k] = type(
                        "K",
                        (BaseModel,),
                        {"__annotations__": prepared_object_recursive["anno"]},
                    )
                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['pipeline_decoder']}"
                    )
                    alias_extra += ObjectDecoder(k, depth)._to_alias_definition(
                        prepared_object_recursive["alias_values"]
                    )
                    pipeline_decoder += (
                        f"""\n        {ObjectDecoder(k, depth).pipeline()}"""
                    )
                    if idx == 0:
                        alias_values += f" {ObjectDecoder(k, depth).alias()}"
                    else:
                        alias_values += (
                            f"\n    {ObjectDecoder(k, depth).nested_alias()}"
                        )

                case ListFlag(obj=obj):
                    match obj:
                        case ListFlag(obj=obj1):
                            raise Exception(
                                "djelm doesn't support a multi-dimensional list types"
                            )
                        case ObjectFlag(obj=obj1):
                            prepared_object_recursive = _prepare_object_helper(
                                ObjectFlag(obj1),
                                ObjectDecoder(k, depth).pipeline_starter(),
                                depth + 1,
                            )
                            anno[k] = typing.List[
                                type(
                                    "K",
                                    (BaseModel,),
                                    {
                                        "__annotations__": prepared_object_recursive[
                                            "anno"
                                        ]
                                    },
                                )
                            ]
                            decoder_extra += (
                                f"\n\n{prepared_object_recursive['pipeline_decoder']}"
                            )
                            alias_extra += ObjectDecoder(k, depth)._to_alias_definition(
                                prepared_object_recursive["alias_values"]
                            )
                            object_decoder = ObjectDecoder(k, depth)
                            list_decoder = ListDecoder(
                                k,
                                object_decoder._to_decoder_name(),
                                object_decoder._to_alias(),
                            )
                            pipeline_decoder += (
                                f"""\n        {list_decoder.pipeline()}"""
                            )

                            if idx == 0:
                                alias_values += f" {list_decoder.alias()}"
                            else:
                                alias_values += f"\n    {list_decoder.nested_alias()}"
                        case other_flag:
                            anno[k] = list[other_flag.t]
                            list_decoder = ListDecoder(
                                k, other_flag.decoder, other_flag.elm_t
                            )
                            pipeline_decoder += (
                                f"""\n        {list_decoder.pipeline()}"""
                            )

                            if idx == 0:
                                alias_values += f" {list_decoder.alias()}"
                            else:
                                alias_values += f"\n    {list_decoder.nested_alias()}"

                case _:
                    raise Exception("Unsopported type")
        except:
            raise Exception("Value needs to be a valid Flag type")
    return {
        "anno": anno,
        "pipeline_decoder": pipeline_decoder + decoder_extra,
        "alias_values": "{" + alias_values + "\n    }" + alias_extra,
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
