from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(slots=True)
class ExitSuccess(Generic[T]):
    value: T
    tag: Literal["Success"] = "Success"


@dataclass(slots=True)
class ExitFailure(Generic[T, E]):
    meta: T
    err: E
    tag: Literal["Failure"] = "Failure"
