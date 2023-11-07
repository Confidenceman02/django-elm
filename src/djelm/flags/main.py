import typing
from dataclasses import dataclass
from functools import reduce

from pydantic import BaseModel, Strict, TypeAdapter
from typing_extensions import Annotated

Primitive = str | int | float | bool
DictType = typing.Dict[str, Primitive]
ListType = typing.List[Primitive]

_annotated_string = Annotated[str, Strict()]
_annotated_int = Annotated[int, Strict()]
_annotated_float = Annotated[float, Strict()]
_annotated_bool = Annotated[bool, Strict()]

StringFlag = TypeAdapter(_annotated_string)
IntFlag = TypeAdapter(_annotated_int)
FloatFlag = TypeAdapter(_annotated_float)
BoolFlag = TypeAdapter(_annotated_bool)
ListFlag = TypeAdapter(typing.List[Primitive])
DictFlag = TypeAdapter(typing.Dict[str, Primitive])


@dataclass(slots=True)
class StringDecoder:
    value: str

    def pipeline(self):
        return f"""|>  required "{self.value}" Decode.string"""

    def alias(self):
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


class FlagMetaClass(type):
    def __new__(cls, class_name, bases, attrs):
        return type(class_name, bases, attrs)


class BaseFlag(metaclass=FlagMetaClass):
    def __new__(cls, d):
        if isinstance(d, dict):
            anno = {}
            pipeline_decoder: list[str] = ["Decode.succeed ToModel"]
            alias_values: list[str] = []
            for idx, (k, v) in enumerate(d.items()):
                try:
                    match v.core_schema["type"]:
                        case "str":
                            anno[k] = str
                            pipeline_decoder.append(
                                f"""\n        {StringDecoder(k).pipeline()}"""
                            )
                            if idx == 0:
                                alias_values.append(f" {StringDecoder(k).alias()}")
                            else:
                                alias_values.append(
                                    f"\n    {StringDecoder(k).nested_alias()}"
                                )

                        case "int":
                            anno[k] = int
                            pipeline_decoder.append(
                                f"""\n        {IntDecoder(k).pipeline()}"""
                            )
                            if idx == 0:
                                alias_values.append(f" {IntDecoder(k).alias()}")
                            else:
                                alias_values.append(
                                    f"\n    {IntDecoder(k).nested_alias()}"
                                )
                        case "float":
                            anno[k] = int
                            pipeline_decoder.append(
                                f"""\n        {FloatDecoder(k).pipeline()}"""
                            )
                            if idx == 0:
                                alias_values.append(f" {FloatDecoder(k).alias()}")
                            else:
                                alias_values.append(
                                    f"\n    {FloatDecoder(k).nested_alias()}"
                                )
                        case "bool":
                            anno[k] = bool
                            pipeline_decoder.append(
                                f"""\n        {BoolDecoder(k).pipeline()}"""
                            )
                            if idx == 0:
                                alias_values.append(f" {BoolDecoder(k).alias()}")
                            else:
                                alias_values.append(
                                    f"\n    {BoolDecoder(k).nested_alias()}"
                                )
                        case _:
                            raise Exception("Unsopported type")
                except:
                    raise Exception("Value needs to be a StringFlag")

            K = type("K", (BaseModel,), {"__annotations__": anno})

            class VD:
                """
                Validtes a dict flag input.
                """

                @staticmethod
                def parse(input) -> str:
                    return K.model_validate(input).model_dump_json()

                @staticmethod
                def to_elm_parser_data() -> dict[str, str]:
                    alias_type = reduce(
                        lambda acc, v: acc + v, iter(["{", *alias_values, "\n    }"])
                    )
                    decoder_body = reduce(
                        lambda acc, v: acc + v, iter(pipeline_decoder)
                    )
                    return {"alias_type": alias_type, "decoder_body": decoder_body}

            return VD
        if isinstance(d, TypeAdapter):

            class VS:
                """Validates a single flag input"""

                @staticmethod
                def parse(input) -> str:
                    # TODO check for List
                    d.validate_python(input)
                    return d.dump_json(input).decode("utf-8")

                @staticmethod
                def to_elm_parser_data() -> dict[str, str]:
                    match d.core_schema["type"]:
                        case "str":
                            return {
                                "alias_type": "String",
                                "decoder_body": "Decode.string",
                            }
                        case "int":
                            return {
                                "alias_type": "Int",
                                "decoder_body": "Decode.int",
                            }
                        case "float":
                            return {
                                "alias_type": "Float",
                                "decoder_body": "Decode.float",
                            }
                        case "bool":
                            return {
                                "alias_type": "Bool",
                                "decoder_body": "Decode.bool",
                            }
                        case _:
                            raise Exception(
                                f"Can't resolve core_schema type: {d.core_schema['type']}"
                            )

            return VS

        raise Exception(
            """
Input needs to be a dict of field names to Flag types or a single flag type

e.g.

Flags({"hello": StringFlag}) # dict of field names to flag types

Flags(StringFlag) # single flag type
"""
        )


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
        parse: typing.Callable[[DictType | Primitive], str]
        to_elm_parser_data: typing.Callable[[], dict[str, str]]

    pass
