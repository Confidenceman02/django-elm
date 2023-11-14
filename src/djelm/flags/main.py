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
class StringFlag:
    adapter = _StringAdapter


@dataclass(slots=True)
class IntFlag:
    adapter = _IntAdapter


@dataclass(slots=True)
class FloatFlag:
    adapter = _FloatAdapter


@dataclass(slots=True)
class BoolFlag:
    adapter = _BoolAdapter


@dataclass(slots=True)
class ObjectFlag:
    obj: typing.Dict[str, "Primitive"]


Primitive = StringFlag | IntFlag | FloatFlag | BoolFlag | ObjectFlag
FlagsObject = dict[str, "PrimitiveFlag"]
FlagsList = list["PrimitiveFlag"]
FlagsArgListType = list["PrimitiveFlagType"]
PrimitiveFlagType = type[str] | type[int] | type[float] | type[bool] | type[BaseModel]
PrimitiveFlag = str | int | float | bool | FlagsObject | FlagsList

ObjHelperReturn = typing.TypedDict(
    "ObjHelperReturn",
    {
        "anno": typing.Dict[str, PrimitiveFlagType],
        "pipeline_decoder": str,
        "alias_values": str,
    },
)


@dataclass(slots=True)
class StringDecoder:
    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" Decode.string"""

    def alias(self) -> str:
        return f"""{self.value} : String"""

    def nested_alias(self):
        return f""", {self.value} : String"""


@dataclass(slots=True)
class IntDecoder:
    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" Decode.int"""

    def alias(self):
        return f"""{self.value} : Int"""

    def nested_alias(self):
        return f""", {self.value} : Int"""


@dataclass(slots=True)
class BoolDecoder:
    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" Decode.bool"""

    def alias(self):
        return f"""{self.value} : Bool"""

    def nested_alias(self):
        return f""", {self.value} : Bool"""


@dataclass(slots=True)
class FloatDecoder:
    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" Decode.float"""

    def alias(self):
        return f"""{self.value} : Float"""

    def nested_alias(self):
        return f""", {self.value} : Float"""


@dataclass(slots=True)
class ObjectDecoder:
    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" {self.value}Decoder"""

    def pipeline_starter(self):
        return f"""{self._to_decoder_annotation()}\n    {self._to_pipeline_succeed()}"""

    def alias(self):
        return f"""{self.value} : {self._to_alias()}"""

    def nested_alias(self):
        return f""", {self.value} : {self._to_alias()}"""

    def _to_alias(self) -> str:
        return self.value[0].upper() + self.value[1:]

    def _to_decoder_annotation(self):
        return f"""{self.value}Decoder : Decode.Decoder {self._to_alias()}\n{self.value}Decoder ="""

    def _to_alias_definition(self, body: str):
        return f"""\n\ntype alias {self._to_alias()} =\n    {body}"""

    def _to_pipeline_succeed(self):
        return f"""Decode.succeed {self._to_alias()}"""


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
                            "decoder_body": "Decode.string",
                        }
                    case IntFlag():
                        return {
                            "alias_type": "Int",
                            "decoder_body": "Decode.int",
                        }
                    case FloatFlag():
                        return {
                            "alias_type": "Float",
                            "decoder_body": "Decode.float",
                        }
                    case BoolFlag():
                        return {
                            "alias_type": "Bool",
                            "decoder_body": "Decode.bool",
                        }
                    case _:
                        raise Exception(
                            f"Can't resolve core_schema type: {d.adapter.core_schema['type']}"
                        )

        return VS


def _prepare_object_helper(d: ObjectFlag, decoder_start: str) -> ObjHelperReturn:
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
                        ObjectFlag(obj), ObjectDecoder(k).pipeline_starter()
                    )
                    anno[k] = type(
                        "K",
                        (BaseModel,),
                        {"__annotations__": prepared_object_recursive["anno"]},
                    )
                    decoder_extra += (
                        f"\n\n{prepared_object_recursive['pipeline_decoder']}"
                    )
                    alias_extra += ObjectDecoder(k)._to_alias_definition(
                        prepared_object_recursive["alias_values"]
                    )
                    pipeline_decoder += f"""\n        {ObjectDecoder(k).pipeline()}"""
                    if idx == 0:
                        alias_values += f" {ObjectDecoder(k).alias()}"
                    else:
                        alias_values += f"\n    {ObjectDecoder(k).nested_alias()}"

                # TODO Handle ListFlag
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

    You can pass a dict or a single flag type.

    f1 = Flags({"hello": StringFlag})
    f1.parse({"hello": "world"}) -> '{"hello":"world"}'

    f2 = Flags(StringFlag)
    f2.parse("hello world") -> '"hello world"'
    """

    if typing.TYPE_CHECKING:
        parse: typing.Callable[[PrimitiveFlag], str]
        to_elm_parser_data: typing.Callable[[], dict[str, str]]

    pass
