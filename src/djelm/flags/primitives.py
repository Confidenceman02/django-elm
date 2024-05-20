from dataclasses import dataclass
import typing

from pydantic import BaseModel


class Flag:
    pass


@dataclass(slots=True)
class StringFlag(Flag):
    """Flag for the Elm String primitive

    literal :
        Will match against the passed string literal.

        Generated decoders will also express the string literal
    """

    literal: str | None = None


@dataclass(slots=True)
class IntFlag(Flag):
    """Flag for the Elm Int primitive"""


@dataclass(slots=True)
class FloatFlag(Flag):
    """Flag for the Elm Float primitive"""


@dataclass(slots=True)
class BoolFlag(Flag):
    """Flag for the Elm Bool primitive"""


@dataclass(slots=True)
class NullableFlag(Flag):
    """Flag for the Elm Maybe monad"""

    obj: Flag


@dataclass(slots=True)
class ListFlag(Flag):
    """Flag for the Elm List primitive"""

    obj: Flag


@dataclass(slots=True)
class ObjectFlag(Flag):
    """Flag for the Elm {} primitive"""

    obj: typing.Dict[str, Flag]


@dataclass(slots=True)
class CustomTypeFlag(Flag):
    """
    A Flag for an Elm custom type.

    <https://guide.elm-lang.org/types/custom_types>

    variants = A list of tuples that specify the a discriminator and flag.

    i.e.
            FlagModel = Flags(CustomTypeFlag(variants=[("Custom1",StringFLag()), ("Custom2",IntFlag())]))

            Turns into the the Elm type:

            type SomeCustomType
                = Custom1 String
                | Custom2 Int

            Then we parse a valid data structure:

            FlagModel.parse("Hi there")
    """

    variants: list[tuple[str, Flag]]


FlagsObject = dict[str, "PrimitiveFlag"]
FlagsList = list["PrimitiveFlag"]
FlagsNullable = typing.Union[type[str], type[int], type[float], type[bool], type[None]]
PrimitiveObjectFlagType = (
    type[str]
    | type[int]
    | type[float]
    | type[bool]
    | type[BaseModel]
    | type[list]
    | FlagsNullable
)
PrimitiveFlag = (
    str | int | float | bool | FlagsObject | FlagsList | FlagsNullable | None
)
