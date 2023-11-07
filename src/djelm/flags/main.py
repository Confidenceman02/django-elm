import typing
from dataclasses import dataclass
from functools import reduce

from pydantic import BaseModel, Strict, TypeAdapter
from typing_extensions import Annotated

# Primitive = typing.Union[str, int, float, bool]
# AllType = typing.Union[
#     "StringFlag",
#     "IntFlag",
#     "FloatFlag",
#     "BoolFlag",
#     typing.List["AllType"],
#     typing.Dict[str, "AllType"],
# ]

_annotated_string = Annotated[str, Strict()]
_annotated_int = Annotated[int, Strict()]
_annotated_float = Annotated[float, Strict()]
_annotated_bool = Annotated[bool, Strict()]

StringAdapter = TypeAdapter(_annotated_string)
IntAdapter = TypeAdapter(_annotated_int)
FloatAdapter = TypeAdapter(_annotated_float)
BoolAdapter = TypeAdapter(_annotated_bool)


@dataclass(slots=True)
class StringFlag:
    adapter = StringAdapter


@dataclass(slots=True)
class IntFlag:
    adapter = IntAdapter


@dataclass(slots=True)
class FloatFlag:
    adapter = FloatAdapter


@dataclass(slots=True)
class BoolFlag:
    adapter = BoolAdapter


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
                    match v:
                        case StringFlag():
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

                        case IntFlag():
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
                        case FloatFlag():
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
                        case BoolFlag():
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
                    raise Exception("Value needs to be a valid Flag type")

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
                            f"Can't resolve core_schema type: {d.core_schema['type']}"
                        )

        return VS

    def parse_dict(self, d):
        for idx, (k, v) in enumerate(d.items()):
            anno = {}
            try:
                match v.core_schema["type"]:
                    case "str":
                        anno[k] = str
                    case "int":
                        anno[k] = int
                    case "float":
                        anno[k] = float
                    case "bool":
                        anno[k] = bool

            except:
                raise Exception("Value needs to be a StringFlag")


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
