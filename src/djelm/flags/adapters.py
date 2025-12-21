from typing_extensions import Annotated
import typing

from pydantic import Field, Strict, TypeAdapter


def string_literal_adapter(v: str):
    T = typing.Literal[v]
    return TypeAdapter(T)


def annotated_string_literal(v: str):
    T = typing.Literal[v]
    return Annotated[T, None]


annotated_string = Annotated[str, Strict()]
annotated_int = Annotated[int, Strict()]
annotated_float = Annotated[float, Strict()]
annotated_bool = Annotated[bool, Strict()]
annotated_alias_key = Annotated[str, Field(pattern=r"^[a-z][A-Za-z0-9_]*$")]

StringAdapter = TypeAdapter(annotated_string)
IntAdapter = TypeAdapter(annotated_int)
FloatAdapter = TypeAdapter(annotated_float)
BoolAdapter = TypeAdapter(annotated_bool)
