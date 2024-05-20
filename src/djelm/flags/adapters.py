from typing_extensions import Annotated
import typing

from pydantic import BeforeValidator, Field, Strict, TypeAdapter


def match_literal(v: str) -> typing.Callable[[str], str]:
    def do_match(v1):
        if v != v1:
            raise Exception(f"#{v} does not match #{v1} for string literal flag")
        else:
            return v1

    return do_match


def string_literal_adapter(v: str):
    return TypeAdapter(Annotated[str, Strict(), BeforeValidator(match_literal(v))])  # type:ignore


def annotated_string_literal(v: str):
    return Annotated[str, Strict(), BeforeValidator(match_literal(v))]


annotated_string = Annotated[str, Strict()]
annotated_int = Annotated[int, Strict()]
annotated_float = Annotated[float, Strict()]
annotated_bool = Annotated[bool, Strict()]
annotated_alias_key = Annotated[str, Field(pattern=r"^[a-z][A-Za-z0-9_]*$")]

StringAdapter = TypeAdapter(annotated_string)
IntAdapter = TypeAdapter(annotated_int)
FloatAdapter = TypeAdapter(annotated_float)
BoolAdapter = TypeAdapter(annotated_bool)
