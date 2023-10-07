from typing import Literal, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E")


@dataclass(slots=True)
class ExitSuccess(Generic[T]):
    value: T = None
    tag: Literal["Success"] = "Success"


@dataclass(slots=True)
class ExitFailure(Generic[T, E]):
    meta: T
    err: E
    tag: Literal["Failure"] = "Failure"
