from dataclasses import dataclass
import typing

from pydantic import BaseModel


class Flag:
    pass


@dataclass(slots=True)
class StringFlag(Flag):
    """Flag for the Elm String primitive"""


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
