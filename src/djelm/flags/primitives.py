from dataclasses import dataclass, field
from typing import Callable

from pydantic import BaseModel

_KEY = object()

type ToGeneric = Callable[[Context], Flag | GenericInContext]
type GenericList = tuple[set[str], ToGeneric]


class Flag:
    pass


@dataclass(slots=True)
class TypeVarFlag(Flag):
    """
    Flag for a generic type variable
    """

    name: str


@dataclass(slots=True)
class UnitFlag(Flag):
    """
    Flag for the Elm Unit primitive

    Unit values will validate against any python value and then ignore it.
    """


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

    obj: dict[str, Flag]


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


class GenericInContext:
    def __init__(self, key: object, param: str) -> None:
        if key is not _KEY:
            raise TypeError(
                "GenericInContext cannot be instantiated directly. "
                "It is created and provided internally by the framework."
            )
        self.param = param


class Context:
    def __init__(self, generics: set[str]) -> None:
        self.generics = generics

    def get(self, param: str) -> GenericInContext | None:
        if param in self.generics:
            return GenericInContext(_KEY, param)
        return None


@dataclass(slots=True)
class AliasFlag(Flag):
    """Flag for creating a static alias.

    This is handy for when you have reusable data structures that
    other flags can reference.

    Example:

        Field = AliasFlag("Field", ObjectFlag({"name": StringFlag(), "scope": StringFlag()}))
        Program = ObjectFlag({"some_field": Field, "some_other_field": Field})
        |
        |
        V
        type alias ToModel =
            { some_field : Field_
            , some_other_field : Field_
            }

        type alias Field_ =
            { name : String
            , scope : String
            }

    The AliasFlag can be referenced at any depth of a flag tree and only one of that alias will be generated with
    the static name provided.

    Params:
        name: The static name of the alias
        obj: The Flag object
    """

    name: str
    obj: ObjectFlag | CustomTypeFlag
    _vars: GenericList | None = None

    @property
    def vars(self) -> GenericList | None:
        if self._vars is None:
            return None
        return self._vars

    def _set_vars(
        self, new_vars: GenericList, to_generic: ToGeneric, *, key: object
    ) -> None:
        if key is not _KEY:
            raise PermissionError("Unauthorized call to _set_vars")
        self._vars = new_vars


class GenericFlag:
    call: ToGeneric

    def __init__(self, call: ToGeneric) -> None:
        pass


class Generics1:
    """
    A generic variable placeholder

    Flags with generics are intended to be reusable.

    Setting up:

        ReusableFoo = Generics1("a", AliasFlag("Foo", ObjectFlag({"b": Context(lambda ctx: ctx.get("a")})))

    Usage:
        SomeIntFlag = ReusableFoo(lambda ctx: IntFlag())
        SomeStringFlag = ReusableFoo(lambda ctx: StringFlag(literal="Foo"))

        Flags = ObjectFlag({"foo": SomeIntFlag, "bar": SomeStringFlag})

    Result:
        You end up with an Elm model that looks like the following:

                type alias ToModel =
                    { foo : Foo_ Int
                    , bar : Foo_ String
                    }

                type alias Foo_ a =
                    { b : a }

    Args:
        with_context:
            A function that takes a context and returns either a Flag or a GenericInContext.
            The context holds all generics that are available for that flag.

    Constriants:
        If generics are added to AliasFlag's and not consumed, the Elm compiler will error.
    """

    def __init__(self, var1: str, flag: AliasFlag):
        self.var1 = var1
        self.flag = flag

    def __call__(
        self, with_context: Callable[[Context], Flag | GenericInContext]
    ) -> AliasFlag:
        self.flag._set_vars((set([self.var1]), with_context), with_context, key=_KEY)
        return self.flag


type FlagsObject = dict[str, "PrimitiveFlag"]
type FlagsList = list["PrimitiveFlag"]
type FlagsNullable = type[str] | type[int] | type[float] | type[bool] | type[None]
type PrimitiveObjectFlagType = (
    type[str]
    | type[int]
    | type[float]
    | type[bool]
    | type[BaseModel]
    | type[list]
    | FlagsNullable
)
type PrimitiveFlag = (
    str | int | float | bool | FlagsObject | FlagsList | FlagsNullable | None
)
