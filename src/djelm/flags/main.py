from pydantic import BaseModel, Strict, TypeAdapter
from typing_extensions import Annotated

_annotated_string = Annotated[str, Strict()]
_annotated_int = Annotated[int, Strict()]

StringFlag = TypeAdapter(_annotated_string)
IntFlag = TypeAdapter(_annotated_int)


class FlagMetaClass(type):
    def __new__(cls, class_name, bases, attrs):
        return type(class_name, bases, attrs)


class BaseFlag(metaclass=FlagMetaClass):
    def __new__(cls, d):
        if isinstance(d, dict):
            anno = {}
            for k, v in d.items():
                try:
                    match v.core_schema["type"]:
                        case "str":
                            anno[k] = str
                        case "int":
                            anno[k] = int
                        case _:
                            raise Exception("Unsopported type")
                except:
                    raise Exception("Value needs to be a StringFlag")

            K = type("K", (BaseModel,), {"__annotations__": anno})

            class T:
                @staticmethod
                def parse(input) -> str:
                    return K.model_validate(input).model_dump_json()

            return T

        raise Exception("Arg needs to be a dict")


class Flags(BaseFlag):
    """
    A class for validating djelm flags that are used in Elm programs.

    You can pass a dict or a single flag type.

    f1 = Flags({"hello": StringFlag})
    f1.parse({"hello": "world"}) -> '{"hello":"world"}'

    f2 = Flags(StringFlag)
    f2.parse("hello world") -> '"hello world"'
    """

    pass
