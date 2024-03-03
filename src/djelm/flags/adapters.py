from typing_extensions import Annotated

from pydantic import Field, Strict, TypeAdapter


annotated_string = Annotated[str, Strict()]
annotated_int = Annotated[int, Strict()]
annotated_float = Annotated[float, Strict()]
annotated_bool = Annotated[bool, Strict()]
annotated_alias_key = Annotated[str, Field(pattern=r"^[a-z][A-Za-z0-9_]*$")]

StringAdapter = TypeAdapter(annotated_string)
IntAdapter = TypeAdapter(annotated_int)
FloatAdapter = TypeAdapter(annotated_float)
BoolAdapter = TypeAdapter(annotated_bool)
